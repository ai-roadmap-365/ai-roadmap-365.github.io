import pytest
import numpy as np
from fairness_lib import (
    compute_fairness_metrics,
    compute_reweighing_weights,
    calibrate_group_thresholds_for_equal_opportunity
)

def test_compute_fairness_metrics():
    # Group 0: 50 samples, Group 1: 50 samples
    y_true = np.array([1]*25 + [0]*25 + [1]*25 + [0]*25)
    sens = np.array([0]*50 + [1]*50)
    # Model predicts Group 1 positive much more frequently (bias)
    y_pred = np.array([1]*10 + [0]*40 + [1]*20 + [0]*30)
    
    res = compute_fairness_metrics(y_true, y_pred, sens)
    assert res["group_0"]["selection_rate"] == 0.20
    assert res["group_1"]["selection_rate"] == 0.40
    assert res["demographic_parity_difference"] == pytest.approx(0.20)
    assert res["disparate_impact_ratio"] == pytest.approx(0.50)
    assert res["equal_opportunity_difference"] > 0.0

def test_reweighing_weights():
    y_true = np.array([1, 1, 0, 0, 1, 0, 0, 0])
    sens = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    weights = compute_reweighing_weights(y_true, sens)
    
    assert len(weights) == len(y_true)
    assert np.all(weights > 0.0)
    # Under-represented group (A=1, Y=1) should receive higher weight than (A=0, Y=1)
    assert weights[4] > weights[0]

def test_group_threshold_calibration():
    rng = np.random.default_rng(42)
    # Simulate uncalibrated probabilities where Group 1 scores systematically higher
    sens = np.array([0]*100 + [1]*100)
    y_true = np.array([1]*50 + [0]*50 + [1]*50 + [0]*50)
    y_prob = np.concatenate([rng.uniform(0.1, 0.7, 100), rng.uniform(0.3, 0.9, 100)])
    
    thresh = calibrate_group_thresholds_for_equal_opportunity(y_true, y_prob, sens, target_tpr=0.80)
    assert "threshold_group_0" in thresh
    assert "threshold_group_1" in thresh
    assert 0.0 < thresh["threshold_group_0"] < 1.0
    assert 0.0 < thresh["threshold_group_1"] < 1.0
