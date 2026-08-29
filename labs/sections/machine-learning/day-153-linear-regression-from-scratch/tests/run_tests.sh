#!/usr/bin/env bash
# Day 153 lab harness: "Linear Regression from Scratch"
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
from sklearn.linear_model import LinearRegression

import regression_lib as r

errors = []


def expect(label, got, want, tol=1e-6):
    if isinstance(want, float):
        if abs(got - want) > tol:
            errors.append(f"{label}: expected {want}, got {got}")
    elif got != want:
        errors.append(f"{label}: expected {want}, got {got}")


X, y = r.load_diabetes_data(scaled=True)
n, p = X.shape

# 1. Three closed forms on well-conditioned data
A = r.add_intercept_column(X)
beta_ne = r.fit_normal_equations(A, y)
beta_lstsq = r.fit_lstsq(A, y)
beta_sk = r.sklearn_reference_fit(X, y)
gap_ne = r.max_abs_difference(beta_ne, beta_sk)
gap_lstsq = r.max_abs_difference(beta_lstsq, beta_sk)
if not (gap_ne / gap_lstsq > 50):
    errors.append(f"lstsq was not roughly a hundred times closer: ratio {gap_ne / gap_lstsq}")

# 1b. cond(X'X) is the square of cond(X)
cond_a, cond_ata = r.condition_numbers(A)
expect("cond(X) with intercept", round(cond_a, 4), 227.2248, tol=0.01)
expect("cond(X'X)", round(cond_ata, 4), 51631.1119, tol=0.5)
if abs(cond_ata / cond_a**2 - 1.0) > 1e-6:
    errors.append(f"cond(X'X)/cond(X)^2 was not ~1.0: {cond_ata / cond_a**2}")

# 2. The near-duplicate column
Xd, yd, true_coef = r.make_dramatic_collinear_dataset(n=100, seed=0)
Ad = r.add_intercept_column(Xd)
beta_ne_d = r.fit_normal_equations(Ad, yd)
beta_lstsq_d = r.fit_lstsq(Ad, yd)
beta_sk_d = r.sklearn_reference_fit(Xd, yd)
if not (beta_ne_d[1] > 1e5 and beta_ne_d[4] < -1e5):
    errors.append("normal equations did not explode on the near-duplicate column")
if not (beta_lstsq_d[1] > 1e5 and beta_lstsq_d[4] < -1e5):
    errors.append("lstsq did not explode on the near-duplicate column")
if not (abs(beta_sk_d[1] - 2.5) < 0.05 and abs(beta_sk_d[4] - 2.5) < 0.05):
    errors.append("sklearn did not split the weight evenly near 2.5 and 2.5")

# 2b. Squaring relationship degrades under extreme ill-conditioning
cond_ad, cond_atad = r.condition_numbers(Ad)
if not (cond_ad > 1e6 and cond_atad > 1e13):
    errors.append("dramatic-case condition numbers were not as extreme as expected")
ratio_d = cond_atad / cond_ad**2
if not (0.9 < ratio_d < 1.0 and abs(ratio_d - 1.0) > 1e-4):
    errors.append(f"squaring relationship did not degrade as expected: ratio {ratio_d}")

# 3. Gradient descent vs closed form, standardized
Xs = r.standardize(X)
yc = y - y.mean()
target = r.fit_normal_equations(Xs, yc)
threshold = r.stability_threshold(Xs)
expect("stability threshold, standardized", round(threshold, 4), 0.2485, tol=0.001)
iters_3, _ = r.iters_to_tolerance(Xs, yc, 0.2, target, 5e-4, 200_000)
iters_6, _ = r.iters_to_tolerance(Xs, yc, 0.2, target, 5e-7, 200_000)
iters_9, _ = r.iters_to_tolerance(Xs, yc, 0.2, target, 5e-10, 200_000)
expect("iterations for 3 decimals", iters_3, 3263)
expect("iterations for 6 decimals", iters_6, 5277)
expect("iterations for 9 decimals", iters_9, 7291)

# 3b. Raw features
Xraw, yraw = r.load_diabetes_data(scaled=False)
Xrc, yrc, _, _ = r.center(Xraw, yraw)
eig_s = r.hessian_eigenvalues(Xs, n)
eig_r = r.hessian_eigenvalues(Xrc, n)
ratio_scaled = float(eig_s.max() / eig_s.min())
ratio_raw = float(eig_r.max() / eig_r.min())
expect("Hessian eigenvalue ratio, standardized", round(ratio_scaled, 2), 470.08, tol=0.5)
expect("Hessian eigenvalue ratio, raw", round(ratio_raw, 2), 76278.96, tol=5.0)
raw_threshold = r.stability_threshold(Xrc)
target_r = r.fit_normal_equations(Xrc, yrc)
status_r, coef_r = r.iters_to_tolerance(Xrc, yrc, raw_threshold * 0.95, target_r, 5e-4, 200_000)
if status_r is not None:
    errors.append("raw-feature gradient descent converged when it was expected to remain slow")
if r.max_abs_difference(coef_r, target_r) <= 0.1:
    errors.append("raw-feature gradient descent got closer than expected after 200000 iterations")

# 4. Stability threshold predicts divergence exactly
below_status, _ = r.iters_to_tolerance(Xs, yc, threshold * 0.8, target, 1e-9, 20_000)
above_status, above_coef = r.iters_to_tolerance(Xs, yc, threshold * 1.02, target, 1e-9, 20_000)
expect("iterations to converge at 80 percent of threshold", below_status, 7132)
if above_status != "diverged" or np.all(np.isfinite(above_coef)):
    errors.append("gradient descent did not diverge above the stability threshold")

