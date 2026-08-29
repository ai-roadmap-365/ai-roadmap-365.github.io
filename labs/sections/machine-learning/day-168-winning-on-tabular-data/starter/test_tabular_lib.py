"""
Tests for starter tabular library.
"""
import pytest
import numpy as np
import tabular_lib as tab


def test_oof_stub():
    with pytest.raises(NotImplementedError):
        tab.generate_out_of_fold_predictions([], np.zeros((10, 2)), np.zeros(10))


def test_perm_stub():
    with pytest.raises(NotImplementedError):
        tab.compute_permutation_importance(None, np.zeros((10, 2)), np.zeros(10))
