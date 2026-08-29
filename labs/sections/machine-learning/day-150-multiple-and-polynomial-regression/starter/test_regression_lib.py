"""Machinery checks: the helpers behave, before any claim is made.

These five tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import regression_lib as r


def test_the_dataset_loads_with_ten_raw_unit_predictors():
    X, y, names = r.load_raw_diabetes()
    assert X.shape == (442, 10)
    assert y.shape == (442,)
    assert names == ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
    # scaled=False: real units, not the default mean-centred unit-norm columns.
    assert X[:, names.index("age")].min() >= 19
    assert X[:, names.index("age")].max() <= 79
    assert y.min() >= 25 and y.max() <= 346


def test_a_perfectly_uncorrelated_pair_has_a_vif_near_one():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 3))
    y = X[:, 0] * 2 + rng.normal(size=500) * 0.1
    vifs = r.variance_inflation_factors(X, ["a", "b", "c"])
    for name in ("a", "b", "c"):
        assert 0.9 < vifs[name] < 1.15


def test_an_exact_duplicate_of_a_column_has_infinite_vif():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 2))
    X_dup = np.hstack([X, X[:, [0]]])
    vifs = r.variance_inflation_factors(X_dup, ["a", "b", "a_copy"])
    assert vifs["a"] == float("inf")
    assert vifs["a_copy"] == float("inf")


def test_duplicating_an_unrelated_random_column_barely_moves_anything():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(300, 2))
    y = X[:, 0] * 3.0 + rng.normal(size=300) * 0.5
    original_coef, coef_a, coef_b, max_diff, r2_orig, r2_dup = r.duplicate_column_exact(X, y, 1)
    # Column 1 has nothing to do with y, so splitting its (near-zero) effect
    # in half still leaves both halves small, and nothing else moves.
    assert abs(coef_a + coef_b - original_coef) < 1e-8
    assert max_diff < 1e-8
    assert abs(r2_dup - r2_orig) < 1e-8


def test_the_spread_helper_reports_mean_sd_min_max():
    result = r.spread([1.0, 2.0, 3.0, 4.0, 5.0])
    assert result == {"mean": 3.0, "sd": 1.4142, "min": 1.0, "max": 5.0}
