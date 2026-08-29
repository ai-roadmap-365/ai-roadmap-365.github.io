"""
Tests for starter hyperparameter tuning.
"""
import pytest
import numpy as np
import tuning_lib as tuning


def test_ei_stub():
    with pytest.raises(NotImplementedError):
        tuning.compute_expected_improvement(np.array([1.0]), np.array([0.5]), 0.8)


def test_grid_stub():
    with pytest.raises(NotImplementedError):
        tuning.grid_search_scratch(None, {}, np.zeros((10, 2)), np.zeros(10))
