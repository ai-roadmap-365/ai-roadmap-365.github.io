"""
Tests for reference Class Imbalance implementation.
"""
import pytest
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import imbalance_lib as imb


def test_balanced_weights():
    # 90 negatives, 10 positives (N=100, K=2)
    # w0 = 100 / (2 * 90) = 100/180 = 0.5555...
    # w1 = 100 / (2 * 10) = 100/20 = 5.0
    y = np.array([0]*90 + [1]*10)
    w = imb.compute_balanced_weights(y)
    
    sk_w = compute_class_weight("balanced", classes=np.array([0, 1]), y=y)
    assert np.isclose(w[0], sk_w[0])
    assert np.isclose(w[1], sk_w[1])
    assert np.isclose(w[1] / w[0], 9.0) # 9x weight ratio


def test_undersampling_balance():
    X = np.random.randn(100, 2)
    y = np.array([0]*90 + [1]*10)
    X_res, y_res = imb.random_undersample(X, y)
    
    assert len(y_res) == 20
    assert np.sum(y_res == 0) == 10
    assert np.sum(y_res == 1) == 10


def test_oversampling_balance():
    X = np.random.randn(100, 2)
    y = np.array([0]*90 + [1]*10)
    X_res, y_res = imb.random_oversample(X, y)
    
    assert len(y_res) == 180
    assert np.sum(y_res == 0) == 90
    assert np.sum(y_res == 1) == 90


def test_smote_interpolation():
    # 2 minority points at [0, 0] and [2, 2]
    X_min = np.array([[0.0, 0.0], [2.0, 2.0]])
    syn = imb.smote_synthetic_points(X_min, n_samples=5, k_neighbors=1, random_state=42)
    
    assert syn.shape == (5, 2)
    # All synthetic points must lie on the line x1 == x2 in [0, 2]
    for pt in syn:
        assert np.isclose(pt[0], pt[1], atol=1e-7)
        assert 0.0 <= pt[0] <= 2.0
