"""
Feature Selection starter library.
"""
import numpy as np


def filter_by_variance_threshold(X: np.ndarray, threshold: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Filter out features with sample variance <= threshold. Return (X_filtered, support_mask)."""
    raise NotImplementedError("Implement filter_by_variance_threshold")


def compute_mutual_information_scores(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute univariate dependency scores between each feature and target."""
    raise NotImplementedError("Implement compute_mutual_information_scores")


def recursive_feature_elimination_scratch(estimator, X: np.ndarray, y: np.ndarray, n_features_to_select: int = 5) -> np.ndarray:
    """Perform RFE by recursively fitting estimator and pruning smallest absolute coefficient."""
    raise NotImplementedError("Implement recursive_feature_elimination_scratch")
