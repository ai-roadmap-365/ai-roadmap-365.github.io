#!/usr/bin/env bash
# Day 145 lab harness: "Two Ways to Be Wrong"
#
# Prints "N checks, M failure(s)" and exits 0 only when M is zero.
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-.venv/bin/python3}"
PYTEST="${PYTEST:-.venv/bin/pytest}"

find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf -- {} + 2>/dev/null
rm -rf .pytest_cache

CHECKS=0
FAILURES=0
ok() { CHECKS=$((CHECKS + 1)); echo "  ok: $1"; }
fail() { CHECKS=$((CHECKS + 1)); FAILURES=$((FAILURES + 1)); echo "  FAIL: $1"; }

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
  if [ "$installed" = "$pin_version" ]; then ok "$pkg $installed matches the pin"
  else fail "$pkg installed=$installed pinned=$pin_version"; fi
done < <(sed 's/==/ ==/' requirements/requirements.txt)

echo ""
echo "2. Every published claim, reproduced directly (no pytest involved)"
DIRECT_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import fitting_lib as f

errors = []
def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")

# 1. Capacity
rows = f.capacity_sweep([1, 2, 3, 4, 6, 8, 10, 14, 18, 24])
expect("capacity sweep", rows, [
    (1, 11.3217, 9.8274, -1.4942), (2, 11.3173, 9.8801, -1.4372),
    (3, 2.7076, 6.123, 3.4154), (4, 2.4964, 5.4911, 2.9948),
    (6, 1.9569, 15.8217, 13.8648), (8, 1.701, 26.1708, 24.4697),
    (10, 1.357, 528.4798, 527.1227), (14, 0.9685, 31307.2782, 31306.3097),
    (18, 1.0037, 75539.3618, 75538.3581), (24, 1.0321, 226667.4689, 226666.4368)])
expect("best degree", f.best_degree(rows), 4)
train = [r[1] for r in rows]
expect("train monotone through degree 14", f.is_monotonically_decreasing(train[:8]), True)
expect("train monotone overall", f.is_monotonically_decreasing(train), False)
expect("post-14 wobble", round(max(train[7:]) - min(train[7:]), 4), 0.0636)
gaps = {d: g for d, _t, _e, g in rows}
if not (gaps[1] < 0 and gaps[2] < 0):
    errors.append("the underfitting gap was not negative")
if not (0 < gaps[4] < 3.0):
    errors.append("the best model's gap was not small and positive")

# 2. Regularisation
reg = f.regularisation_sweep([0.0, 1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0])
expect("regularisation sweep", reg, [
    (0.0, 1.0321, 226667.4689), (1e-06, 1.2031, 130776.6548),
    (0.001, 1.5741, 128.3127), (0.1, 2.2259, 15.8339),
    (1.0, 2.7461, 5.7257), (10.0, 3.9689, 6.1559), (100.0, 6.28, 6.784)])
expect("best alpha", f.best_alpha(reg), 1.0)
expect("rescue factor", round(reg[0][2] / min(r[2] for r in reg), 0), 39588.0)
reg_train = [r[1] for r in reg]
if not all(a < b for a, b in zip(reg_train, reg_train[1:])):
    errors.append("training error did not rise monotonically with the penalty")

# 3. Data
data = f.data_sweep([15, 25, 50, 100, 400, 2000])
expect("data sweep", data, [
    (15, {1: 8.5023, 4: 4.9218, 24: 215413.2388}),
    (25, {1: 8.862, 4: 6.1904, 24: 64631547.2994}),
    (50, {1: 8.2457, 4: 4.2661, 24: 6070.3302}),
    (100, {1: 8.3583, 4: 4.2934, 24: 5.3571}),
    (400, {1: 8.3007, 4: 3.9958, 24: 4.3139}),
    (2000, {1: 8.2393, 4: 3.988, 24: 4.0055})])
expect("irreducible floor", f.irreducible_variance(), 4.0)
underfit = [s[1] for _n, s in data]
overfit = [s[24] for _n, s in data]
expect("underfit range", round(max(underfit) - min(underfit), 4), 0.6227)
if overfit[1] / overfit[-1] < 1e7:
    errors.append("more data did not cure the overfit model by seven orders of magnitude")
if abs(data[-1][1][24] - 4.0) > 0.01 or abs(data[-1][1][4] - 4.0) > 0.02:
    errors.append("the good models did not converge to the irreducible floor")
