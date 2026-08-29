"""
Tests for starter metrics implementation.
"""
import pytest
import numpy as np
import metrics_lib as met


def test_confusion_stub():
    with pytest.raises(NotImplementedError):
        met.compute_confusion_matrix(np.array([0, 1]), np.array([0, 1]))


def test_metrics_stub():
    with pytest.raises(NotImplementedError):
        met.compute_metrics(np.array([0, 1]), np.array([0, 1]))
