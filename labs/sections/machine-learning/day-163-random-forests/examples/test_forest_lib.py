"""
Tests for reference Random Forest implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer, make_classification
from sklearn.ensemble import RandomForestClassifier
import forest_lib as forest


def test_bootstrap_properties():
    N = 1000
    X = np.zeros((N, 2))
    y = np.zeros(N)
    rng = np.random.default_rng(42)
    
    _, _, oob_idx = forest.bootstrap_sample(X, y, rng)
    oob_fraction = len(oob_idx) / N
    
    # Mathematical asymptotic OOB expectation: 1/e ~ 0.3678
    assert np.isclose(oob_fraction, 1.0 / np.e, atol=0.04)


def test_random_forest_classification_accuracy():
    X, y = make_classification(
        n_samples=200, n_features=10, n_informative=5, n_classes=2, random_state=42
    )
    
    rf_scratch = forest.RandomForestClassifierScratch(n_estimators=20, max_depth=5, random_state=42)
    rf_scratch.fit(X, y)
    preds = rf_scratch.predict(X)
    acc = np.mean(preds == y)
    
    assert acc >= 0.90
    assert rf_scratch.oob_score_ >= 0.80


def test_breast_cancer_benchmark():
    cancer = load_breast_cancer()
    X, y = cancer.data, cancer.target
    
    rf_scratch = forest.RandomForestClassifierScratch(n_estimators=25, max_depth=5, random_state=42)
    rf_scratch.fit(X, y)
    scratch_acc = np.mean(rf_scratch.predict(X) == y)
    
    rf_sk = RandomForestClassifier(n_estimators=25, max_depth=5, random_state=42, oob_score=True)
    rf_sk.fit(X, y)
    sk_acc = rf_sk.score(X, y)
    
    assert scratch_acc >= 0.95
    assert sk_acc >= 0.95
    assert abs(scratch_acc - sk_acc) < 0.05
