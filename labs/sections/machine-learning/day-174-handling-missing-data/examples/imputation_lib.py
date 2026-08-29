"""
Handling Missing Data reference library implementation.
"""
import numpy as np


def compute_nan_euclidean_distance(u: np.ndarray, v: np.ndarray) -> float:
    """
    NaN-Euclidean Distance formula:
    d(u, v) = sqrt( (D_total / D_valid) * sum_{j in valid} (u_j - v_j)^2 )
    If no coordinates overlap, returns infinity.
    """
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    total_dim = len(u)
    
    valid_mask = ~np.isnan(u) & ~np.isnan(v)
    valid_count = np.sum(valid_mask)
    
    if valid_count == 0:
        return float("inf")
        
    diffs_sq = (u[valid_mask] - v[valid_mask]) ** 2
    scaled_sq_sum = (total_dim / valid_count) * np.sum(diffs_sq)
    return float(np.sqrt(scaled_sq_sum))


def generate_missing_indicator(X: np.ndarray) -> np.ndarray:
    """
    Returns boolean matrix of shape (N, D) where True indicates NaN.
    """
    X = np.asarray(X)
    return np.isnan(X)


def knn_imputer_scratch(X: np.ndarray, n_neighbors: int = 3) -> np.ndarray:
    """
    KNN Imputation from scratch:
    For each row with NaNs, finds k nearest neighbors based on NaN-Euclidean distance
    over observed features, and imputes missing coordinates using uniform neighbor mean.
    """
    X = np.asarray(X, dtype=float).copy()
    n_samples, n_features = X.shape
    
    # Precompute column means for extreme fallback
    col_means = np.nanmean(X, axis=0)
    # If a column is entirely NaN, fill with 0.0
    col_means = np.nan_to_num(col_means, nan=0.0)
    
    for i in range(n_samples):
        row = X[i]
        nan_cols = np.where(np.isnan(row))[0]
        if len(nan_cols) == 0:
            continue
            
        # Compute distances to all other samples
        distances = []
        for j in range(n_samples):
            if i == j:
                distances.append((float("inf"), j))
            else:
                dist = compute_nan_euclidean_distance(row, X[j])
                distances.append((dist, j))
                
        distances.sort(key=lambda item: item[0])
        neighbor_indices = [idx for d, idx in distances if not np.isinf(d)][:n_neighbors]
        
        for c in nan_cols:
            vals = [X[nbr, c] for nbr in neighbor_indices if not np.isnan(X[nbr, c])]
            if len(vals) > 0:
                X[i, c] = float(np.mean(vals))
            else:
                X[i, c] = col_means[c]
                
    return X
