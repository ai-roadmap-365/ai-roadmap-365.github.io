#!/usr/bin/env bash
# Day 150 lab harness: "Many Predictors, One Model"
#
# Prints "N checks, M failure(s)" and exits 0 only when M is zero.
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-.venv/bin/python3}"
PYTEST="${PYTEST:-.venv/bin/pytest}"

# Clear caches at the START so the final cleanliness check measures what
# THIS run left behind, not what a previous `pytest starter -q` left.
find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf -- {} + 2>/dev/null
rm -rf .pytest_cache

CHECKS=0
FAILURES=0

ok() {
  CHECKS=$((CHECKS + 1))
  echo "  ok: $1"
}

fail() {
  CHECKS=$((CHECKS + 1))
  FAILURES=$((FAILURES + 1))
  echo "  FAIL: $1"
}

if [ ! -x "$PYTHON" ]; then
  echo "No lab .venv found at $PYTHON."
  echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements/requirements.txt"
  exit 2
fi

echo "1. Installed versions match requirements/requirements.txt"
VERSION_CHECK=$("$PYTHON" - <<'PYEOF'
import numpy, sklearn, pytest
print("numpy", numpy.__version__)
print("scikit-learn", sklearn.__version__)
print("pytest", pytest.__version__)
PYEOF
)
echo "$VERSION_CHECK" | sed 's/^/    /'
while read -r pkg pin; do
  pin_version="${pin#*==}"
  installed=$(echo "$VERSION_CHECK" | awk -v p="$pkg" '$1==p {print $2}')
  if [ "$installed" = "$pin_version" ]; then
    ok "$pkg $installed matches the pin"
  else
    fail "$pkg installed=$installed pinned=$pin_version"
  fi
done < <(sed 's/==/ ==/' requirements/requirements.txt)

echo ""
echo "2. Every published claim, reproduced directly (no pytest involved)"
DIRECT_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")

import numpy as np

import regression_lib as r

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


X, y, names = r.load_raw_diabetes()

# 1. VIF and correlation
vifs = r.variance_inflation_factors(X, names)
expect(
    "variance inflation factors",
    vifs,
    {
        "age": 1.2173, "sex": 1.2781, "bmi": 1.5094, "bp": 1.4594,
        "s1": 59.2025, "s2": 39.1934, "s3": 15.4022, "s4": 8.891,
        "s5": 10.076, "s6": 1.4846,
    },
)
expect("correlation s1,s2", round(r.correlation(X, names, "s1", "s2"), 4), 0.8967)
expect("correlation s3,s4", round(r.correlation(X, names, "s3", "s4"), 4), -0.7385)

# 2. Exact duplicate
idx_s1 = names.index("s1")
original, coef_a, coef_b, max_diff, r2_orig, r2_dup = r.duplicate_column_exact(X, y, idx_s1)
expect("original s1 coefficient", round(original, 4), -1.09)
expect("duplicate coefficient a", round(coef_a, 4), -0.545)
expect("duplicate coefficient b", round(coef_b, 4), -0.545)
if abs((coef_a + coef_b) - original) >= 1e-8:
    errors.append("the two duplicate coefficients did not sum to the original")
if max_diff >= 1e-10:
    errors.append(f"exact duplicate moved predictions by {max_diff}")
if abs(r2_dup - r2_orig) >= 1e-10:
    errors.append("exact duplicate changed R2")

# 3. Noisy duplicate
noise_scale = 0.01 * float(X[:, idx_s1].std())
n_coef_a, n_coef_b, n_sum, n_max_diff, n_r2 = r.duplicate_column_noisy(X, y, idx_s1, noise_scale, seed=0)
expect("noisy coefficient a (seed 0)", round(n_coef_a, 4), 0.7592)
expect("noisy coefficient b (seed 0)", round(n_coef_b, 4), -1.8451)
expect("noisy sum (seed 0)", round(n_sum, 4), -1.0859)
spread10 = r.duplicate_noisy_spread(X, y, idx_s1, noise_scale, range(10))
if spread10["coef_a"]["sd"] <= 4.0 or spread10["coef_b"]["sd"] <= 4.0:
    errors.append("noisy coefficients were less volatile than expected")
