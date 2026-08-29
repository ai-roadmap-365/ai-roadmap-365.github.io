"""
Tests for starter Complete Classification Project.
"""
import pytest
import numpy as np
import project_lib as prj


def test_pipeline_stub():
    pipe = prj.ClassificationProjectPipeline()
    with pytest.raises(NotImplementedError):
        pipe.fit_and_select(np.zeros((10, 2)), np.array([0, 1]*5))
