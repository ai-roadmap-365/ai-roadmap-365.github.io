import pytest
import numpy as np
from examples.a_segmentation_study_lib import CustomerSegmentationPipeline

def test_segmentation_pipeline_execution():
    np.random.seed(42)
    X = np.random.exponential(scale=100.0, size=(120, 3)) + 1.0
    pipe = CustomerSegmentationPipeline(n_clusters=3).fit(X)

    assert len(np.unique(pipe.labels_)) == 3
    assert len(pipe.labels_) == 120
    assert pipe.centroids_.shape[0] == 3

def test_persona_profiles_output():
    np.random.seed(42)
    X = np.random.uniform(10, 500, size=(60, 3))
    pipe = CustomerSegmentationPipeline(n_clusters=2).fit(X)
    profiles = pipe.compute_persona_profiles(X)

    assert len(profiles) == 2
    assert "Cluster_0" in profiles
    assert "mean_monetary" in profiles["Cluster_0"]
    assert profiles["Cluster_0"]["count"] > 0
