"""
Tests for starter scikit-learn pipelines.
"""
import pytest
import numpy as np
import pipeline_lib as pl


def test_log_transformer_stub():
    tr = pl.CustomLogTransformer()
    with pytest.raises(NotImplementedError):
        tr.fit(np.ones((5, 2)))


def test_outlier_clipper_stub():
    tr = pl.OutlierClipperTransformer()
    with pytest.raises(NotImplementedError):
        tr.fit(np.ones((5, 2)))
