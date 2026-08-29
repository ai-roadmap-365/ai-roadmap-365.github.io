"""
Tests for starter KNN implementation.
"""
import pytest
import numpy as np
import knn_lib as knn


def test_distance_stub():
    with pytest.raises(NotImplementedError):
        knn.compute_distance_matrix(np.zeros((2, 2)), np.zeros((3, 2)))


def test_predict_stub():
    with pytest.raises(NotImplementedError):
        knn.predict_knn(np.zeros((5, 2)), np.array([0, 1, 0, 1, 0]), np.zeros((2, 2)))
