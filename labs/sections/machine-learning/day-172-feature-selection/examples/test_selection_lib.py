"""
Tests for reference feature selection implementation.
"""
import pytest
import numpy as np
from sklearn.linear_model import LogisticRegression
import selection_lib as fs


def test_variance_threshold_filter():
    # Feature 0: constant (var=0), Feature 1: binary (var=0.25), Feature 2: random (var > 1.0)
    X = np.array([
        [1.0, 0.0, 10.0],
        [1.0, 1.0, 20.0],
        [1.0, 0.0, 15.0],
        [1.0, 1.0, 25.0]
    ])
    
    X_sel, support = fs.filter_by_variance_threshold(X, threshold=0.0)
    assert np.array_equal(support, [False, True, True])
    assert X_sel.shape == (4, 2)


def test_rfe_scratch_identifies_informative_features():
    # 5 informative features + 5 pure noise features
    rng = np.random.default_rng(42)
    X_info = rng.normal(size=(100, 5))
    y = (X_info[:, 0] + 2.0 * X_info[:, 1] - X_info[:, 2] > 0).astype(int)
    X_noise = rng.normal(size=(100, 5))
    X_total = np.hstack([X_info, X_noise])
    
    lr = LogisticRegression(penalty=None, solver="lbfgs", random_state=42)
    support = fs.recursive_feature_elimination_scratch(lr, X_total, y, n_features_to_select=3)
    
    # Selected 3 features must be within the first 5 informative features
    assert np.sum(support) == 3
    assert np.sum(support[:5]) >= 2 # At least 2 of top 3 are informative


def test_boruta_shadow_filter():
    rng = np.random.default_rng(42)
    X_sig = rng.normal(size=(200, 2))
    y = 5.0 * X_sig[:, 0] + 3.0 * X_sig[:, 1] + rng.normal(scale=0.1, size=200)
    X_noise = rng.normal(size=(200, 4))
    X_all = np.hstack([X_sig, X_noise])
    
    selected = fs.boruta_shadow_filter(X_all, y, n_trials=10, random_state=42)
    # The two signal features must be selected
    assert selected[0] == True
    assert selected[1] == True
