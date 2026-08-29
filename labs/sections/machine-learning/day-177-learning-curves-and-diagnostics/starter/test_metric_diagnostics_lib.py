import pytest
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.datasets import make_regression
from metric_diagnostics_lib import (
    compute_learning_curves,
    compute_validation_curves,
    diagnose_model_regime
)

@pytest.fixture
def regression_data():
    X, y = make_regression(n_samples=200, n_features=10, noise=5.0, random_state=42)
    return X, y

def test_compute_learning_curves(regression_data):
    X, y = regression_data
    model = Ridge(alpha=1.0)
    res = compute_learning_curves(model, X, y, train_sizes=[0.2, 0.5, 1.0], cv=3)
    
    assert len(res["train_sizes"]) == 3
    assert len(res["train_scores_mean"]) == 3
    assert len(res["val_scores_mean"]) == 3
    # Training score typically starts high and stabilizes
    assert res["train_scores_mean"][0] >= res["train_scores_mean"][-1] - 0.20
    # Validation score typically increases with sample size
    assert res["val_scores_mean"][-1] > res["val_scores_mean"][0]

def test_compute_validation_curves(regression_data):
    X, y = regression_data
    model = DecisionTreeRegressor(random_state=42)
    depths = [1, 3, 6, 10]
    res = compute_validation_curves(model, X, y, param_name="max_depth", param_range=depths, cv=3)
    
    assert res["param_name"] == "max_depth"
    assert len(res["val_scores_mean"]) == 4

def test_diagnose_model_regime():
    # Case 1: High Bias (both train and val scores low)
    d_bias = diagnose_model_regime(train_score=0.45, val_score=0.42, benchmark_score=0.85)
    assert d_bias["regime"] == "HIGH_BIAS"
    assert "Add polynomial features" in d_bias["actionable_remedies"][0]
    
    # Case 2: High Variance (train score high, val score low)
    d_var = diagnose_model_regime(train_score=0.98, val_score=0.65, generalization_gap_threshold=0.15)
    assert d_var["regime"] == "HIGH_VARIANCE"
    assert "Collect more training data" in d_var["actionable_remedies"][0]
    
    # Case 3: Optimal Regime
    d_opt = diagnose_model_regime(train_score=0.92, val_score=0.89, generalization_gap_threshold=0.10)
    assert d_opt["regime"] == "OPTIMAL"
