import numpy as np

class PCAFromScratch:
    def __init__(self, n_components=2, whiten=False):
        self.n_components = n_components
        self.whiten = whiten
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None

    def fit(self, X):
        # TODO: Implement zero-centering, SVD decomposition, and eigenvalue extraction
        pass

    def transform(self, X):
        # TODO: Project centered data onto principal components
        pass

    def inverse_transform(self, Z):
        # TODO: Reconstruct original coordinates
        pass
