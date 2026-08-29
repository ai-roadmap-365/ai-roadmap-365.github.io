import pytest
import numpy as np
from examples.hierarchical_clustering_and_dbscan_lib import DBSCANFromScratch

def test_dbscan_cluster_discovery():
    np.random.seed(42)
    c1 = np.random.normal(loc=[-4.0, 0.0], scale=0.2, size=(40, 2))
    c2 = np.random.normal(loc=[4.0, 0.0], scale=0.2, size=(40, 2))
    X = np.vstack([c1, c2])

    db = DBSCANFromScratch(eps=0.8, min_samples=4).fit(X)
    unique_labels = set(db.labels_) - {-1}
    assert len(unique_labels) == 2
    assert db.labels_[0] != db.labels_[45]

def test_dbscan_noise_filtering():
    np.random.seed(42)
    c1 = np.random.normal(loc=[0.0, 0.0], scale=0.2, size=(30, 2))
    noise = np.array([[15.0, 15.0], [-15.0, -15.0]])
    X = np.vstack([c1, noise])

    db = DBSCANFromScratch(eps=0.8, min_samples=4).fit(X)
    assert db.labels_[-1] == -1
    assert db.labels_[-2] == -1
    assert db.labels_[0] != -1
