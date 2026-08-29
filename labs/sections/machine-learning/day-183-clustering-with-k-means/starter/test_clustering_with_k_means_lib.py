import pytest
import numpy as np
from examples.clustering_with_k_means_lib import KMeansFromScratch

def test_kmeans_convergence_and_inertia():
    np.random.seed(42)
    c1 = np.random.normal(loc=[-5.0, 0.0], scale=0.5, size=(50, 2))
    c2 = np.random.normal(loc=[5.0, 0.0], scale=0.5, size=(50, 2))
    X = np.vstack([c1, c2])

    kmeans = KMeansFromScratch(n_clusters=2, random_state=42).fit(X)
    assert kmeans.cluster_centers_.shape == (2, 2)
    assert kmeans.inertia_ > 0
    assert kmeans.inertia_ < 100.0

def test_kmeans_prediction_accuracy():
    np.random.seed(42)
    c1 = np.random.normal(loc=[-10.0, -10.0], scale=0.2, size=(30, 2))
    c2 = np.random.normal(loc=[10.0, 10.0], scale=0.2, size=(30, 2))
    X = np.vstack([c1, c2])

    kmeans = KMeansFromScratch(n_clusters=2, random_state=42).fit(X)
    p1 = kmeans.predict(np.array([[-10.0, -10.0]]))
    p2 = kmeans.predict(np.array([[10.0, 10.0]]))
    assert p1[0] != p2[0]
