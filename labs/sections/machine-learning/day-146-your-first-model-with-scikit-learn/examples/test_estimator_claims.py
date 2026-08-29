"""The reference solutions: what the estimator API actually guarantees,
measured against the real library rather than assumed from its docs.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import estimator_lib as e


@pytest.fixture(scope="module")
def data():
    return e.classification_dataset()


# --- 1. The hand-built estimator against the library one -----------------


def test_01_the_hand_built_classifier_matches_the_library_one():
    assert e.matches_dummy_classifier() is True


# --- 2. What fitting actually adds ----------------------------------------


def test_02_fitting_adds_exactly_five_learned_attributes(data):
    X, y = data
    gained = e.gained_attributes(LogisticRegression(max_iter=1000), X, y)
    assert gained == ["classes_", "coef_", "intercept_", "n_features_in_", "n_iter_"]
    # Every one of them is a documented convention: learned from data.
    assert all(name.endswith("_") and not name.startswith("__") for name in gained)


def test_02b_predict_before_fit_raises_notfittederror_with_a_useful_message(data):
    X, _y = data
    library_message = e.predict_before_fit_message(LogisticRegression(), n_features=X.shape[1])
    ours_message = e.predict_before_fit_message(e.MajorityClassifier(), n_features=X.shape[1])
    for message in (library_message, ours_message):
        assert "is not fitted yet" in message
        assert "Call 'fit'" in message


# --- 3. get_params, set_params, clone -------------------------------------


def test_03_get_params_and_set_params_round_trip_through_each_other():
    after = e.params_roundtrip(LogisticRegression(max_iter=1000), C=2.0)
    assert after["C"] == 2.0
    assert after["max_iter"] == 1000
    # Setting params back to what get_params() reports is a no-op.
    model = LogisticRegression(C=0.7, max_iter=500)
    same = e.params_roundtrip(model, **model.get_params())
    assert same == model.get_params()


def test_03b_clone_produces_a_fresh_unfitted_copy_with_identical_hyperparameters(data):
    X, y = data
    fitted = LogisticRegression(C=0.3, max_iter=1000).fit(X, y)
    result = e.clone_is_fresh(fitted, "coef_")
    assert result == {
        "params_equal": True,
        "fresh_is_unfitted": True,
        "original_still_fitted": True,
    }


# --- 4. Pipeline as an estimator itself -----------------------------------


def test_04_pipeline_exposes_its_steps_nested_hyperparameters():
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=0.5, max_iter=1000))])
    keys = e.pipeline_param_keys(pipe)
    assert "clf" in keys and "scaler" in keys
    assert "clf__C" in keys and "scaler__with_mean" in keys
    # The step's own name plus "__" plus its parameter name, mechanically.
    assert len(keys) == 23


def test_04b_setting_a_nested_parameter_changes_the_live_step(data):
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=0.5, max_iter=1000))])
    after = e.pipeline_set_nested(pipe, **{"clf__C": 2.0})
    assert after["clf__C"] == 2.0
    assert pipe.named_steps["clf"].C == 2.0


def test_05_a_pipeline_step_is_refit_once_per_cv_fold_on_training_rows_only(data):
    X, y = data
    assert e.fits_per_fold(X, y, folds=5) == 5
    assert e.fits_per_fold(X, y, folds=10) == 10


# --- 5. Where "just a protocol" needs a footnote --------------------------


def test_06_a_from_scratch_estimator_breaks_inside_cross_val_score(data):
    X, y = data
    message = e.bare_estimator_breaks_in_cross_val_score(X, y)
    assert "__sklearn_tags__" in message
    assert "BaseEstimator" in message


def test_06b_inheriting_bare_baseestimator_fixes_it(data):
    X, y = data
    scores = e.base_estimator_works_in_pipeline_and_cv(X, y)
    assert len(scores) == 5
    assert all(0.0 <= score <= 1.0 for score in scores)
    assert not any(np.isnan(scores))
    # get_params/set_params are not written anywhere in MajorityClassifierBase's
    # own source -- BaseEstimator supplies both by introspecting __init__.
    assert "get_params" not in e.MajorityClassifierBase.__dict__
    assert "set_params" not in e.MajorityClassifierBase.__dict__


# --- 6. How many estimators implement fit? --------------------------------


def test_07_scikit_learn_discovers_210_estimators_and_all_implement_fit():
    census = e.estimator_census()
    assert census["total"] == 210
    assert census["has_fit"] == 210


def test_07b_transform_and_predict_are_not_mutually_exclusive():
    census = e.estimator_census()
    assert census["has_transform"] == 90
    assert census["has_predict"] == 119
    assert len(census["both_transform_and_predict"]) == 20
    assert "KMeans" in census["both_transform_and_predict"]
    assert "Pipeline" in census["both_transform_and_predict"]


def test_07c_the_210_total_depends_on_an_explicit_experimental_import():
    census = e.estimator_census()
    # Discovery without the experimental enabler undercounts by exactly the
    # two Halving search estimators -- not a fuzzy "roughly fewer," an exact
    # gap, because that gap IS the mechanism being measured.
    assert census["bare_total"] == 208
    assert census["total"] - census["bare_total"] == 2
    assert census["newly_visible_after_experimental_enable"] == [
        "HalvingGridSearchCV",
        "HalvingRandomSearchCV",
    ]


# --- 7. predict, predict_proba, decision_function -------------------------


def test_08_argmax_of_predict_proba_equals_predict(data):
    X, y = data
    assert e.proba_argmax_matches_predict(X, y) is True


def test_08b_decision_function_agrees_with_predict_too(data):
    X, y = data
    assert e.decision_function_matches_predict(X, y) is True


# --- 8. random_state: what None actually costs -----------------------------


def test_09_a_fixed_random_state_reproduces_identical_predictions_every_time(data):
    X, y = data
    result = e.random_state_reproducibility(X, y)
    assert result["fixed_identical_across_repeats"] is True


def test_09b_random_state_none_produces_a_different_model_on_every_fit(data):
    X, y = data
    result = e.random_state_reproducibility(X, y)
    # Sampled by design -- assert the structural claim, not one captured value.
    assert result["none_distinct_prediction_vectors"] >= 2
    assert result["accuracy_spread_sd"] > 0.0


# --- 9. The estimator contract, checked mechanically ------------------------


def test_10_check_estimator_reports_48_of_52_checks_passing():
    report = e.check_estimator_report(e.MajorityClassifierBase())
    assert report["total"] == 52
    assert report["passed"] == 48
    assert report["failed"] == ["check_classifiers_regression_target", "check_classifiers_train"]
    assert report["skipped"] == ["check_array_api_input", "check_classifier_data_not_an_array"]
