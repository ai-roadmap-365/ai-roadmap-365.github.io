"""Machinery checks: the helpers behave, before any claim is made.

These five tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np
import pytest

import regression_lib as r


def test_the_dataset_loads_offline_and_matches_its_shape():
    X, y, names = r.load_dataset()
    assert X.shape == (442, 10)
    assert y.shape == (442,)
    assert names == ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
    assert float(y.min()) == 25.0
    assert float(y.max()) == 346.0


def test_candidate_configs_really_are_twenty_three_distinct_pipelines():
    configs = r.candidate_configs()
    assert len(configs) == 23
    seen = set()
    for family, param, make in configs:
        pipe = make()
        assert hasattr(pipe, "fit") and hasattr(pipe, "predict")
        seen.add((family, param))
    # No two configs share a (family, hyperparameter) pair.
    assert len(seen) == 23


def test_the_gated_test_set_counts_and_refuses():
    class AlwaysMean:
        def predict(self, X):
            return np.full(len(X), 150.0)

    y = np.array([100.0, 200.0, 150.0, 150.0])
    gate = r.GatedTestSet(np.zeros((4, 2)), y)
    rmse, r2, mae = gate.evaluate(AlwaysMean())
    assert rmse > 0
    with pytest.raises(r.TestSetTouchedTwice):
        gate.evaluate(AlwaysMean())
    # A fresh gate is a fresh budget; the class holds no global state.
    fresh_rmse, _r2, _mae = r.GatedTestSet(np.zeros((4, 2)), y).evaluate(AlwaysMean())
    assert fresh_rmse == rmse


def test_the_normal_ppf_matches_known_reference_points():
    # Well-known standard-normal quantiles, to a few decimals.
    assert abs(r._normal_ppf(np.array([0.5]))[0] - 0.0) < 1e-6
    assert abs(r._normal_ppf(np.array([0.975]))[0] - 1.959964) < 1e-4
    assert abs(r._normal_ppf(np.array([0.025]))[0] - (-1.959964)) < 1e-4


def test_largest_residuals_returns_them_sorted_by_magnitude():
    y_test = np.array([10.0, 20.0, 30.0, 40.0])
    pred_test = np.array([10.0, 25.0, 10.0, 41.0])
    rows = r.largest_residuals(y_test, pred_test, n=2)
    assert len(rows) == 2
    # Row 2 (residual +20) is the largest in magnitude; row 3 (residual -1) is smallest.
    assert rows[0][0] == 2
    assert rows[0][3] == 20.0
