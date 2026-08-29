"""
Tests for starter Random Forest implementation.
"""
import pytest
import numpy as np
import forest_lib as forest


def test_bootstrap_stub():
    with pytest.raises(NotImplementedError):
        forest.bootstrap_sample(np.zeros((10, 2)), np.zeros(10))


def test_fit_stub():
    rf = forest.RandomForestClassifierScratch()
    with pytest.raises(NotImplementedError):
        rf.fit(np.zeros((10, 2)), np.zeros(10))
