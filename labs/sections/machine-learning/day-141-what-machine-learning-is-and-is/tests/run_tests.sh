#!/usr/bin/env bash
# Day 141 lab harness: "What the Number Is Not Telling You"
#
# Prints "N checks, M failure(s)" and exits 0 only when M is zero.
set -u

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_DIR"

PYTHON="${PYTHON:-.venv/bin/python3}"
PYTEST="${PYTEST:-.venv/bin/pytest}"

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
echo "2. The nine claims, reproduced directly (no pytest involved)"
DIRECT_CHECK=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")

import numpy as np
from sklearn.datasets import load_iris

import ml_lib as m

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


# 1. Perfect accuracy, zero learning
X_tr, y_tr = m.pure_noise_dataset(200, seed=141)
X_te, y_te = m.pure_noise_dataset(1000, seed=242)
hand = m.HandwrittenNearestNeighbour().fit(X_tr, y_tr)
expect("1-NN train on noise", m.accuracy(y_tr, hand.predict(X_tr)), 1.0)
expect("1-NN test on noise", m.accuracy(y_te, hand.predict(X_te)), 0.518)
lib = m.one_nn().fit(X_tr, y_tr)
expect("sklearn 1-NN train on noise", m.accuracy(y_tr, lib.predict(X_tr)), 1.0)
expect("sklearn 1-NN test on noise", m.accuracy(y_te, lib.predict(X_te)), 0.518)

X_iris, y_iris = load_iris(return_X_y=True)
expect("iris shape", X_iris.shape, (150, 4))
expect("iris unique rows", len({tuple(r) for r in X_iris}), 149)
scrambled = np.random.default_rng(141).permutation(y_iris)
expect(
    "1-NN train, iris real labels",
    m.accuracy(y_iris, m.HandwrittenNearestNeighbour().fit(X_iris, y_iris).predict(X_iris)),
    1.0,
)
if m.accuracy(
    scrambled,
    m.HandwrittenNearestNeighbour().fit(X_iris, scrambled).predict(X_iris),
) >= 1.0:
    errors.append("scrambled-label iris 1-NN unexpectedly scored a perfect 1.0")

# 2. A rule beats a model
X_tr, y_tr = m.rule_dataset(300, seed=11)
X_te, y_te = m.rule_dataset(2000, seed=12)
expect("rule accuracy", m.accuracy(y_te, m.exact_rule(X_te)), 1.0)
expect("depth-3 tree", m.fit_score(m.shallow_tree(3), X_tr, y_tr, X_te, y_te), 0.8855)
best = max(
    m.fit_score(model, X_tr, y_tr, X_te, y_te)
    for model in (m.shallow_tree(3), m.shallow_tree(8), m.deep_tree(), m.smooth_knn(15))
)
expect("best trained model", best, 0.9675)
if best >= 1.0:
    errors.append("a trained model matched the rule, which contradicts the exercise")

# 3. The generalisation gap
perm = np.random.default_rng(141).permutation(len(y_iris))
tr, te = perm[:100], perm[100:]
tree = m.deep_tree().fit(X_iris[tr], y_iris[tr])
expect("iris train", m.accuracy(y_iris[tr], tree.predict(X_iris[tr])), 1.0)
expect("iris test", m.accuracy(y_iris[te], tree.predict(X_iris[te])), 0.96)
X_tr, y_tr = m.noisy_rule_dataset(300, seed=21, noise_rate=0.2)
X_te, y_te = m.noisy_rule_dataset(2000, seed=22, noise_rate=0.2)
noisy = m.deep_tree().fit(X_tr, y_tr)
expect("noisy train", m.accuracy(y_tr, noisy.predict(X_tr)), 1.0)
expect("noisy test", m.accuracy(y_te, noisy.predict(X_te)), 0.6535)
simple = m.linear_classifier().fit(X_tr, y_tr)
expect("simple model train", m.accuracy(y_tr, simple.predict(X_tr)), 0.78)
expect("simple model test", m.accuracy(y_te, simple.predict(X_te)), 0.7655)

# 4. Distribution shift
X_tr, y_tr = m.rule_dataset(400, seed=31)
X_in, y_in = m.rule_dataset(2000, seed=32)
X_sh, y_sh = m.rule_dataset(2000, seed=33, offset=3.0)
tree = m.deep_tree().fit(X_tr, y_tr)
expect("in-distribution", m.accuracy(y_in, tree.predict(X_in)), 0.948)
expect("shifted", m.accuracy(y_sh, tree.predict(X_sh)), 0.4895)
expect("rule on shifted region", m.accuracy(y_sh, m.exact_rule(X_sh)), 1.0)

# 5. Interpolation versus extrapolation
X_tr, y_tr = m.quadratic_curve(300, 0.0, 10.0, seed=41)
X_in, y_in = m.quadratic_curve(200, 0.0, 10.0, seed=42)
X_out, y_out = m.quadratic_curve(200, 10.0, 20.0, seed=43)
knn = m.knn_regressor(5).fit(X_tr, y_tr)
expect("MAE inside", round(m.mean_absolute_error(y_in, knn.predict(X_in)), 3), 0.18)
expect("MAE outside", round(m.mean_absolute_error(y_out, knn.predict(X_out)), 3), 139.704)
if float(np.max(knn.predict(X_out))) > float(np.max(y_tr)):
    errors.append("a nearest-neighbour regressor predicted beyond its training range")
linear = m.linear_regressor().fit(X_tr, y_tr)
expect("linear MAE inside", round(m.mean_absolute_error(y_in, linear.predict(X_in)), 3), 6.007)
expect("linear MAE outside", round(m.mean_absolute_error(y_out, linear.predict(X_out)), 3), 101.643)

