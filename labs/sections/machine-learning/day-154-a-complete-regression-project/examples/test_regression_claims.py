"""The reference solutions: one regression project, run properly, once.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import inspect

import numpy as np
import pytest
from sklearn.datasets import fetch_california_housing, load_diabetes
from sklearn.dummy import DummyRegressor

import regression_lib as r


@pytest.fixture(scope="module")
def dataset():
    return r.load_dataset()


@pytest.fixture(scope="module")
def split(dataset):
    X, y, _names = dataset
    return r.split_once(X, y, seed=0)


# --- 1. The dataset, and why it is the only one used ------------------------


def test_01_the_dataset_is_the_only_bundled_regression_set(dataset):
    X, y, names = dataset
    assert X.shape == (442, 10)
    assert names == ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
    assert round(float(y.min()), 4) == 25.0
    assert round(float(y.max()), 4) == 346.0
    assert round(float(y.mean()), 4) == 152.1335
    # fetch_california_housing downloads by default -- forbidden by this
    # lab's offline rule -- while load_diabetes never touches the network.
    sig = inspect.signature(fetch_california_housing)
    assert sig.parameters["download_if_missing"].default is True


def test_01b_raw_units_are_not_the_scikit_learn_default(dataset):
    X, y, names = dataset
    # This lab's loader asks for scaled=False. Compare against scikit-learn's
    # own default (scaled=True) to see why: the default is mean-centred and
    # variance-scaled to tiny floats, not the years and mg/dL a reader could
    # sanity-check a coefficient against.
    default = load_diabetes(scaled=True)
    age_index = names.index("age")
    assert X[:, age_index].min() == 19.0
    assert X[:, age_index].max() == 79.0
    assert -0.2 < default.data[:, age_index].min() < 0
    assert 0 < default.data[:, age_index].max() < 0.2


# --- 2. The frame and the baseline -----------------------------------------


def test_02_the_baseline_before_any_model(split):
    x_train, x_test, y_train, y_test = split
    rmse, r2 = r.baseline_metrics(x_train, y_train, x_test, y_test)
    assert rmse == 70.4637
    assert r2 == -0.0001
    # Every model below has to beat 70.4637 RMSE to be worth building.


# --- 3. The split -------------------------------------------------------


def test_03_the_split_holds_the_test_rows_back(dataset):
    X, y, _names = dataset
    x_train, x_test, y_train, y_test = r.split_once(X, y, seed=0)
    assert x_train.shape == (331, 10)
    assert x_test.shape == (111, 10)
    # 111 test rows on a 442-row dataset: small, and every interval below
    # is wide because of it -- that is the point, not a flaw to fix.


# --- 4. The sweep --------------------------------------------------------


def test_04_the_sweep_counts_twenty_three_candidate_pipelines():
    assert r.candidate_count() == 23
    families = [family for family, _param, _make in r.candidate_configs()]
    assert families.count("ridge") == 11
    assert families.count("lasso") == 11
    assert families.count("ols") == 1


# --- 5. Cross-validate, then select --------------------------------------


def test_05_cross_validation_selects_the_winner_on_train_rows_only(split):
    x_train, _x_test, y_train, _y_test = split
    family, param, cv_rmse, fitted = r.select_best(x_train, y_train, seed=0)
    assert (family, param) == ("lasso", 1)
    assert cv_rmse == 53.8958
    assert hasattr(fitted, "predict")
    # The winner was chosen on cross-validated train rows; test has not
    # been touched.


# --- 6. The gate: one look at the test set ----------------------------------


def test_06_the_gate_permits_exactly_one_test_evaluation(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    gate = r.GatedTestSet(x_test, y_test)
    assert gate.evaluations == 0
    rmse, r2, mae = gate.evaluate(fitted)
    assert rmse == 56.5566
    assert r2 == 0.3557
    assert mae == 45.2846
    assert gate.evaluations == 1
    with pytest.raises(r.TestSetTouchedTwice) as excinfo:
        gate.evaluate(fitted)
    assert "validation score" in str(excinfo.value)
    assert gate.evaluations == 1


# --- 7. The margin, with a bootstrap interval ------------------------------


def test_07_the_margin_has_a_bootstrap_interval(split):
    x_train, x_test, y_train, y_test = split
    baseline = DummyRegressor(strategy="mean").fit(x_train, y_train)
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    pred_baseline = baseline.predict(x_test)
    pred_model = fitted.predict(x_test)
    lower, upper = r.margin_bootstrap_interval(y_test, pred_baseline, pred_model, seed=0)
    assert lower == 5.5852
    assert upper == 22.3324
    rmse_base, _r2_base = r.baseline_metrics(x_train, y_train, x_test, y_test)
    rmse_model = float(np.sqrt(np.mean((y_test - pred_model) ** 2)))
    margin = round(rmse_base - rmse_model, 4)
    assert margin == 13.9071
    # The margin (13.9071) clears the interval's lower bound (5.5852): this
    # model IS distinguishable from the baseline at this test-set size.
    assert r.margin_distinguishable(lower, upper) is True


# --- 8. Residual diagnostics -- the centrepiece ----------------------------


def test_08_the_residual_vs_fitted_diagnostic(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    pred = fitted.predict(x_test)
    resid_mean, resid_std = r.residual_summary(y_test, pred)
    assert resid_mean == -3.6262
    assert resid_std == 56.4402
    het = r.heteroscedasticity_signal(pred, y_test)
    curv = r.curvature_signal(pred, y_test)
    assert het == 0.2386
    assert curv == -0.1278
    # A modest positive heteroscedasticity signal (errors fan out a little
    # as predictions rise) and a weak curvature signal (no strong missed
    # trend) -- neither dramatic, both worth reporting rather than ignoring.


def test_08b_the_normal_probability_check_and_the_largest_residuals(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    pred = fitted.predict(x_test)
    qq = r.normal_probability_correlation(y_test, pred)
    assert qq == 0.9901
    rows = r.largest_residuals(y_test, pred, n=5)
    assert len(rows) == 5
    assert rows[0] == (60, 52.0, 209.3314, -157.3314)
    assert rows[1] == (65, 302.0, 153.8865, 148.1135)
    # 0.9901 is close to a perfectly straight Q-Q line: these residuals are
    # not wildly non-normal, even on real data with only 111 test rows.


# --- 9. Is the model worse for high-value targets? Measure it. -------------


def test_09_error_by_target_level(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    pred = fitted.predict(x_test)
    rmse_low, rmse_high, ratio = r.error_by_target_level(y_test, pred)
    assert rmse_low == 55.2464
    assert rmse_high == 57.8601
    assert ratio == 1.0473
    # Only 4.73 percent worse on the more-severe half: not the dramatic
    # fairness problem this exercise sets out to check for, at this seed --
    # and that is exactly why the check has to run rather than be assumed.


# --- 10. The leaky version --------------------------------------------------


def test_10_the_leaky_version_selects_by_peeking_at_the_test_set(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    honest_rmse = round(float(np.sqrt(np.mean((y_test - fitted.predict(x_test)) ** 2))), 4)
    leaky_rmse = r.leaky_selection_test_rmse(x_train, y_train, x_test, y_test)
    assert honest_rmse == 56.5566
    assert leaky_rmse == 55.5212
    # Lower RMSE is better: the leak can only match or beat the honest
    # score, never lose to it.
    assert leaky_rmse <= honest_rmse


def test_10b_the_leaky_gap_over_twenty_seeds(dataset):
    X, y, _names = dataset
    rows = r.leaky_vs_honest_over_seeds(X, y, seeds=range(20))
    assert len(rows) == 20
    gaps = np.array([row[3] for row in rows])
    assert round(float(gaps.mean()), 4) == 0.5279
    assert round(float(gaps.std()), 4) == 0.3686
    assert round(float(gaps.min()), 4) == 0.011
    assert round(float(gaps.max()), 4) == 1.1451
    # The leak never once hurt the reported number, across 20 independent
    # seeds: the mechanism, not luck.
    assert (gaps >= 0).all()


# --- 11. Prediction intervals, and their realised coverage -----------------


def test_11_prediction_interval_coverage(split):
    x_train, x_test, y_train, y_test = split
    _family, _param, _cv, fitted = r.select_best(x_train, y_train, seed=0)
    half_width, coverage = r.prediction_interval_coverage(
        x_train, y_train, x_test, y_test, fitted, seed=0
    )
    assert half_width == 105.8797
    assert coverage == 0.9459
    # Nominal is 0.95; measured is 0.9459 -- close, on only 111 test rows.
    assert 0.85 < coverage <= 1.0
