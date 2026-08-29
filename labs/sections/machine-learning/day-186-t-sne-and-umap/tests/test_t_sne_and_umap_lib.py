import pytest
import numpy as np
from examples.t_sne_and_umap_lib import TSNEFromScratch

def test_tsne_affinities_properties():
    np.random.seed(42)
    X = np.random.normal(0, 1, (30, 3))
    tsne = TSNEFromScratch(perplexity=10.0)
    P = tsne._compute_affinities(X)

    assert P.shape == (30, 30)
    assert np.allclose(P, P.T)
    assert np.all(P >= 0)
    assert np.isclose(np.sum(P), 1.0, atol=1e-4)

def test_tsne_embedding_output_shape():
    np.random.seed(42)
    X = np.random.normal(0, 1, (40, 5))
    tsne = TSNEFromScratch(n_components=2, perplexity=10.0, n_iter=50)
    Y = tsne.fit_transform(X)

    assert Y.shape == (40, 2)
    assert not np.isnan(Y).any()
