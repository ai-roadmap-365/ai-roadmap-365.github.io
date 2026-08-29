#!/usr/bin/env bash
# Day 148 lab harness: "One Line, Measured"
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


# 1. The BMI line
bmi, y = r.load_bmi_and_target()
model = r.fit_line(bmi, y)
residuals = y - model.predict(bmi)
expect("bmi slope", round(float(model.coef_[0]), 4), 10.2331)
expect("bmi intercept", round(float(model.intercept_), 4), -117.7734)
expect("bmi r2", round(float(model.score(bmi, y)), 4), 0.3439)
se = r.slope_standard_error(bmi, residuals)
expect("bmi slope se", round(se, 4), 0.6738)
expect("bmi slope ci", r.confidence_interval(float(model.coef_[0]), se), (8.9125, 11.5538))
predicted_at_mean, mean_y, diff = r.passes_through_the_means(model, bmi, y)
if abs(diff) >= 1e-8:
    errors.append(f"line does not pass through the means: diff={diff}")
if abs(r.residual_sum(residuals)) >= 1e-6:
    errors.append(f"residuals do not sum to zero: {r.residual_sum(residuals)}")

# 2. Recovering a known slope
rows = r.slope_recovery_error([20, 50, 200, 1000, 5000])
expect(
    "slope recovery",
    rows,
    [(20, 0.2315), (50, 0.1556), (200, 0.078), (1000, 0.0357), (5000, 0.0159)],
)
errs = [e for _n, e in rows]
if not all(a > b for a, b in zip(errs, errs[1:])):
    errors.append("slope recovery error did not strictly decrease with n")

# 3. Curvature
xc, yc = r.curved_dataset()
model_c = r.fit_line(xc, yc)
residuals_c = yc - model_c.predict(xc)
expect("curved r2", round(float(model_c.score(xc, yc)), 4), 0.852)
bins = r.binned_residual_means(xc, residuals_c, bins=5)
means = [m for _x, m in bins]
if not (means[0] > 0 and means[2] < 0 and means[-1] > 0):
    errors.append(f"curvature bins did not show positive/negative/positive: {means}")
expect("curvature quadratic r2", round(r.quadratic_fit_r_squared(xc, residuals_c), 4), 0.3558)

# 4. Heteroscedasticity
xh, yh = r.heteroscedastic_dataset()
model_h = r.fit_line(xh, yh)
residuals_h = yh - model_h.predict(xh)
expect("hetero r2", round(float(model_h.score(xh, yh)), 4), 0.5723)
low_sd, high_sd = r.residual_spread_by_half(xh, residuals_h)
expect("hetero low sd", round(low_sd, 4), 4.7427)
expect("hetero high sd", round(high_sd, 4), 12.0684)
expect("hetero ratio", round(high_sd / low_sd, 4), 2.5446)

# 5. Leverage
xl, yl = r.leverage_dataset()
model_without = r.fit_line(xl.reshape(-1, 1), yl)
xl_with, yl_with = r.add_point(xl, yl, x_new=40.0, y_new=5.0)
model_with = r.fit_line(xl_with.reshape(-1, 1), yl_with)
expect("leverage slope without", round(float(model_without.coef_[0]), 4), 1.5196)
expect("leverage slope with", round(float(model_with.coef_[0]), 4), 0.2138)
expect(
    "leverage slope change",
    round(float(model_with.coef_[0]) - float(model_without.coef_[0]), 4),
    -1.3059,
)
leverage_new = r.leverage_of_point(xl_with, 40.0)
typical = r.mean_leverage_excluding(xl_with, 40.0)
expect("leverage value", round(leverage_new, 4), 0.8048)
expect("leverage typical", round(typical, 4), 0.0299)
expect("leverage ratio", round(leverage_new / typical, 2), 26.94)

# 6. fit_intercept=False
xi, yi = r.intercept_dataset()
model_yes = r.fit_line(xi, yi, fit_intercept=True)
model_no = r.fit_line(xi, yi, fit_intercept=False)
rmse_yes = r.rmse(yi, model_yes.predict(xi))
rmse_no = r.rmse(yi, model_no.predict(xi))
expect("rmse with intercept", round(rmse_yes, 4), 6.1401)
expect("rmse without intercept", round(rmse_no, 4), 9.7878)
expect("rmse ratio", round(rmse_no / rmse_yes, 4), 1.5941)

# 7. Telling curvature apart from noise
expect("bmi quadratic r2", round(r.quadratic_fit_r_squared(bmi, residuals), 4), 0.0002)
expect("bmi residual skew", round(r.skewness(residuals), 4), 0.156)

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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d148-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^16 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_regression_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert round(rmse_no / rmse_yes, 4) == 1.5941"
replacement = "assert round(rmse_no / rmse_yes, 4) == 1.0"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_06_forcing_the_intercept_to_zero_costs_you"; then
  ok "breaking exercise 6's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The direction of every result holds beyond the quoted seed"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import regression_lib as r

problems = []

# Slope recovery error keeps shrinking at a different true slope and
# replication count.
rows = r.slope_recovery_error([20, 200, 2000], replications=80, true_slope=-3.0)
errs = [e for _n, e in rows]
if not all(a > b for a, b in zip(errs, errs[1:])):
    problems.append(f"slope recovery error did not shrink at true_slope=-3.0: {rows}")

# Curvature bins keep the same shape at other dataset seeds.
for seed in (2, 3, 4):
    x, y = r.curved_dataset(seed=seed)
    model = r.fit_line(x, y)
    resid = y - model.predict(x)
    means = [m for _x, m in r.binned_residual_means(x, resid, bins=5)]
    if not (means[0] > 0 and means[2] < 0 and means[-1] > 0):
        problems.append(f"seed {seed}: curvature bins lost their shape: {means}")

# Heteroscedasticity fans at other seeds.
for seed in (3, 4, 5):
    x, y = r.heteroscedastic_dataset(seed=seed)
    model = r.fit_line(x, y)
    resid = y - model.predict(x)
    low, high = r.residual_spread_by_half(x, resid)
    if high <= low * 1.5:
        problems.append(f"seed {seed}: heteroscedasticity ratio too small: {high / low:.4f}")

# The leverage point moves the slope substantially at other base seeds.
for seed in (10, 11, 12):
    x, y = r.leverage_dataset(seed=seed)
    m0 = r.fit_line(x.reshape(-1, 1), y)
    x2, y2 = r.add_point(x, y, 40.0, 5.0)
    m1 = r.fit_line(x2.reshape(-1, 1), y2)
    change = float(m1.coef_[0]) - float(m0.coef_[0])
    if change > -0.5:
        problems.append(f"seed {seed}: leverage point did not move the slope enough: {change:.4f}")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "slope recovery, curvature, heteroscedasticity and leverage all hold at seeds the lesson does not quote"
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
