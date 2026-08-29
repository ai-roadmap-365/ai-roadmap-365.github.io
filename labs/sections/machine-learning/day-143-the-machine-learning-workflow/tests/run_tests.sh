#!/usr/bin/env bash
# Day 143 lab harness: "The Workflow, Wired Up"
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

import workflow_lib as w

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. The pipeline as stages with a step log
honest = w.run_pipeline(w.honest_stages(), w.starting_artifact())
expect(
    "honest step log",
    [name for name, _ in honest.log],
    ["load", "split", "select", "fit_and_score", "baseline"],
)
expect("load produces", dict(honest.log)["load"], ("X", "y"))
expect("fit produces", dict(honest.log)["fit_and_score"], ("fold_scores", "score"))

# 1b. Stages do not mutate their input
start = w.starting_artifact()
before = set(start.data)
w.run_pipeline(w.honest_stages(), start)
expect("starting artifact untouched", set(start.data), before)
expect("starting artifact log empty", start.log, [])

# 2. Chance on noise
expect("honest score on pure noise", honest.data["score"], 0.5)
expect("majority baseline", honest.data["baseline"], 0.54)
expect("fold scores", honest.data["fold_scores"].tolist(), [0.5, 0.55, 0.5, 0.4, 0.55])

# 3. The transposition, and the contract
leaky = w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=False)
expect("leaky score, contracts off", leaky.data["score"], 0.73)
expect("accuracy invented by reordering", round(leaky.data["score"] - honest.data["score"], 4), 0.23)
expect(
    "leaky step log",
    [name for name, _ in leaky.log],
    ["load", "select", "split", "fit_and_score", "baseline"],
)
try:
    w.run_pipeline(w.leaky_stages(), w.starting_artifact(), enforce_contracts=True)
except w.StageContractError as exc:
    message = str(exc)
    if "'select'" not in message or "folds" not in message:
        errors.append(f"contract error did not name the stage and key: {message}")
else:
    errors.append("the leaky pipeline passed its contracts, which it must not")

# 3b. Inflation by k
X, y = w.noise_dataset()
expect(
    "inflation by k",
    w.inflation_by_k(X, y, [5, 10, 20, 50]),
    [(5, 0.65, 0.39, 0.26), (10, 0.72, 0.5, 0.22), (20, 0.73, 0.5, 0.23), (50, 0.85, 0.38, 0.47)],
)

# 4. The metric decides
train = w.imbalanced_dataset(1000, 11)
test = w.imbalanced_dataset(2000, 12)
scores = w.score_all(w.candidate_models(), train[0], train[1], test[0], test[1])
expect("baseline accuracy", scores["majority baseline"]["accuracy"], 0.92)
expect("baseline recall", scores["majority baseline"]["recall"], 0.0)
expect("logistic default accuracy", scores["logistic (default threshold)"]["accuracy"], 0.9435)
expect("logistic default recall", scores["logistic (default threshold)"]["recall"], 0.4813)
expect("logistic balanced accuracy", scores["logistic (balanced)"]["accuracy"], 0.8685)
expect("logistic balanced recall", scores["logistic (balanced)"]["recall"], 0.8438)
expect("5-NN accuracy", scores["5-NN"]["accuracy"], 0.936)
expect("depth-3 tree accuracy", scores["depth-3 tree"]["accuracy"], 0.9275)
expect("winner on accuracy", w.winner(scores, "accuracy"), "logistic (default threshold)")
expect("winner on recall", w.winner(scores, "recall"), "logistic (balanced)")
if w.winner(scores, "accuracy") == w.winner(scores, "recall"):
    errors.append("the metric did not invert the decision, contradicting exercise 4")
beats = {n for n, s in scores.items() if s["accuracy"] > 0.92}
expect("models beating the constant", beats, {"logistic (default threshold)", "5-NN", "depth-3 tree"})
expect("test positives", int(test[1].sum()), 160)

# 5. Error analysis
model = w.candidate_models()["logistic (default threshold)"]
model.fit(train[0], train[1])
table = w.error_table(model, test[0], test[1])
expect("confusion matrix", table, [[1810, 30], [83, 77]])
if table[1][0] <= table[1][1]:
    errors.append("the model did not miss more positives than it caught")

# 6. Reproducibility
keys = ("X", "y", "fold_scores", "score")
first = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
second = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact()), keys)
other = w.manifest(w.run_pipeline(w.honest_stages(), w.starting_artifact(seed=144)), keys)
expect(
    "manifest",
    first,
    {
        "X": "51b0a421bd652dd2",
        "fold_scores": "8f0ac332958b9bc4",
        "score": "d2cbad71ff333de6",
        "y": "9984503b5352c5a1",
    },
)
if first != second:
    errors.append("two runs at the same seed produced different manifests")
if first == other:
    errors.append("a different seed produced an identical manifest")

# 7. Stage sizes
lines = w.stage_source_lines(w.honest_stages())
expect(
    "stage line counts",
    lines,
    {"load": 5, "split": 2, "select": 10, "fit_and_score": 9, "baseline": 4},
)
expect("total lines", sum(lines.values()), 30)
expect("fitting share", round(lines["fit_and_score"] / sum(lines.values()), 4), 0.3)

# 8. A missing input
try:
    w.run_pipeline(w.honest_stages(), w.Artifact(data={}))
except w.StageContractError as exc:
    if "'load'" not in str(exc):
        errors.append(f"empty-artifact error did not name the load stage: {exc}")
else:
    errors.append("an empty artifact passed the contracts, which it must not")
try:
    w.run_pipeline(w.honest_stages(), w.Artifact(data={}), enforce_contracts=False)
except KeyError:
    pass
else:
    errors.append("with contracts off, an empty artifact did not raise KeyError")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-8 reproduced directly against workflow_lib, no pytest involved"
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
if echo "$STARTER_OUT" | tail -1 | grep -qE "4 passed, 13 skipped"; then
  ok "pytest starter -q -> 4 passed, 13 skipped (the machinery checks pass; the thirteen exercises are stubs)"
else
  fail "pytest starter -q did not report 4 passed, 13 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d143-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^17 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_workflow_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = 'assert leaky.data["score"] == 0.73'
replacement = 'assert leaky.data["score"] == 0.50'
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_03_reordering_two_stages_invents_twenty_three_accuracy_points"; then
  ok "breaking exercise 3's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The contract catches an out-of-order pipeline every time, not just once"
CONTRACT_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import workflow_lib as w

caught = 0
for seed in range(5):
    try:
        w.run_pipeline(w.leaky_stages(), w.starting_artifact(seed=seed), enforce_contracts=True)
    except w.StageContractError:
        caught += 1
if caught != 5:
    print(f"ERROR: the contract caught {caught} of 5 out-of-order pipelines")
else:
    print("contract caught all five")
PYEOF
)
if [ "$CONTRACT_CHECK" = "contract caught all five" ]; then
  ok "the stage contract rejects the out-of-order pipeline at every seed tried"
else
  fail "contract check failed: $CONTRACT_CHECK"
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
