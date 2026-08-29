"""
Tests for starter feature selection.
"""
import pytest
import numpy as np
import selection_lib as fs


def test_variance_stub():
    with pytest.raises(NotImplementedError):
        fs.filter_by_variance_threshold(np.zeros((5, 3)))


def test_rfe_stub():
    with pytest.raises(NotImplementedError):
        fs.recursive_feature_elimination_scratch(None, np.zeros((5, 3)), np.zeros(5))
