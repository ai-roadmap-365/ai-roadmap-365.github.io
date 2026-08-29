"""Regression metrics, measured: what each one reports, and what it hides.

Day 149 drew the line once: a loss is what you optimise, a metric is what
you report, and they need not be the same function. This module measures
the reporting side for regression -- RMSE, MAE, MAPE, R-squared and
adjusted R-squared -- and the traps in each, on the diabetes dataset
(``sklearn.datasets.load_diabetes``) and on constructed data where a
property needs to be exact rather than merely typical.

Everything here is deterministic given a seed.
"""

from __future__ import annotations

import numpy as np

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


# --------------------------------------------------------------------------
# 0. The dataset this module shares
# --------------------------------------------------------------------------


def diabetes_split(scaled: bool = True, seed: int = 0):
    """The 75/25 split every measurement below is built on."""
    X, y = load_diabetes(return_X_y=True, scaled=scaled)
    return train_test_split(X, y, test_size=0.25, random_state=seed)


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mae(y_true, y_pred) -> float:
    return float(mean_absolute_error(y_true, y_pred))


# --------------------------------------------------------------------------
# 1. Train R-squared is not a quality measure: the noise-column climb
# --------------------------------------------------------------------------


def adjusted_r2(r2: float, n: int, p: int) -> float:
    """R-squared, penalised for the number of predictors used to get it."""
    return 1.0 - (1.0 - r2) * (n - 1) / (n - p - 1)


def noise_column_r2_curve(noise_counts=(0, 1, 5, 20, 100), seed: int = 0):
    """Train R2 and adjusted R2 as pure-noise columns are added.

    Every added column is independent standard-normal noise with no
    relationship whatsoever to the target. Returns rows of
    ``(n_noise, n_rows, n_predictors, train_r2, adjusted_r2)``.
    """
    X_train, _X_test, y_train, _y_test = diabetes_split(seed=0)
    rng = np.random.default_rng(seed)
    rows = []
    for n_noise in noise_counts:
        if n_noise == 0:
            X_aug = X_train
        else:
            noise = rng.normal(size=(X_train.shape[0], n_noise))
            X_aug = np.hstack([X_train, noise])
        model = LinearRegression().fit(X_aug, y_train)
        r2 = r2_score(y_train, model.predict(X_aug))
        n_rows, n_predictors = X_aug.shape
        rows.append((n_noise, n_rows, n_predictors, round(r2, 4), round(adjusted_r2(r2, n_rows, n_predictors), 4)))
    return rows


def full_model_test_r2(seed: int = 0) -> float:
    """The test R2 of the ordinary ten-feature model -- the honest number."""
    X_train, X_test, y_train, y_test = diabetes_split(seed=seed)
    model = LinearRegression().fit(X_train, y_train)
    return round(float(r2_score(y_test, model.predict(X_test))), 4)


# --------------------------------------------------------------------------
# 2. R-squared is not bounded below by zero
# --------------------------------------------------------------------------


def constant_mean_test_r2(seed: int = 0) -> float:
    """R2 of predicting the train mean for every test row."""
    _X_train, _X_test, y_train, y_test = diabetes_split(seed=seed)
    prediction = np.full_like(y_test, y_train.mean(), dtype=float)
    return round(float(r2_score(y_test, prediction)), 4)


def bad_predictor_test_r2(seed: int = 0) -> float:
    """R2 of a deliberately bad predictor: zero, always."""
    _X_train, _X_test, _y_train, y_test = diabetes_split(seed=seed)
    prediction = np.zeros_like(y_test, dtype=float)
    return round(float(r2_score(y_test, prediction)), 4)


# --------------------------------------------------------------------------
# 3. RMSE versus MAE under an outlier
# --------------------------------------------------------------------------


def rmse_mae_outlier_shift(seed: int = 1, n: int = 50, shift: float = 200.0):
    """Same predictions, one target moved far away. Which metric moves more?

    Returns ``(rmse_before, mae_before, rmse_after, mae_after)``.
    """
    rng = np.random.default_rng(seed)
    y_true = rng.normal(100.0, 10.0, size=n)
    y_pred = y_true + rng.normal(0.0, 3.0, size=n)
    before = (rmse(y_true, y_pred), mae(y_true, y_pred))

    y_true_shifted = y_true.copy()
    y_true_shifted[0] += shift
    after = (rmse(y_true_shifted, y_pred), mae(y_true_shifted, y_pred))
    return round(before[0], 4), round(before[1], 4), round(after[0], 4), round(after[1], 4)


# --------------------------------------------------------------------------
# 4. MAPE breaking: zero targets, near-zero targets, and structural asymmetry
# --------------------------------------------------------------------------