if overfit[1] != max(overfit):
    errors.append("the overfit column did not peak at the interpolation threshold")

# 4. Decomposition
worst = 0.0
for degree in (1, 2, 3, 4, 6, 8, 12):
    r = f.bias_variance(degree)
    rel = abs(r["predicted_total"] - r["observed"]) / r["observed"]
    worst = max(worst, rel)
    if rel >= 0.011:
        errors.append(f"degree {degree}: decomposition off by {rel:.4f}")
    if abs(r["bias_squared"] + r["variance"] + r["noise"] - r["predicted_total"]) > 0.0002:
        errors.append(f"degree {degree}: the parts did not sum to the total")
expect("worst decomposition disagreement", round(worst, 5), 0.01003)
one, three, twelve = f.bias_variance(1), f.bias_variance(3), f.bias_variance(12)
expect("degree 1 bias squared", one["bias_squared"], 4.2985)
expect("degree 1 variance", one["variance"], 0.7112)
expect("degree 3 bias squared", three["bias_squared"], 0.0033)
expect("degree 12 variance", twelve["variance"], 452183.1336)
if one["bias_squared"] / one["variance"] <= 6:
    errors.append("bias did not dominate at degree 1")
if twelve["variance"] / twelve["bias_squared"] <= 100:
    errors.append("variance did not dominate at degree 12")
two = f.bias_variance(2)
expect("degree 2 bias squared", two["bias_squared"], 4.3342)
if two["bias_squared"] <= one["bias_squared"]:
    errors.append("degree 2 did not have more bias than degree 1")

# 5. Early stopping
train_hist, test_hist = f.training_history()
expect("epochs", len(train_hist), 600)
expect("training monotone", f.is_monotonically_decreasing(train_hist), True)
expect("first training error", round(train_hist[0], 4), 7.3906)
expect("last training error", round(train_hist[-1], 4), 2.4744)
best = int(np.argmin(test_hist))
expect("best epoch index", best, 13)
expect("best test error", round(test_hist[best], 4), 5.4555)
expect("test error at 600", round(test_hist[-1], 4), 5.8978)
expect("worst after best", round(max(test_hist[best + 1:]), 4), 7.1435)
expect("epochs worse than best", sum(1 for v in test_hist if v > min(test_hist)), 599)
expect("first gap", round(test_hist[0] - train_hist[0], 4), 0.6771)
expect("last gap", round(test_hist[-1] - train_hist[-1], 4), 3.4234)
for patience in (5, 10, 20, 50):
    expect(f"patience {patience}", f.stop_with_patience(test_hist, patience), best)

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-5 reproduced directly against fitting_lib, no pytest involved"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d145-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^18 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_fitting_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert f.best_degree(rows) == 4"
replacement = "assert f.best_degree(rows) == 24"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_01_training_error_falls_with_capacity_and_test_error_does_not"; then
  ok "breaking exercise 1's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The shape of every result survives a different data seed"
SHAPE=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import fitting_lib as f

problems = []
for seed in (301, 302, 303):
    rows = f.capacity_sweep([1, 3, 4, 8, 24], train_seed=seed, test_seed=seed + 50)
    test = {d: t for d, _tr, t, _g in rows}
    train = {d: tr for d, tr, _t, _g in rows}
    if train[24] >= train[1]:
        problems.append(f"seed {seed}: training error did not fall with capacity")
    if test[24] <= test[4]:
        problems.append(f"seed {seed}: the degree-24 model did not overfit")
    if test[1] <= test[4]:
        problems.append(f"seed {seed}: the degree-1 model did not underfit")

# And the decomposition's shape: bias dominant when rigid, variance when not.
low = f.bias_variance(1, datasets=60)
high = f.bias_variance(12, datasets=60)
if low["bias_squared"] <= low["variance"]:
    problems.append("bias did not dominate for the rigid model at a smaller sample")
if high["variance"] <= high["bias_squared"]:
    problems.append("variance did not dominate for the flexible model at a smaller sample")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every shape held")
PYEOF
)
if [ "$SHAPE" = "every shape held" ]; then
  ok "underfitting, overfitting and the decomposition's shape hold at seeds the lesson does not quote"
else
  fail "a shape failed beyond the quoted seed"
  echo "$SHAPE" | sed 's/^/    /'
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
if [ "$FAILURES" -ne 0 ]; then exit 1; fi
exit 0
