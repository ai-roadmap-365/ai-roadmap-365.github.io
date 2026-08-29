"""
Tests for starter Class Imbalance implementation.
"""
import pytest
import numpy as np
import imbalance_lib as imb


def test_weights_stub():
    with pytest.raises(NotImplementedError):
        imb.compute_balanced_weights(np.array([0, 0, 0, 1]))


def test_smote_stub():
    with pytest.raises(NotImplementedError):
        imb.smote_synthetic_points(np.zeros((10, 2)), 5)
