#!/usr/bin/env bash
# Day 144 lab harness: "Three Sets, and Why"
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
from sklearn.linear_model import LogisticRegression

import splits_lib as s

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. Selection bias
rows = s.selection_bias_curve([1, 2, 5, 10, 25, 50, 100, 500, 1000])
expect(
    "selection bias curve",
    rows,
    [
        (1, 0.4984, 0.5011, -0.0028),
        (2, 0.5115, 0.4992, 0.0123),
        (5, 0.5256, 0.5005, 0.0251),
        (10, 0.5331, 0.4999, 0.0332),
        (25, 0.5436, 0.5009, 0.0427),
        (50, 0.5508, 0.5014, 0.0493),
        (100, 0.5567, 0.4992, 0.0575),
        (500, 0.5682, 0.4978, 0.0704),
        (1000, 0.572, 0.4992, 0.0728),
    ],
)
validation = [v for _k, v, _t, _o in rows]
if not all(a < b for a, b in zip(validation, validation[1:])):
    errors.append("the validation column was not strictly increasing in K")
test_column = [t for _k, _v, t, _o in rows]
if max(test_column) - min(test_column) >= 0.005:
    errors.append("the test column moved, which it must not")
for score in test_column:
    if abs(score - 0.5) >= 0.005:
        errors.append(f"a test score drifted from chance: {score}")

# 1b. The optimism equals the expected maximum
standard_error = s.proportion_standard_error(0.5, 500)
expect("standard error at n=500", round(standard_error, 4), 0.0224)
for k, _v, _t, optimism in rows[1:]:
    in_errors = optimism / standard_error
    simulated = s.expected_max_of_normals(k)
    if abs(in_errors - simulated) >= 0.2:
        errors.append(f"K={k}: optimism {in_errors:.2f} SEs vs expected max {simulated:.2f}")
    if s.sqrt_two_log_k(k) <= simulated:
        errors.append(f"K={k}: sqrt(2 ln K) did not overestimate the expected maximum")
expect("expected max at K=100", round(s.expected_max_of_normals(100), 2), 2.5)
expect("sqrt(2 ln 100)", round(s.sqrt_two_log_k(100), 2), 3.03)

# 2. Stratification
X, y = s.rare_class_dataset()
expect("population positive rate", round(float(y.mean()), 4), 0.05)
random_rates, stratified_rates, empty = s.split_positive_rates(X, y)
expect(
    "random split spread",
    s.spread(random_rates),
    {"mean": 0.0504, "sd": 0.0265, "min": 0.0, "max": 0.16},
)
expect(
    "stratified split spread",
    s.spread(stratified_rates),
    {"mean": 0.05, "sd": 0.01, "min": 0.04, "max": 0.06},
)
expect("random splits with no positives", empty, 21)

# 3. Groups
Xg, yg, groups = s.grouped_dataset()
rowwise, group_aware = s.rowwise_vs_group_split(Xg, yg, groups)
expect("row-wise split", round(rowwise, 4), 0.976)
expect("group-aware split", round(group_aware, 4), 0.4112)
expect("accuracy invented by ignoring groups", round(rowwise - group_aware, 4), 0.5648)
expect("people in both halves", s.groups_shared_between_halves(groups), 50)
if not (group_aware < 0.5 < rowwise):
    errors.append("the group-aware score was not below chance while the row-wise one was above it")

# 4. Time
temporal = s.temporal_inflation_over_constructions()
inflation = [gap for _s, _sh, _ch, _b, gap in temporal]
expect("constructions", len(temporal), 20)
expect("constructions where shuffling won", sum(1 for g in inflation if g > 0), 20)
expect("shuffled mean", round(float(np.mean([r[1] for r in temporal])), 4), 0.5961)
expect("chronological mean", round(float(np.mean([r[2] for r in temporal])), 4), 0.5233)
expect("baseline mean", round(float(np.mean([r[3] for r in temporal])), 4), 0.5235)
expect("inflation mean", round(float(np.mean(inflation)), 4), 0.0728)
expect("inflation sd", round(float(np.std(inflation)), 4), 0.0596)
expect("smallest inflation", round(min(inflation), 4), 0.016)
expect("largest inflation", round(max(inflation), 4), 0.2557)
expect("ratio of largest to smallest", round(max(inflation) / min(inflation), 1), 16.0)

