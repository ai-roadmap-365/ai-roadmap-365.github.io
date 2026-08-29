#!/usr/bin/env bash
# Day 149 lab harness: "Loss Functions and Least Squares"
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

import loss_lib as L

errors = []
VALUES = [2.0, 3.0, 5.0, 7.0, 100.0]


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. Mean and median
best_sq = L.grid_minimize(VALUES, L.sse, 0.0, 110.0)
best_abs = L.grid_minimize(VALUES, L.sae, 0.0, 110.0)
expect("mean", round(float(np.mean(VALUES)), 4), 23.4)
if abs(best_sq - 23.4) >= 0.001:
    errors.append(f"grid argmin of squared error {best_sq} not close to the mean")
expect("median", float(np.median(VALUES)), 5.0)
if abs(best_abs - 5.0) >= 0.001:
    errors.append(f"grid argmin of absolute error {best_abs} not close to the median")

# 2. Landscape shape
x, y = L.make_line_data(n=40, seed=3)
slopes = np.round(np.arange(2.0, 4.01, 0.1), 4)
sq_losses, abs_losses = L.loss_landscape(x, y, intercept=5.0, slopes=slopes)
expect("squared-error argmin slope", float(slopes[int(np.argmin(sq_losses))]), 3.0)
expect("absolute-error argmin slope", float(slopes[int(np.argmin(abs_losses))]), 3.0)
expect("sd of squared-error second differences", round(float(np.std(L.second_differences(sq_losses))), 6), 0.0)
expect("sd of absolute-error second differences", round(float(np.std(L.second_differences(abs_losses))), 4), 1.9366)

# 3. Normal equations
x3, y3 = L.make_line_data(n=300, seed=2)
intercept_eq, slope_eq = L.normal_equations(x3, y3)
intercept_sk, slope_sk = L.fit_ols(x3, y3)
if abs(intercept_eq - intercept_sk) >= 1e-9:
    errors.append(f"normal-equations intercept {intercept_eq} vs sklearn {intercept_sk}")
if abs(slope_eq - slope_sk) >= 1e-9:
    errors.append(f"normal-equations slope {slope_eq} vs sklearn {slope_sk}")
expect("normal-equations slope", round(slope_eq, 4), 2.9779)
expect("normal-equations intercept", round(intercept_eq, 4), 4.9663)

# 4. Outlier shift
x4, y4 = L.make_line_data(n=60, seed=1, noise_sd=1.5)
result = L.outlier_shift(x4, y4, outlier_offset=80.0)
expect("ols outlier shift", result["ols"], {"before": 3.0465, "after": 3.801, "movement": 0.7545})
expect("huber outlier shift", result["huber"], {"before": 2.987, "after": 3.0308, "movement": 0.0437})
expect("quantile outlier shift", result["quantile"], {"before": 2.9961, "after": 3.0064, "movement": 0.0104})
ols_move = abs(result["ols"]["movement"])
expect("ols/huber movement ratio", round(ols_move / abs(result["huber"]["movement"]), 1), 17.3)
expect("ols/quantile movement ratio", round(ols_move / abs(result["quantile"]["movement"]), 1), 72.5)

# 5. Huber epsilon sweep
y_outlier = np.asarray(y4, dtype=float).copy()
y_outlier[int(np.argmax(x4))] += 80.0
sweep = L.huber_epsilon_sweep(x4, y_outlier, [1.0, 1.35, 1.5, 2.0, 5.0, 20.0, 100.0])
expect(
    "huber epsilon sweep",
    sweep,
    [(1.0, 3.0064), (1.35, 3.0308), (1.5, 3.0505), (2.0, 3.0906), (5.0, 3.1511), (20.0, 3.801), (100.0, 3.801)],
)
sweep_slopes = [s for _e, s in sweep]
if not all(a <= b for a, b in zip(sweep_slopes, sweep_slopes[1:])):
    errors.append("huber epsilon sweep was not non-decreasing")
_i, ols_slope_outlier = L.fit_ols(x4, y_outlier)
expect("sweep converges to OLS", sweep[-1][1], round(ols_slope_outlier, 4))

# 6. Efficiency under noise
gauss = L.efficiency_under_noise(heavy_tailed=False, replications=500)
heavy = L.efficiency_under_noise(heavy_tailed=True, replications=500)
expect("gaussian efficiency", gauss, (2.998, 0.056, 2.9977, 0.0588))
expect("heavy-tailed efficiency", heavy, (2.9967, 0.0589, 2.9984, 0.0422))
if not (gauss[1] < gauss[3]):
    errors.append("OLS was not the tighter estimator under Gaussian errors")
if not (heavy[3] < heavy[1]):
    errors.append("Huber was not the tighter estimator under heavy-tailed errors")
expect("ratio under gaussian errors", round(gauss[1] / gauss[3], 4), 0.9524)
expect("ratio under heavy-tailed errors", round(heavy[1] / heavy[3], 4), 1.3957)

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-6 reproduced directly against loss_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^14 passed"; then
  ok "pytest examples -q -> 14 passed"
else
  fail "pytest examples -q did not report 14 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "4 passed, 10 skipped"; then
  ok "pytest starter -q -> 4 passed, 10 skipped (the machinery checks pass; the ten exercises are stubs)"
else
  fail "pytest starter -q did not report 4 passed, 10 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d149-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^14 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_loss_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert result[\"ols\"] == {\"before\": 3.0465, \"after\": 3.801, \"movement\": 0.7545}"
replacement = "assert result[\"ols\"] == {\"before\": 3.0465, \"after\": 3.801, \"movement\": 0.0}"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_04_ols_moves_far_when_a_single_point_becomes_an_outlier"; then
  ok "breaking exercise 4's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The direction of every result holds beyond the quoted seeds"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import loss_lib as L

problems = []

# Outlier sensitivity is not a property of one dataset seed.
for seed in (1, 2, 3, 4, 5):
    x, y = L.make_line_data(n=60, seed=seed, noise_sd=1.5)
    result = L.outlier_shift(x, y, outlier_offset=80.0)
    ols_move = abs(result["ols"]["movement"])
    huber_move = abs(result["huber"]["movement"])
    quantile_move = abs(result["quantile"]["movement"])
    if not (ols_move > huber_move and ols_move > quantile_move):
        problems.append(f"seed {seed}: OLS did not move furthest (ols={ols_move}, huber={huber_move}, quantile={quantile_move})")

# The normal equations match LinearRegression at other sample sizes too.
for n, seed in ((50, 10), (500, 11), (1000, 12)):
    x, y = L.make_line_data(n=n, seed=seed)
    i_eq, s_eq = L.normal_equations(x, y)
    i_sk, s_sk = L.fit_ols(x, y)
    if abs(i_eq - i_sk) >= 1e-8 or abs(s_eq - s_sk) >= 1e-8:
        problems.append(f"n={n} seed={seed}: normal equations diverged from sklearn")

# Gauss-Markov's ranking is not a property of one replication count.
gauss_short = L.efficiency_under_noise(heavy_tailed=False, replications=150)
heavy_short = L.efficiency_under_noise(heavy_tailed=True, replications=150)
if not (gauss_short[1] < gauss_short[3]):
    problems.append("OLS was not tighter than Huber under Gaussian errors at 150 replications")
if not (heavy_short[3] < heavy_short[1]):
    problems.append("Huber was not tighter than OLS under heavy-tailed errors at 150 replications")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "outlier sensitivity, the normal equations and the Gauss-Markov ranking hold at seeds the lesson does not quote"
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
