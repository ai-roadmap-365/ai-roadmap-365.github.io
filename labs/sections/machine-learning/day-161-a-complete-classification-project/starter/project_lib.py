"""
Complete Classification Project starter library.
"""
import numpy as np


class ClassificationProjectPipeline:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.scaler = None
        self.best_model = None
        self.optimal_threshold = 0.50

    def fit_and_select(self, X_train: np.ndarray, y_train: np.ndarray) -> dict[str, float]:
        """Fit candidate models via Stratified 5-Fold CV and select top performer."""
        raise NotImplementedError("Implement fit_and_select")

    def calibrate_threshold(self, X_val: np.ndarray, y_val: np.ndarray, cost_fp: float = 1.0, cost_fn: float = 5.0) -> float:
        """Find optimal decision threshold minimizing asymmetric cost on validation split."""
        raise NotImplementedError("Implement calibrate_threshold")

    def evaluate_test(self, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, float]:
        """Perform ONE final evaluation on held-out test data."""
        raise NotImplementedError("Implement evaluate_test")
