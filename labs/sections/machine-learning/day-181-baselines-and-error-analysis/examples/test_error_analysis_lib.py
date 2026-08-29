import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from error_analysis_lib import (
    compute_baseline_benchmarks,
    compute_error_slices,
    compute_error_reduction_ceiling
)

def test_compute_baseline_benchmarks():
    rng = np.random.default_rng(42)
    X_train = rng.normal(size=(200, 3))
    y_train = (X_train[:, 0] + X_train[:, 1] > 0).astype(int)
    X_test = rng.normal(size=(50, 3))
    y_test = (X_test[:, 0] + X_test[:, 1] > 0).astype(int)
    
    rf = RandomForestClassifier(n_estimators=10, random_state=42).fit(X_train, y_train)
    bench = compute_baseline_benchmarks(X_train, y_train, X_test, y_test, candidate_model=rf)
    
    assert "dummy_majority" in bench
    assert "linear_baseline" in bench
    assert "candidate_model" in bench
    assert bench["candidate_model"]["accuracy"] >= bench["dummy_majority"]["accuracy"]

def test_compute_error_slices():
    df = pd.DataFrame({
        "device_os": ["iOS", "iOS", "Android", "Android", "Android"],
        "user_tier": ["Free", "VIP", "Free", "VIP", "Free"],
        "y_true": [1, 1, 0, 1, 0],
        "y_pred": [1, 0, 0, 0, 1] # Errors on rows 1 (iOS/VIP), 3 (Android/VIP), 4 (Android/Free)
    })
    
    slices = compute_error_slices(df, "y_true", "y_pred", ["device_os", "user_tier"])
    assert "device_os" in slices
    assert "user_tier" in slices
    # VIP error rate is 2/2 = 1.0
    vip_report = [s for s in slices["user_tier"] if s["user_tier"] == "VIP"][0]
    assert vip_report["error_rate"] == 1.0

def test_error_reduction_ceiling():
    tags = {
        "Label Noise": 40,
        "Audio Background Glitch": 30,
        "Rare Dialect": 10
    }
    ceilings = compute_error_reduction_ceiling(tags, total_sample_count=1000, baseline_error_count=80)
    assert len(ceilings) == 3
    assert ceilings[0]["error_category"] == "Label Noise"
    assert ceilings[0]["pct_of_total_errors"] == 0.50 # 40 / 80
    assert ceilings[0]["max_potential_accuracy_gain"] == 0.04 # 40 / 1000
