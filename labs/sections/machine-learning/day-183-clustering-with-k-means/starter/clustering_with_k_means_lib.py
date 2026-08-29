import numpy as np

class KMeansFromScratch:
    def __init__(self, n_clusters=3, max_iter=300, tol=1e-4, init='k-means++', random_state=42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.random_state = random_state
        self.cluster_centers_ = None
        self.inertia_ = None

    def fit(self, X):
        # TODO: Implement k-means++ initialization, Lloyd assignment and update steps
        pass

    def predict(self, X):
        # TODO: Return index of closest centroid for each sample
        pass