# 6. The baseline
X_tr, y_tr = m.imbalanced_noise_dataset(1000, seed=51)
X_te, y_te = m.imbalanced_noise_dataset(1000, seed=52)
baseline = m.fit_score(m.majority_baseline(), X_tr, y_tr, X_te, y_te)
expect("majority baseline", baseline, 0.9)
one_nn = m.fit_score(m.one_nn(), X_tr, y_tr, X_te, y_te)
deep = m.fit_score(m.deep_tree(), X_tr, y_tr, X_te, y_te)
expect("1-NN on imbalanced noise", one_nn, 0.821)
expect("tree on imbalanced noise", deep, 0.817)
if not (one_nn < baseline and deep < baseline):
    errors.append("a model beat the majority baseline, contradicting exercise 6")
expect(
    "iris baseline",
    m.fit_score(m.majority_baseline(), X_iris[tr], y_iris[tr], X_iris[te], y_iris[te]),
    0.26,
)
expect(
    "iris 1-NN",
    m.fit_score(m.one_nn(), X_iris[tr], y_iris[tr], X_iris[te], y_iris[te]),
    0.98,
)

# 7. The noise ceiling
ceiling = 0.75
X_tr, y_tr = m.noisy_rule_dataset(2000, seed=61, noise_rate=0.25)
X_te, y_te = m.noisy_rule_dataset(4000, seed=62, noise_rate=0.25)
measured = {
    "logistic regression": m.fit_score(m.linear_classifier(), X_tr, y_tr, X_te, y_te),
    "15-NN": m.fit_score(m.smooth_knn(15), X_tr, y_tr, X_te, y_te),
    "depth-3 tree": m.fit_score(m.shallow_tree(3), X_tr, y_tr, X_te, y_te),
    "full-depth tree": m.fit_score(m.deep_tree(), X_tr, y_tr, X_te, y_te),
}
expect("logistic regression at the ceiling", measured["logistic regression"], 0.73725)
expect("15-NN at the ceiling", measured["15-NN"], 0.72675)
expect("depth-3 tree at the ceiling", measured["depth-3 tree"], 0.68825)
expect("full-depth tree at the ceiling", measured["full-depth tree"], 0.60875)
for name, score in measured.items():
    if score > ceiling:
        errors.append(f"{name} scored {score}, above the {ceiling} ceiling")
_, y_clean = m.rule_dataset(4000, seed=62)
expect("exact flipped test labels", int(np.sum(y_clean != y_te)), 1000)

# 8. More data does not fix the wrong thing
X_te_c, y_te_c = m.checkerboard_dataset(4000, seed=71)
small = m.fit_score(m.deep_tree(), *m.checkerboard_dataset(50, seed=120), X_te_c, y_te_c)
large = m.fit_score(m.deep_tree(), *m.checkerboard_dataset(5000, seed=5070), X_te_c, y_te_c)
expect("variance-limited n=50", small, 0.5995)
expect("variance-limited n=5000", large, 0.99725)
X_te_n, y_te_n = m.noisy_rule_dataset(4000, seed=81, noise_rate=0.30)
few = m.fit_score(
    m.linear_classifier(), *m.noisy_rule_dataset(200, seed=280, noise_rate=0.30), X_te_n, y_te_n
)
many = m.fit_score(
    m.linear_classifier(), *m.noisy_rule_dataset(5000, seed=5080, noise_rate=0.30), X_te_n, y_te_n
)
expect("noise-limited n=200", few, 0.6655)
expect("noise-limited n=5000", many, 0.68675)
if (large - small) <= 15 * (many - few):
    errors.append("the variance gain was not decisively larger than the noise gain")

# 9. The decision function
verdicts = {
    m.should_use_ml(m.problem(True, True, True, True)): "write the rule",
    m.should_use_ml(m.problem(False, False, True, True)): "get labels first",
    m.should_use_ml(m.problem(False, True, False, True)): "not yet: the distribution moves",
    m.should_use_ml(m.problem(False, True, True, False)): "no: errors are not tolerable",
    m.should_use_ml(m.problem(False, True, True, True)): "yes",
}
if len(verdicts) != 5:
    errors.append("should_use_ml did not produce five distinct verdicts")
try:
    m.should_use_ml({"exact_rule_exists": False})
except KeyError:
    pass
else:
    errors.append("should_use_ml accepted an incomplete problem")

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-9 reproduced directly against ml_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^13 passed"; then
  ok "pytest examples -q -> 13 passed"
else
  fail "pytest examples -q did not report 13 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "3 passed, 10 skipped"; then
  ok "pytest starter -q -> 3 passed, 10 skipped (the machinery checks pass; the ten exercises are stubs)"
else
  fail "pytest starter -q did not report 3 passed, 10 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d141-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^13 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_ml_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = "assert train_acc == 1.0"
replacement = "assert train_acc == 0.5"
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_01_one_nn_scores_a_perfect_1_000_having_learned_nothing"; then
  ok "breaking exercise 1's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. Offline, and nothing left behind"
if ! grep -rInE "https?://" examples/*.py starter/*.py > /dev/null 2>&1; then
  ok "no URLs inside examples/ or starter/ source -- this lab reaches no network"
else
  fail "found a URL inside examples/ or starter/"
fi
if [ -z "$(find . -path ./.venv -prune -o -type d -name '__pycache__' -print 2>/dev/null)" ]; then
  ok "no __pycache__ left behind"
else
  find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
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
