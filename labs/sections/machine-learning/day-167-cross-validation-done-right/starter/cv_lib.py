"""
Cross-Validation starter library.
"""
import numpy as np
from typing import Generator


def stratified_kfold_scratch(y: np.ndarray, n_splits: int = 5, shuffle: bool = True, random_state: int = 42) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Generate train/val indices preserving exact class ratios per fold."""
    raise NotImplementedError("Implement stratified_kfold_scratch")


def group_kfold_scratch(groups: np.ndarray, n_splits: int = 3) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Generate train/val indices ensuring groups are completely disjoint across folds."""
    raise NotImplementedError("Implement group_kfold_scratch")


def time_series_split_scratch(n_samples: int, n_splits: int = 4) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Generate expanding-window temporal train/val indices."""
    raise NotImplementedError("Implement time_series_split_scratch")


def nested_cross_validation_score(estimator_cls, param_grid: dict, X: np.ndarray, y: np.ndarray, outer_k: int = 3, inner_k: int = 3) -> float:
    """Compute unbiased generalization score using double (nested) cross-validation."""
    raise NotImplementedError("Implement nested_cross_validation_score")