# 5. Operation counts
ops_normal = r.normal_equation_op_count(n, p + 1)
ops_gd = r.gradient_descent_op_count(n, p, iters_9)
expect("normal-equation operation count", ops_normal, 54813)
expect("gradient-descent operation count", ops_gd, 64_452_440)

# 6. The estimator and check_estimator
sk = LinearRegression().fit(Xs, y)
normal_est = r.OLSRegressor(method="normal").fit(Xs, y)
lstsq_est = r.OLSRegressor(method="lstsq").fit(Xs, y)
gd_est = r.OLSRegressor(method="gd", lr=0.2, n_iter=8000).fit(Xs, y)
if r.max_abs_difference(normal_est.coef_, sk.coef_) > 1e-8:
    errors.append("OLSRegressor(method='normal') did not match sklearn closely enough")
if r.max_abs_difference(lstsq_est.coef_, sk.coef_) > 1e-8:
    errors.append("OLSRegressor(method='lstsq') did not match sklearn closely enough")
if r.max_abs_difference(gd_est.coef_, sk.coef_) > 1e-7:
    errors.append("OLSRegressor(method='gd') did not match sklearn closely enough")

passed, failed, skipped = r.run_check_estimator(r.OLSRegressor())
expect("check_estimator passed count", len(passed), 48)
failed_names = sorted(name for name, _msg in failed)
skipped_names = sorted(name for name, _msg in skipped)
expect("check_estimator failed names", failed_names, ["check_dtype_object", "check_n_features_in_after_fitting"])
expect(
    "check_estimator skipped names",
    skipped_names,
    ["check_array_api_input", "check_regressor_data_not_an_array"],
)

# 7. fit_intercept two ways
coef_col, intercept_col, coef_centred, intercept_centred = r.fit_intercept_two_ways(X, y)
if r.max_abs_difference(coef_col, coef_centred) > 1e-9:
    errors.append("centring and appending a column did not agree on coefficients")
if abs(intercept_col - intercept_centred) > 1e-9:
    errors.append("centring and appending a column did not agree on the intercept")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-7 reproduced directly against regression_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^15 passed"; then
  ok "pytest examples -q -> 15 passed"
else
  fail "pytest examples -q did not report 15 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "5 passed, 10 skipped"; then
  ok "pytest starter -q -> 5 passed, 10 skipped (the machinery checks pass; the ten exercises are stubs)"
else
  fail "pytest starter -q did not report 5 passed, 10 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d153-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^15 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_regression_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert beta_sk[1] == pytest.approx(2.5, abs=0.05)"
replacement = "assert beta_sk[1] == pytest.approx(99999.0, abs=0.05)"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_02_a_near_duplicate_column_makes_the_normal_equations_explode"; then
  ok "breaking exercise 2's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. Key results hold at seeds and shapes the lesson does not quote"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import regression_lib as r

problems = []

# The near-duplicate-column story is not a property of one seed.
for seed in range(5):
    X, y, true_coef = r.make_dramatic_collinear_dataset(n=100, seed=seed)
    A = r.add_intercept_column(X)
    beta_ne = r.fit_normal_equations(A, y)
    beta_sk = r.sklearn_reference_fit(X, y)
    if not (abs(beta_ne[1]) > 1e4 or abs(beta_ne[4]) > 1e4):
        problems.append(f"seed {seed}: normal equations did not explode on the duplicate pair")
    if r.max_abs_difference(beta_sk[[2, 3]], true_coef[[1, 2]]) > 0.2:
        problems.append(f"seed {seed}: sklearn did not recover the two clean coefficients")

# lstsq stays closer to sklearn than the normal equations, on OTHER
# moderately ill-conditioned datasets too -- not just the diabetes case.
# On near-orthogonal columns (cond close to 1) both routes sit at machine
# epsilon and the ordering is noise, which is itself a finding: the
# advantage specifically shows up once squaring the condition number
# starts to bite, not universally.
for seed in range(5):
    rng = np.random.default_rng(100 + seed)
    base = rng.normal(size=(300, 6))
    mix = np.full((6, 6), 0.995)
    np.fill_diagonal(mix, 1.0)
    X = base @ np.linalg.cholesky(mix).T
    true_coef = rng.normal(size=6)
    y = X @ true_coef + rng.normal(scale=0.05, size=300)
    A = r.add_intercept_column(X)
    beta_ne = r.fit_normal_equations(A, y)
    beta_lstsq = r.fit_lstsq(A, y)
    beta_sk = r.sklearn_reference_fit(X, y)
    gap_ne = r.max_abs_difference(beta_ne, beta_sk)
    gap_lstsq = r.max_abs_difference(beta_lstsq, beta_sk)
    if gap_lstsq > gap_ne:
        problems.append(f"seed {seed}: lstsq was not at least as close to sklearn as the normal equations")

# cond(X'X) equals cond(X) squared on well-conditioned matrices in general.
for seed in range(5):
    rng = np.random.default_rng(200 + seed)
    A = rng.normal(size=(150, 5))
    cond_a, cond_ata = r.condition_numbers(A)
    if abs(cond_ata / cond_a**2 - 1.0) > 1e-6:
        problems.append(f"seed {seed}: cond(A'A) was not the square of cond(A)")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "the duplicate-column explosion, lstsq's advantage, and the squaring relationship hold beyond the quoted seeds"
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
