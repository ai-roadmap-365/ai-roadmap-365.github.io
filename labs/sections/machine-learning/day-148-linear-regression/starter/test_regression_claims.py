"""Twelve exercises in what a simple linear regression actually gets you,
and what it hides.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`regression_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import regression_lib as r  # noqa: F401  (you will need it)


# --- 1. The line, fitted to real data in real units ----------------------


def test_01_bmi_slope_and_intercept_in_raw_units():
    pytest.skip(
        "Load bmi, y with r.load_bmi_and_target() and fit r.fit_line(bmi, y). "
        "Assert model.coef_[0] rounds to 10.2331, model.intercept_ rounds to "
        "-117.7734, and model.score(bmi, y) rounds to 0.3439. That slope "
        "means one more unit of BMI is associated with about ten more points "
        "of one-year disease progression, on this population."
    )


def test_01b_slope_standard_error_and_confidence_interval():
    pytest.skip(
        "Fit the same BMI model, compute its residuals, and pass them to "
        "r.slope_standard_error(bmi, residuals). Assert it rounds to 0.6738. "
        "Then assert r.confidence_interval(slope, se) equals (8.9125, "
        "11.5538), and that slope / se rounds to 15.19 -- about fifteen "
        "standard errors from zero."
    )


def test_01c_the_line_passes_through_the_means_exactly():
    pytest.skip(
        "Call r.passes_through_the_means(model, bmi, y) and assert the "
        "difference is smaller than 1e-8, with both the predicted value at "
        "mean(bmi) and mean(y) rounding to 152.1335. Then assert "
        "r.residual_sum(residuals) is smaller than 1e-6 in absolute value -- "
        "not approximately zero, to within floating point."
    )


# --- 2. Recovering a slope you know to be true ----------------------------


def test_02_the_estimate_gets_closer_to_the_truth_as_n_grows():
    pytest.skip(
        "Call r.slope_recovery_error([20, 50, 200, 1000, 5000]) and assert it "
        "equals [(20, 0.2315), (50, 0.1556), (200, 0.078), (1000, 0.0357), "
        "(5000, 0.0159)]. Then assert the errors are strictly decreasing as n "
        "grows. The true slope is 5.0 and was never told to the fit."
    )


def test_02b_the_error_shrinks_roughly_like_one_over_root_n():
    pytest.skip(
        "Using the same rows, compute the ratio of the error at n=200 to the "
        "error at n=20 and assert it falls between 0.25 and 0.40 (predicted "
        "by one-over-root-n: 1/sqrt(10) = 0.316). Then assert the ratio from "
        "n=20 to n=5000 falls between 0.04 and 0.09 (predicted 1/sqrt(250) = "
        "0.063). This is a noisy quantity, so assert a range, not a formula."
    )


# --- 3. Curvature: a fit that looks fine and is not ------------------------


def test_03_residuals_reveal_the_curve_the_scatter_hides():
    pytest.skip(
        "Fit r.curved_dataset() with r.fit_line and assert the R-squared "
        "rounds to 0.852 -- a respectable-looking number. Then call "
        "r.binned_residual_means(x, residuals, bins=5) and assert the first "
        "bin's mean residual is positive, the middle bin's is negative, and "
        "the last bin's is positive: the missed curve, visible only in the "
        "residuals."
    )


def test_03b_quantifying_the_curvature_with_a_quadratic_fit_to_the_residuals():
    pytest.skip(
        "Assert r.quadratic_fit_r_squared(x, residuals) on the curved "
        "dataset rounds to 0.3558 -- a quadratic explains over a third of "
        "the RESIDUALS' own variance. Then assert "
        "np.corrcoef(residuals, x.flatten() ** 2)[0, 1] rounds to 0.148."
    )


# --- 4. Heteroscedasticity: error that grows with x -------------------------


def test_04_heteroscedasticity_fans_the_residuals_while_the_fit_looks_fine():
    pytest.skip(
        "Fit r.heteroscedastic_dataset() and assert the R-squared rounds to "
        "0.5723. Then call r.residual_spread_by_half(x, residuals) and "
        "assert the low-x-half standard deviation rounds to 4.7427, the "
        "high-x-half rounds to 12.0684, and their ratio rounds to 2.5446. "
        "Nothing in the scatterplot or the R-squared shows this; only the "
        "residual plot does."
    )


# --- 5. One point that moves the line ----------------------------------------


def test_05_one_high_leverage_point_moves_the_line():
    pytest.skip(
        "Fit r.leverage_dataset() with and without one extra point at "
        "x_new=40.0, y_new=5.0 added via r.add_point. Assert the slope "
        "without it rounds to 1.5196, the slope with it rounds to 0.2138, "
        "and the change rounds to -1.3059 -- one row out of forty-one "
        "cutting the slope by more than eighty-five percent."
    )


def test_05b_the_leverage_value_names_the_mechanism():
    pytest.skip(
        "With the extra point added, call r.leverage_of_point(x_with, 40.0) "
        "and r.mean_leverage_excluding(x_with, 40.0). Assert the first "
        "rounds to 0.8048, the second to 0.0299, and their ratio to 26.94 -- "
        "computed from the point's x-value alone, before its y-value is even "
        "considered."
    )


# --- 6. fit_intercept=False, and what it costs -------------------------------


def test_06_forcing_the_intercept_to_zero_costs_you():
    pytest.skip(
        "Fit r.intercept_dataset() with fit_intercept=True and False. Assert "
        "the RMSE with an intercept rounds to 6.1401 and without it rounds "
        "to 9.7878, a ratio of 1.5941. Then assert the intercept-free "
        "model's intercept_ is exactly 0.0 and its slope rounds to 4.4232 -- "
        "the true slope was 3.0 and the true intercept was 25.0; forcing the "
        "intercept to zero makes the slope absorb the difference."
    )


# --- 7. Telling curvature apart from noise ------------------------------------


def test_07_the_bmi_models_residuals_show_no_such_curvature():
    pytest.skip(
        "On the BMI model's own residuals, assert "
        "r.quadratic_fit_r_squared(bmi, residuals) rounds to 0.0002 -- "
        "contrast with exercise 3b's 0.3558 on data with real curvature. "
        "Then assert r.skewness(residuals) rounds to 0.156 and its absolute "
        "value is below 0.5: mildly asymmetric, nothing alarming."
    )
