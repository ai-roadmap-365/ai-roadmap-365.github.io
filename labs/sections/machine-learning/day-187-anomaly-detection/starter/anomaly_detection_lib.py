import numpy as np

def c_factor(n):
    # TODO: Implement BST average path length normalization
    pass

class IsolationTree:
    def __init__(self, current_depth=0, max_depth=10):
        self.current_depth = current_depth
        self.max_depth = max_depth
        self.split_feature = None
        self.split_value = None
        self.left = None
        self.right = None
        self.size = 0
        self.is_leaf = False

    def fit(self, X):
        # TODO: Recursively partition sub-sample
        pass

    def path_length(self, x):
        # TODO: Compute path length h(x)
        pass

class IsolationForestFromScratch:
    def __init__(self, n_estimators=50, max_samples=128, contamination=0.05):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.trees = []

    def fit(self, X):
        # TODO: Train ensemble of iTrees
        pass

    def decision_function(self, X):
        # TODO: Compute anomaly scores s(x, n)
        pass
