"""
Tests for reference imputation implementation.
"""
import pytest
import numpy as np
import imputation_lib as mi


def test_nan_euclidean_distance_math():
    # u = [1, NaN, 3], v = [4, 5, 7]
    # Overlapping indices: 0 and 2. diffs: (1-4)^2=9, (3-7)^2=16. sum=25.
    # Total dim = 3, Valid dim = 2. Scaled sum = 3/2 * 25 = 37.5.
    # Distance = sqrt(37.5) = 6.1237
    u = np.array([1.0, np.nan, 3.0])
    v = np.array([4.0, 5.0, 7.0])
    dist = mi.compute_nan_euclidean_distance(u, v)
    assert np.isclose(dist, np.sqrt(37.5), atol=1e-5)


def test_missing_indicator_shape():
    X = np.array([
        [1.0, np.nan],
        [np.nan, 2.0],
        [3.0, 4.0]
    ])
    indicator = mi.generate_missing_indicator(X)
    assert np.array_equal(indicator, [[False, True], [True, False], [False, False]])


def test_knn_imputation_reconstruction():
    # Sample 0 and Sample 1 are identical twins except sample 0 is missing col 1
    X = np.array([
        [10.0, np.nan, 100.0],
        [10.0, 50.0, 100.0],
        [10.0, 50.0, 100.0],
        [90.0, 900.0, 900.0]
    ])
    X_imp = mi.knn_imputer_scratch(X, n_neighbors=2)
    # The imputed value for row 0 col 1 should be 50.0
    assert np.isclose(X_imp[0, 1], 50.0, atol=1e-5)
    assert not np.isnan(X_imp).any()
