"""Ten exercises in what choosing a loss function actually decides.

Read `../starter/00_brief.md` first. `loss_lib.py` is complete -- it is the
machinery, not the exercise. This file holds the reference solutions.

Run this suite on its own:

    .venv/bin/pytest examples -q

Never run `pytest examples starter` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np

import loss_lib as L

VALUES = [2.0, 3.0, 5.0, 7.0, 100.0]


def test_01_mean_minimizes_squared_error():
    best = L.grid_minimize(VALUES, L.sse, 0.0, 110.0)
    assert round(np.mean(VALUES), 4) == 23.4
    assert abs(best - 23.4) < 0.001


def test_01b_median_minimizes_absolute_error():
    best = L.grid_minimize(VALUES, L.sae, 0.0, 110.0)
    assert np.median(VALUES) == 5.0
    assert abs(best - 5.0) < 0.001
    # The mean is dragged toward the 100.0 outlier; the median ignores its
    # size entirely and only counts how many values sit on each side of it.
    assert np.mean(VALUES) > 4 * np.median(VALUES)


def test_02_squared_error_landscape_is_smooth_with_one_minimum():
    x, y = L.make_line_data(n=40, seed=3)
    slopes = np.round(np.arange(2.0, 4.01, 0.1), 4)
    sq_losses, _abs_losses = L.loss_landscape(x, y, intercept=5.0, slopes=slopes)
    assert slopes[int(np.argmin(sq_losses))] == 3.0
    # A parabola has a CONSTANT second difference; this is what "smooth,
    # one minimum" means numerically rather than just visually.
    second = L.second_differences(sq_losses)
    assert round(float(np.std(second)), 6) == 0.0


def test_02b_absolute_error_landscape_is_piecewise_linear_and_kinked():
    x, y = L.make_line_data(n=40, seed=3)
    slopes = np.round(np.arange(2.0, 4.01, 0.1), 4)
    _sq_losses, abs_losses = L.loss_landscape(x, y, intercept=5.0, slopes=slopes)
    assert slopes[int(np.argmin(abs_losses))] == 3.0
    # Absolute error's second difference is NOT constant: the slope of the
    # loss changes only at the slopes where a residual crosses zero, so the
    # curve is a sequence of straight segments meeting at kinks.
    second = L.second_differences(abs_losses)
    assert round(float(np.std(second)), 4) == 1.9366
    assert float(np.std(second)) > 0.0


def test_03_the_normal_equations_solve_squared_error_in_closed_form():
    x, y = L.make_line_data(n=300, seed=2)
    intercept_eq, slope_eq = L.normal_equations(x, y)
    intercept_sk, slope_sk = L.fit_ols(x, y)
    assert abs(intercept_eq - intercept_sk) < 1e-9
    assert abs(slope_eq - slope_sk) < 1e-9
    assert round(slope_eq, 4) == 2.9779
    assert round(intercept_eq, 4) == 4.9663


def test_04_ols_moves_far_when_a_single_point_becomes_an_outlier():
    x, y = L.make_line_data(n=60, seed=1, noise_sd=1.5)
    result = L.outlier_shift(x, y, outlier_offset=80.0)
    assert result["ols"] == {"before": 3.0465, "after": 3.801, "movement": 0.7545}


def test_04b_huber_and_median_regression_barely_move():
    x, y = L.make_line_data(n=60, seed=1, noise_sd=1.5)
    result = L.outlier_shift(x, y, outlier_offset=80.0)
    assert result["huber"] == {"before": 2.987, "after": 3.0308, "movement": 0.0437}
    assert result["quantile"] == {"before": 2.9961, "after": 3.0064, "movement": 0.0104}
    # OLS moved roughly 17x further than Huber and 72x further than the
    # median fit, from the identical single outlier.
    ols_move = abs(result["ols"]["movement"])
    assert round(ols_move / abs(result["huber"]["movement"]), 1) == 17.3
    assert round(ols_move / abs(result["quantile"]["movement"]), 1) == 72.5


def test_05_hubers_delta_interpolates_between_absolute_and_squared_error():
    x, y = L.make_line_data(n=60, seed=1, noise_sd=1.5)
    y_outlier = np.asarray(y, dtype=float).copy()
    y_outlier[int(np.argmax(x))] += 80.0
    sweep = L.huber_epsilon_sweep(x, y_outlier, [1.0, 1.35, 1.5, 2.0, 5.0, 20.0, 100.0])
    assert sweep == [
        (1.0, 3.0064),
        (1.35, 3.0308),
        (1.5, 3.0505),
        (2.0, 3.0906),
        (5.0, 3.1511),
        (20.0, 3.801),
        (100.0, 3.801),
    ]
    slopes = [s for _e, s in sweep]
    assert all(a <= b for a, b in zip(slopes, slopes[1:]))
    ols_intercept, ols_slope = L.fit_ols(x, y_outlier)
    assert sweep[-1][1] == round(ols_slope, 4)


def test_06_squared_error_is_the_most_efficient_choice_under_gaussian_errors():
    ols_mean, ols_sd, huber_mean, huber_sd = L.efficiency_under_noise(
        heavy_tailed=False, replications=500
    )
    assert (ols_mean, ols_sd, huber_mean, huber_sd) == (2.998, 0.056, 2.9977, 0.0588)
    assert abs(ols_mean - 3.0) < 0.01
    assert abs(huber_mean - 3.0) < 0.01
    # Under Gaussian errors OLS has the smaller spread -- Gauss-Markov's
    # promise that it is the BEST (lowest-variance) LINEAR UNBIASED
    # ESTIMATOR is not an abstraction here, it is this ratio being below 1.
    assert round(ols_sd / huber_sd, 4) == 0.9524
    assert ols_sd < huber_sd


def test_06b_but_not_under_heavy_tailed_errors():
    ols_mean, ols_sd, huber_mean, huber_sd = L.efficiency_under_noise(
        heavy_tailed=True, replications=500
    )
    assert (ols_mean, ols_sd, huber_mean, huber_sd) == (2.9967, 0.0589, 2.9984, 0.0422)
    assert abs(ols_mean - 3.0) < 0.01
    assert abs(huber_mean - 3.0) < 0.01
    # Both estimators are still roughly unbiased. But with fat-tailed
    # errors the ranking flips: Huber's spread is now the smaller one.
    assert round(ols_sd / huber_sd, 4) == 1.3957
    assert huber_sd < ols_sd
