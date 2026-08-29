"""
Hyperparameter Tuning starter library.
"""
import numpy as np


def compute_expected_improvement(mu: np.ndarray, sigma: np.ndarray, best_y: float, xi: float = 0.01) -> np.ndarray:
    """Compute Expected Improvement (EI) acquisition function values."""
    raise NotImplementedError("Implement compute_expected_improvement")


def grid_search_scratch(estimator_fn, param_grid: dict, X: np.ndarray, y: np.ndarray, cv: int = 3) -> tuple[dict, float]:
    """Exhaustively evaluate all Cartesian product combinations of parameters."""
    raise NotImplementedError("Implement grid_search_scratch")


def random_search_scratch(estimator_fn, param_dists: dict, n_iter: int, X: np.ndarray, y: np.ndarray, cv: int = 3) -> tuple[dict, float]:
    """Evaluate n_iter random combinations sampled from distributions."""
    raise NotImplementedError("Implement random_search_scratch")
