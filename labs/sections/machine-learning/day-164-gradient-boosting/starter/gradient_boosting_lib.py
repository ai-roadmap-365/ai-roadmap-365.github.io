"""
Gradient Boosting starter library.
"""
import numpy as np
from sklearn.tree import DecisionTreeRegressor


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Sigmoid activation: 1 / (1 + exp(-z))."""
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


def compute_pseudo_residuals_classification(y: np.ndarray, raw_scores: np.ndarray) -> np.ndarray:
    """Compute negative gradient of log-loss: r_i = y_i - p_i."""
    raise NotImplementedError("Implement compute_pseudo_residuals_classification")


class GradientBoostingRegressorScratch:
    def __init__(self, n_estimators: int = 50, learning_rate: float = 0.1, max_depth: int = 3):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.f0 = 0.0
        self.trees = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit sequential additive regression trees on residuals."""
        raise NotImplementedError("Implement fit")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict continuous targets."""
        raise NotImplementedError("Implement predict")


class GradientBoostingClassifierScratch:
    def __init__(self, n_estimators: int = 30, learning_rate: float = 0.1, max_depth: int = 3):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.f0 = 0.0
        self.trees = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit sequential additive trees on pseudo-residuals with Newton-Raphson leaf updates."""
        raise NotImplementedError("Implement fit")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        raise NotImplementedError("Implement predict_proba")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict binary class labels."""
        raise NotImplementedError("Implement predict")
