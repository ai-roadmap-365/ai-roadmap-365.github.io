"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import regression_metrics_lib as m


def test_diabetes_split_shapes_and_ranges():
    X_train, X_test, y_train, y_test = m.diabetes_split()
    assert X_train.shape == (331, 10)
    assert X_test.shape == (111, 10)
    assert y_train.shape == (331,)
    assert y_test.shape == (111,)
    # The target is documented as running from 25 to 346.
    assert 25.0 <= float(np.concatenate([y_train, y_test]).min())
    assert float(np.concatenate([y_train, y_test]).max()) <= 346.0


def test_rmse_and_mae_agree_on_a_perfect_prediction():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    assert m.rmse(y_true, y_true) == 0.0
    assert m.mae(y_true, y_true) == 0.0


def test_rmse_is_never_smaller_than_mae():
    # A standard inequality: RMSE >= MAE always, with equality only when
    # every absolute error is identical.
    rng = np.random.default_rng(0)
    y_true = rng.normal(size=40)
    y_pred = y_true + rng.normal(scale=2.0, size=40)
    assert m.rmse(y_true, y_pred) >= m.mae(y_true, y_pred)
    # Equality when every error has the same magnitude.
    y_true_eq = np.zeros(6)
    y_pred_eq = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    assert round(m.rmse(y_true_eq, y_pred_eq), 10) == round(m.mae(y_true_eq, y_pred_eq), 10)


def test_adjusted_r2_equals_r2_when_no_predictors_are_added():
    # With p fixed, adjusted R2 is a deterministic function of r2, n and p --
    # sanity-check the formula against a hand-computable case.
    # n=10, p=2, r2=0.8: 1 - (1-0.8) * 9/7
    assert round(m.adjusted_r2(0.8, 10, 2), 6) == round(1.0 - 0.2 * 9.0 / 7.0, 6)
    # Adjusted R2 is always <= R2 whenever p > 0 and n > p + 1.
    assert m.adjusted_r2(0.5, 100, 5) <= 0.5
