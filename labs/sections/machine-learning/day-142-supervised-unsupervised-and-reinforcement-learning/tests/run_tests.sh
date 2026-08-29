#!/usr/bin/env bash
# Day 142 lab harness: "Three Kinds of Feedback"
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

import feedback_lib as f

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


X, y = f.iris_features_and_labels()

# 1. Supervised: an answer per example
train, test = f.split_indices(len(y), 100, seed=142)
expect("5-NN on iris", f.supervised_score(X, y, train, test, n_neighbors=5), 0.92)
expect("training rows", len(train), 100)

# 2. Cluster ids are arbitrary
assignment = f.cluster(X, 3, seed=0).labels_
raw = f.raw_cluster_accuracy(y, assignment)
best, mapping = f.best_permutation_accuracy(y, assignment)
expect("raw cluster accuracy", raw, 0.24)
expect("best-permutation accuracy", round(best, 10), 0.8933333333)
expect("relabelling", mapping, (1, 0, 2))
expect("gap from numbering alone", round(best - raw, 4), 0.6533)

# 3. What k-means found
table = f.cluster_confusion(y, assignment, 3, 3)
expect("species 0 row", table[0].tolist(), [0, 50, 0])
expect("species 1 row", table[1].tolist(), [48, 0, 2])
expect("species 2 row", table[2].tolist(), [14, 0, 36])

# 4. Structure is not unique
scaled = f.cluster(f.standardise(X), 3, seed=0).labels_
expect("ARI raw vs scaled", round(f.agreement(assignment, scaled), 10), 0.803611742)
raw_truth = f.agreement(y, assignment)
scaled_truth = f.agreement(y, scaled)
expect("ARI raw vs species", round(raw_truth, 10), 0.7302382723)
expect("ARI scaled vs species", round(scaled_truth, 10), 0.6201351809)
if scaled_truth >= raw_truth:
    errors.append("standardising did not move away from the species, contradicting exercise 4")

# 5. k is a choice
ks = [2, 3, 4, 5, 6]
inertia = f.inertia_curve(X, ks)
silhouette = f.silhouette_curve(X, ks)
expect("inertia curve", [round(v, 3) for v in inertia], [152.348, 78.851, 57.228, 46.446, 39.04])
expect(
    "silhouette curve",
    [round(v, 4) for v in silhouette],
    [0.681, 0.5528, 0.4981, 0.4887, 0.3648],
)
if not all(a > b for a, b in zip(inertia, inertia[1:])):
    errors.append("inertia was not monotonically decreasing")
expect("silhouette's chosen k", ks[int(np.argmax(silhouette))], 2)

# 6. Evaluative feedback and the cost of not exploring
greedy = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.0)
small = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.01)
explore = f.average_bandit(runs=200, k=10, steps=1000, epsilon=0.1)
expect("greedy mean reward", round(greedy[0], 4), 0.9838)
expect("greedy optimal rate", round(greedy[1], 4), 0.313)
expect("epsilon=0.01 mean reward", round(small[0], 4), 1.1314)
expect("epsilon=0.01 optimal rate", round(small[1], 4), 0.4336)
expect("epsilon=0.1 mean reward", round(explore[0], 4), 1.28)
expect("epsilon=0.1 optimal rate", round(explore[1], 4), 0.708)
expect("cost of never exploring", round(explore[1] - greedy[1], 4), 0.3949)

# 7. Delayed feedback and the tie-breaking bug
world = f.GridWorld(5)
expect("shortest path", world.shortest_path_length(), 8)
_qb, lengths_bad, reached_bad = f.q_learning(world, episodes=300, seed=0, break_ties_randomly=False)
q_good, lengths_good, reached_good = f.q_learning(
    world, episodes=300, seed=0, break_ties_randomly=True
)
expect("np.argmax tie-breaking, goals reached", reached_bad, 0)
expect("random tie-breaking, goals reached", reached_good, 300)
expect("first ten episodes", round(float(np.mean(lengths_good[:10])), 1), 46.8)
expect("last ten episodes", round(float(np.mean(lengths_good[-10:])), 1), 10.4)
expect("greedy path after training", f.greedy_path_length(world, q_good), 8)
spread = f.value_spread_by_episode(world, [1, 2, 3, 5, 10, 25, 50, 100, 300])
expect("states valued per episode", [s for _n, s, _p in spread], [1, 2, 3, 5, 10, 18, 20, 21, 22])
expect("greedy path at 10 episodes", spread[4][2], 200)
expect("greedy path at 25 episodes", spread[5][2], 8)