# 5. Holdout versus cross-validation
Xw, yw = s.weak_signal_dataset()
holdout, cross = s.holdout_vs_cross_validation(Xw, yw)
expect(
    "holdout spread",
    s.spread(holdout),
    {"mean": 0.7519, "sd": 0.0381, "min": 0.66, "max": 0.85},
)
expect(
    "cross-validated spread",
    s.spread(cross),
    {"mean": 0.7546, "sd": 0.0061, "min": 0.7375, "max": 0.77},
)
expect("holdout range", round(max(holdout) - min(holdout), 4), 0.19)
expect("steadiness ratio", round(float(np.std(holdout) / np.std(cross)), 4), 6.2344)

# 6. Test-set size
expect(
    "test size table",
    s.test_size_table([50, 100, 200, 500, 1000, 5000]),
    [
        (50, 0.0505, 0.0505, 0.099),
        (100, 0.0357, 0.0357, 0.07),
        (200, 0.0252, 0.0254, 0.0495),
        (500, 0.016, 0.016, 0.0313),
        (1000, 0.0113, 0.0112, 0.0221),
        (5000, 0.005, 0.0051, 0.0099),
    ],
)
expect("rows for +/-0.02", s.rows_needed_for_precision(0.85, 0.02), 1225)
expect("rows for +/-0.01", s.rows_needed_for_precision(0.85, 0.01), 4899)

# 7. The gate
model = LogisticRegression(max_iter=1000).fit(Xw, yw)
gate = s.GatedTestSet(Xw, yw)
expect("first evaluation", round(gate.evaluate(model), 4), 0.7575)
expect("evaluation counter", gate.evaluations, 1)
try:
    gate.evaluate(model)
except s.TestSetTouchedTwice as exc:
    if "validation score" not in str(exc):
        errors.append(f"the gate's message did not explain itself: {exc}")
    if gate.evaluations != 1:
        errors.append("the counter advanced on a refused evaluation")
else:
    errors.append("the gate permitted a second evaluation, which it must not")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-7 reproduced directly against splits_lib, no pytest involved"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d144-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^18 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_splits_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert round(rowwise - group_aware, 4) == 0.5648"
replacement = "assert round(rowwise - group_aware, 4) == 0.0"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_03_splitting_rows_when_the_unit_is_a_person_invents_fifty_six_points"; then
  ok "breaking exercise 3's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. The direction of every split result holds beyond the quoted seed"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import numpy as np
import splits_lib as s

problems = []

# Group leakage is not a property of one dataset seed.
for seed in range(5):
    X, y, groups = s.grouped_dataset(n_people=40, rows_each=15, seed=seed)
    rowwise, grouped = s.rowwise_vs_group_split(X, y, groups, splits=5)
    if rowwise <= grouped:
        problems.append(f"seed {seed}: row-wise {rowwise:.4f} did not beat group-aware {grouped:.4f}")

# Selection optimism is not a property of one replication count.
short = s.selection_bias_curve([1, 100], replications=120)
if short[1][1] <= short[0][1]:
    problems.append("selection optimism vanished at a different replication count")

# Stratification always narrows the spread.
for seed in (144, 145, 146):
    X, y = s.rare_class_dataset(seed=seed)
    r, st, _empty = s.split_positive_rates(X, y, splits=200)
    if s.spread(st)["sd"] >= s.spread(r)["sd"]:
        problems.append(f"seed {seed}: stratifying did not narrow the spread")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every direction held")
PYEOF
)
if [ "$DIRECTION" = "every direction held" ]; then
  ok "group leakage, selection optimism and stratification hold at seeds the lesson does not quote"
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
