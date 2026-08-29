"""
Tests for starter Gradient Boosting implementation.
"""
import pytest
import numpy as np
import gradient_boosting_lib as gb


def test_pseudo_residuals_stub():
    with pytest.raises(NotImplementedError):
        gb.compute_pseudo_residuals_classification(np.array([1, 0]), np.array([0.0, 0.0]))


def test_fit_stub():
    clf = gb.GradientBoostingClassifierScratch()
    with pytest.raises(NotImplementedError):
        clf.fit(np.zeros((10, 2)), np.zeros(10))
