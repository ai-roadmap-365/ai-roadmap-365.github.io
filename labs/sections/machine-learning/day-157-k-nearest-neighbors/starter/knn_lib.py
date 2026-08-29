"""
k-Nearest Neighbors starter library.
"""
import numpy as np


def compute_distance_matrix(X_train: np.ndarray, X_test: np.ndarray, metric: str = "euclidean") -> np.ndarray:
    """Compute pairwise distance matrix between test points and training points."""
    raise NotImplementedError("Implement compute_distance_matrix")


def predict_knn(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    k: int = 5,
    weights: str = "uniform",
) -> np.ndarray:
    """Predict class labels for test points using k-nearest neighbors."""
    raise NotImplementedError("Implement predict_knn")


def predict_proba_knn(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    k: int = 5,
    weights: str = "uniform",
) -> np.ndarray:
    """Compute class probability distributions for test points."""
    raise NotImplementedError("Implement predict_proba_knn")
