#!/usr/bin/env bash
# Day 151 lab harness: "What the Penalty Does"
#
# Prints "N checks, M failure(s)" and exits 0 only when M is zero.
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-.venv/bin/python3}"
PYTEST="${PYTEST:-.venv/bin/pytest}"

# Clear caches at the START so the final cleanliness check measures what
# THIS run left behind, not what a previous manual pytest invocation left.
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
import regularization_lib as r

ALPHA_GRID = [0.001, 0.01, 0.1, 1.0]
PATH_ALPHAS = np.logspace(-3, 2, 60)

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. Ridge never zeros; lasso zeros progressively more
rows = r.zero_counts_and_r2(ALPHA_GRID)
expect(
    "zero counts and r2",
    rows,
    [
        (0.001, 0, 0.3588, 0, 0.3586),
        (0.01, 1, 0.3541, 0, 0.3567),
        (0.1, 3, 0.355, 0, 0.369),
        (1.0, 8, 0.2782, 0, 0.357),
    ],
)
ridge_zeros = [row[3] for row in rows]
lasso_zeros = [row[1] for row in rows]
expect("ridge zeros at every alpha", ridge_zeros, [0, 0, 0, 0])
if not all(a <= b for a, b in zip(lasso_zeros, lasso_zeros[1:])):
    errors.append("lasso zero count decreased somewhere as alpha grew")

# 1b. LassoCV
cv = r.lasso_cv_selection()
expect("LassoCV alpha", round(cv["alpha"], 5), 0.07874)
expect("LassoCV zeros", cv["zeros"], 4)
expect("LassoCV kept", cv["kept"], ["sex", "bmi", "bp", "s1", "s3", "s5"])
expect("LassoCV r2", cv["r2"], 0.3562)

# 2. Coefficient path
zero_at, ridge_ever_zero = r.alpha_where_each_lasso_coefficient_first_hits_zero(PATH_ALPHAS)
if any(v is None for v in zero_at.values()):
    errors.append("not every lasso coefficient zeroed within the sweep")
expect("ridge ever zero", ridge_ever_zero, False)
weakest_first = min(zero_at, key=zero_at.get)
strongest_last = max(zero_at, key=zero_at.get)
expect("weakest coefficient to zero", weakest_first, "s3")
expect("strongest coefficient to zero", strongest_last, "bmi")
expect("s3 zeros at", round(zero_at["s3"], 4), 0.0032)
expect("bmi zeros at", round(zero_at["bmi"], 4), 2.4538)

# 3. Sparse recovery
p1, r1, n1 = r.sparse_recovery(alpha=1.0, noise=1.0, seed=0)
expect("recovery precision, low noise", p1, 1.0)
expect("recovery recall, low noise", r1, 1.0)
expect("recovery n_selected, low noise", n1, 5)

# 3b. Recovery degrades
_p, r_high, n_high = r.sparse_recovery(alpha=80.0, noise=30.0, seed=0)
expect("recall, heavy penalty + noise", r_high, 0.2)
expect("n_selected, heavy penalty + noise", n_high, 1)
_p2, r_none, n_none = r.sparse_recovery(alpha=80.0, noise=10.0, seed=0)
expect("recall, heavy penalty zeroes truth", r_none, 0.0)
expect("n_selected, heavy penalty zeroes truth", n_none, 0)
mp_low, mr_low = r.sparse_recovery_across_seeds(alpha=1.0, noise=1.0)
mp_high, mr_high = r.sparse_recovery_across_seeds(alpha=1.0, noise=10.0)
expect("mean precision, low noise, 10 seeds", mp_low, 1.0)
expect("mean precision, high noise, 10 seeds", mp_high, 0.6792)
if not (mp_high < mp_low):
    errors.append("mean precision did not fall with more noise")

# 4. Scale dependence
scale = r.scale_dependence(alpha=1.0)
expect("raw n_kept", scale["raw"]["n_kept"], 10)
expect("standardized n_kept", scale["standardized"]["n_kept"], 7)
expect("sklearn_unit_norm n_kept", scale["sklearn_unit_norm"]["n_kept"], 3)
expect(
    "standardized kept set",
    scale["standardized"]["kept"],
    ["sex", "bmi", "bp", "s1", "s3", "s5", "s6"],
)
expect("sklearn_unit_norm kept set", scale["sklearn_unit_norm"]["kept"], ["bmi", "bp", "s5"])

