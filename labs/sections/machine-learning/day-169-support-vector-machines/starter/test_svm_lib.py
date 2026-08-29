"""
Tests for starter SVM library.
"""
import pytest
import numpy as np
import svm_lib as svm


def test_rbf_stub():
    with pytest.raises(NotImplementedError):
        svm.compute_rbf_kernel(np.zeros((2, 2)), np.zeros((2, 2)))


def test_svm_stub():
    clf = svm.LinearSVMScratch()
    with pytest.raises(NotImplementedError):
        clf.fit(np.zeros((4, 2)), np.array([1, -1, 1, -1]))
