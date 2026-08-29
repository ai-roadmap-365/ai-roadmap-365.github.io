"""
Decision Trees starter library.
"""
import numpy as np


def compute_gini(y: np.ndarray) -> float:
    """Compute Gini impurity: G = 1 - sum(p_k^2)."""
    raise NotImplementedError("Implement compute_gini")


def compute_entropy(y: np.ndarray) -> float:
    """Compute Shannon entropy: H = -sum(p_k * log2(p_k))."""
    raise NotImplementedError("Implement compute_entropy")


def find_best_split(X: np.ndarray, y: np.ndarray) -> tuple[int, float, float]:
    """Find the feature and threshold that minimize weighted child Gini impurity."""
    raise NotImplementedError("Implement find_best_split")


class DecisionTreeClassifierScratch:
    def __init__(self, max_depth: int = 3, min_samples_split: int = 2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit decision tree recursively."""
        raise NotImplementedError("Implement fit")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for X."""
        raise NotImplementedError("Implement predict")
