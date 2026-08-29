"""
Tests for reference KNN implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import knn_lib as knn


def test_euclidean_distance_matrix():
    train = np.array([[0.0, 0.0], [3.0, 4.0]])
    test = np.array([[0.0, 4.0]])
    # dist(test[0], train[0]) = 4.0; dist(test[0], train[1]) = 3.0
    d = knn.compute_distance_matrix(train, test, metric="euclidean")
    assert d.shape == (1, 2)
    np.testing.assert_allclose(d[0], np.array([4.0, 3.0]), atol=1e-7)


def test_knn_perfect_1nn_memorization():
    X = np.array([[1.0, 2.0], [5.0, 6.0], [9.0, 10.0]])
    y = np.array([0, 1, 0])
    preds = knn.predict_knn(X, y, X, k=1)
    np.testing.assert_array_equal(preds, y)


def test_knn_matches_scikit_learn_iris():
    iris = load_iris()
    X = iris.data
    y = iris.target
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Scratch KNN
    scratch_preds = knn.predict_knn(X_scaled, y, X_scaled, k=5, weights="uniform")
    
    # Scikit-learn KNN
    sk_knn = KNeighborsClassifier(n_neighbors=5, weights="uniform", algorithm="brute")
    sk_knn.fit(X_scaled, y)
    sk_preds = sk_knn.predict(X_scaled)

    # Must match 100%
    np.testing.assert_array_equal(scratch_preds, sk_preds)


def test_knn_distance_weighting():
    # 2 near points of class 0, 3 slightly farther points of class 1
    X_train = np.array([[0.0, 0.0], [0.1, 0.0], [1.0, 0.0], [1.1, 0.0], [1.2, 0.0]])
    y_train = np.array([0, 0, 1, 1, 1])
    X_test = np.array([[0.05, 0.0]])

    # Uniform voting prefers class 1 (3 votes vs 2 votes)
    p_uniform = knn.predict_knn(X_train, y_train, X_test, k=5, weights="uniform")
    assert p_uniform[0] == 1

    # Distance-weighted voting strongly prefers class 0 (distances ~0.05 vs ~1.0)
    p_dist = knn.predict_knn(X_train, y_train, X_test, k=5, weights="distance")
    assert p_dist[0] == 0
