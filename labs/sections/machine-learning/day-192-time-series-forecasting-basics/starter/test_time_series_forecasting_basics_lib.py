import pytest
import numpy as np
from examples.time_series_forecasting_basics_lib import (
    create_lag_and_rolling_features, compute_smape, WalkForwardTimeSeriesSplit
)

def test_lag_feature_shapes_and_values():
    series = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0])
    X, y = create_lag_and_rolling_features(series, lags=[1, 2], window_size=3)

    # max_lag = 3, so first target is series[3] = 40.0
    assert y[0] == 40.0
    # Lag 1 of t=3 is series[2] = 30.0; Lag 2 is series[1] = 20.0
    assert X[0, 0] == 30.0
    assert X[0, 1] == 20.0
    # Rolling mean of [10, 20, 30] = 20.0
    assert np.isclose(X[0, 2], 20.0)

def test_walk_forward_splits_no_overlap():
    X = np.zeros((50, 4))
    splitter = WalkForwardTimeSeriesSplit(n_splits=3, test_size=10)
    splits = splitter.split(X)

    assert len(splits) == 3
    for train_idx, test_idx in splits:
        assert len(test_idx) == 10
        assert np.max(train_idx) < np.min(test_idx) # No lookahead leakage!
