import pytest
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from shap_lib import (
    compute_permutation_importance,
    compute_exact_shapley_values,
    compute_partial_dependence_1d
)

def test_permutation_importance():
    X = np.random.normal(size=(100, 3))
    # Feature 0 is primary driver, Feature 2 is pure noise
    y = 5.0 * X[:, 0] + 0.5 * X[:, 1] + np.random.normal(scale=0.1, size=100)
    
    model = LinearRegression().fit(X, y)
    res = compute_permutation_importance(model, X, y, r2_score, n_repeats=3)
    
    # Feature 0 must have strictly higher importance than Feature 2
    assert res["importances_mean"][0] > res["importances_mean"][2]
    assert res["importances_mean"][0] > 0.50

def test_exact_shapley_efficiency_axiom():
    # True linear model: y = 2*x0 + 3*x1 + 10
    X_bg = np.array([
        [1.0, 2.0],
        [2.0, 4.0],
        [3.0, 6.0],
        [4.0, 8.0]
    ])
    def predict_fn(X):
        return 2.0 * X[:, 0] + 3.0 * X[:, 1] + 10.0
        
    x_test = np.array([5.0, 10.0])
    res = compute_exact_shapley_values(predict_fn, x_test, X_bg)
    
    # Efficiency axiom: base_value + sum(shapley_values) == instance_prediction
    assert res["efficiency_check_diff"] < 1e-5
    # Feature 1 should have higher attribution than Feature 0
    assert res["shapley_values"][1] > res["shapley_values"][0]

def test_partial_dependence_1d():
    X = np.random.uniform(0, 10, size=(50, 2))
    y = 3.0 * X[:, 0] + 2.0
    model = LinearRegression().fit(X, y)
    
    pdp = compute_partial_dependence_1d(model, X, feature_idx=0, grid_resolution=10)
    assert len(pdp["grid"]) == 10
    assert len(pdp["pdp_values"]) == 10
    # PDP should be strictly monotonically increasing for feature 0
    assert pdp["pdp_values"][-1] > pdp["pdp_values"][0]
