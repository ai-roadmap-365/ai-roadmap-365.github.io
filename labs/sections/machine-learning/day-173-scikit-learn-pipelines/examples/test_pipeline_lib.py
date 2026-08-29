"""
Tests for reference pipeline implementation.
"""
import pytest
import numpy as np
from sklearn.base import clone
from sklearn.linear_model import Ridge
import pipeline_lib as pl


def test_log_transformer_math():
    X = np.array([[0.0], [np.e - 1.0], [np.e**2 - 1.0]])
    tr = pl.CustomLogTransformer(offset=1.0)
    X_log = tr.fit_transform(X)
    
    assert np.isclose(X_log[0, 0], 0.0)
    assert np.isclose(X_log[1, 0], 1.0)
    assert np.isclose(X_log[2, 0], 2.0)


def test_outlier_clipper_bounds_and_clone():
    X_train = np.linspace(0, 100, 101).reshape(-1, 1)
    clipper = pl.OutlierClipperTransformer(lower_percentile=5.0, upper_percentile=95.0)
    
    # Test clone compatibility
    cloned = clone(clipper)
    assert cloned.lower_percentile == 5.0
    assert cloned.upper_percentile == 95.0
    
    clipper.fit(X_train)
    # Test data with extreme outliers below 0 and above 100
    X_test = np.array([[-500.0], [50.0], [5000.0]])
    X_clipped = clipper.transform(X_test)
    
    assert np.isclose(X_clipped[0, 0], 5.0)   # 5th percentile of 0..100 is 5.0
    assert np.isclose(X_clipped[1, 0], 50.0)
    assert np.isclose(X_clipped[2, 0], 95.0)  # 95th percentile is 95.0


def test_heterogeneous_pipeline_end_to_end():
    # 2 numerical columns, 1 categorical column
    X_num = np.random.randn(100, 2) * 50.0
    X_cat = np.random.choice(["Red", "Green", "Blue"], size=(100, 1))
    X_mixed = np.hstack([X_num, X_cat])
    
    y = X_num[:, 0] * 2.0 + (X_cat[:, 0] == "Red").astype(float) * 10.0
    
    pipeline = pl.build_heterogeneous_tabular_pipeline(
        num_indices=[0, 1], cat_indices=[2], estimator=Ridge(alpha=1.0)
    )
    
    pipeline.fit(X_mixed, y)
    preds = pipeline.predict(X_mixed)
    assert len(preds) == 100
    assert preds.ndim == 1
