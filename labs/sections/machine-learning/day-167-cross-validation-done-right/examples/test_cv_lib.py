"""
Tests for reference Cross-Validation implementation.
"""
import pytest
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import cv_lib as cv


def test_stratified_kfold_ratio_preservation():
    # 80 Class 0, 20 Class 1 (80% / 20% ratio)
    y = np.array([0] * 80 + [1] * 20)
    
    for train_idx, val_idx in cv.stratified_kfold_scratch(y, n_splits=4, shuffle=True):
        val_y = y[val_idx]
        p_pos = np.mean(val_y == 1)
        # Ratio must be exactly 0.20 in every fold
        assert np.isclose(p_pos, 0.20, atol=0.05)
        assert len(np.intersect1d(train_idx, val_idx)) == 0


def test_group_kfold_disjoint_guarantee():
    # 4 patients/groups: Group 1 has 10 rows, Group 2 has 10 rows, etc.
    groups = np.repeat([1, 2, 3, 4], 10)
    
    for train_idx, val_idx in cv.group_kfold_scratch(groups, n_splits=4):
        train_groups = set(groups[train_idx])
        val_groups = set(groups[val_idx])
        # Intersection between train groups and val groups MUST be strictly empty!
        assert len(train_groups.intersection(val_groups)) == 0


def test_time_series_split_temporal_order():
    n_samples = 100
    for train_idx, val_idx in cv.time_series_split_scratch(n_samples, n_splits=4):
        # Maximum training index must be strictly less than minimum validation index
        assert np.max(train_idx) < np.min(val_idx)
        # Training indices start at index 0 (expanding window)
        assert train_idx[0] == 0


def test_nested_cross_validation_execution():
    X = np.random.randn(90, 4)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    grid = {"max_depth": [2, 4], "random_state": [42]}
    score = cv.nested_cross_validation_score(
        DecisionTreeClassifier, grid, X, y, outer_k=3, inner_k=3
    )
    
    assert 0.50 <= score <= 1.0