# 8. A log is not a supervised dataset
arms, _rewards, best_arm, counts = f.logged_policy_dataset(k=10, steps=2000, epsilon=0.1, seed=0)
pulls = f.arm_pull_counts(counts)
expect("logged best arm", best_arm, 6)
expect("pulls of the best arm", pulls[6], 1813)
expect("pulls shared by the other nine", sum(v for a, v in pulls.items() if a != 6), 187)
greedy_logs = f.log_verdicts(range(8), epsilon=0.0)
explored_logs = f.log_verdicts(range(8), epsilon=0.1)
expect("greedy logs that are right", sum(1 for r in greedy_logs if r[4]), 3)
expect("greedy logs holding one arm", sum(1 for r in greedy_logs if r[1] == 1), 4)
expect("explored logs that are right", sum(1 for r in explored_logs if r[4]), 7)
expect("explored logs holding all ten arms", sum(1 for r in explored_logs if r[1] == 10), 8)
arms1, rewards1, _b1, counts1 = f.logged_policy_dataset(k=10, steps=2000, epsilon=0.1, seed=1)
bandit1 = f.GaussianBandit(k=10, seed=1)
means1 = f.logged_arm_means(arms1, rewards1)
expect("winner's curse: pulls of arm 4", int(counts1[4]), 1524)
expect("winner's curse: pulls of arm 1", int(counts1[1]), 274)
expect("winner's curse: true mean of arm 4", round(float(bandit1.means[4]), 4), 0.9054)
expect("winner's curse: true mean of arm 1", round(float(bandit1.means[1]), 4), 0.8216)
expect("winner's curse: logged mean of arm 4", round(means1[4], 4), 0.8634)
expect("winner's curse: logged mean of arm 1", round(means1[1], 4), 0.9262)
expect("winner's curse: the log's pick", f.logged_best_arm(arms1, rewards1), 1)

# 9. Labels are the expensive part
budgets = [3, 5, 10, 20, 50]
curve = f.average_label_budget_curve(X, y, budgets, repeats=40)
expect("averaged budget curve", [round(v, 4) for v in curve], [0.6455, 0.778, 0.896, 0.924, 0.947])
single = f.label_budget_curve(X, y, budgets, seed=142)
expect("single-split budget curve", single, [0.64, 0.92, 0.92, 0.86, 0.96])
if all(a <= b for a, b in zip(single, single[1:])):
    errors.append("the single-split curve was monotone, so averaging is not motivated")
if not all(a < b for a, b in zip(curve, curve[1:])):
    errors.append("the averaged curve was not strictly increasing")
chosen = f.average_cluster_then_label(X, y, 3, repeats=40)
ceiling = f.average_full_supervision(X, y, repeats=40)
expect("three chosen labels", round(chosen, 4), 0.876)
expect("every row labelled", round(ceiling, 4), 0.9535)
expect("what choosing is worth", round(chosen - curve[0], 4), 0.2305)
if not (curve[1] < chosen < curve[2]):
    errors.append("three chosen labels did not land between five and ten random ones")

# 10. Naming the setting
verdicts = [
    f.classify_problem(f.problem(has_labels=True, actions_change_the_data=False, feedback_is_immediate=True)),
    f.classify_problem(f.problem(has_labels=False, actions_change_the_data=False, feedback_is_immediate=True)),
    f.classify_problem(f.problem(has_labels=True, actions_change_the_data=True, feedback_is_immediate=True)),
    f.classify_problem(f.problem(has_labels=True, actions_change_the_data=True, feedback_is_immediate=False)),
]
expect(
    "the four verdicts",
    verdicts,
    [
        "supervised learning",
        "unsupervised learning",
        "reinforcement learning: contextual bandit",
        "reinforcement learning: sequential, with delayed credit",
    ],
)
try:
    f.classify_problem({"has_labels": True})
except KeyError:
    pass
else:
    errors.append("classify_problem accepted an incomplete problem description")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-10 reproduced directly against feedback_lib, no pytest involved"
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
if echo "$STARTER_OUT" | tail -1 | grep -qE "4 passed, 15 skipped"; then
  ok "pytest starter -q -> 4 passed, 15 skipped (the machinery checks pass; the fifteen exercises are stubs)"
else
  fail "pytest starter -q did not report 4 passed, 15 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d142-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^19 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_feedback_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert reached_good == 300"
replacement = "assert reached_good == 299"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_07_argmax_tie_breaking_decides_whether_the_agent_learns_at_all"; then
  ok "breaking exercise 7's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The gridworld and the bandit are genuinely deterministic"
DETERMINISM=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import feedback_lib as f

world = f.GridWorld(5)
a = f.q_learning(world, episodes=40, seed=7)[1]
b = f.q_learning(world, episodes=40, seed=7)[1]
c = f.q_learning(world, episodes=40, seed=8)[1]
bandit_a = f.run_bandit(seed=7)["rewards"]
bandit_b = f.run_bandit(seed=7)["rewards"]
if a != b:
    print("ERROR: two runs at the same seed disagreed")
elif a == c:
    print("ERROR: two runs at different seeds were identical")
elif not np.array_equal(bandit_a, bandit_b):
    print("ERROR: the bandit was not reproducible at a fixed seed")
else:
    print("deterministic")
PYEOF
)
if [ "$DETERMINISM" = "deterministic" ]; then
  ok "same seed reproduces exactly; different seeds do not"
else
  fail "determinism check failed: $DETERMINISM"
fi

echo ""
echo "9. Offline, and nothing left behind"
if ! grep -rInE "https?://" examples/*.py starter/*.py > /dev/null 2>&1; then
  ok "no URLs inside examples/ or starter/ source -- this lab reaches no network"
else
  fail "found a URL inside examples/ or starter/"
fi
LEFTOVER_PYC=$(find . -path ./.venv -prune -o -type d -name '__pycache__' -print 2>/dev/null)
if [ -z "$LEFTOVER_PYC" ]; then
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
