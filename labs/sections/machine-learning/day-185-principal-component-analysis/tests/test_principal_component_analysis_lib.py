import pytest
import numpy as np
from examples.principal_component_analysis_lib import PCAFromScratch

def test_pca_shapes_and_explained_variance():
    np.random.seed(42)
    X = np.random.normal(0, 1, (100, 4))
    pca = PCAFromScratch(n_components=2).fit(X)

    assert pca.components_.shape == (2, 4)
    assert len(pca.explained_variance_ratio_) == 2
    assert np.sum(pca.explained_variance_ratio_) <= 1.0
    assert pca.explained_variance_ratio_[0] >= pca.explained_variance_ratio_[1]

def test_pca_reconstruction():
    np.random.seed(42)
    X = np.random.normal(0, 1, (50, 3))
    pca = PCAFromScratch(n_components=3).fit(X)
    Z = pca.transform(X)
    X_rec = pca.inverse_transform(Z)

    assert np.allclose(X, X_rec, atol=1e-5)
