"""
Logistic Regression library starter implementation.
"""
import numpy as np


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Compute the logistic sigmoid function."""
    raise NotImplementedError("Implement sigmoid")


def predict_proba(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    """Compute predicted probabilities for class 1."""
    raise NotImplementedError("Implement predict_proba")


def binary_cross_entropy(y_true: np.ndarray, y_prob: np.ndarray, eps: float = 1e-15) -> float:
    """Compute binary cross-entropy (log loss)."""
    raise NotImplementedError("Implement binary_cross_entropy")


def compute_gradients(X: np.ndarray, y_true: np.ndarray, y_prob: np.ndarray) -> tuple[np.ndarray, float]:
    """Compute gradients of loss with respect to w and b."""
    raise NotImplementedError("Implement compute_gradients")


def fit_logistic_regression(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.1,
    epochs: int = 1000,
    tol: float = 1e-6
) -> tuple[np.ndarray, float, list[float]]:
    """Fit logistic regression model using batch gradient descent."""
    raise NotImplementedError("Implement fit_logistic_regression")


def predict_classes(X: np.ndarray, w: np.ndarray, b: float, threshold: float = 0.5) -> np.ndarray:
    """Predict binary class labels (0 or 1) based on probability threshold."""
    raise NotImplementedError("Implement predict_classes")
