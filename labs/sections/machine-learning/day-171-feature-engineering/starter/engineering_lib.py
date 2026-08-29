"""
Feature Engineering starter library.
"""
import numpy as np


def encode_cyclical_time(timestamps: np.ndarray, period: float = 24.0) -> tuple[np.ndarray, np.ndarray]:
    """Encode periodic timestamps into continuous (sin, cos) cyclical coordinate pairs."""
    raise NotImplementedError("Implement encode_cyclical_time")


def compute_polynomial_interactions(X: np.ndarray) -> np.ndarray:
    """Generate all pairwise product interactions x_i * x_j for i <= j."""
    raise NotImplementedError("Implement compute_polynomial_interactions")


def compute_group_aggregations(groups_train: np.ndarray, values_train: np.ndarray, groups_test: np.ndarray) -> np.ndarray:
    """Compute leak-free group mean and std on training data, mapping onto test data with global fallback."""
    raise NotImplementedError("Implement compute_group_aggregations")
