"""
Tests for reference feature scaling and encoding.
"""
import pytest
import numpy as np
import scaling_encoding_lib as se


def test_standard_scaler_mean_and_variance():
    rng = np.random.default_rng(42)
    X = rng.normal(loc=10.0, scale=3.0, size=(1000, 3))
    
    scaler = se.StandardScalerScratch()
    X_std = scaler.fit_transform(X)
    
    assert np.allclose(np.mean(X_std, axis=0), 0.0, atol=1e-7)
    assert np.allclose(np.std(X_std, axis=0), 1.0, atol=1e-7)


def test_robust_scaler_outlier_resilience():
    # Data with extreme outliers
    X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0], [10000.0]])
    
    scaler = se.RobustScalerScratch()
    X_rob = scaler.fit_transform(X)
    
    # Median is (3+4)/2 = 3.5 -> centered around 0
    assert np.isclose(np.median(X_rob, axis=0)[0], 0.0, atol=1e-7)


def test_oof_target_encoding_leak_free():
    # 3 categories: High (target=1.0), Low (target=0.0), Mix (target=0.5)
    cats = np.array(["High"] * 50 + ["Low"] * 50 + ["Mix"] * 50)
    target = np.array([1.0] * 50 + [0.0] * 50 + [0.0] * 25 + [1.0] * 25)
    
    encoded = se.out_of_fold_target_encode(cats, target, cv=5, smoothing=5.0)
    
    # "High" encoded values should be significantly higher than "Low"
    assert np.mean(encoded[:50]) > 0.80
    assert np.mean(encoded[50:100]) < 0.20
    assert len(encoded) == 150
