import pytest
import numpy as np
import pandas as pd
from leakage_lib import (
    detect_target_leakage,
    detect_group_contamination,
    detect_temporal_lookahead
)

def test_detect_target_leakage():
    # Feature 0 is clean, Feature 1 is a direct target leak
    y = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0])
    x0 = np.random.normal(size=10)
    x1_leaky = y.astype(float) + np.random.normal(0, 0.001, size=10) # 0.999 correlation
    
    df = pd.DataFrame({"clean_feat": x0, "leaky_feat": x1_leaky, "target": y})
    leaks = detect_target_leakage(df, "target", correlation_threshold=0.95)
    
    assert len(leaks) >= 1
    assert leaks[0]["feature"] == "leaky_feat"
    assert leaks[0]["metric_value"] >= 0.95

def test_detect_group_contamination():
    # 5 patients in train, 2 shared with test
    train_df = pd.DataFrame({"patient_id": ["P1", "P2", "P3", "P4", "P5"], "val": [1, 2, 3, 4, 5]})
    test_df = pd.DataFrame({"patient_id": ["P4", "P5", "P6", "P7"], "val": [4, 5, 6, 7]})
    
    audit = detect_group_contamination(train_df, test_df, "patient_id")
    assert audit["is_contaminated"] is True
    assert audit["n_overlapping_groups"] == 2
    assert audit["overlap_ratio"] == 0.50

def test_detect_temporal_lookahead():
    dates = pd.date_range("2026-01-01", periods=10, freq="D")
    y = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    # Future feature shifted: feat[t] = y[t] exactly
    df = pd.DataFrame({"date": dates, "leaky_future_sales": y, "sales_target": y})
    
    audit = detect_temporal_lookahead(df, "date", ["leaky_future_sales"], "sales_target")
    assert audit["is_chronologically_sorted"] is True
    assert len(audit["lookahead_risks"]) >= 1
