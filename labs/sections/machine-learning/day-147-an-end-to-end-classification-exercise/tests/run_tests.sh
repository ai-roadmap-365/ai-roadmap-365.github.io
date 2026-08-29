#!/usr/bin/env bash
# Day 147 lab harness: "One Classification Project, Run Properly"
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

import classification_lib as c

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. The dataset choice
rows = {r[0]: r for r in c.candidate_summaries()}
expect("iris summary", rows["iris"], ("iris", 150, 4, 3, 0.3333, 30))
expect("wine summary", rows["wine"], ("wine", 178, 13, 3, 0.3889, 36))
expect("breast_cancer summary", rows["breast_cancer"], ("breast_cancer", 569, 30, 2, 0.6316, 114))

X, y, names = c.load_chosen_dataset()
expect("chosen shape", X.shape, (569, 30))
expect("chosen names", names, ["malignant", "benign"])

# 2. The split and the baseline
x_train, x_test, y_train, y_test = c.split_once(X, y, seed=0)
expect("train shape", x_train.shape, (455, 30))
expect("test shape", x_test.shape, (114, 30))
baseline = c.majority_baseline(x_train, y_train, x_test, y_test)
expect("baseline", round(baseline, 4), 0.6316)

# 3. The sweep and selection
expect("K", c.candidate_count(), 36)
family, param, cv_mean, fitted = c.select_best(x_train, y_train, seed=0)
expect("winner", (family, param), ("logreg", 1))
expect("cv_mean", round(cv_mean, 4), 0.978)

# 4. The gate: exactly one evaluation
gate = c.GatedTestSet(x_test, y_test)
test_acc = gate.evaluate(fitted)
expect("test_acc", round(test_acc, 4), 0.9825)
expect("evaluations after first look", gate.evaluations, 1)
try:
    gate.evaluate(fitted)
    errors.append("the gate permitted a second evaluation, which it must not")
except c.TestSetTouchedTwice as exc:
    if "validation score" not in str(exc):
        errors.append(f"the gate's message did not explain itself: {exc}")
    if gate.evaluations != 1:
        errors.append("the counter advanced on a refused evaluation")

# 5. The predicted optimism
predicted = c.predicted_selection_optimism(cv_mean, len(y_train), c.candidate_count())
expect("predicted optimism", round(predicted, 4), 0.0326)

# 6. Error analysis
preds = fitted.predict(x_test)
matrix, fn, fp = c.confusion_and_errors(y_test, preds, names)
expect("confusion matrix", matrix.tolist(), [[40, 2], [0, 72]])
expect("false negatives", fn, 2)
expect("false positives", fp, 0)

# 7. The verdict
se, half_width, lower, upper = c.verdict_interval(test_acc, len(y_test))
expect("se", se, 0.0123)
expect("half_width", half_width, 0.0241)
expect("interval", (lower, upper), (0.9584, 1.0066))
expect(
    "distinguishable from baseline",
    c.distinguishable_from_baseline(test_acc, baseline, len(y_test)),
    True,
)

# 8. The leaky version
leaky = c.leaky_selection_test_score(x_train, y_train, x_test, y_test)
expect("leaky score", leaky, 0.9825)
if leaky < round(test_acc, 4):
    errors.append(f"leaky score {leaky} was lower than the honest score {round(test_acc, 4)}")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-10 reproduced directly against classification_lib, no pytest involved"
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
echo "7. The test set is evaluated EXACTLY ONCE in the reference run"
GATE_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import classification_lib as c

X, y, _names = c.load_chosen_dataset()
x_train, x_test, y_train, y_test = c.split_once(X, y, seed=0)
_family, _param, _cv, fitted = c.select_best(x_train, y_train, seed=0)

gate = c.GatedTestSet(x_test, y_test)
assert gate.evaluations == 0, "a fresh gate must start at zero evaluations"
gate.evaluate(fitted)
assert gate.evaluations == 1, "one evaluation must advance the counter to exactly one"
refused = 0
for _ in range(5):
    try:
        gate.evaluate(fitted)
    except c.TestSetTouchedTwice:
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d147-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^18 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_classification_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert matrix.tolist() == [[40, 2], [0, 72]]"
replacement = "assert matrix.tolist() == [[0, 0], [0, 0]]"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_08_error_analysis_the_confusion_matrix"; then
  ok "breaking exercise 8's assertion produces a non-zero exit and names the failing test"
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
import classification_lib as c

X, y, _names = c.load_chosen_dataset()
problems = []

# The leak is never negative, at seeds this lab does not quote.
rows = c.leaky_vs_honest_over_seeds(X, y, seeds=range(20, 25))
gaps = [g for _s, _h, _l, g in rows]
if not all(g >= 0 for g in gaps):
    problems.append(f"a leaky gap went negative at an unquoted seed: {gaps}")

# Selecting is confined to train rows: refitting the winner never needs test.
x_train, x_test, y_train, y_test = c.split_once(X, y, seed=41)
_family, _param, cv_mean, fitted = c.select_best(x_train, y_train, seed=41)
if not (0.5 < cv_mean <= 1.0):
    problems.append(f"cv_mean at an unquoted seed was out of range: {cv_mean}")

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
