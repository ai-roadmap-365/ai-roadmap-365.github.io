"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np
import pytest

import fitting_lib as f


def test_the_data_generator_is_the_true_function_plus_noise():
    X, y = f.make_data(2000, seed=1)
    residuals = y - f.true_function(X.ravel())
    # The noise is centred and has the standard deviation it claims.
    assert abs(float(residuals.mean())) < 0.15
    assert abs(float(residuals.std()) - f.NOISE_SD) < 0.1
    assert f.irreducible_variance() == f.NOISE_SD**2 == 4.0
    # Two calls at one seed agree; two seeds do not.
    assert np.array_equal(f.make_data(50, 3)[1], f.make_data(50, 3)[1])
    assert not np.array_equal(f.make_data(50, 3)[1], f.make_data(50, 4)[1])


def test_a_degree_three_model_can_represent_the_truth_exactly():
    # With no noise at all, a cubic fit should be essentially perfect and
    # a straight line should not.
    X, y = f.make_data(200, seed=2, noise_sd=0.0)
    cubic = f.polynomial_model(3).fit(X, y)
    line = f.polynomial_model(1).fit(X, y)
    assert f.mse(cubic, X, y) < 1e-12
    # A straight line cannot, and is left with 4.174 of pure bias.
    assert round(f.mse(line, X, y), 3) == 4.174


def test_scaling_is_what_keeps_the_high_degree_fit_numerically_sane():
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures

    X, y = f.make_data(25, seed=145)
    scaled = f.polynomial_model(24).fit(X, y)
    unscaled = make_pipeline(PolynomialFeatures(24), LinearRegression()).fit(X, y)
    # Both fit the training data; the scaled pipeline fits it better,
    # because the unscaled normal equations are badly conditioned.
    assert f.mse(scaled, X, y) < f.mse(unscaled, X, y)


def test_the_stopping_helpers_agree_on_a_hand_checkable_sequence():
    values = [10.0, 8.0, 5.0, 6.0, 7.0, 9.0]
    assert f.first_increase(values) == 3
    assert not f.is_monotonically_decreasing(values)
    assert f.is_monotonically_decreasing([5.0, 4.0, 4.0, 3.0])
    # Patience 2 waits two non-improving epochs, then returns the best.
    assert f.stop_with_patience(values, 2) == 2
    # A sequence that keeps improving is never stopped early.
    assert f.stop_with_patience([5.0, 4.0, 3.0, 2.0], 2) == 3
