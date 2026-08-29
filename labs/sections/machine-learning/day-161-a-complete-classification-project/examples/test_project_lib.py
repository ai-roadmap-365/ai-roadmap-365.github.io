"""
Tests for reference Complete Classification Project implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
import project_lib as prj


def test_complete_pipeline_flow():
    cancer = load_breast_cancer()
    X, y = cancer.data, cancer.target
    
    # 3-way split: 60% Train, 20% Val, 20% Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, stratify=y_train_val, random_state=42)
    
    pipe = prj.ClassificationProjectPipeline(random_state=42)
    cv_scores = pipe.fit_and_select(X_train, y_train, cv_folds=5)
    
    assert len(cv_scores) == 4
    assert pipe.best_model is not None
    
    # Calibrate threshold on Val
    tau = pipe.calibrate_threshold(X_val, y_val, cost_fp=10.0, cost_fn=100.0)
    assert 0.0 < tau < 1.0
    
    # Single Test Evaluation
    metrics = pipe.evaluate_test(X_test, y_test)
    assert metrics["f1"] >= 0.90
    assert metrics["roc_auc"] >= 0.95
    
    # Assert second test evaluation raises error
    with pytest.raises(RuntimeError):
        pipe.evaluate_test(X_test, y_test)
