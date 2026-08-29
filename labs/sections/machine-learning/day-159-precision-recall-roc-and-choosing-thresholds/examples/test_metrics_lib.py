"""
Tests for reference classification metrics implementation.
"""
import pytest
import numpy as np
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score, matthews_corrcoef
)
import metrics_lib as met


def test_confusion_matrix_agreement():
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0])
    
    cm_scratch = met.compute_confusion_matrix(y_true, y_pred)
    cm_sk = confusion_matrix(y_true, y_pred)
    np.testing.assert_array_equal(cm_scratch, cm_sk)


def test_metrics_values():
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0])
    
    m = met.compute_metrics(y_true, y_pred)
    
    assert np.isclose(m["precision"], precision_score(y_true, y_pred))
    assert np.isclose(m["recall"], recall_score(y_true, y_pred))
    assert np.isclose(m["f1"], f1_score(y_true, y_pred))
    assert np.isclose(m["mcc"], matthews_corrcoef(y_true, y_pred))


def test_roc_auc_trapezoid():
    y_true = np.array([0, 0, 1, 1])
    y_scores = np.array([0.1, 0.4, 0.35, 0.8])
    
    fpr, tpr, _ = met.compute_roc_curve(y_true, y_scores)
    auc_scratch = met.compute_auc(fpr, tpr)
    auc_sk = roc_auc_score(y_true, y_scores)
    
    assert np.isclose(auc_scratch, auc_sk, atol=1e-7)


def test_cost_sensitive_threshold():
    # FN is 10x more expensive than FP ($100 vs $10)
    y_true = np.array([1, 1, 1, 0, 0, 0])
    y_scores = np.array([0.9, 0.4, 0.35, 0.2, 0.15, 0.1])
    
    best_tau, min_cost = met.find_optimal_cost_threshold(y_true, y_scores, cost_fp=10.0, cost_fn=100.0)
    # To catch the FN at score 0.35, tau must be <= 0.35
    assert best_tau <= 0.35
    assert min_cost == 0.0 # Catches all 3 positives with 0 false positives