# 5. ElasticNet
en_rows = r.elasticnet_sweep(alpha=0.1, l1_ratios=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
expect(
    "elasticnet sweep",
    en_rows,
    [
        (0.0, 0, 0.0555),
        (0.1, 0, 0.0605),
        (0.3, 0, 0.0741),
        (0.5, 0, 0.0963),
        (0.7, 1, 0.1389),
        (0.9, 0, 0.2511),
        (1.0, 3, 0.355),
    ],
)

# 5b. Ridge/ElasticNet alpha scale
ridge_head, elastic_head, max_diff = r.ridge_elasticnet_equivalence(alpha=0.1)
if not (max_diff < 0.001):
    errors.append(f"ridge/elasticnet correction did not converge: max_diff={max_diff}")
expect("ridge head", ridge_head, [6.3098, 1.229, 22.6076])
expect("elastic head", elastic_head, [6.3097, 1.229, 22.6076])

# 6. Near duplicates
_X, _y, correlation = r.near_duplicate_dataset()
if not (correlation > 0.999):
    errors.append(f"near-duplicate correlation too low: {correlation}")
dup_rows_1 = r.ridge_vs_lasso_on_duplicates([1.0])
_alpha, ridge_c, lasso_c = dup_rows_1[0]
if abs(ridge_c[0] - ridge_c[1]) >= 0.15:
    errors.append("ridge did not split the duplicate weight evenly at alpha=1.0")
if lasso_c[1] != 0.0:
    errors.append("lasso did not zero the second duplicate at alpha=1.0")

# 6b. High alpha
dup_rows_10 = r.ridge_vs_lasso_on_duplicates([10.0])
_alpha10, ridge_c10, lasso_c10 = dup_rows_10[0]
expect("lasso zeros both duplicates at alpha=10", lasso_c10, [0.0, 0.0, 0.0])
if not (ridge_c10[0] > 2.5 and ridge_c10[1] > 2.5):
    errors.append("ridge zeroed a duplicate at alpha=10, which it must never do")

# 7. Closed form vs iterative
info = r.ridge_has_no_iteration_count()
expect("ridge has n_iter_", info["ridge_has_n_iter"], False)
expect("lasso has n_iter_", info["lasso_has_n_iter"], True)
counts = r.lasso_iteration_counts(ALPHA_GRID)
expect("lasso iteration counts", counts, {0.001: 368, 0.01: 62, 0.1: 135, 1.0: 6})

# 8. The corner
ols, corner_rows = r.two_feature_corner_demo([0.001, 0.5, 1.0, 3.0, 8.0])
expect("OLS reference coefficients", ols, [1.9564, 1.9381])
by_alpha = {a: (rc, lc) for a, rc, lc in corner_rows}
ridge3, lasso3 = by_alpha[3.0]
expect("lasso lands on the axis at alpha=3.0", lasso3, [0.8919, 0.0])
if ridge3[0] == 0.0 or ridge3[1] == 0.0:
    errors.append("ridge produced an exact zero, which it must never do")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-8 reproduced directly against regularization_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^18 passed"; then
  ok "pytest examples -q -> 18 passed"
else
  fail "pytest examples -q did not report 18 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "4 passed, 14 skipped"; then
  ok "pytest starter -q -> 4 passed, 14 skipped (the machinery checks pass; the fourteen exercises are stubs)"
else
  fail "pytest starter -q did not report 4 passed, 14 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d151-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^18 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_regularization_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert lasso_x2 == 0.0"
replacement = "assert lasso_x2 == 999.0"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_06_ridge_splits_the_weight_between_near_duplicates"; then
  ok "breaking exercise 6's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The direction of every result holds beyond the quoted alpha or seed"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import regularization_lib as r

problems = []

# Ridge never zeros a coefficient, at alphas the lesson does not quote.
_lasso_path, ridge_path = r.coefficient_path(np.logspace(-4, 3, 25))
if np.any(ridge_path == 0.0):
    problems.append("ridge produced an exact zero at an unquoted alpha")

# Lasso's zero count is monotone non-decreasing over a different, denser grid.
alphas = np.logspace(-3, 0.5, 12)
lasso_zeros = []
X_train, X_test, y_train, y_test = r.load_train_test()
from sklearn.linear_model import Lasso
for a in alphas:
    lasso_zeros.append(int(np.sum(Lasso(alpha=a, max_iter=50000).fit(X_train, y_train).coef_ == 0)))
if not all(a <= b for a, b in zip(lasso_zeros, lasso_zeros[1:])):
    problems.append(f"lasso zero count was not monotone over a denser alpha grid: {lasso_zeros}")

# Near-duplicate splitting holds at other dataset seeds too.
for seed in (1, 2, 3):
    X, y, corr = r.near_duplicate_dataset(seed=seed)
    if corr <= 0.999:
        problems.append(f"seed {seed}: near-duplicate correlation too low ({corr})")
    from sklearn.linear_model import Ridge
    ridge = Ridge(alpha=1.0).fit(X, y)
    lasso = Lasso(alpha=1.0, max_iter=50000).fit(X, y)
    if abs(ridge.coef_[0] - ridge.coef_[1]) >= 0.2:
        problems.append(f"seed {seed}: ridge did not split the duplicate weight")
    # lasso need not land on an EXACT zero at every seed -- these columns
    # are correlated at 0.9999, not identically collinear -- but it must
    # produce a heavily asymmetric split rather than ridge's near-even one
    small, large = sorted(abs(c) for c in lasso.coef_[:2])
    if large < 20 * max(small, 1e-6):
        problems.append(f"seed {seed}: lasso did not produce an asymmetric split ({lasso.coef_[:2]})")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "ridge never-zeros, lasso monotone zeroing, and duplicate splitting hold beyond the quoted alphas and seeds"
else
  fail "a direction failed beyond the quoted alpha or seed"
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
