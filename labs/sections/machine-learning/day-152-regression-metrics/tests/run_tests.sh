#!/usr/bin/env bash
# Day 152 lab harness: "What You Report Is Not What You Optimise"
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

import regression_metrics_lib as m

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. Noise-column climb
rows = m.noise_column_r2_curve()
expect(
    "noise-column curve",
    rows,
    [
        (0, 331, 10, 0.5554, 0.5415),
        (1, 331, 11, 0.5555, 0.5402),
        (5, 331, 15, 0.5648, 0.5441),
        (20, 331, 30, 0.5754, 0.5329),
        (100, 331, 110, 0.7403, 0.6104),
    ],
)
train_r2 = [row[3] for row in rows]
if not all(a < b for a, b in zip(train_r2, train_r2[1:])):
    errors.append("train R2 was not strictly increasing in the number of noise columns")

# 1b. Adjusted R2 corrects, then breaks down
by_noise = {row[0]: row for row in rows}
if not (by_noise[20][4] < by_noise[0][4]):
    errors.append("adjusted R2 at 20 noise columns did not fall below the baseline")
if not (by_noise[100][4] > by_noise[0][4]):
    errors.append("adjusted R2 at 100 noise columns did not rise back above the baseline")

# 2 and 2b. R2's bounds
expect("full-model test R2", m.full_model_test_r2(), 0.3594)
constant = m.constant_mean_test_r2()
if abs(constant) >= 0.001:
    errors.append(f"constant-mean test R2 was not near zero: {constant}")
expect("bad-predictor test R2", m.bad_predictor_test_r2(), -4.7009)

# 3. RMSE vs MAE under an outlier
expect(
    "outlier shift",
    m.rmse_mae_outlier_shift(),
    (2.4801, 1.9833, 28.2569, 5.9448),
)

# 4. MAPE breaking
if m.mape_at_zero_target() <= 1.0e10:
    errors.append("MAPE at a zero true value did not explode as expected")
expect("MAPE near zero", m.mape_near_zero_target(), (3.3667, 5.0))
expect("MAPE asymmetry bound", m.mape_asymmetry_bound(), (1.0, 10.0))

# 5. Ranking inversion
rmse_a, mae_a, rmse_b, mae_b = m.ranking_inversion_models()
expect("ranking inversion", (rmse_a, mae_a, rmse_b, mae_b), (1.947, 1.586, 4.4353, 0.8417))
if not (rmse_a < rmse_b and mae_b < mae_a):
    errors.append("the RMSE/MAE ranking did not invert between the two models")

# 6. Units
results = m.raw_and_scaled_metrics()
expect("scaled-feature metrics", results["scaled"], (56.3929, 45.1206, 0.3594))
expect("raw-feature metrics", results["raw"], (56.3929, 45.1206, 0.3594))

# 7. r2_score agreement and argument order
expect("r2_score vs model.score", m.r2_score_vs_model_score(), (0.359409, 0.359409))
expect("r2_score argument order", m.r2_score_argument_order(), (0.359409, -0.209635))

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "every claim reproduced directly against regression_metrics_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^16 passed"; then
  ok "pytest examples -q -> 16 passed"
else
  fail "pytest examples -q did not report 16 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "4 passed, 12 skipped"; then
  ok "pytest starter -q -> 4 passed, 12 skipped (the machinery checks pass; the twelve exercises are stubs)"
else
  fail "pytest starter -q did not report 4 passed, 12 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d152-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^16 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_metrics_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert (rmse_a, mae_a, rmse_b, mae_b) == (1.947, 1.586, 4.4353, 0.8417)"
replacement = "assert (rmse_a, mae_a, rmse_b, mae_b) == (0.0, 0.0, 0.0, 0.0)"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_06_rmse_and_mae_prefer_different_models"; then
  ok "breaking exercise 6's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. Key results hold at seeds the lesson does not quote"
SEED_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import regression_metrics_lib as m

problems = []

# The noise-column climb is not a property of one dataset seed.
for seed in (1, 2, 3):
    rows = m.noise_column_r2_curve(seed=seed)
    train_r2 = [row[3] for row in rows]
    if not (train_r2[-1] > train_r2[0]):
        problems.append(f"seed {seed}: train R2 did not climb with noise columns")

# The RMSE/MAE ranking inversion is not a property of one seed either.
for seed in (5, 6, 7):
    rmse_a, mae_a, rmse_b, mae_b = m.ranking_inversion_models(seed=seed)
    if not (rmse_a < rmse_b and mae_b < mae_a):
        problems.append(f"seed {seed}: the RMSE/MAE ranking did not invert")

# RMSE is never smaller than MAE, at other outlier shifts.
for shift in (50.0, 100.0, 500.0):
    _rb, mb, ra, ma = m.rmse_mae_outlier_shift(shift=shift)
    if not (ra >= ma):
        problems.append(f"shift {shift}: RMSE was smaller than MAE")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$SEED_CHECK" = "every direction held" ]; then
  ok "the noise-column climb and the RMSE/MAE ranking inversion hold at seeds the lesson does not quote"
else
  fail "a direction failed beyond the quoted seed"
  echo "$SEED_CHECK" | sed 's/^/    /'
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
