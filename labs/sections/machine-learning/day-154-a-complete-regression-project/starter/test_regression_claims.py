"""Fourteen exercises: one regression project, run properly, once.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`regression_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import inspect

import numpy as np  # noqa: F401  (you will need it)
import pytest
from sklearn.datasets import fetch_california_housing, load_diabetes  # noqa: F401
from sklearn.dummy import DummyRegressor  # noqa: F401

import regression_lib as r  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def dataset():
    return r.load_dataset()


@pytest.fixture(scope="module")
def split(dataset):
    X, y, _names = dataset
    return r.split_once(X, y, seed=0)


def test_01_the_dataset_is_the_only_bundled_regression_set(dataset):
    pytest.skip(
        "Unpack (X, y, names) from the dataset fixture. Assert X.shape == "
        "(442, 10), names == ['age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', "
        "'s4', 's5', 's6'], y.min() rounds to 25.0, y.max() rounds to 346.0, "
        "and y.mean() rounds to 152.1335. Then assert "
        "inspect.signature(fetch_california_housing).parameters"
        "['download_if_missing'].default is True -- the reason that dataset "
        "is forbidden here and load_diabetes is used instead."
    )


def test_01b_raw_units_are_not_the_scikit_learn_default(dataset):
    pytest.skip(
        "Unpack (X, y, names) from the dataset fixture. Find age's column "
        "index and assert X[:, age_index].min() == 19.0 and .max() == 79.0 "
        "-- real years. Then load load_diabetes(scaled=True) (scikit-learn's "
        "own default) and assert its age column's min is between -0.2 and 0, "
        "and its max is between 0 and 0.2 -- tiny centred floats. This is "
        "why this lab asks for scaled=False."
    )


def test_02_the_baseline_before_any_model(split):
    pytest.skip(
        "Unpack (x_train, x_test, y_train, y_test) from the split fixture. "
        "Call r.baseline_metrics and assert the RMSE rounds to 70.4637 and "
        "R2 rounds to -0.0001. Every model in this exercise has to beat "
        "70.4637 RMSE to be worth building at all."
    )


def test_03_the_split_holds_the_test_rows_back(dataset):
    pytest.skip(
        "Unpack (X, y, _names) from the dataset fixture and call "
        "r.split_once(X, y, seed=0). Assert x_train.shape == (331, 10) and "
        "x_test.shape == (111, 10). 111 test rows on 442 total is small -- "
        "every interval computed later in this exercise is wide because of "
        "it, and that is the point, not a bug."
    )


def test_04_the_sweep_counts_twenty_three_candidate_pipelines():
    pytest.skip(
        "Assert r.candidate_count() == 23. Then unpack the (family, param, "
        "make) triples from r.candidate_configs() and assert there are 11 "
        "'ridge', 11 'lasso' and 1 'ols' entries. K is the number nobody "
        "remembers -- count it before doing anything else with it."
    )


def test_05_cross_validation_selects_the_winner_on_train_rows_only(split):
    pytest.skip(
        "Unpack (x_train, _x_test, y_train, _y_test) from the split fixture "
        "and call r.select_best(x_train, y_train, seed=0). Assert the "
        "returned (family, param) equals ('lasso', 1) and cv_rmse equals "
        "53.8958. The winner was chosen on cross-validated train rows -- "
        "the test rows have not been touched yet."
    )


def test_06_the_gate_permits_exactly_one_test_evaluation(split):
    pytest.skip(
        "Fit the winner from r.select_best on the train rows, wrap "
        "(x_test, y_test) in r.GatedTestSet, and assert the first "
        "evaluation returns (56.5566, 0.3557, 45.2846) for (rmse, r2, mae) "
        "and the counter becomes 1. Then assert a second evaluation raises "
        "r.TestSetTouchedTwice mentioning 'validation score', and that the "
        "counter did NOT advance on the refused attempt."
    )


def test_07_the_margin_has_a_bootstrap_interval(split):
    pytest.skip(
        "Fit a DummyRegressor(strategy='mean') baseline and the winner from "
        "r.select_best, both on x_train/y_train. Predict both on x_test. "
        "Call r.margin_bootstrap_interval(y_test, pred_baseline, pred_model, "
        "seed=0) and assert it returns (5.5852, 22.3324). Assert the point "
        "margin -- baseline RMSE minus model RMSE -- rounds to 13.9071, and "
        "that r.margin_distinguishable(lower, upper) is True: the margin "
        "clears the interval's lower bound."
    )


def test_08_the_residual_vs_fitted_diagnostic(split):
    pytest.skip(
        "Fit the winner and predict on x_test. Call r.residual_summary and "
        "assert it returns (-3.6262, 56.4402). Call "
        "r.heteroscedasticity_signal(pred, y_test) and assert it rounds to "
        "0.2386. Call r.curvature_signal(pred, y_test) and assert it rounds "
        "to -0.1278. Neither signal is dramatic here -- report both anyway."
    )


def test_08b_the_normal_probability_check_and_the_largest_residuals(split):
    pytest.skip(
        "Fit the winner and predict on x_test. Call "
        "r.normal_probability_correlation(y_test, pred) and assert it "
        "rounds to 0.9901. Call r.largest_residuals(y_test, pred, n=5) and "
        "assert the first two rows equal (60, 52.0, 209.3314, -157.3314) "
        "and (65, 302.0, 153.8865, 148.1135). 0.9901 is close to a straight "
        "Q-Q line -- these residuals are close to normal even on real data."
    )


def test_09_error_by_target_level(split):
    pytest.skip(
        "Fit the winner and predict on x_test. Call "
        "r.error_by_target_level(y_test, pred) and assert it returns "
        "(55.2464, 57.8601, 1.0473). A ratio of 1.0473 means the model is "
        "only 4.73 percent worse on the more-severe half of test targets -- "
        "measure it before assuming a disease-progression model is fair or "
        "unfair across severity."
    )


def test_10_the_leaky_version_selects_by_peeking_at_the_test_set(split):
    pytest.skip(
        "Fit the honest winner and compute its test RMSE (round to 4 "
        "places). Call r.leaky_selection_test_rmse(x_train, y_train, "
        "x_test, y_test), which fits every one of the 23 candidates and "
        "lets the test set itself pick the winner by lowest RMSE. Assert "
        "the honest RMSE is 56.5566, the leaky RMSE is 55.5212, and "
        "leaky_rmse <= honest_rmse -- lower RMSE is better, so the leak can "
        "only match or beat the honest score, never lose to it."
    )


def test_10b_the_leaky_gap_over_twenty_seeds(dataset):
    pytest.skip(
        "Call r.leaky_vs_honest_over_seeds(X, y, seeds=range(20)). Assert "
        "20 rows come back. Compute the mean, sd, min and max of the gap "
        "column and assert they round to 0.5279, 0.3686, 0.011 and 1.1451. "
        "Then assert every single gap is non-negative -- across 20 "
        "independent seeds, selecting by peeking at the test set never once "
        "reported a worse (higher) RMSE than selecting honestly."
    )


def test_11_prediction_interval_coverage(split):
    pytest.skip(
        "Fit the winner. Call r.prediction_interval_coverage(x_train, "
        "y_train, x_test, y_test, fitted, seed=0) and assert it returns "
        "(105.8797, 0.9459). The half-width comes from TRAINING residuals "
        "only, never from the test residuals themselves -- sizing an "
        "interval from the data you are about to check it against would be "
        "circular. 0.9459 measured against a 0.95 nominal, on 111 test rows."
    )
