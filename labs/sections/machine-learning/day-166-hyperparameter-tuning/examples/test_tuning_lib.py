"""
Tests for reference hyperparameter tuning implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
import tuning_lib as tuning


def test_expected_improvement_analytical_values():
    # If mu is significantly higher than best_y, EI is large
    mu = np.array([0.95])
    sigma = np.array([0.05])
    best_y = 0.80
    ei = tuning.compute_expected_improvement(mu, sigma, best_y, xi=0.0)
    assert ei[0] > 0.10

    # If sigma is near zero and mu < best_y, EI is 0.0
    mu_low = np.array([0.50])
    sigma_zero = np.array([0.0])
    ei_zero = tuning.compute_expected_improvement(mu_low, sigma_zero, best_y, xi=0.0)
    assert ei_zero[0] == 0.0


def test_grid_search_scratch_iris():
    cancer = load_breast_cancer()
    X, y = cancer.data[:150], cancer.target[:150]
    
    grid = {
        "max_depth": [2, 4, 6],
        "min_samples_split": [2, 5],
        "random_state": [42]
    }
    
    best_params, best_score = tuning.grid_search_scratch(
        DecisionTreeClassifier, grid, X, y, cv=3
    )
    
    assert best_score >= 0.85
    assert best_params["max_depth"] in [2, 4, 6]
    assert best_params["min_samples_split"] in [2, 5]


def test_random_search_scratch_iris():
    cancer = load_breast_cancer()
    X, y = cancer.data[:150], cancer.target[:150]
    
    dists = {
        "max_depth": [2, 3, 4, 5, 6, 8],
        "min_samples_split": [2, 4, 6, 8],
        "random_state": [42]
    }
    
    best_params, best_score = tuning.random_search_scratch(
        DecisionTreeClassifier, dists, n_iter=6, X, y, cv=3, random_state=42
    )
    
    assert best_score >= 0.85
    assert "max_depth" in best_params