if spread10["sum"]["sd"] >= 0.05:
    errors.append(f"the sum was less stable than expected: sd={spread10['sum']['sd']}")
expect("sum mean, seeds 0-9 (2dp)", round(spread10["sum"]["mean"], 2), -1.09)
if spread10["max_pred_diff_overall"] >= 10.0:
    errors.append("predictions moved more than expected across noise seeds")

# 4. Bootstrap instability
boot = r.bootstrap_coefficient_spread(X, y, names, reps=500, seed=0)
expect("bootstrap s1 cv (2dp)", round(boot["s1"]["cv"], 2), 0.51)
expect("bootstrap bmi cv (2dp)", round(boot["bmi"]["cv"], 2), 0.13)
if boot["s1"]["cv"] <= boot["bmi"]["cv"]:
    errors.append("high-VIF predictor was not more unstable than a low-VIF one")

# 5. Sign flips
svm = r.simple_vs_multiple_coefficients(X, y, names)
flips = {name for name, v in svm.items() if v["sign_flip"]}
expect("predictors whose sign flips", flips, {"age", "sex", "s1", "s3"})
expect("s1 simple coefficient", svm["s1"]["simple"], 0.4723)
expect("s1 multiple coefficient", svm["s1"]["multiple"], -1.09)

# 6. Polynomial equals normal equations
idx_bmi, idx_bp = names.index("bmi"), names.index("bp")
X2 = X[:, [idx_bmi, idx_bp]]
poly_names, sk_coefs, sk_intercept, ne_coefs, ne_intercept, coef_diff, intercept_diff = (
    r.polynomial_matches_normal_equations(X2, y, degree=2, feature_names=["bmi", "bp"])
)
expect("expanded design matrix columns", poly_names, ["bmi", "bp", "bmi^2", "bmi bp", "bp^2"])
expect("sklearn coefficients == normal-eq coefficients", sk_coefs, ne_coefs)
if coef_diff >= 1e-9 or intercept_diff >= 1e-9:
    errors.append("sklearn and the normal equations disagreed beyond floating-point noise")

r2_with, r2_without, interaction_coef = r.interaction_term_effect(X2, y)
expect("R2 with interaction term", round(r2_with, 6), 0.40417)
expect("R2 without interaction term", round(r2_without, 6), 0.399896)
if r2_with <= r2_without:
    errors.append("the interaction term did not improve R2")

# 7. R2 with added noise columns
rows = r.r2_with_added_noise_columns(X, y, [1, 2, 5, 10], seed=42)
expect(
    "R2 with added noise columns",
    rows,
    [
        (1, 0.518064, 0.000316),
        (2, 0.523041, 0.005293),
        (5, 0.527615, 0.009867),
        (10, 0.532455, 0.014707),
    ],
)
r2_col = [row[1] for row in rows]
if not all(a < b for a, b in zip(r2_col, r2_col[1:])):
    errors.append("R2 did not strictly increase as noise columns were added")

# 8. Scaling
raw_coefs, scaled_coefs, r2_raw, r2_scaled, max_pred_diff = r.scaling_effect(X, y)
expect("raw s1 coefficient", raw_coefs[idx_s1], -1.09)
expect("scaled s1 coefficient", scaled_coefs[idx_s1], -37.68)
if r2_raw != r2_scaled:
    errors.append("scaling changed R2, which it must not")
if max_pred_diff >= 1e-9:
    errors.append("scaling changed predictions, which it must not")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-8 reproduced directly against regression_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^17 passed"; then
  ok "pytest examples -q -> 17 passed"
else
  fail "pytest examples -q did not report 17 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "5 passed, 12 skipped"; then
  ok "pytest starter -q -> 5 passed, 12 skipped (the machinery checks pass; the twelve exercises are stubs)"
else
  fail "pytest starter -q did not report 5 passed, 12 skipped"
  echo "$STARTER_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "5. pytest examples starter (one invocation) aborts on the module-name collision"
COMBINED_OUT=$("$PYTEST" examples starter 2>&1)
if echo "$COMBINED_OUT" | grep -q "import file mismatch"; then
  ok "combined invocation reports import file mismatch, as documented -- never run starter and examples together"
else
  fail "combined invocation did not fail with import file mismatch as expected"
