"""
Tests for reference Gradient Boosting implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import make_regression, load_breast_cancer
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
import gradient_boosting_lib as gb


def test_pseudo_residuals_exact_values():
    # p = sigmoid(0) = 0.5
    raw = np.array([0.0, 0.0])
    y = np.array([1.0, 0.0])
    r = gb.compute_pseudo_residuals_classification(y, raw)
    # y=1 -> r = 1 - 0.5 = +0.5; y=0 -> r = 0 - 0.5 = -0.5
    assert np.allclose(r, [0.5, -0.5])


def test_gradient_boosting_regressor_convergence():
    X, y = make_regression(n_samples=150, n_features=5, noise=0.1, random_state=42)
    
    gbr_scratch = gb.GradientBoostingRegressorScratch(n_estimators=40, learning_rate=0.1, max_depth=3)
    gbr_scratch.fit(X, y)
    preds = gbr_scratch.predict(X)
    
    mse = np.mean((y - preds) ** 2)
    # Residuals should decrease rapidly
    assert mse < 5.0


def test_gradient_boosting_classifier_breast_cancer():
    cancer = load_breast_cancer()
    X, y = cancer.data, cancer.target
    
    gbc_scratch = gb.GradientBoostingClassifierScratch(n_estimators=30, learning_rate=0.1, max_depth=3)
    gbc_scratch.fit(X, y)
    scratch_acc = np.mean(gbc_scratch.predict(X) == y)
    
    gbc_sk = GradientBoostingClassifier(n_estimators=30, learning_rate=0.1, max_depth=3, random_state=42)
    gbc_sk.fit(X, y)
    sk_acc = gbc_sk.score(X, y)
    
    assert scratch_acc >= 0.95
    assert sk_acc >= 0.95
    assert abs(scratch_acc - sk_acc) < 0.05
