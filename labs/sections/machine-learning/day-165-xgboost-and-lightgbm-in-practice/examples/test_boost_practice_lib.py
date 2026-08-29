"""
Tests for reference XGBoost/LightGBM foundations implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import make_classification
import boost_practice_lib as boost


def test_xgboost_gain_exact_math():
    # Symmetric zero split -> gain should be exactly 0.0 - gamma
    gain = boost.compute_xgboost_split_gain(
        g_l=0.0, h_l=1.0, g_r=0.0, h_r=1.0, reg_lambda=1.0, gamma=0.0
    )
    assert np.isclose(gain, 0.0)

    # Strong gradient separation: G_L = -10, G_R = +10, H_L = H_R = 10, lambda=0, gamma=1.0
    # Score_L = 100 / 10 = 10; Score_R = 100 / 10 = 10; Score_tot = 0 / 20 = 0
    # Gain = 0.5 * (10 + 10 - 0) - 1.0 = 10.0 - 1.0 = 9.0
    gain_strong = boost.compute_xgboost_split_gain(
        g_l=-10.0, h_l=10.0, g_r=10.0, h_r=10.0, reg_lambda=0.0, gamma=1.0
    )
    assert np.isclose(gain_strong, 9.0)


def test_histogram_binning_bounds():
    x = np.random.randn(1000)
    binned, thresholds = boost.histogram_bin_feature(x, n_bins=256)
    
    assert binned.dtype == np.uint8
    assert np.min(binned) == 0
    assert np.max(binned) <= 255
    assert len(thresholds) <= 256


def test_histogram_gb_with_missing_values():
    # Generate tabular dataset
    X, y = make_classification(n_samples=300, n_features=12, n_informative=8, random_state=42)
    
    # Inject 10% missing values (NaNs) into X
    rng = np.random.default_rng(42)
    mask = rng.random(X.shape) < 0.10
    X_missing = X.copy()
    X_missing[mask] = np.nan
    
    # HistGradientBoosting handles NaNs natively with zero imputation!
    model = boost.HistogramGBSimplified(n_estimators=40, learning_rate=0.1, random_state=42)
    model.fit(X_missing, y)
    preds = model.predict(X_missing)
    acc = np.mean(preds == y)
    
    assert acc >= 0.90
