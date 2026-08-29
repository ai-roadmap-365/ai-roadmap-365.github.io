"""
Feature Scaling and Encoding starter library.
"""
import numpy as np


class StandardScalerScratch:
    """Standardize features by removing mean and scaling to unit variance."""
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray):
        raise NotImplementedError("Implement fit")

    def transform(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implement transform")

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class RobustScalerScratch:
    """Scale features using statistics robust to outliers (Median and IQR)."""
    def __init__(self):
        self.center_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray):
        raise NotImplementedError("Implement fit")

    def transform(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implement transform")


def out_of_fold_target_encode(categories: np.ndarray, target: np.ndarray, cv: int = 5, smoothing: float = 10.0, random_state: int = 42) -> np.ndarray:
    """Compute leak-free smoothed out-of-fold target encoding for a categorical column."""
    raise NotImplementedError("Implement out_of_fold_target_encode")
