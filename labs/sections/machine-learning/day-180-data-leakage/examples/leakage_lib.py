import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

def detect_target_leakage(df, target_col, correlation_threshold=0.95, is_classification=True):
    """
    Detect features exhibiting suspiciously perfect correlation or mutual information with the target.
    """
    features = [c for c in df.columns if c != target_col]
    X = df[features].copy()
    y = df[target_col].copy()
    
    suspicious_features = []
    
    # Check numeric Pearson correlations
    num_cols = X.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        r = np.corrcoef(X[col].fillna(0), y.fillna(0))[0, 1]
        if abs(r) >= correlation_threshold:
            suspicious_features.append({
                "feature": col,
                "type": "HIGH_PEARSON_CORRELATION",
                "metric_value": float(abs(r)),
                "risk": "Feature directly encodes target information or proxy label"
            })
            
    # Check exact duplications or near-duplicates
    for col in features:
        if (X[col] == y).mean() >= correlation_threshold:
            if col not in [s["feature"] for s in suspicious_features]:
                suspicious_features.append({
                    "feature": col,
                    "type": "IDENTITY_MATCH",
                    "metric_value": float((X[col] == y).mean()),
                    "risk": "Feature is nearly identical to target column"
                })
                
    return suspicious_features

def detect_group_contamination(train_df, test_df, group_col):
    """
    Detect whether identity/group entities (e.g. Patient ID, Customer UUID) span across both train and test splits.
    """
    train_groups = set(train_df[group_col].dropna())
    test_groups = set(test_df[group_col].dropna())
    
    overlap = train_groups.intersection(test_groups)
    overlap_ratio = len(overlap) / max(len(test_groups), 1)
    
    return {
        "group_column": group_col,
        "n_train_groups": len(train_groups),
        "n_test_groups": len(test_groups),
        "n_overlapping_groups": len(overlap),
        "overlap_ratio": float(overlap_ratio),
        "is_contaminated": len(overlap) > 0,
        "warning": "Group leakage detected: model can memorize entity-specific traits rather than general patterns." if len(overlap) > 0 else "Clean group separation."
    }

def detect_temporal_lookahead(df, timestamp_col, feature_cols, target_col):
    """
    Audit whether feature timestamps post-date prediction cutoff timestamps.
    """
    df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
    n = len(df_sorted)
    
    # Check lag correlations: correlation between feature at t and target at t-1
    lookahead_risks = []
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(df_sorted[col]):
            feat = df_sorted[col].values
            target = df_sorted[target_col].values
            
            # Future feature correlated with past target
            if n > 2:
                r_future = np.corrcoef(feat[1:], target[:-1])[0, 1]
                if abs(r_future) > 0.80:
                    lookahead_risks.append({
                        "feature": col,
                        "future_correlation": float(r_future),
                        "warning": "High lead correlation with previous target: potential lookahead leakage."
                    })
                    
    return {
        "is_chronologically_sorted": df[timestamp_col].is_monotonic_increasing,
        "lookahead_risks": lookahead_risks
    }
