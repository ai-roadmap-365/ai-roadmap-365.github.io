"""
Random Forests starter library.
"""
import numpy as np


def bootstrap_sample(X: np.ndarray, y: np.ndarray, random_state=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a bootstrap sample and return (X_boot, y_boot, oob_indices)."""
    raise NotImplementedError("Implement bootstrap_sample")


class RandomForestClassifierScratch:
    def __init__(self, n_estimators: int = 15, max_depth: int = 5, max_features: str = "sqrt", random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []
        self.oob_score_ = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit ensemble of randomized decision trees with OOB tracking."""
        raise NotImplementedError("Implement fit")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels via majority voting."""
        raise NotImplementedError("Implement predict")
