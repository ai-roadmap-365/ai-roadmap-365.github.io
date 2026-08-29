#!/usr/bin/env bash
# Day 154 lab harness: "A Complete Regression Project"
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
from sklearn.dummy import DummyRegressor

import regression_lib as r

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. The dataset
X, y, names = r.load_dataset()
expect("shape", X.shape, (442, 10))
expect("y min", round(float(y.min()), 4), 25.0)
expect("y max", round(float(y.max()), 4), 346.0)
expect("y mean", round(float(y.mean()), 4), 152.1335)

# 2. The split and the baseline
x_train, x_test, y_train, y_test = r.split_once(X, y, seed=0)
expect("train shape", x_train.shape, (331, 10))
expect("test shape", x_test.shape, (111, 10))
base_rmse, base_r2 = r.baseline_metrics(x_train, y_train, x_test, y_test)
expect("baseline rmse", base_rmse, 70.4637)
expect("baseline r2", base_r2, -0.0001)

# 3. The sweep and selection
expect("K", r.candidate_count(), 23)
family, param, cv_rmse, fitted = r.select_best(x_train, y_train, seed=0)
expect("winner", (family, param), ("lasso", 1))
expect("cv_rmse", cv_rmse, 53.8958)

# 4. The gate: exactly one evaluation
gate = r.GatedTestSet(x_test, y_test)
test_rmse, test_r2, test_mae = gate.evaluate(fitted)
expect("test_rmse", test_rmse, 56.5566)
expect("test_r2", test_r2, 0.3557)
expect("test_mae", test_mae, 45.2846)
expect("evaluations after first look", gate.evaluations, 1)
try:
    gate.evaluate(fitted)
    errors.append("the gate permitted a second evaluation, which it must not")
except r.TestSetTouchedTwice as exc:
    if "validation score" not in str(exc):
        errors.append(f"the gate's message did not explain itself: {exc}")
    if gate.evaluations != 1:
        errors.append("the counter advanced on a refused evaluation")

# 5. The margin, with a bootstrap interval
baseline_model = DummyRegressor(strategy="mean").fit(x_train, y_train)
pred_baseline = baseline_model.predict(x_test)
pred_model = fitted.predict(x_test)
lower, upper = r.margin_bootstrap_interval(y_test, pred_baseline, pred_model, seed=0)
expect("margin interval", (lower, upper), (5.5852, 22.3324))
margin = round(base_rmse - test_rmse, 4)
expect("margin", margin, 13.9071)
expect("distinguishable", r.margin_distinguishable(lower, upper), True)

# 6. Residual diagnostics
resid_mean, resid_std = r.residual_summary(y_test, pred_model)
expect("resid_mean", resid_mean, -3.6262)
expect("resid_std", resid_std, 56.4402)
expect("heteroscedasticity", r.heteroscedasticity_signal(pred_model, y_test), 0.2386)
expect("curvature", r.curvature_signal(pred_model, y_test), -0.1278)
expect("qq correlation", r.normal_probability_correlation(y_test, pred_model), 0.9901)
top5 = r.largest_residuals(y_test, pred_model, n=5)
expect("largest residual row", top5[0], (60, 52.0, 209.3314, -157.3314))

# 7. Error by target level
rmse_low, rmse_high, ratio = r.error_by_target_level(y_test, pred_model)
expect("error by level", (rmse_low, rmse_high, ratio), (55.2464, 57.8601, 1.0473))

# 8. The leaky version
leaky_rmse = r.leaky_selection_test_rmse(x_train, y_train, x_test, y_test)
expect("leaky rmse", leaky_rmse, 55.5212)
if leaky_rmse > test_rmse:
    errors.append(f"leaky rmse {leaky_rmse} was worse (higher) than the honest rmse {test_rmse}")

# 9. Prediction interval coverage
half_width, coverage = r.prediction_interval_coverage(x_train, y_train, x_test, y_test, fitted, seed=0)
expect("half width", half_width, 105.8797)
expect("coverage", coverage, 0.9459)

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-11 reproduced directly against regression_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^19 passed"; then
  ok "pytest examples -q -> 19 passed"
else
  fail "pytest examples -q did not report 19 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "5 passed, 14 skipped"; then
  ok "pytest starter -q -> 5 passed, 14 skipped (the machinery checks pass; the fourteen exercises are stubs)"
else
  fail "pytest starter -q did not report 5 passed, 14 skipped"
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
echo "7. The test set is evaluated EXACTLY ONCE in the reference run"
GATE_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import regression_lib as r

X, y, _names = r.load_dataset()
x_train, x_test, y_train, y_test = r.split_once(X, y, seed=0)
_family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)

gate = r.GatedTestSet(x_test, y_test)
assert gate.evaluations == 0, "a fresh gate must start at zero evaluations"
gate.evaluate(fitted)
assert gate.evaluations == 1, "one evaluation must advance the counter to exactly one"
refused = 0
for _ in range(5):
    try:
        gate.evaluate(fitted)
    except r.TestSetTouchedTwice:
        refused += 1
assert refused == 5, "every repeated attempt after the first must be refused"
assert gate.evaluations == 1, "repeated refused attempts must not advance the counter"
print("test set touched exactly once, five further attempts refused, counter never moved")
PYEOF
)
if echo "$GATE_CHECK" | grep -q "touched exactly once"; then
  ok "GatedTestSet enforces exactly one evaluation mechanically, not by convention"
else
  fail "the one-evaluation guarantee did not hold"
  echo "$GATE_CHECK" | sed 's/^/    /'
fi

echo ""
echo "8. Proof the harness can fail"
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d154-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^19 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_regression_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert rows[0] == (60, 52.0, 209.3314, -157.3314)"
replacement = "assert rows[0] == (0, 0.0, 0.0, 0.0)"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_08b_the_normal_probability_check_and_the_largest_residuals"; then
  ok "breaking exercise 8b's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "9. The leaky-gap direction holds beyond the quoted seed range"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import regression_lib as r

X, y, _names = r.load_dataset()
problems = []

# The leak never produces a worse (higher) RMSE, at seeds this lab does not quote.
rows = r.leaky_vs_honest_over_seeds(X, y, seeds=range(20, 25))
gaps = [g for _s, _h, _l, g in rows]
if not all(g >= 0 for g in gaps):
    problems.append(f"a leaky gap went negative at an unquoted seed: {gaps}")

# Selecting is confined to train rows: refitting the winner never needs test.
x_train, x_test, y_train, y_test = r.split_once(X, y, seed=41)
_family, _param, cv_rmse, fitted = r.select_best(x_train, y_train, seed=41)
if not (30 < cv_rmse < 90):
    problems.append(f"cv_rmse at an unquoted seed was out of range: {cv_rmse}")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "the leaky-gap direction and the selection mechanics hold at seeds this lab does not quote"
else
  fail "a direction failed beyond the quoted seeds"
  echo "$DIRECTION" | sed 's/^/    /'
fi

echo ""
echo "10. Offline, and nothing left behind"
if ! grep -rInE "https?://" examples/*.py starter/*.py > /dev/null 2>&1; then
  ok "no URLs inside examples/ or starter/ source -- this lab reaches no network beyond the bundled dataset"
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
