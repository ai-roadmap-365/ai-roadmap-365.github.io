"""The reference solutions: what a simple linear regression actually gets
you, and what it hides.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np

import regression_lib as r


# --- 1. The line, fitted to real data in real units ----------------------


def test_01_bmi_slope_and_intercept_in_raw_units():
    bmi, y = r.load_bmi_and_target()
    model = r.fit_line(bmi, y)
    assert round(float(model.coef_[0]), 4) == 10.2331
    assert round(float(model.intercept_), 4) == -117.7734
    assert round(float(model.score(bmi, y)), 4) == 0.3439
    # In words: each additional unit of BMI is associated with about ten
    # more points of one-year disease progression, on this population.


def test_01b_slope_standard_error_and_confidence_interval():
    bmi, y = r.load_bmi_and_target()
    model = r.fit_line(bmi, y)
    residuals = y - model.predict(bmi)
    se = r.slope_standard_error(bmi, residuals)
    assert round(se, 4) == 0.6738
    ci = r.confidence_interval(float(model.coef_[0]), se)
    assert ci == (8.9125, 11.5538)
    # The slope is about fifteen standard errors from zero -- not a
    # borderline effect.
    assert round(float(model.coef_[0]) / se, 2) == 15.19


def test_01c_the_line_passes_through_the_means_exactly():
    bmi, y = r.load_bmi_and_target()
    model = r.fit_line(bmi, y)
    residuals = y - model.predict(bmi)
    predicted_at_mean, mean_y, diff = r.passes_through_the_means(model, bmi, y)
    assert abs(diff) < 1e-8
    assert round(predicted_at_mean, 4) == round(mean_y, 4) == 152.1335
    # And the residuals sum to (essentially) zero -- not approximately,
    # to within floating point.
    assert abs(r.residual_sum(residuals)) < 1e-6


# --- 2. Recovering a slope you know to be true ----------------------------


def test_02_the_estimate_gets_closer_to_the_truth_as_n_grows():
    rows = r.slope_recovery_error([20, 50, 200, 1000, 5000])
    assert rows == [
        (20, 0.2315),
        (50, 0.1556),
        (200, 0.078),
        (1000, 0.0357),
        (5000, 0.0159),
    ]
    errors = [e for _n, e in rows]
    # Strictly shrinking as n grows.
    assert all(a > b for a, b in zip(errors, errors[1:]))


def test_02b_the_error_shrinks_roughly_like_one_over_root_n():
    rows = r.slope_recovery_error([20, 50, 200, 1000, 5000])
    by_n = dict(rows)
    # 200 has 10x the rows of 20; one-over-root-n predicts a shrink of
    # about 1/sqrt(10) = 0.316. The measured ratio is close, not exact --
    # this is a noisy quantity averaged over 200 replications, not a
    # formula being evaluated.
    ratio_20_to_200 = by_n[200] / by_n[20]
    assert 0.25 < ratio_20_to_200 < 0.40
    # 5000 has 250x the rows of 20; predicted shrink about 1/sqrt(250) = 0.063.
    ratio_20_to_5000 = by_n[5000] / by_n[20]
    assert 0.04 < ratio_20_to_5000 < 0.09


# --- 3. Curvature: a fit that looks fine and is not -----------------------


def test_03_residuals_reveal_the_curve_the_scatter_hides():
    x, y = r.curved_dataset()
    model = r.fit_line(x, y)
    residuals = y - model.predict(x)
    # The line's own R-squared looks respectable...
    assert round(float(model.score(x, y)), 4) == 0.852
    # ...but the residuals, binned by x, trace the missed curve: positive
    # at both ends, negative in the middle.
    bins = r.binned_residual_means(x, residuals, bins=5)
    means = [m for _x, m in bins]
    assert means[0] > 0
    assert means[2] < 0
    assert means[-1] > 0


def test_03b_quantifying_the_curvature_with_a_quadratic_fit_to_the_residuals():
    x, y = r.curved_dataset()
    model = r.fit_line(x, y)
    residuals = y - model.predict(x)
    # A quadratic curve explains over a third of the *residuals'* own
    # variance -- there is a whole model's worth of missed structure left
    # in what the line called "error".
    quad_r2 = r.quadratic_fit_r_squared(x, residuals)
    assert round(quad_r2, 4) == 0.3558
    corr = float(np.corrcoef(residuals, x.flatten() ** 2)[0, 1])
    assert round(corr, 4) == 0.148


# --- 4. Heteroscedasticity: error that grows with x ------------------------


def test_04_heteroscedasticity_fans_the_residuals_while_the_fit_looks_fine():
    x, y = r.heteroscedastic_dataset()
    model = r.fit_line(x, y)
    residuals = y - model.predict(x)
    # A perfectly ordinary-looking R-squared...
    assert round(float(model.score(x, y)), 4) == 0.5723
    # ...over noise whose spread more than doubles from the low half of x
    # to the high half. Nothing in the scatterplot or the R-squared says
    # so; only the residual plot does.
    low_sd, high_sd = r.residual_spread_by_half(x, residuals)
    assert round(low_sd, 4) == 4.7427
    assert round(high_sd, 4) == 12.0684
    assert round(high_sd / low_sd, 4) == 2.5446


# --- 5. One point that moves the line --------------------------------------


def test_05_one_high_leverage_point_moves_the_line():
    x, y = r.leverage_dataset()
    model_without = r.fit_line(x.reshape(-1, 1), y)
    x_with, y_with = r.add_point(x, y, x_new=40.0, y_new=5.0)
    model_with = r.fit_line(x_with.reshape(-1, 1), y_with)
    slope_without = float(model_without.coef_[0])
    slope_with = float(model_with.coef_[0])
    assert round(slope_without, 4) == 1.5196
    assert round(slope_with, 4) == 0.2138
    # One row, out of forty-one, cuts the slope by more than eighty-five
    # percent.
    assert round(slope_with - slope_without, 4) == -1.3059


def test_05b_the_leverage_value_names_the_mechanism():
    x, _y = r.leverage_dataset()
    x_with, _y_with = r.add_point(x, _y, x_new=40.0, y_new=5.0)
    leverage_new = r.leverage_of_point(x_with, 40.0)
    typical = r.mean_leverage_excluding(x_with, 40.0)
    assert round(leverage_new, 4) == 0.8048
    assert round(typical, 4) == 0.0299
    # Nearly twenty-seven times the pull of an ordinary point, computed
    # from its x-value alone -- before its y-value is even considered.
    assert round(leverage_new / typical, 2) == 26.94


# --- 6. fit_intercept=False, and what it costs ------------------------------


def test_06_forcing_the_intercept_to_zero_costs_you():
    x, y = r.intercept_dataset()
    model_yes = r.fit_line(x, y, fit_intercept=True)
    model_no = r.fit_line(x, y, fit_intercept=False)
    rmse_yes = r.rmse(y, model_yes.predict(x))
    rmse_no = r.rmse(y, model_no.predict(x))
    assert round(rmse_yes, 4) == 6.1401
    assert round(rmse_no, 4) == 9.7878
    # Nearly sixty percent worse, on data whose x-values never go near
    # zero -- the true intercept was 25.0, and forcing it to 0 makes the
    # slope absorb the difference instead.
    assert round(rmse_no / rmse_yes, 4) == 1.5941
    assert model_no.intercept_ == 0.0
    assert round(float(model_no.coef_[0]), 4) == 4.4232


# --- 7. Telling curvature apart from noise ----------------------------------


def test_07_the_bmi_models_residuals_show_no_such_curvature():
    bmi, y = r.load_bmi_and_target()
    model = r.fit_line(bmi, y)
    residuals = y - model.predict(bmi)
    # Contrast with test 03b's 0.3558: on real data with no known missed
    # curvature, a quadratic explains essentially none of the residuals'
    # variance.
    quad_r2 = r.quadratic_fit_r_squared(bmi, residuals)
    assert round(quad_r2, 4) == 0.0002
    # And the residuals are only mildly asymmetric -- not a formal test,
    # but nothing that should alarm you.
    skew = r.skewness(residuals)
    assert round(skew, 4) == 0.156
    assert abs(skew) < 0.5
