"""
Classification Metrics reference library.
"""
import numpy as np


def compute_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Compute 2x2 confusion matrix:
    [[TN, FP],
     [FN, TP]]
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    
    return np.array([[tn, fp], [fn, tp]])


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """
    Compute comprehensive classification metrics:
    accuracy, precision, recall (sensitivity), specificity, f1, f2, mcc.
    """
    cm = compute_confusion_matrix(y_true, y_pred)
    tn, fp = cm[0, 0], cm[0, 1]
    fn, tp = cm[1, 0], cm[1, 1]
    total = tn + fp + fn + tp
    
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    # F1 score: harmonic mean of precision and recall
    f1 = 2.0 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # F2 score: beta=2 favors recall
    beta = 2.0
    beta_sq = beta ** 2
    f2 = (1.0 + beta_sq) * (precision * recall) / (beta_sq * precision + recall) if (beta_sq * precision + recall) > 0 else 0.0
    
    # Matthews Correlation Coefficient (MCC)
    denom = np.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    mcc = ((tp * tn) - (fp * fn)) / denom if denom > 0 else 0.0
    
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "specificity": float(specificity),
        "f1": float(f1),
        "f2": float(f2),
        "mcc": float(mcc),
    }


def compute_roc_curve(y_true: np.ndarray, y_scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute False Positive Rates (FPR), True Positive Rates (TPR), and Thresholds.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_scores = np.asarray(y_scores, dtype=float)
    
    num_pos = int(np.sum(y_true == 1))
    num_neg = int(np.sum(y_true == 0))
    if num_pos == 0 or num_neg == 0:
        raise ValueError("Both positive and negative samples required for ROC curve")
        
    # Sort distinct thresholds in descending order
    distinct_scores = np.unique(y_scores)
    thresholds = np.sort(distinct_scores)[::-1]
    # Add boundary threshold above max
    thresholds = np.r_[thresholds[0] + 1e-5, thresholds, -1e-5]
    
    fpr_list = []
    tpr_list = []
    
    for tau in thresholds:
        y_pred = (y_scores >= tau).astype(int)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        
        tpr_list.append(tp / num_pos)
        fpr_list.append(fp / num_neg)
        
    return np.array(fpr_list), np.array(tpr_list), thresholds


def compute_auc(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Area Under Curve via composite trapezoidal rule:
    integral y dx
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # Ensure sorted by x
    sort_idx = np.argsort(x)
    x_sorted = x[sort_idx]
    y_sorted = y[sort_idx]
    return float(np.sum((x_sorted[1:] - x_sorted[:-1]) * (y_sorted[1:] + y_sorted[:-1]) / 2.0))


def find_optimal_cost_threshold(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    cost_fp: float,
    cost_fn: float,
) -> tuple[float, float]:
    """
    Find decision threshold tau that minimizes total cost:
    Total Cost = cost_fp * FP + cost_fn * FN
    Returns (optimal_tau, min_cost).
    """
    y_true = np.asarray(y_true, dtype=int)
    y_scores = np.asarray(y_scores, dtype=float)
    
    thresholds = np.linspace(0.0, 1.0, 1001)
    best_tau = 0.5
    min_cost = float("inf")
    
    for tau in thresholds:
        y_pred = (y_scores >= tau).astype(int)
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        cost = float(cost_fp * fp + cost_fn * fn)
        if cost < min_cost:
            min_cost = cost
            best_tau = float(tau)
            
    return best_tau, min_cost
