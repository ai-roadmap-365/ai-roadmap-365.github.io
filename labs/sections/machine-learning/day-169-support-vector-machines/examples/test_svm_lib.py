"""
Tests for reference SVM implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import make_classification, make_blobs
from sklearn.metrics import accuracy_score
import svm_lib as svm


def test_rbf_kernel_properties():
    X = np.array([[0.0, 0.0], [1.0, 1.0]])
    K = svm.compute_rbf_kernel(X, X, gamma=0.5)
    
    # Diagonal must be exactly 1.0 (distance to self is 0)
    assert np.isclose(K[0, 0], 1.0)
    assert np.isclose(K[1, 1], 1.0)
    # Off-diagonal: exp(-0.5 * 2) = exp(-1.0) ≈ 0.367879
    assert np.isclose(K[0, 1], np.exp(-1.0))
    assert np.isclose(K[0, 1], K[1, 0]) # Symmetric Gram matrix


def test_linear_svm_scratch_separable_blobs():
    X, y = make_blobs(n_samples=100, centers=2, random_state=42, cluster_std=0.8)
    
    clf = svm.LinearSVMScratch(C=10.0, max_iter=500, random_state=42)
    clf.fit(X, y)
    preds = clf.predict(X)
    
    acc = accuracy_score(y, preds)
    assert acc >= 0.95
