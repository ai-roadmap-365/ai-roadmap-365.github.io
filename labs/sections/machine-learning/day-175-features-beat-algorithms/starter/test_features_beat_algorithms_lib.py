"""
Tests for starter features beat algorithms benchmark.
"""
import pytest
import numpy as np
import features_beat_algorithms_lib as fba


def test_domain_rep_stub():
    with pytest.raises(NotImplementedError):
        fba.engineer_domain_representation(np.zeros((5, 4)))


def test_benchmark_stub():
    with pytest.raises(NotImplementedError):
        fba.benchmark_raw_vs_engineered(np.zeros((5, 2)), np.zeros(5), np.zeros((5, 2)), np.zeros(5))
