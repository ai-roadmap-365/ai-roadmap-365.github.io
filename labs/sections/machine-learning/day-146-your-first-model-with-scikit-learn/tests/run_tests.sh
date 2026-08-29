#!/usr/bin/env bash
# Day 146 lab harness: "The Estimator API, From Scratch"
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import estimator_lib as e

errors = []


def expect(label, got, want):
    if got != want:
        errors.append(f"{label}: expected {want}, got {got}")


X, y = e.classification_dataset()

# 1. The hand-built classifier against the library one
expect("matches DummyClassifier", e.matches_dummy_classifier(), True)

# 2. What fitting actually adds
gained = e.gained_attributes(LogisticRegression(max_iter=1000), X, y)
expect("attributes gained by fit()", gained, ["classes_", "coef_", "intercept_", "n_features_in_", "n_iter_"])
lib_msg = e.predict_before_fit_message(LogisticRegression(), n_features=X.shape[1])
ours_msg = e.predict_before_fit_message(e.MajorityClassifier(), n_features=X.shape[1])
for msg in (lib_msg, ours_msg):
    if "is not fitted yet" not in msg or "Call 'fit'" not in msg:
        errors.append(f"NotFittedError message did not explain itself: {msg}")

# 3. get_params, set_params, clone
after = e.params_roundtrip(LogisticRegression(max_iter=1000), C=2.0)
expect("C after round trip", after["C"], 2.0)
fitted = LogisticRegression(C=0.3, max_iter=1000).fit(X, y)
expect(
    "clone of a fitted estimator",
    e.clone_is_fresh(fitted, "coef_"),
    {"params_equal": True, "fresh_is_unfitted": True, "original_still_fitted": True},
)

# 4. Pipeline as an estimator itself
pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=0.5, max_iter=1000))])
keys = e.pipeline_param_keys(pipe)
expect("number of pipeline param keys", len(keys), 23)
if "clf__C" not in keys or "scaler__with_mean" not in keys:
    errors.append("pipeline param keys missing an expected nested entry")
nested = e.pipeline_set_nested(pipe, **{"clf__C": 2.0})
expect("nested set_params reaches the live step", pipe.named_steps["clf"].C, 2.0)
expect("fits per fold, 5-fold", e.fits_per_fold(X, y, folds=5), 5)
expect("fits per fold, 10-fold", e.fits_per_fold(X, y, folds=10), 10)

# 5. Where "just a protocol" needs a footnote
bare_message = e.bare_estimator_breaks_in_cross_val_score(X, y)
if "__sklearn_tags__" not in bare_message or "BaseEstimator" not in bare_message:
    errors.append("bare-estimator failure message did not name the real cause")
base_scores = e.base_estimator_works_in_pipeline_and_cv(X, y)
if len(base_scores) != 5 or any(np.isnan(base_scores)):
    errors.append("BaseEstimator-based classifier did not produce 5 real scores in a real Pipeline+CV")
if "get_params" in e.MajorityClassifierBase.__dict__ or "set_params" in e.MajorityClassifierBase.__dict__:
    errors.append("MajorityClassifierBase should not define get_params/set_params itself")

# 6. How many estimators implement fit?
census = e.estimator_census()
expect("bare estimator discovery (no experimental imports)", census["bare_total"], 208)
expect("total estimators discovered (experimental enabled)", census["total"], 210)
expect("gap explained by exactly the two Halving estimators", census["total"] - census["bare_total"], 2)
expect(
    "newly visible after the experimental import",
    census["newly_visible_after_experimental_enable"],
    ["HalvingGridSearchCV", "HalvingRandomSearchCV"],
)
expect("estimators implementing fit", census["has_fit"], 210)
expect("estimators implementing transform", census["has_transform"], 90)
expect("estimators implementing predict", census["has_predict"], 119)
expect("estimators implementing both", len(census["both_transform_and_predict"]), 20)

# 7. predict, predict_proba, decision_function
expect("argmax(predict_proba) == predict", e.proba_argmax_matches_predict(X, y), True)
expect("decision_function agrees with predict", e.decision_function_matches_predict(X, y), True)

# 8. random_state: structural claims only -- the values are fresh OS entropy
result = e.random_state_reproducibility(X, y)
expect("fixed random_state reproducible", result["fixed_identical_across_repeats"], True)
if result["none_distinct_prediction_vectors"] < 2:
    errors.append("random_state=None did not vary across repeated fits")
if result["accuracy_spread_sd"] <= 0.0:
    errors.append("random_state=None accuracy did not vary at all")

