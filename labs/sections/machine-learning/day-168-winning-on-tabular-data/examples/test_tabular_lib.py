"""
Tests for reference tabular library implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import tabular_lib as tab


def test_oof_predictions_matrix_shape():
    cancer = load_breast_cancer()
    X, y = cancer.data[:120], cancer.target[:120]
    
    models = [
        LogisticRegression(max_iter=500, random_state=42),
        RandomForestClassifier(n_estimators=20, max_depth=3, random_state=42)
    ]
    
    oof = tab.generate_out_of_fold_predictions(models, X, y, cv=3)
    assert oof.shape == (120, 2)
    assert np.all((oof >= 0.0) & (oof <= 1.0))


def test_stacking_ensemble_end_to_end():
    cancer = load_breast_cancer()
    X_tr, y_tr = cancer.data[:400], cancer.target[:400]
    X_te, y_te = cancer.data[400:], cancer.target[400:]
    
    base_models = [
        LogisticRegression(max_iter=1000, random_state=42),
        RandomForestClassifier(n_estimators=30, max_depth=4, random_state=42),
        GradientBoostingClassifier(n_estimators=30, max_depth=3, random_state=42)
    ]
    meta = LogisticRegression(random_state=42)
    
    fitted_base, fitted_meta = tab.fit_stacking_ensemble(base_models, meta, X_tr, y_tr, cv=3)
    preds = tab.predict_stacking_ensemble(fitted_base, fitted_meta, X_te)
    
    acc = accuracy_score(y_te, preds)
    assert acc >= 0.90


def test_permutation_importance_signal_detection():
    # Construct synthetic data where feature 0 is 100% predictive, feature 1 is pure noise
    rng = np.random.default_rng(42)
    y = rng.choice([0, 1], size=100)
    X = np.zeros((100, 2))
    X[:, 0] = y * 5.0 + rng.normal(0, 0.1, size=100) # Informative
    X[:, 1] = rng.normal(0, 1.0, size=100)           # Noise
    
    clf = RandomForestClassifier(n_estimators=20, random_state=42).fit(X, y)
    imp = tab.compute_permutation_importance(clf, X, y, n_repeats=5)
    
    # Feature 0 importance must be significantly higher than Feature 1
    assert imp[0] > 0.30
    assert imp[1] < 0.05
