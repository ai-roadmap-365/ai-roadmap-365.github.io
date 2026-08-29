"""
Feature Engineering reference library implementation.
"""
import numpy as np


def encode_cyclical_time(timestamps: np.ndarray, period: float = 24.0) -> tuple[np.ndarray, np.ndarray]:
    """
    Encode periodic timestamps into continuous 2D coordinates:
    sin_feat = sin(2 * pi * t / period)
    cos_feat = cos(2 * pi * t / period)
    Preserves distance continuity across boundary (e.g. 23:59 and 00:01).
    """
    t = np.asarray(timestamps, dtype=float)
    radians = 2.0 * np.pi * t / period
    sin_feat = np.sin(radians)
    cos_feat = np.cos(radians)
    return sin_feat, cos_feat


def compute_polynomial_interactions(X: np.ndarray) -> np.ndarray:
    """
    Generate original features + all pairwise interaction terms x_i * x_j for i <= j.
    """
    X = np.asarray(X, dtype=float)
    n_samples, n_features = X.shape
    
    terms = [X]
    for i in range(n_features):
        for j in range(i, n_features):
            interaction = (X[:, i] * X[:, j])[:, np.newaxis]
            terms.append(interaction)
            
    return np.hstack(terms)


def compute_group_aggregations(
    groups_train: np.ndarray, values_train: np.ndarray, groups_test: np.ndarray
) -> np.ndarray:
    """
    Compute training group statistics (mean, std) and map to test data.
    Unseen test groups fallback to global training statistics.
    Returns array of shape (N_test, 2) [group_mean, group_std].
    """
    groups_tr = np.asarray(groups_train)
    vals_tr = np.asarray(values_train, dtype=float)
    groups_te = np.asarray(groups_test)
    
    global_mean = float(np.mean(vals_tr))
    global_std = float(np.std(vals_tr))
    if global_std < 1e-9:
        global_std = 1.0
        
    unique_groups = np.unique(groups_tr)
    group_stats = {}
    for g in unique_groups:
        mask = groups_tr == g
        g_vals = vals_tr[mask]
        g_mean = float(np.mean(g_vals))
        g_std = float(np.std(g_vals)) if len(g_vals) > 1 else global_std
        if g_std < 1e-9:
            g_std = 1.0
        group_stats[g] = (g_mean, g_std)
        
    out = np.zeros((len(groups_te), 2), dtype=float)
    for i, g in enumerate(groups_te):
        if g in group_stats:
            out[i, 0], out[i, 1] = group_stats[g]
        else:
            out[i, 0], out[i, 1] = global_mean, global_std
            
    return out
