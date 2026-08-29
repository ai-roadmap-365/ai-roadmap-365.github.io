"""
Tests for starter XGBoost/LightGBM foundations.
"""
import pytest
import numpy as np
import boost_practice_lib as boost


def test_xgboost_gain_stub():
    with pytest.raises(NotImplementedError):
        boost.compute_xgboost_split_gain(1.0, 1.0, 1.0, 1.0)


def test_binning_stub():
    with pytest.raises(NotImplementedError):
        boost.histogram_bin_feature(np.array([1.0, 2.0]))
