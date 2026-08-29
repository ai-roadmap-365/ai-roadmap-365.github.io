"""
Support Vector Machines starter library.
"""
import numpy as np


def compute_rbf_kernel(X1: np.ndarray, X2: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """Compute RBF Gaussian Gram matrix: K(x, z) = exp(-gamma * ||x - z||^2)."""
    raise NotImplementedError("Implement compute_rbf_kernel")


class LinearSVMScratch:
    """Soft-margin linear SVM trained via Pegasos subgradient descent on Hinge Loss."""
    def __init__(self, C: float = 1.0, learning_rate: float = 0.01, max_iter: int = 1000, random_state: int = 42):
        self.C = C
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.random_state = random_state
        self.w = None
        self.b = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        raise NotImplementedError("Implement fit")

    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implement predict")
