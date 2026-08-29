"""Seventeen exercises in what the scikit-learn estimator API actually
guarantees. Read `00_brief.md` first. Each function below is a
`pytest.skip` naming exactly what to build and what to assert; replace the
skip with real code. `estimator_lib.py` is complete -- it is the
machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

from sklearn.linear_model import LogisticRegression  # noqa: F401
from sklearn.pipeline import Pipeline  # noqa: F401
from sklearn.preprocessing import StandardScaler  # noqa: F401

import estimator_lib as e  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def data():
    return e.classification_dataset()


def test_01_the_hand_built_classifier_matches_the_library_one():
    pytest.skip(
        "Assert e.matches_dummy_classifier() is True. MajorityClassifier "
        "inherits nothing from scikit-learn -- it implements fit, predict, "
        "predict_proba, score, get_params and set_params by hand -- yet its "
        "predictions and probabilities are byte-identical to "
        "DummyClassifier(strategy='most_frequent') across five seeds."
    )


def test_02_fitting_adds_exactly_five_learned_attributes(data):
    pytest.skip(
        "Assert e.gained_attributes(LogisticRegression(max_iter=1000), X, y) "
        "equals ['classes_', 'coef_', 'intercept_', 'n_features_in_', "
        "'n_iter_'] -- computed as dir(model) after fit() minus dir(model) "
        "before it. Then assert every gained name ends with '_' and does "
        "not start with '__'. The trailing underscore is not a style "
        "choice; it is a documented convention meaning 'learned from data', "
        "and it is why you can inspect a fitted model's guts without "
        "reading its source."
    )


def test_02b_predict_before_fit_raises_notfittederror_with_a_useful_message(data):
    pytest.skip(
        "Call e.predict_before_fit_message on an unfitted LogisticRegression "
        "and on an unfitted e.MajorityClassifier. Assert both returned "
        "messages contain 'is not fitted yet' and \"Call 'fit'\". The "
        "library estimator and the one built from scratch fail the same "
        "way, for the same reason: neither has anything with a trailing "
        "underscore yet."
    )


def test_03_get_params_and_set_params_round_trip_through_each_other():
    pytest.skip(
        "Assert e.params_roundtrip(LogisticRegression(max_iter=1000), C=2.0) "
        "reports C=2.0 and max_iter=1000 unchanged. Then build a "
        "LogisticRegression(C=0.7, max_iter=500), call "
        "e.params_roundtrip(model, **model.get_params()), and assert the "
        "result equals model.get_params() -- setting params back to what "
        "get_params() already reports must be a no-op. This round trip is "
        "what makes GridSearchCV possible at all: it is nothing more than "
        "get_params, set_params, fit, score, repeated."
    )


def test_03b_clone_produces_a_fresh_unfitted_copy_with_identical_hyperparameters(data):
    pytest.skip(
        "Fit a LogisticRegression(C=0.3, max_iter=1000) on the data fixture. "
        "Call e.clone_is_fresh(fitted, 'coef_') and assert the result equals "
        "{'params_equal': True, 'fresh_is_unfitted': True, "
        "'original_still_fitted': True}. clone() copies hyper-parameters, "
        "never learned state -- which is exactly what lets cross-validation "
        "give every fold a genuinely fresh model."
    )


def test_04_pipeline_exposes_its_steps_nested_hyperparameters():
    pytest.skip(
        "Build Pipeline([('scaler', StandardScaler()), ('clf', "
        "LogisticRegression(C=0.5, max_iter=1000))]). Assert "
        "e.pipeline_param_keys(pipe) contains 'clf', 'scaler', 'clf__C' and "
        "'scaler__with_mean', and that it has exactly 23 entries in total. "
        "A Pipeline is an estimator itself: its own get_params() reaches "
        "into every step's get_params() and prefixes each key with "
        "'<step name>__'."
    )


def test_04b_setting_a_nested_parameter_changes_the_live_step(data):
    pytest.skip(
        "Build the same Pipeline as the previous exercise. Call "
        "e.pipeline_set_nested(pipe, **{'clf__C': 2.0}) and assert the "
        "returned dict has clf__C == 2.0, then assert "
        "pipe.named_steps['clf'].C == 2.0 directly -- the nested set_params "
        "call reached through the Pipeline and mutated the actual "
        "LogisticRegression object living inside it."
    )


def test_05_a_pipeline_step_is_refit_once_per_cv_fold_on_training_rows_only(data):
    pytest.skip(
        "Assert e.fits_per_fold(X, y, folds=5) == 5 and "
        "e.fits_per_fold(X, y, folds=10) == 10. Every fold gets a freshly "
        "cloned copy of the whole pipeline, fit on that fold's training "
        "rows alone -- which is the object-model mechanism that makes Day "
        "143's rule ('anything fitted is fitted on training rows only') "
        "enforceable rather than merely advisable."
    )


def test_06_a_from_scratch_estimator_breaks_inside_cross_val_score(data):
    pytest.skip(
        "Call e.bare_estimator_breaks_in_cross_val_score(X, y) and assert "
        "the returned message contains '__sklearn_tags__' and "
        "'BaseEstimator'. e.MajorityClassifier's fit/predict/score all work "
        "fine when called directly -- this failure comes from "
        "scikit-learn's OWN machinery, which needs to check whether the "
        "estimator is fitted and does so through a method only "
        "BaseEstimator supplies."
    )


def test_06b_inheriting_bare_baseestimator_fixes_it(data):
    pytest.skip(
        "Call e.base_estimator_works_in_pipeline_and_cv(X, y) and assert it "
        "returns 5 scores, all between 0.0 and 1.0, none of them NaN. Then "
        "assert 'get_params' not in e.MajorityClassifierBase.__dict__ and "
        "likewise for 'set_params' -- neither is written anywhere in that "
        "class's own source. BaseEstimator supplies both by inspecting "
        "__init__'s signature, which is the actual mechanism behind the "
        "word 'boilerplate'."
    )


def test_07_scikit_learn_discovers_210_estimators_and_all_implement_fit():
    pytest.skip(
        "Call e.estimator_census() and assert census['total'] == 210 and "
        "census['has_fit'] == 210. Every single one -- classifiers, "
        "regressors, transformers, clusterers, meta-estimators -- "
        "implements fit. That is the whole protocol's foundation."
    )


def test_07b_transform_and_predict_are_not_mutually_exclusive():
    pytest.skip(
        "From the same census, assert has_transform == 90, has_predict == "
        "119, and len(both_transform_and_predict) == 20. Assert 'KMeans' "
        "and 'Pipeline' are both in that list. A plain classifier must "
        "never grow a transform method -- but a clustering estimator "
        "legitimately has both predict (which cluster) and transform "
        "(distance to every cluster centre), and a meta-estimator like "
        "Pipeline inherits both by wrapping whatever it is given."
    )


def test_07c_the_210_total_depends_on_an_explicit_experimental_import():
    pytest.skip(
        "Assert census['bare_total'] == 208, that census['total'] - "
        "census['bare_total'] == 2, and that "
        "census['newly_visible_after_experimental_enable'] equals "
        "['HalvingGridSearchCV', 'HalvingRandomSearchCV']. "
        "'How many estimators does scikit-learn have' has no single "
        "answer: all_estimators() only sees estimators registered in "
        "modules that have actually been imported, and these two live "
        "behind sklearn.experimental.enable_halving_search_cv. The gap is "
        "the mechanism this exercise measures, not the total by itself."
    )


def test_08_argmax_of_predict_proba_equals_predict(data):
    pytest.skip(
        "Assert e.proba_argmax_matches_predict(X, y) is True. predict() and "
        "predict_proba() are not two independent sources of truth -- "
        "predict() is defined as classes_[argmax(predict_proba(X), axis=1)] "
        "on every fitted classifier that has both."
    )


def test_08b_decision_function_agrees_with_predict_too(data):
    pytest.skip(
        "Assert e.decision_function_matches_predict(X, y) is True. For a "
        "binary classifier, predict() is (decision_function(X) > 0); for "
        "multiclass it is classes_[argmax(decision_function(X), axis=1)]. "
        "Three methods, one underlying score."
    )


def test_09_a_fixed_random_state_reproduces_identical_predictions_every_time(data):
    pytest.skip(
        "Call e.random_state_reproducibility(X, y) and assert "
        "result['fixed_identical_across_repeats'] is True. Fitting the same "
        "RandomForestClassifier(random_state=42) five times on the same "
        "data produces five byte-identical prediction vectors."
    )


def test_09b_random_state_none_produces_a_different_model_on_every_fit(data):
    pytest.skip(
        "From the same result, assert "
        "result['none_distinct_prediction_vectors'] >= 2 and "
        "result['accuracy_spread_sd'] > 0.0. random_state=None draws fresh "
        "entropy from the OS on every call by design, so only the "
        "structural claim -- that it varies at all -- is asserted here, "
        "never one captured accuracy figure."
    )


def test_10_check_estimator_reports_48_of_52_checks_passing():
    pytest.skip(
        "Call e.check_estimator_report(e.MajorityClassifierBase()) and "
        "assert report == {'total': 52, 'passed': 48, 'failed': "
        "['check_classifiers_regression_target', 'check_classifiers_train'], "
        "'skipped': ['check_array_api_input', "
        "'check_classifier_data_not_an_array']}. Read troubleshooting.md for "
        "why each of those two checks genuinely fails -- both are honest "
        "findings, not bugs in this lab."
    )
