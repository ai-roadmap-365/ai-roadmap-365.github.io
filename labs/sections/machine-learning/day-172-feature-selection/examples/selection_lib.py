"""
Feature Selection reference library implementation.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge


def filter_by_variance_threshold(X: np.ndarray, threshold: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """
    Remove features whose empirical variance is strictly <= threshold.
    Returns (X_selected, boolean_support_mask).
    """
    X = np.asarray(X, dtype=float)
    variances = np.var(X, axis=0)
    support = variances > threshold
    return X[:, support], support


def compute_mutual_information_scores(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute Pearson correlation magnitude as a fast univariate dependency proxy:
    score_j = |Corr(x_j, y)|
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n_samples, n_features = X.shape
    
    y_centered = y - np.mean(y)
    y_norm = np.linalg.norm(y_centered)
    
    scores = np.zeros(n_features)
    for j in range(n_features):
        x_col = X[:, j]
        x_centered = x_col - np.mean(x_col)
        x_norm = np.linalg.norm(x_centered)
        if x_norm > 1e-9 and y_norm > 1e-9:
            corr = np.abs(np.dot(x_centered, y_centered) / (x_norm * y_norm))
            scores[j] = corr
        else:
            scores[j] = 0.0
            
    return scores


def recursive_feature_elimination_scratch(
    estimator, X: np.ndarray, y: np.ndarray, n_features_to_select: int = 5
) -> np.ndarray:
    """
    Recursive Feature Elimination (RFE):
    Iteratively fits estimator, finds feature with smallest absolute weight |w_j|,
    prunes it, and repeats until n_features_to_select remain.
    Returns boolean support mask of selected features.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n_samples, n_features = X.shape
    
    active_indices = list(range(n_features))
    
    while len(active_indices) > n_features_to_select:
        X_sub = X[:, active_indices]
        estimator.fit(X_sub, y)
        
        if hasattr(estimator, "coef_"):
            coef = estimator.coef_
            if coef.ndim > 1:
                importances = np.mean(np.abs(coef), axis=0)
            else:
                importances = np.abs(coef)
        elif hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
        else:
            raise ValueError("Estimator must have coef_ or feature_importances_")
            
        # Prune the feature with lowest importance
        min_idx = np.argmin(importances)
        active_indices.pop(min_idx)
        
    support = np.zeros(n_features, dtype=bool)
    support[active_indices] = True
    return support


def boruta_shadow_filter(X: np.ndarray, y: np.ndarray, n_trials: int = 20, random_state: int = 42) -> np.ndarray:
    """
    Simplified Boruta shadow feature test using Ridge regression coefficients:
    Compares feature importances against randomly permuted shadow copies.
    """
    rng = np.random.default_rng(random_state)
    X = np.asarray(X, dtype=float)
    n_samples, n_features = X.shape
    
    hits = np.zeros(n_features, dtype=int)
    
    for _ in range(n_trials):
        # Create shadow features by permuting columns independently
        X_shadow = np.zeros_like(X)
        for j in range(n_features):
            X_shadow[:, j] = rng.permutation(X[:, j])
            
        X_extended = np.hstack([X, X_shadow])
        model = Ridge(alpha=1.0).fit(X_extended, y)
        coefs = np.abs(model.coef_)
        
        orig_coefs = coefs[:n_features]
        shadow_max = np.max(coefs[n_features:])
        
        # Real feature beats maximum shadow feature
        hits += (orig_coefs > shadow_max).astype(int)
        
    # Return features that beat shadow features in >= 50% of trials
    return hits >= (n_trials // 2)
