import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

def compute_classification_metrics(y_true, y_pred, y_prob=None, beta=1.0):
    """
    Compute comprehensive classification metrics including MCC and F-beta.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    n = len(y_true)
    accuracy = (tp + tn) / max(n, 1)
    
    precision = tp / max(tp + fp, 1e-9)
    recall = tp / max(tp + fn, 1e-9)
    specificity = tn / max(tn + fp, 1e-9)
    
    b2 = beta ** 2
    f_beta = (1.0 + b2) * (precision * recall) / max((b2 * precision) + recall, 1e-9)
    
    mcc_denom = np.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    mcc = float((tp * tn) - (fp * fn)) / max(mcc_denom, 1e-9)
    
    res = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "specificity": float(specificity),
        "f_beta": float(f_beta),
        "mcc": float(mcc),
        "confusion_matrix": {"tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn)}
    }
    
    if y_prob is not None:
        y_prob = np.asarray(y_prob, dtype=float)
        try:
            res["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except Exception:
            res["roc_auc"] = 0.5
        try:
            res["pr_auc"] = float(average_precision_score(y_true, y_prob))
        except Exception:
            res["pr_auc"] = float(np.mean(y_true))
            
    return res

def find_optimal_cost_threshold(y_true, y_prob, cost_matrix, thresholds=None):
    """
    Calculate the optimal decision threshold minimizing expected financial cost.
    cost_matrix: dict with keys 'c_tp', 'c_tn', 'c_fp', 'c_fn'
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    if thresholds is None:
        thresholds = np.linspace(0.01, 0.99, 99)
        
    best_cost = float("inf")
    best_threshold = 0.5
    
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        
        total_cost = (
            tp * cost_matrix.get("c_tp", 0.0) +
            tn * cost_matrix.get("c_tn", 0.0) +
            fp * cost_matrix.get("c_fp", 0.0) +
            fn * cost_matrix.get("c_fn", 0.0)
        )
        if total_cost < best_cost:
            best_cost = total_cost
            best_threshold = t
            
    return float(best_threshold), float(best_cost)

def compute_regression_metrics(y_true, y_pred):
    """
    Compute standard, robust, and percentage regression metrics.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    errors = y_true - y_pred
    mse = np.mean(errors ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(errors))
    median_ae = np.median(np.abs(errors))
    
    # MAPE with epsilon guard
    mape = np.mean(np.abs(errors) / np.maximum(np.abs(y_true), 1e-6)) * 100.0
    
    # Symmetric MAPE (sMAPE)
    smape_denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    smape = np.mean(np.abs(errors) / np.maximum(smape_denom, 1e-6)) * 100.0
    
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_res = np.sum(errors ** 2)
    r2 = 1.0 - (ss_res / max(ss_tot, 1e-9))
    
    return {
        "mse": float(mse),
        "rmse": float(rmse),
        "mae": float(mae),
        "median_ae": float(median_ae),
        "mape": float(mape),
        "smape": float(smape),
        "r2": float(r2)
    }

def compute_ranking_ndcg(y_true_relevance, y_score, k=5):
    """
    Compute Normalized Discounted Cumulative Gain at Rank K (NDCG@K).
    """
    y_true_relevance = np.asarray(y_true_relevance, dtype=float)
    y_score = np.asarray(y_score, dtype=float)
    
    order = np.argsort(y_score)[::-1][:k]
    rel_at_k = y_true_relevance[order]
    
    gains = (2.0 ** rel_at_k) - 1.0
    discounts = np.log2(np.arange(len(rel_at_k)) + 2.0)
    dcg = np.sum(gains / discounts)
    
    ideal_order = np.argsort(y_true_relevance)[::-1][:k]
    ideal_rel = y_true_relevance[ideal_order]
    ideal_gains = (2.0 ** ideal_rel) - 1.0
    idcg = np.sum(ideal_gains / discounts)
    
    if idcg <= 0.0:
        return 0.0
    return float(dcg / idcg)
