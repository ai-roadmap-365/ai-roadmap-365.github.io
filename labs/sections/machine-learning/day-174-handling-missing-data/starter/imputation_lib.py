"""
Handling Missing Data starter library.
"""
import numpy as np


def compute_nan_euclidean_distance(u: np.ndarray, v: np.ndarray) -> float:
    """Compute NaN-aware Euclidean distance between two vectors with missing coordinates."""
    raise NotImplementedError("Implement compute_nan_euclidean_distance")


def generate_missing_indicator(X: np.ndarray) -> np.ndarray:
    """Generate binary indicator matrix I_{mis} where 1 indicates missing (NaN) and 0 indicates observed."""
    raise NotImplementedError("Implement generate_missing_indicator")


def knn_imputer_scratch(X: np.ndarray, n_neighbors: int = 3) -> np.ndarray:
    """Impute missing values using distance-weighted K-Nearest Neighbors."""
    raise NotImplementedError("Implement knn_imputer_scratch")
