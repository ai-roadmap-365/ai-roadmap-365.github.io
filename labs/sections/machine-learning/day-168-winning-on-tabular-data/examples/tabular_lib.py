"""
Winning on Tabular Data reference library implementation.
"""
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.base import clone


def generate_out_of_fold_predictions(models: list, X: np.ndarray, y: np.ndarray, cv: int = 5, random_state: int = 42) -> np.ndarray:
    """
    Generate an (N, M) matrix of out-of-fold positive-class probability predictions.
    N = number of samples, M = number of base models.
    """
    X = np.asarray(X)
    y = np.asarray(y)
    n_samples = len(y)
    n_models = len(models)
    
    oof_preds = np.zeros((n_samples, n_models), dtype=float)
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    
    for m_idx, base_model in enumerate(models):
        for train_idx, val_idx in skf.split(X, y):
            clf = clone(base_model)
            clf.fit(X[train_idx], y[train_idx])
            if hasattr(clf, "predict_proba"):
                probs = clf.predict_proba(X[val_idx])[:, 1]
            else:
                probs = clf.predict(X[val_idx])
            oof_preds[val_idx, m_idx] = probs
            
    return oof_preds


def fit_stacking_ensemble(level0_models: list, meta_learner, X: np.ndarray, y: np.ndarray, cv: int = 5) -> tuple[list, object]:
    """
    1. Generate OOF matrix Z (N, M) from training data.
    2. Fit meta-learner on (Z, y).
    3. Fit each base model on 100% of X, y for test-time inference.
    """
    X = np.asarray(X)
    y = np.asarray(y)
    
    # 1. OOF Matrix
    Z = generate_out_of_fold_predictions(level0_models, X, y, cv=cv)
    
    # 2. Fit Meta-Learner
    meta = clone(meta_learner)
    meta.fit(Z, y)
    
    # 3. Fit base models on all training data
    fitted_base_models = []
    for model in level0_models:
        clf = clone(model)
        clf.fit(X, y)
        fitted_base_models.append(clf)
        
    return fitted_base_models, meta


def predict_stacking_ensemble(fitted_level0: list, meta_learner, X_test: np.ndarray) -> np.ndarray:
    """
    At test time:
    1. Predict test probabilities from each base model to form Z_test (N_test, M).
    2. Pass Z_test to meta-learner to get final ensemble predictions.
    """
    X_test = np.asarray(X_test)
    n_test = len(X_test)
    n_models = len(fitted_level0)
    
    Z_test = np.zeros((n_test, n_models), dtype=float)
    for m_idx, model in enumerate(fitted_level0):
        if hasattr(model, "predict_proba"):
            Z_test[:, m_idx] = model.predict_proba(X_test)[:, 1]
        else:
            Z_test[:, m_idx] = model.predict(X_test)
            
    return meta_learner.predict(Z_test)


def compute_permutation_importance(model, X_val: np.ndarray, y_val: np.ndarray, n_repeats: int = 5, random_state: int = 42) -> np.ndarray:
    """
    Compute mean accuracy drop for each feature when randomly shuffled.
    Higher value = more important feature.
    """
    X_val = np.asarray(X_val)
    y_val = np.asarray(y_val)
    rng = np.random.default_rng(random_state)
    
    base_preds = model.predict(X_val)
    baseline_score = accuracy_score(y_val, base_preds)
    
    n_features = X_val.shape[1]
    importances = np.zeros(n_features)
    
    for f in range(n_features):
        drops = []
        for _ in range(n_repeats):
            X_shuffled = X_val.copy()
            shuffled_col = X_shuffled[:, f].copy()
            rng.shuffle(shuffled_col)
            X_shuffled[:, f] = shuffled_col
            
            shuf_preds = model.predict(X_shuffled)
            shuf_score = accuracy_score(y_val, shuf_preds)
            drops.append(baseline_score - shuf_score)
            
        importances[f] = np.mean(drops)
        
    return importances
