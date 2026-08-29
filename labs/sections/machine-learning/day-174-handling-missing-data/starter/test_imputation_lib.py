"""
Tests for starter missing data handling.
"""
import pytest
import numpy as np
import imputation_lib as mi


def test_nan_dist_stub():
    with pytest.raises(NotImplementedError):
        mi.compute_nan_euclidean_distance(np.array([1.0, np.nan]), np.array([2.0, 3.0]))


def test_knn_imputer_stub():
    with pytest.raises(NotImplementedError):
        mi.knn_imputer_scratch(np.array([[1.0, np.nan], [2.0, 3.0]]))
