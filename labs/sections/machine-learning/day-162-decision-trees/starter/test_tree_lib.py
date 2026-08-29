"""
Tests for starter Decision Tree implementation.
"""
import pytest
import numpy as np
import tree_lib as tree


def test_gini_stub():
    with pytest.raises(NotImplementedError):
        tree.compute_gini(np.array([0, 1]))


def test_fit_stub():
    clf = tree.DecisionTreeClassifierScratch()
    with pytest.raises(NotImplementedError):
        clf.fit(np.zeros((10, 2)), np.zeros(10))
