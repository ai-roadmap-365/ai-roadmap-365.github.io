"""
Tests for starter Cross-Validation.
"""
import pytest
import numpy as np
import cv_lib as cv


def test_stratified_stub():
    with pytest.raises(NotImplementedError):
        list(cv.stratified_kfold_scratch(np.array([0, 1, 0, 1])))


def test_group_stub():
    with pytest.raises(NotImplementedError):
        list(cv.group_kfold_scratch(np.array([1, 1, 2, 2])))
