"""
Hyperparameter Tuning reference library implementation.
"""
import itertools
import numpy as np
from scipy.stats import norm
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score


def compute_expected_improvement(
    mu: np.ndarray, sigma: np.ndarray, best_y: float, xi: float = 0.01
) -> np.ndarray:
    """
    Analytical Expected Improvement for maximization:
    EI(x) = (mu(x) - best_y - xi) * Phi(Z) + sigma(x) * phi(Z)
    where Z = (mu(x) - best_y - xi) / sigma(x)
    """
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    
    ei = np.zeros_like(mu)
    valid = sigma > 1e-9
    
    improvement = mu[valid] - best_y - xi
    Z = improvement / sigma[valid]
    
    ei[valid] = improvement * norm.cdf(Z) + sigma[valid] * norm.pdf(Z)
    return ei


def _kfold_cv_score(estimator, X: np.ndarray, y: np.ndarray, cv: int = 3) -> float:
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    scores = []
    for train_idx, val_idx in skf.split(X, y):
        X_tr, y_tr = X[train_idx], y[train_idx]
        X_va, y_val = X[val_idx], y[val_idx]
        estimator.fit(X_tr, y_tr)
        preds = estimator.predict(X_va)
        scores.append(accuracy_score(y_val, preds))
    return float(np.mean(scores))


def grid_search_scratch(
    estimator_cls, param_grid: dict, X: np.ndarray, y: np.ndarray, cv: int = 3
) -> tuple[dict, float]:
    """
    Exhaustively evaluate all Cartesian product combinations of parameter values.
    Returns (best_params, best_mean_cv_score).
    """
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = [dict(zip(keys, prod)) for prod in itertools.product(*values)]
    
    best_score = -float("inf")
    best_params = {}
    
    for params in combinations:
        model = estimator_cls(**params)
        score = _kfold_cv_score(model, X, y, cv=cv)
        if score > best_score:
            best_score = score
            best_params = params
            
    return best_params, best_score


def random_search_scratch(
    estimator_cls, param_dists: dict, n_iter: int, X: np.ndarray, y: np.ndarray, cv: int = 3, random_state: int = 42
) -> tuple[dict, float]:
    """
    Evaluate n_iter randomly sampled configurations.
    Returns (best_params, best_mean_cv_score).
    """
    rng = np.random.default_rng(random_state)
    best_score = -float("inf")
    best_params = {}
    
    for _ in range(n_iter):
        sampled_params = {}
        for key, dist in param_dists.items():
            if isinstance(dist, list):
                sampled_params[key] = rng.choice(dist)
            elif hasattr(dist, "rvs"):
                sampled_params[key] = dist.rvs(random_state=rng)
            else:
                sampled_params[key] = dist
                
        model = estimator_cls(**sampled_params)
        score = _kfold_cv_score(model, X, y, cv=cv)
        if score > best_score:
            best_score = score
            best_params = sampled_params
            
    return best_params, best_score
