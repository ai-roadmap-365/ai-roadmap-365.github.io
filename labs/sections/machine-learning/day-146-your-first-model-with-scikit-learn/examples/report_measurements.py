#!/usr/bin/env python3
"""Print every measured pair in this lab as one table.

The harness compares this output byte for byte against
expected-output/measured-values.txt, so the report is not a convenience:
it is how the lab notices that a number in the lesson has gone stale.

Two sections below print structural facts rather than captured numbers,
and say so: exercises 9 and 9b measure what random_state=None costs, and
that cost is a fresh draw of OS entropy on every run by design.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

import estimator_lib as e  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    print("Day 146 -- the scikit-learn estimator API, measured")
    print("=" * 52)

    data = e.classification_dataset()
    X, y = data

    rule("1. The hand-built classifier against the library one")
    print(f"  matches DummyClassifier(strategy='most_frequent') exactly: {e.matches_dummy_classifier()}")

    rule("2. What fitting actually adds")
    gained = e.gained_attributes(LogisticRegression(max_iter=1000), X, y)
    print(f"  attributes gained by fit(): {gained}")
    lib_msg = e.predict_before_fit_message(LogisticRegression(), n_features=X.shape[1])
    ours_msg = e.predict_before_fit_message(e.MajorityClassifier(), n_features=X.shape[1])
    print(f"  LogisticRegression before fit -> {lib_msg}")
    print(f"  MajorityClassifier before fit -> {ours_msg}")

    rule("3. get_params, set_params, clone")
    after = e.params_roundtrip(LogisticRegression(max_iter=1000), C=2.0)
    print(f"  set_params(C=2.0) then get_params() -> C={after['C']}, max_iter={after['max_iter']}")
    fitted = LogisticRegression(C=0.3, max_iter=1000).fit(X, y)
    print(f"  clone() of a fitted estimator: {e.clone_is_fresh(fitted, 'coef_')}")

    rule("4. Pipeline as an estimator itself")
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=0.5, max_iter=1000))])
    keys = e.pipeline_param_keys(pipe)
    print(f"  pipeline.get_params(deep=True) has {len(keys)} keys, including {['clf__C', 'scaler__with_mean']}")
    nested = e.pipeline_set_nested(pipe, **{"clf__C": 2.0})
    print(f"  set_params(clf__C=2.0) -> clf__C={nested['clf__C']}, live step C={pipe.named_steps['clf'].C}")
    print(f"  a preprocessing step is fit {e.fits_per_fold(X, y, folds=5)} times under 5-fold cross_val_score")
    print(f"  and {e.fits_per_fold(X, y, folds=10)} times under 10-fold -- once per fold, every time")

    rule('5. Where "just a protocol" needs a footnote')
    bare_message = e.bare_estimator_breaks_in_cross_val_score(X, y)
    print("  cross_val_score on an estimator inheriting nothing from sklearn:")
    print(f"    {bare_message}")
    base_scores = e.base_estimator_works_in_pipeline_and_cv(X, y)
    rounded_scores = [round(float(score), 4) for score in base_scores]
    print(f"  the same classifier, inheriting bare BaseEstimator, inside a real Pipeline: {rounded_scores}")

    rule("6. How many estimators implement fit?")
    census = e.estimator_census()
    print(f"  bare discovery (no experimental imports): {census['bare_total']}")
    print(f"  discovered with sklearn.experimental.enable_halving_search_cv: {census['total']}, implement fit: {census['has_fit']}")
    print(f"  newly visible after that import: {census['newly_visible_after_experimental_enable']}")
    print(f"  implement transform: {census['has_transform']}, implement predict: {census['has_predict']}")
    print(f"  implement both: {len(census['both_transform_and_predict'])} -- {census['both_transform_and_predict']}")

    rule("7. predict, predict_proba, decision_function")
    print(f"  argmax(predict_proba(X)) == predict(X): {e.proba_argmax_matches_predict(X, y)}")
    print(f"  decision_function agrees with predict(X): {e.decision_function_matches_predict(X, y)}")

    rule("8. random_state: what None actually costs")
    result = e.random_state_reproducibility(X, y)
    print(f"  random_state=42, five independent fits, identical predictions: {result['fixed_identical_across_repeats']}")
    print(f"  random_state=None, five independent fits, at least two distinct vectors: {result['none_distinct_prediction_vectors'] >= 2}")
    print(f"  random_state=None, accuracy varies across 20 fits (sd > 0): {result['accuracy_spread_sd'] > 0.0}")
    print("  the exact counts and spread are fresh OS entropy every run and are NOT byte-comparable;")
    print("  one real capture lives in expected-output/FIELDS.md, never asserted as a fixed value")

    rule("9. The estimator contract, checked mechanically")
    report = e.check_estimator_report(e.MajorityClassifierBase())
    print(f"  check_estimator: {report['total']} checks, {report['passed']} passed")
    print(f"  failed: {report['failed']}")
    print(f"  skipped: {report['skipped']}")


if __name__ == "__main__":
    main()
