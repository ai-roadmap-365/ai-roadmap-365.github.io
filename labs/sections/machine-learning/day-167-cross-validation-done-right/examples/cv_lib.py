"""
Cross-Validation reference library implementation.
"""
import itertools
import numpy as np
from typing import Generator
from sklearn.metrics import accuracy_score


def stratified_kfold_scratch(
    y: np.ndarray, n_splits: int = 5, shuffle: bool = True, random_state: int = 42
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generate stratified folds where each fold preserves the empirical class ratio.
    """
    y = np.asarray(y)
    n_samples = len(y)
    classes, counts = np.unique(y, return_counts=True)
    
    rng = np.random.default_rng(random_state)
    class_indices = {}
    for c in classes:
        idx = np.where(y == c)[0]
        if shuffle:
            rng.shuffle(idx)
        class_indices[c] = idx
        
    # Split each class indices into n_splits chunks
    folds = [[] for _ in range(n_splits)]
    for c in classes:
        splits = np.array_split(class_indices[c], n_splits)
        for fold_idx in range(n_splits):
            folds[fold_idx].extend(splits[fold_idx])
            
    for val_fold_idx in range(n_splits):
        val_idx = np.array(folds[val_fold_idx], dtype=int)
        train_idx = np.setdiff1d(np.arange(n_samples), val_idx)
        yield train_idx, val_idx


def group_kfold_scratch(
    groups: np.ndarray, n_splits: int = 3
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generate disjoint group folds such that no group appears in both train and validation.
    """
    groups = np.asarray(groups)
    n_samples = len(groups)
    unique_groups = np.unique(groups)
    n_groups = len(unique_groups)
    
    if n_splits > n_groups:
        raise ValueError(f"Cannot have n_splits={n_splits} greater than unique groups={n_groups}")
        
    group_splits = np.array_split(unique_groups, n_splits)
    
    for split in group_splits:
        val_mask = np.isin(groups, split)
        val_idx = np.where(val_mask)[0]
        train_idx = np.where(~val_mask)[0]
        yield train_idx, val_idx


def time_series_split_scratch(
    n_samples: int, n_splits: int = 4, min_train_size: int = None
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """
    Generate expanding-window temporal folds where training strictly precedes validation.
    """
    test_size = n_samples // (n_splits + 1)
    if min_train_size is None:
        min_train_size = n_samples - test_size * n_splits
        
    for i in range(n_splits):
        train_end = min_train_size + i * test_size
        val_end = train_end + test_size
        train_idx = np.arange(0, train_end)
        val_idx = np.arange(train_end, val_end)
        yield train_idx, val_idx


def nested_cross_validation_score(
    estimator_cls, param_grid: dict, X: np.ndarray, y: np.ndarray, outer_k: int = 3, inner_k: int = 3
) -> float:
    """
    Unbiased double cross-validation:
    Outer loop measures true generalization; Inner loop selects optimal hyperparameters.
    """
    X = np.asarray(X)
    y = np.asarray(y)
    
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    combinations = [dict(zip(keys, prod)) for prod in itertools.product(*values)]
    
    outer_scores = []
    
    # Outer Loop: Generalization evaluation
    for outer_tr, outer_va in stratified_kfold_scratch(y, n_splits=outer_k, shuffle=True, random_state=42):
        X_out_tr, y_out_tr = X[outer_tr], y[outer_tr]
        X_out_va, y_out_va = X[outer_va], y[outer_va]
        
        best_inner_score = -float("inf")
        best_params = combinations[0]
        
        # Inner Loop: Hyperparameter selection on outer training data only!
        for params in combinations:
            inner_scores = []
            for inner_tr, inner_va in stratified_kfold_scratch(y_out_tr, n_splits=inner_k, shuffle=True, random_state=100):
                model = estimator_cls(**params)
                model.fit(X_out_tr[inner_tr], y_out_tr[inner_tr])
                inner_preds = model.predict(X_out_tr[inner_va])
                inner_scores.append(accuracy_score(y_out_tr[inner_va], inner_preds))
                
            mean_inner = np.mean(inner_scores)
            if mean_inner > best_inner_score:
                best_inner_score = mean_inner
                best_params = params
                
        # Fit optimal parameters on full outer training split and score on clean outer validation fold
        final_model = estimator_cls(**best_params)
        final_model.fit(X_out_tr, y_out_tr)
        outer_pred = final_model.predict(X_out_va)
        outer_scores.append(accuracy_score(y_out_va, outer_pred))
        
    return float(np.mean(outer_scores))
