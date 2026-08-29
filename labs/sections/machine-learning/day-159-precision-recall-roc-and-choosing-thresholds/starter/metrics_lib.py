"""
Classification Metrics starter library.
"""
import numpy as np


def compute_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Compute 2x2 confusion matrix: [[TN, FP], [FN, TP]]."""
    raise NotImplementedError("Implement compute_confusion_matrix")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute precision, recall, specificity, f1, f2, and mcc."""
    raise NotImplementedError("Implement compute_metrics")


def compute_roc_curve(y_true: np.ndarray, y_scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute False Positive Rates, True Positive Rates, and Thresholds."""
    raise NotImplementedError("Implement compute_roc_curve")


def compute_auc(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Area Under Curve using composite trapezoidal rule."""
    raise NotImplementedError("Implement compute_auc")


def find_optimal_cost_threshold(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    cost_fp: float,
    cost_fn: float,
) -> tuple[float, float]:
    """Find decision threshold tau that minimizes total financial/clinical cost."""
    raise NotImplementedError("Implement find_optimal_cost_threshold")
