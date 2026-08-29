import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

def compute_baseline_benchmarks(X_train, y_train, X_test, y_test, candidate_model=None):
    """
    Evaluate candidate model against the strict 3-tier baseline hierarchy:
    1. Trivial Majority Baseline (DummyClassifier)
    2. Linear Baseline (LogisticRegression)
    3. Candidate Model (e.g. Tree Ensemble)
    """
    # 1. Dummy Majority
    dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    dummy_pred = dummy.predict(X_test)
    dummy_acc = float(accuracy_score(y_test, dummy_pred))
    dummy_f1 = float(f1_score(y_test, dummy_pred, zero_division=0))
    
    # 2. Linear Baseline
    linear = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    linear_pred = linear.predict(X_test)
    linear_acc = float(accuracy_score(y_test, linear_pred))
    linear_f1 = float(f1_score(y_test, linear_pred, zero_division=0))
    
    results = {
        "dummy_majority": {"accuracy": dummy_acc, "f1_score": dummy_f1},
        "linear_baseline": {"accuracy": linear_acc, "f1_score": linear_f1}
    }
    
    if candidate_model is not None:
        cand_pred = candidate_model.predict(X_test)
        cand_acc = float(accuracy_score(y_test, cand_pred))
        cand_f1 = float(f1_score(y_test, cand_pred, zero_division=0))
        results["candidate_model"] = {
            "accuracy": cand_acc,
            "f1_score": cand_f1,
            "lift_over_dummy": float(cand_acc - dummy_acc),
            "lift_over_linear": float(cand_acc - linear_acc),
            "beats_all_baselines": (cand_acc > linear_acc) and (cand_acc > dummy_acc)
        }
        
    return results

def compute_error_slices(df_test, y_true_col, y_pred_col, slice_cols):
    """
    Compute slice-specific error rates across demographic and operational segments.
    """
    df = df_test.copy()
    df["is_error"] = (df[y_true_col] != df[y_pred_col]).astype(int)
    
    slice_reports = {}
    
    for col in slice_cols:
        grouped = df.groupby(col).agg(
            total_count=("is_error", "count"),
            error_count=("is_error", "sum"),
            error_rate=("is_error", "mean")
        ).reset_index()
        
        slice_reports[col] = grouped.to_dict(orient="records")
        
    return slice_reports

def compute_error_reduction_ceiling(error_tag_counts, total_sample_count, baseline_error_count):
    """
    Compute Andrew Ng's Error Reduction Ceiling:
    What is the maximum potential accuracy improvement if an error category is 100% fixed?
    """
    ceilings = []
    
    for tag, count in error_tag_counts.items():
        pct_of_errors = count / max(baseline_error_count, 1)
        max_accuracy_gain = count / max(total_sample_count, 1)
        
        ceilings.append({
            "error_category": tag,
            "error_count": int(count),
            "pct_of_total_errors": float(pct_of_errors),
            "max_potential_accuracy_gain": float(max_accuracy_gain)
        })
        
    # Sort descending by impact
    ceilings.sort(key=lambda x: x["max_potential_accuracy_gain"], reverse=True)
    return ceilings