def mape_at_zero_target() -> float:
    """MAPE where one true value is exactly zero.

    Not undefined in the mathematical sense of raising -- scikit-learn
    floors the denominator at machine epsilon, so this returns a huge,
    silently wrong number rather than an error or a warning.
    """
    y_true = np.array([10.0, 20.0, 0.0, 30.0])
    y_pred = np.array([12.0, 18.0, 5.0, 28.0])
    return float(mean_absolute_percentage_error(y_true, y_pred))


def mape_near_zero_target():
    """MAPE explodes on a true value close to (but not) zero.

    Returns ``(mape, mae)`` on the same three rows, so the contrast between
    a metric that explodes and one that does not is visible in one call.
    """
    y_true = np.array([100.0, 100.0, 0.5])
    y_pred = np.array([105.0, 95.0, 5.5])
    return (
        round(float(mean_absolute_percentage_error(y_true, y_pred)), 4),
        round(float(mean_absolute_error(y_true, y_pred)), 4),
    )


def mape_asymmetry_bound(true_value: float = 100.0):
    """MAPE's structural asymmetry: bounded under, unbounded over.

    A model that under-predicts every row can be wrong by at most 100
    percent (predict zero, and the error cannot exceed the true value).
    A model that over-predicts has no such ceiling. Returns
    ``(max_under_prediction_mape, ten_times_over_prediction_mape)``.
    """
    y_true = np.full(5, true_value)
    max_under = np.zeros(5)  # the worst possible under-prediction: always zero
    ten_x_over = y_true * 11.0  # predicting eleven times the true value
    return (
        round(float(mean_absolute_percentage_error(y_true, max_under)), 4),
        round(float(mean_absolute_percentage_error(y_true, ten_x_over)), 4),
    )


# --------------------------------------------------------------------------
# 5. A metric ranking inversion: RMSE and MAE prefer different models
# --------------------------------------------------------------------------


def ranking_inversion_models(seed: int = 2, n: int = 100):
    """Two models scored on the same targets: one wins on RMSE, one on MAE.

    Model A makes many small, consistent errors. Model B is right almost
    everywhere but wrong by a lot on a few rows. Returns
    ``(rmse_a, mae_a, rmse_b, mae_b)``.
    """
    rng = np.random.default_rng(seed)
    y_true = rng.normal(50.0, 5.0, size=n)

    errors_a = rng.normal(0.0, 2.0, size=n)
    pred_a = y_true + errors_a

    errors_b = np.zeros(n)
    big_idx = rng.choice(n, size=5, replace=False)
    errors_b[big_idx] = rng.normal(0.0, 15.0, size=5)
    pred_b = y_true + errors_b

    return (
        round(rmse(y_true, pred_a), 4),
        round(mae(y_true, pred_a), 4),
        round(rmse(y_true, pred_b), 4),
        round(mae(y_true, pred_b), 4),
    )


# --------------------------------------------------------------------------
# 6. Units: RMSE and MAE carry the units of the target
# --------------------------------------------------------------------------


def raw_and_scaled_metrics(seed: int = 0):
    """RMSE, MAE and R2 fit on raw-unit features versus standardised ones.

    ``load_diabetes(scaled=False)`` returns the ten features in their
    original units -- age in years, bmi as bmi, blood pressure as measured
    -- while the target is the same disease-progression score either way.
    Ordinary least squares is invariant to a per-column affine rescaling of
    its inputs, so this returns identical numbers under both, which is
    itself the thing worth confirming rather than assuming.
    """
    results = {}
    for label, scaled in (("scaled", True), ("raw", False)):
        X_train, X_test, y_train, y_test = diabetes_split(scaled=scaled, seed=seed)
        model = LinearRegression().fit(X_train, y_train)
        pred = model.predict(X_test)
        results[label] = (round(rmse(y_test, pred), 4), round(mae(y_test, pred), 4), round(float(r2_score(y_test, pred)), 4))
    return results


# --------------------------------------------------------------------------
# 7. r2_score: agreement with .score, and the argument-order bug
# --------------------------------------------------------------------------


def r2_score_vs_model_score(seed: int = 0):
    """r2_score(y_true, y_pred) against LinearRegression.score(X, y)."""
    X_train, X_test, y_train, y_test = diabetes_split(seed=seed)
    model = LinearRegression().fit(X_train, y_train)
    pred = model.predict(X_test)
    return round(float(r2_score(y_test, pred)), 6), round(float(model.score(X_test, y_test)), 6)


def r2_score_argument_order(seed: int = 0):
    """r2_score is NOT symmetric in its two arguments: swap them and it changes.

    Returns ``(correct_order, swapped_order)``.
    """
    X_train, X_test, y_train, y_test = diabetes_split(seed=seed)
    model = LinearRegression().fit(X_train, y_train)
    pred = model.predict(X_test)
    return round(float(r2_score(y_test, pred)), 6), round(float(r2_score(pred, y_test)), 6)
