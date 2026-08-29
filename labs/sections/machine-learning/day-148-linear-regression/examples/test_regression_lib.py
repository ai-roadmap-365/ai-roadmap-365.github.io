"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import regression_lib as r


def test_load_bmi_and_target_has_the_right_shape_and_raw_units():
    bmi, y = r.load_bmi_and_target()
    assert bmi.shape == (442, 1)
    assert y.shape == (442,)
    # Raw units, not the mean-centred, unit-norm-scaled default.
    assert bmi.min() >= 18.0 and bmi.max() <= 42.2
    assert y.min() >= 25.0 and y.max() <= 346.0


def test_fit_line_respects_fit_intercept():
    x = np.array([[1.0], [2.0], [3.0], [4.0]])
    y = np.array([3.0, 5.0, 7.0, 9.0])
    with_intercept = r.fit_line(x, y, fit_intercept=True)
    without_intercept = r.fit_line(x, y, fit_intercept=False)
    assert round(float(with_intercept.coef_[0]), 4) == 2.0
    assert round(float(with_intercept.intercept_), 4) == 1.0
    assert without_intercept.intercept_ == 0.0


def test_leverage_of_a_central_point_is_smaller_than_an_extreme_one():
    x = np.linspace(0, 10, 11)
    central = r.leverage_of_point(x, 5.0)
    extreme = r.leverage_of_point(x, 40.0)
    assert extreme > central
    # Leverage is never below 1/n for any point, including the mean.
    assert r.leverage_of_point(x, float(x.mean())) >= 1.0 / len(x) - 1e-9


def test_skewness_is_zero_for_a_symmetric_sample():
    rng = np.random.default_rng(0)
    symmetric = rng.normal(size=5000)
    assert abs(r.skewness(symmetric)) < 0.1
    lopsided = np.concatenate([np.zeros(950), np.full(50, 20.0)])
    assert r.skewness(lopsided) > 1.0
