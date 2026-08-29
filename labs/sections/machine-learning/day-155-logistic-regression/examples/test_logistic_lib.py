"""
Tests for reference logistic regression implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import logistic_lib as logreg


def test_sigmoid_properties():
    assert abs(logreg.sigmoid(np.array([0.0]))[0] - 0.5) < 1e-9
    assert logreg.sigmoid(np.array([100.0]))[0] > 0.9999
    assert logreg.sigmoid(np.array([-100.0]))[0] < 0.0001
    
    z = np.array([-3.5, -1.0, 0.0, 1.2, 4.0])
    np.testing.assert_allclose(logreg.sigmoid(-z), 1.0 - logreg.sigmoid(z), atol=1e-9)


def test_binary_cross_entropy_extremes():
    y_true = np.array([1.0, 0.0])
    y_perfect = np.array([0.99999, 0.00001])
    assert logreg.binary_cross_entropy(y_true, y_perfect) < 1e-4

    y_mid = np.array([0.5, 0.5])
    assert abs(logreg.binary_cross_entropy(y_true, y_mid) - np.log(2.0)) < 1e-4


def test_gradient_descent_convergence():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(100, 2))
    y = ((X[:, 0] * 2.0 - X[:, 1] * 1.5 + 0.5) > 0).astype(float)

    w, b, history = logreg.fit_logistic_regression(X, y, lr=0.5, epochs=300)
    assert history[-1] < history[0]
    assert history[-1] < 0.25

    preds = logreg.predict_classes(X, w, b)
    acc = np.mean(preds == y)
    assert acc >= 0.90


def test_breast_cancer_benchmark():
    data = load_breast_cancer()
    X = data.data
    y = data.target
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    w, b, history = logreg.fit_logistic_regression(X_scaled, y, lr=0.2, epochs=1000)
    scratch_preds = logreg.predict_classes(X_scaled, w, b)
    scratch_acc = np.mean(scratch_preds == y)

    sk_model = LogisticRegression(C=1e9, solver="lbfgs", max_iter=1000)
    sk_model.fit(X_scaled, y)
    sk_preds = sk_model.predict(X_scaled)
    sk_acc = np.mean(sk_preds == y)

    assert scratch_acc >= 0.95
    assert sk_acc >= 0.95
    assert abs(scratch_acc - sk_acc) < 0.03
