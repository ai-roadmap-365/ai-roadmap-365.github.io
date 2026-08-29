"""
Tests for reference features beat algorithms benchmark.
"""
import pytest
import numpy as np
import features_beat_algorithms_lib as fba


def test_engineer_domain_representation_shape():
    # 4 raw columns -> 7 engineered columns
    X_raw = np.array([
        [1.75, 70.0, 30.0, 14.0],
        [1.80, 85.0, 45.0, 22.0]
    ])
    X_eng = fba.engineer_domain_representation(X_raw)
    assert X_eng.shape == (2, 7)
    
    # Verify BMI = 70 / (1.75^2) = 22.8571
    assert np.isclose(X_eng[0, 3], 70.0 / (1.75**2), atol=1e-4)


def test_benchmark_engineered_superiority():
    rng = np.random.default_rng(42)
    n_samples = 600
    
    # Physical measurements: Height (1.5 - 2.0m), Weight (50 - 120kg), Age (20 - 70), Hour (0 - 24)
    h = rng.uniform(1.5, 2.0, size=n_samples)
    w = rng.uniform(50.0, 120.0, size=n_samples)
    age = rng.uniform(20.0, 70.0, size=n_samples)
    hr = rng.uniform(0.0, 24.0, size=n_samples)
    
    X_raw = np.column_stack([h, w, age, hr])
    
    # Ground truth health score heavily depends on BMI = w / h^2 and circadian peak at 14:00
    true_bmi = w / (h ** 2)
    circadian = 5.0 * np.cos(2.0 * np.pi * (hr - 14.0) / 24.0)
    y = 50.0 + 2.5 * true_bmi + 0.5 * age + circadian + rng.normal(0, 0.5, size=n_samples)
    
    # Train / Test split (80% / 20%)
    X_tr, X_te = X_raw[:480], X_raw[480:]
    y_tr, y_te = y[:480], y[480:]
    
    results = fba.benchmark_raw_vs_engineered(X_tr, y_tr, X_te, y_te)
    
    # Engineered representation must substantially beat raw representation (R2 delta > 0.40)
    assert results["engineered_r2"] > 0.90
    assert results["raw_r2"] < results["engineered_r2"]
    assert results["r2_delta"] > 0.40
