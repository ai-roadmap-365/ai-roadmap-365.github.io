import numpy as np
import itertools
from sklearn.base import clone

def compute_permutation_importance(estimator, X, y, metric_fn, n_repeats=5, random_state=42):
    """
    Compute out-of-sample Permutation Feature Importance.
    metric_fn: function(y_true, y_pred) -> score (higher is better)
    """
    rng = np.random.default_rng(random_state)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    
    baseline_pred = estimator.predict(X)
    baseline_score = metric_fn(y, baseline_pred)
    
    n_features = X.shape[1]
    importances = np.zeros((n_features, n_repeats))
    
    for j in range(n_features):
        for r in range(n_repeats):
            X_perm = X.copy()
            perm_indices = rng.permutation(len(X))
            X_perm[:, j] = X_perm[perm_indices, j]
            
            perm_pred = estimator.predict(X_perm)
            perm_score = metric_fn(y, perm_pred)
            importances[j, r] = baseline_score - perm_score
            
    return {
        "importances_mean": np.mean(importances, axis=1).tolist(),
        "importances_std": np.std(importances, axis=1).tolist(),
        "baseline_score": float(baseline_score)
    }

def compute_exact_shapley_values(predict_fn, x_instance, background_data):
    """
    Compute exact Shapley values for an instance across all 2^D feature coalitions.
    predict_fn: function(X) -> 1D array of predictions
    """
    x_instance = np.asarray(x_instance, dtype=float).ravel()
    background_data = np.asarray(background_data, dtype=float)
    d = len(x_instance)
    n_bg = len(background_data)
    
    # Base expected value across background dataset
    base_val = float(np.mean(predict_fn(background_data)))
    
    def evaluate_coalition(subset):
        # Construct synthetic background matrix with features in subset replaced by x_instance
        if len(subset) == 0:
            return base_val
        X_eval = background_data.copy()
        for idx in subset:
            X_eval[:, idx] = x_instance[idx]
        return float(np.mean(predict_fn(X_eval)))
    
    shapley_values = np.zeros(d)
    all_indices = set(range(d))
    
    import math
    for i in range(d):
        other_indices = list(all_indices - {i})
        phi_i = 0.0
        
        # Iterate over all subsets of other indices
        for s_len in range(d):
            subsets = list(itertools.combinations(other_indices, s_len))
            weight = (math.factorial(s_len) * math.factorial(d - s_len - 1)) / math.factorial(d)
            for S in subsets:
                v_with = evaluate_coalition(set(S) | {i})
                v_without = evaluate_coalition(set(S))
                phi_i += weight * (v_with - v_without)
                
        shapley_values[i] = phi_i
        
    instance_pred = float(predict_fn(x_instance[np.newaxis, :])[0])
    
    return {
        "base_value": base_val,
        "instance_prediction": instance_pred,
        "shapley_values": shapley_values.tolist(),
        "efficiency_check_diff": float(abs((base_val + np.sum(shapley_values)) - instance_pred))
    }

def compute_partial_dependence_1d(estimator, X, feature_idx, grid_resolution=20):
    """
    Compute 1D Partial Dependence curve for feature_idx.
    """
    X = np.asarray(X, dtype=float)
    feat_vals = X[:, feature_idx]
    grid = np.linspace(np.min(feat_vals), np.max(feat_vals), grid_resolution)
    
    pdp_values = []
    for val in grid:
        X_pdp = X.copy()
        X_pdp[:, feature_idx] = val
        preds = estimator.predict(X_pdp)
        pdp_values.append(float(np.mean(preds)))
        
    return {
        "grid": grid.tolist(),
        "pdp_values": pdp_values
    }