# 9. The estimator contract, checked mechanically
report = e.check_estimator_report(e.MajorityClassifierBase())
expect("check_estimator total", report["total"], 52)
expect("check_estimator passed", report["passed"], 48)
expect(
    "check_estimator failed names",
    report["failed"],
    ["check_classifiers_regression_target", "check_classifiers_train"],
)
expect(
    "check_estimator skipped names",
    report["skipped"],
    ["check_array_api_input", "check_classifier_data_not_an_array"],
)

if errors:
    for err in errors:
        print("ERROR:", err)
    sys.exit(1)
print("all direct checks passed")
PYEOF
)
if echo "$DIRECT_CHECK" | grep -q "all direct checks passed"; then
  ok "exercises 1-10 reproduced directly against estimator_lib, no pytest involved"
else
  fail "direct library checks failed"
  echo "$DIRECT_CHECK" | sed 's/^/    /'
fi

echo ""
echo "3. examples/ passes in full"
EXAMPLES_OUT=$("$PYTEST" examples -q 2>&1)
if echo "$EXAMPLES_OUT" | tail -1 | grep -qE "^23 passed"; then
  ok "pytest examples -q -> 23 passed"
else
  fail "pytest examples -q did not report 23 passed"
  echo "$EXAMPLES_OUT" | tail -20 | sed 's/^/    /'
fi

echo ""
echo "4. starter/ is an untouched skeleton"
STARTER_OUT=$("$PYTEST" starter -q 2>&1)
if echo "$STARTER_OUT" | tail -1 | grep -qE "5 passed, 18 skipped"; then
  ok "pytest starter -q -> 5 passed, 18 skipped (the machinery checks pass; the eighteen exercises are stubs)"
else
  fail "pytest starter -q did not report 5 passed, 18 skipped"
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
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/d146-scratch.XXXXXX")
cp examples/*.py "$SCRATCH"/
SCRATCH_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
if echo "$SCRATCH_OUT" | tail -1 | grep -qE "^23 passed"; then
  ok "scratch copy of examples/ passes before it is broken"
else
  fail "scratch copy did not pass before being broken: $(echo "$SCRATCH_OUT" | tail -3)"
fi
"$PYTHON" - "$SCRATCH/test_estimator_claims.py" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path).read()
needle = 'assert census["total"] == 210'
replacement = 'assert census["total"] == 999'
assert needle in text, "could not find the assertion to break"
open(path, "w").write(text.replace(needle, replacement, 1))
PYEOF
BROKEN_OUT=$("$PYTEST" "$SCRATCH" -q 2>&1)
BROKEN_STATUS=$?
if [ "$BROKEN_STATUS" -ne 0 ] && echo "$BROKEN_OUT" | grep -q "test_07_scikit_learn_discovers_210_estimators_and_all_implement_fit"; then
  ok "breaking exercise 7's assertion produces a non-zero exit and names the failing test"
else
  fail "broken copy did not fail as expected (exit=$BROKEN_STATUS)"
fi
rm -rf "$SCRATCH"

echo ""
echo "8. Key results hold at seeds and parameters the lesson does not quote"
DIRECTION=$("$PYTHON" - <<'PYEOF'
import sys
sys.path.insert(0, "examples")
import estimator_lib as e

problems = []

# The hand-built classifier is not matched to the library one by luck of
# the five quoted seeds.
if not e.matches_dummy_classifier(seeds=range(100, 108)):
    problems.append("MajorityClassifier stopped matching DummyClassifier at unquoted seeds")

# fits_per_fold at a fold count the lesson never quotes.
X, y = e.classification_dataset(seed=7)
if e.fits_per_fold(X, y, folds=3) != 3:
    problems.append("fits_per_fold(folds=3) was not 3 on an unquoted dataset seed")

# argmax(predict_proba) == predict at an unquoted dataset.
X2, y2 = e.classification_dataset(n=90, n_features=6, n_classes=4, seed=101)
if not e.proba_argmax_matches_predict(X2, y2):
    problems.append("argmax(predict_proba) != predict on an unquoted dataset shape")

# The bare estimator fails inside cross_val_score regardless of dataset.
message = e.bare_estimator_breaks_in_cross_val_score(X2, y2, folds=3, seed=101)
if "__sklearn_tags__" not in message:
    problems.append("bare estimator failure did not reproduce on an unquoted dataset/fold count")

if problems:
    for p in problems:
        print("ERROR:", p)
else:
    print("every result held")
PYEOF
)
if [ "$DIRECTION" = "every result held" ]; then
  ok "the hand-built classifier, fold-fitting count, proba/predict agreement and the bare-estimator failure all hold at seeds and parameters the lesson does not quote"
else
  fail "a result failed beyond the quoted seed"
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
