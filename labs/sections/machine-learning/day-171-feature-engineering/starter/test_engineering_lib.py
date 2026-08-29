"""
Tests for starter feature engineering.
"""
import pytest
import numpy as np
import engineering_lib as fe


def test_cyclical_stub():
    with pytest.raises(NotImplementedError):
        fe.encode_cyclical_time(np.array([0.0, 12.0]))


def test_poly_stub():
    with pytest.raises(NotImplementedError):
        fe.compute_polynomial_interactions(np.zeros((5, 2)))
