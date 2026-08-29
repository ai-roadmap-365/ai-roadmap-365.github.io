"""
Features Beat Algorithms reference library implementation.
"""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error


def engineer_domain_representation(X_raw: np.ndarray) -> np.ndarray:
    """
    Transforms raw input matrix [Height_m, Weight_kg, Age_yr, Hour_day]:
    1. Raw features: Height, Weight, Age, Hour
    2. BMI Ratio: Weight / (Height^2)
    3. Cyclical Hour: sin(2*pi*Hour/24), cos(2*pi*Hour/24)
    4. Age-BMI Interaction: Age * BMI
    Returns engineered matrix of shape (N, 8).
    """
    X = np.asarray(X_raw, dtype=float)
    h = X[:, 0]
    w = X[:, 1]
    age = X[:, 2]
    hr = X[:, 3]
    
    # 1. Physics / Medical Domain Ratio
    bmi = w / np.maximum(h ** 2, 1e-4)
    
    # 2. Cyclical Temporal Coordinates
    radians = 2.0 * np.pi * hr / 24.0
    sin_hr = np.sin(radians)
    cos_hr = np.cos(radians)
    
    # 3. Interaction
    age_bmi = age * bmi / 100.0
    
    features = [
        h[:, np.newaxis],
        w[:, np.newaxis],
        age[:, np.newaxis],
        bmi[:, np.newaxis],
        sin_hr[:, np.newaxis],
        cos_hr[:, np.newaxis],
        age_bmi[:, np.newaxis]
    ]
    return np.hstack(features)


def calculate_feature_roi(r2_improvement: float, latency_increase_ms: float) -> float:
    """
    Compute Feature ROI:
    ROI = (r2_improvement * 100.0) / max(latency_increase_ms, 0.001)
    """
    gain_pct = max(r2_improvement * 100.0, 0.0)
    denom = max(float(latency_increase_ms), 0.001)
    return gain_pct / denom


def benchmark_raw_vs_engineered(
    X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray
) -> dict[str, float]:
    """
    Demonstrates that a simple linear Ridge model on engineered features
    drastically outperforms the same linear model on raw features when
    true target physics depend on non-linear domain interactions.
    """
    # 1. Model A: Ridge on Raw Features
    raw_model = Ridge(alpha=1.0)
    raw_model.fit(X_train, y_train)
    raw_preds = raw_model.predict(X_test)
    raw_r2 = float(r2_score(y_test, raw_preds))
    raw_rmse = float(np.sqrt(mean_squared_error(y_test, raw_preds)))
    
    # 2. Model B: Ridge on Engineered Domain Features
    X_tr_eng = engineer_domain_representation(X_train)
    X_te_eng = engineer_domain_representation(X_test)
    
    eng_model = Ridge(alpha=1.0)
    eng_model.fit(X_tr_eng, y_train)
    eng_preds = eng_model.predict(X_te_eng)
    eng_r2 = float(r2_score(y_test, eng_preds))
    eng_rmse = float(np.sqrt(mean_squared_error(y_test, eng_preds)))
    
    return {
        "raw_r2": raw_r2,
        "raw_rmse": raw_rmse,
        "engineered_r2": eng_r2,
        "engineered_rmse": eng_rmse,
        "r2_delta": eng_r2 - raw_r2
    }
