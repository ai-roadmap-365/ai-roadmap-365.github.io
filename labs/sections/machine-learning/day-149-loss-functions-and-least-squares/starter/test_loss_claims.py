"""Ten exercises in what choosing a loss function actually decides.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`loss_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import loss_lib as L  # noqa: F401  (you will need it)

VALUES = [2.0, 3.0, 5.0, 7.0, 100.0]


def test_01_mean_minimizes_squared_error():
    pytest.skip(
        "Call L.grid_minimize(VALUES, L.sse, 0.0, 110.0) and assert it is "
        "within 0.001 of np.mean(VALUES), which rounds to 23.4. The mean is "
        "not chosen for squared error by convention -- it is what a grid "
        "search over the loss actually finds."
    )


def test_01b_median_minimizes_absolute_error():
    pytest.skip(
        "Call L.grid_minimize(VALUES, L.sae, 0.0, 110.0) and assert it is "
        "within 0.001 of np.median(VALUES), which is 5.0. Then assert "
        "np.mean(VALUES) is more than four times np.median(VALUES): the "
        "single value of 100.0 drags the mean far from the other four "
        "points, while the median only counts how many values sit on each "
        "side of it and ignores their size entirely."
    )


def test_02_squared_error_landscape_is_smooth_with_one_minimum():
    pytest.skip(
        "Build x, y = L.make_line_data(n=40, seed=3). Sweep slopes = "
        "np.round(np.arange(2.0, 4.01, 0.1), 4) with the intercept fixed "
        "at 5.0 using L.loss_landscape, and assert the squared-error "
        "minimiser is exactly slope 3.0. Then assert "
        "round(np.std(L.second_differences(sq_losses)), 6) == 0.0 -- a "
        "CONSTANT second difference is the numerical signature of a "
        "parabola: smooth, with one minimum."
    )


def test_02b_absolute_error_landscape_is_piecewise_linear_and_kinked():
    pytest.skip(
        "Using the same x, y and slopes as test_02, assert the "
        "absolute-error minimiser is also exactly slope 3.0, but that "
        "round(np.std(L.second_differences(abs_losses)), 4) == 1.9366 -- "
        "NOT constant. Absolute error only bends where a residual crosses "
        "zero, so its landscape is a sequence of straight segments meeting "
        "at kinks rather than one smooth curve."
    )


def test_03_the_normal_equations_solve_squared_error_in_closed_form():
    pytest.skip(
        "Build x, y = L.make_line_data(n=300, seed=2). Solve with "
        "L.normal_equations(x, y) and separately with L.fit_ols(x, y), and "
        "assert the two intercepts agree to within 1e-9 and the two slopes "
        "agree to within 1e-9. Then assert the normal-equations slope "
        "rounds to 2.9779 and the intercept to 4.9663. Squared error is "
        "smooth everywhere, so setting its derivative to zero gives a "
        "linear system with an exact solution -- absolute error has no "
        "equivalent closed form, because it has no derivative at a "
        "residual of exactly zero."
    )


def test_04_ols_moves_far_when_a_single_point_becomes_an_outlier():
    pytest.skip(
        "Build x, y = L.make_line_data(n=60, seed=1, noise_sd=1.5) and call "
        "L.outlier_shift(x, y, outlier_offset=80.0). Assert result['ols'] "
        "equals {'before': 3.0465, 'after': 3.801, 'movement': 0.7545}. "
        "Moving ONE point 80 units off the line moves the least-squares "
        "slope by three quarters of a unit."
    )


def test_04b_huber_and_median_regression_barely_move():
    pytest.skip(
        "Using the same result from test_04, assert result['huber'] equals "
        "{'before': 2.987, 'after': 3.0308, 'movement': 0.0437} and "
        "result['quantile'] equals {'before': 2.9961, 'after': 3.0064, "
        "'movement': 0.0104}. Then assert OLS's movement, divided by "
        "Huber's, rounds to 17.3, and divided by the median fit's, rounds "
        "to 72.5. Same data, same outlier, same single point moved -- only "
        "the loss changed."
    )


def test_05_hubers_delta_interpolates_between_absolute_and_squared_error():
    pytest.skip(
        "Reuse x, y from test_04, copy y, add 80.0 to the row at "
        "np.argmax(x), and call L.huber_epsilon_sweep on the contaminated "
        "data with epsilons [1.0, 1.35, 1.5, 2.0, 5.0, 20.0, 100.0]. Assert "
        "the result equals [(1.0, 3.0064), (1.35, 3.0308), (1.5, 3.0505), "
        "(2.0, 3.0906), (5.0, 3.1511), (20.0, 3.801), (100.0, 3.801)]. "
        "Assert the slopes are non-decreasing in epsilon, and that the "
        "final slope equals L.fit_ols on the same contaminated data, "
        "rounded to 4 places. Small epsilon leans on absolute error; large "
        "epsilon converges to plain least squares."
    )


def test_06_squared_error_is_the_most_efficient_choice_under_gaussian_errors():
    pytest.skip(
        "Call L.efficiency_under_noise(heavy_tailed=False, "
        "replications=500) and assert it equals (2.998, 0.056, 2.9977, "
        "0.0588) -- (ols_mean, ols_sd, huber_mean, huber_sd). Assert both "
        "means are within 0.01 of the true slope of 3.0 (both estimators "
        "are roughly unbiased), then assert round(ols_sd / huber_sd, 4) == "
        "0.9524 and that ols_sd < huber_sd. Under Gaussian errors, OLS has "
        "the smaller spread -- this ratio being below 1 is what Gauss-"
        "Markov's promise of the BEST (lowest-variance) LINEAR UNBIASED "
        "ESTIMATOR looks like when you measure it."
    )


def test_06b_but_not_under_heavy_tailed_errors():
    pytest.skip(
        "Call L.efficiency_under_noise(heavy_tailed=True, "
        "replications=500) and assert it equals (2.9967, 0.0589, 2.9984, "
        "0.0422). Assert both means are still within 0.01 of 3.0, then "
        "assert round(ols_sd / huber_sd, 4) == 1.3957 and that huber_sd < "
        "ols_sd -- the ranking has FLIPPED. Gauss-Markov's guarantee is "
        "conditional on the errors; change what the errors look like and "
        "the best linear unbiased estimator is no longer the most precise "
        "one available."
    )
