"""
Tests for reference decision boundaries implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_iris, make_moons
import boundary_lib as bnd


def test_linear_boundary_geometry():
    # 2*x1 - 1*x2 + 4 = 0 ==> x2 = 2*x1 + 4
    w = np.array([2.0, -1.0])
    b = 4.0
    x1_vals = np.array([0.0, 1.0, -2.0])
    x2_vals = bnd.compute_linear_boundary_2d(w, b, x1_vals)
    expected_x2 = np.array([4.0, 6.0, 0.0])
    np.testing.assert_allclose(x2_vals, expected_x2, atol=1e-9)


def test_signed_distance_to_boundary():
    # Boundary x1 = 3 (w = [1, 0], b = -3)
    w = np.array([1.0, 0.0])
    b = -3.0
    points = np.array([[3.0, 5.0], [5.0, 0.0], [1.0, -2.0]])
    dists = bnd.signed_distance_to_boundary(points, w, b)
    expected_dists = np.array([0.0, 2.0, -2.0])
    np.testing.assert_allclose(dists, expected_dists, atol=1e-9)


def test_polynomial_features_shape():
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    poly = bnd.polynomial_features_2d(X, degree=2)
    assert poly.shape == (2, 5)
    # Check first row: [1, 2, 1^2=1, 1*2=2, 2^2=4]
    np.testing.assert_allclose(poly[0], np.array([1.0, 2.0, 1.0, 2.0, 4.0]))


def test_ovr_iris_classification():
    iris = load_iris()
    X = iris.data[:, :2] # 2 features for visualization clarity
    y = iris.target
    models = bnd.fit_ovr_classifier(X, y)
    assert len(models) == 3

    preds = bnd.predict_ovr(X, models)
    acc = np.mean(preds == y)
    assert acc >= 0.75 # 2-feature Iris baseline
