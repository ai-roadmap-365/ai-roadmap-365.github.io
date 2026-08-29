"""
Tests for starter logistic regression implementation.
"""
import pytest
import numpy as np
import logistic_lib as logreg


def test_sigmoid_stub():
    with pytest.raises(NotImplementedError):
        logreg.sigmoid(np.array([0.0]))


def test_predict_proba_stub():
    with pytest.raises(NotImplementedError):
        logreg.predict_proba(np.zeros((2, 2)), np.zeros(2), 0.0)


def test_binary_cross_entropy_stub():
    with pytest.raises(NotImplementedError):
        logreg.binary_cross_entropy(np.array([1, 0]), np.array([0.8, 0.2]))
