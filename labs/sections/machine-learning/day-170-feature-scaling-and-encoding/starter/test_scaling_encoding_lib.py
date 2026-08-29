"""
Tests for starter feature scaling and encoding.
"""
import pytest
import numpy as np
import scaling_encoding_lib as se


def test_standard_scaler_stub():
    scaler = se.StandardScalerScratch()
    with pytest.raises(NotImplementedError):
        scaler.fit(np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_target_encode_stub():
    with pytest.raises(NotImplementedError):
        se.out_of_fold_target_encode(np.array(["A", "B"]), np.array([1, 0]))
