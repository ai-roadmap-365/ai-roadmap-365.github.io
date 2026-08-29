"""
Tests for starter decision boundaries library.
"""
import pytest
import numpy as np
import boundary_lib as bnd


def test_linear_boundary_stub():
    with pytest.raises(NotImplementedError):
        bnd.compute_linear_boundary_2d(np.array([1.0, 2.0]), 0.0, np.array([0.0]))


def test_distance_stub():
    with pytest.raises(NotImplementedError):
        bnd.signed_distance_to_boundary(np.zeros((2, 2)), np.array([1.0, 1.0]), 0.0)


def test_poly_stub():
    with pytest.raises(NotImplementedError):
        bnd.polynomial_features_2d(np.zeros((2, 2)), 2)
