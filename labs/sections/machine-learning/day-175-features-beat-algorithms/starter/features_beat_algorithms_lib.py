"""
Features Beat Algorithms starter library.
"""
import numpy as np


def engineer_domain_representation(X_raw: np.ndarray) -> np.ndarray:
    """Transform raw physical measurements [height, weight, age, hours] into rich domain features."""
    raise NotImplementedError("Implement engineer_domain_representation")


def calculate_feature_roi(r2_improvement: float, latency_increase_ms: float) -> float:
    """Calculate the efficiency ROI metric of adding feature engineering complexity."""
    raise NotImplementedError("Implement calculate_feature_roi")


def benchmark_raw_vs_engineered(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, float]:
    """Compare Ridge on raw features vs Ridge on engineered features."""
    raise NotImplementedError("Implement benchmark_raw_vs_engineered")