fi

echo ""
echo "6. The report reproduces the captured table exactly"
REPORT_OUT=$("$PYTHON" examples/report_measurements.py 2>&1)
if [ "$REPORT_OUT" = "$(cat expected-output/measured-values.txt)" ]; then
  ok "report_measurements.py output is byte-identical to expected-output/measured-values.txt"
else
  fail "report_measurements.py drifted from expected-output/measured-values.txt"
  echo "$REPORT_OUT" | diff - expected-output/measured-values.txt | head -20 | sed 's/^/    /'
fi

echo ""
echo "7. Proof the harness can fail"
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d150-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^17 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_regression_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = 'assert round(interaction_coef, 6) == 0.095079'
replacement = 'assert round(interaction_coef, 6) == 0.0'
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_06b_dropping_the_interaction_term_costs_real_r_squared"; then
  ok "breaking exercise 6b's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. Key results hold at seeds and predictors the lesson does not quote"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import regression_lib as r

problems = []
X, y, names = r.load_raw_diabetes()

# The duplicate-column contrast is not a property of one noise seed.
idx_s1 = names.index("s1")
noise_scale = 0.01 * float(X[:, idx_s1].std())
for seeds in ([10, 11, 12, 13, 14], [20, 21, 22, 23, 24]):
    spread = r.duplicate_noisy_spread(X, y, idx_s1, noise_scale, seeds)
    if spread["coef_a"]["sd"] <= 2.0:
        problems.append(f"seeds {seeds}: coefficient a was not volatile ({spread['coef_a']['sd']})")
    if spread["sum"]["sd"] >= 0.1:
        problems.append(f"seeds {seeds}: the sum was not stable ({spread['sum']['sd']})")

# The duplicate contrast is not specific to s1: try s2 (also high VIF).
idx_s2 = names.index("s2")
noise_scale_s2 = 0.01 * float(X[:, idx_s2].std())
spread_s2 = r.duplicate_noisy_spread(X, y, idx_s2, noise_scale_s2, range(5))
if spread_s2["coef_a"]["sd"] <= 1.0:
    problems.append("duplicating s2 did not produce unstable coefficients")
if spread_s2["sum"]["sd"] >= 0.1:
    problems.append("duplicating s2 did not leave the sum stable")

# R2 never decreasing is not a property of seed 42 alone.
for seed in (1, 2, 3):
    rows = r.r2_with_added_noise_columns(X, y, [1, 3, 8], seed=seed)
    values = [row[1] for row in rows]
    if not all(a < b for a, b in zip(values, values[1:])):
        problems.append(f"seed {seed}: R2 did not strictly increase with added noise columns")

# Bootstrap instability tracking VIF is not a property of one replication count.
boot = r.bootstrap_coefficient_spread(X, y, names, reps=150, seed=3)
if boot["s2"]["cv"] <= boot["bp"]["cv"]:
    problems.append("at a different replication count, a high-VIF predictor was not more unstable")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "duplicate-column instability, R2 monotonicity and VIF-linked instability hold beyond the quoted seeds and predictors"
else
  fail "a direction failed beyond the quoted seed"
  echo "$DIRECTION" | sed 's/^/    /'
fi

echo ""
echo "9. Offline, and nothing left behind"
if ! grep -rInE "https?://" examples/*.py starter/*.py > /dev/null 2>&1; then
  ok "no URLs inside examples/ or starter/ source -- this lab reaches no network"
else
  fail "found a URL inside examples/ or starter/"
fi
if [ -z "$(find . -path ./.venv -prune -o -type d -name '__pycache__' -print 2>/dev/null)" ]; then
  ok "no __pycache__ left behind"
else
  find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf -- {} + 2>/dev/null
  ok "no __pycache__ left behind (cleaned during this run)"
fi
if [ ! -d .pytest_cache ]; then
  ok "no .pytest_cache left behind"
else
  rm -rf .pytest_cache
  ok "no .pytest_cache left behind (cleaned during this run)"
fi

echo ""
echo "---------------------------------------------------------------"
echo "$CHECKS checks, $FAILURES failure(s)"
if [ "$FAILURES" -ne 0 ]; then
  exit 1
fi
exit 0
