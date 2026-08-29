import pytest
import numpy as np
from metric_lib import (
    compute_classification_metrics,
    find_optimal_cost_threshold,
    compute_regression_metrics,
    compute_ranking_ndcg
)

def test_classification_metrics():
    y_true = [1, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 0, 0, 1, 1]
    y_prob = [0.9, 0.4, 0.1, 0.2, 0.8, 0.6]
    
    res = compute_classification_metrics(y_true, y_pred, y_prob, beta=1.0)
    assert res["confusion_matrix"]["tp"] == 2
    assert res["confusion_matrix"]["tn"] == 2
    assert res["confusion_matrix"]["fp"] == 1
    assert res["confusion_matrix"]["fn"] == 1
    assert 0.0 <= res["mcc"] <= 1.0
    assert 0.5 <= res["roc_auc"] <= 1.0

def test_cost_optimal_threshold():
    y_true = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
    y_prob = np.array([0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05, 0.01])
    # Massive cost for False Negatives ($1000) vs False Positives ($10)
    cost_matrix = {"c_tp": 0, "c_tn": 0, "c_fp": 10, "c_fn": 1000}
    
    best_t, best_cost = find_optimal_cost_threshold(y_true, y_prob, cost_matrix)
    # The optimal threshold should be low to avoid expensive False Negatives
    assert best_t <= 0.65
    assert best_cost < 100.0

def test_regression_metrics():
    y_true = [10.0, 20.0, 30.0, 40.0]
    y_pred = [12.0, 18.0, 33.0, 38.0]
    
    res = compute_regression_metrics(y_true, y_pred)
    assert res["mae"] == 2.25
    assert res["r2"] > 0.90
    assert res["mape"] > 0.0
    assert res["smape"] > 0.0

def test_ranking_ndcg():
    # Documents graded 0 to 3
    relevance = [3, 2, 3, 0, 1, 2]
    # Model assigns higher scores to relevant documents
    scores = [0.95, 0.80, 0.70, 0.10, 0.30, 0.60]
    
    ndcg = compute_ranking_ndcg(relevance, scores, k=3)
    assert 0.80 <= ndcg <= 1.0
