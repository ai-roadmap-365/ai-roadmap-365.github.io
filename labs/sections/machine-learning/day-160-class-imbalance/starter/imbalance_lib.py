"""
Class Imbalance starter library.
"""
import numpy as np


def compute_balanced_weights(y: np.ndarray) -> dict[int, float]:
    """Compute balanced class weights: w_c = N / (K * N_c)."""
    raise NotImplementedError("Implement compute_balanced_weights")


def random_undersample(X: np.ndarray, y: np.ndarray, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Undersample majority class to match minority class sample count."""
    raise NotImplementedError("Implement random_undersample")


def random_oversample(X: np.ndarray, y: np.ndarray, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Oversample minority class with replacement to match majority sample count."""
    raise NotImplementedError("Implement random_oversample")


def smote_synthetic_points(
    X_minority: np.ndarray,
    n_samples: int,
    k_neighbors: int = 5,
    random_state: int = 42,
) -> np.ndarray:
    """Generate synthetic minority points via k-NN line segment interpolation."""
    raise NotImplementedError("Implement smote_synthetic_points")
