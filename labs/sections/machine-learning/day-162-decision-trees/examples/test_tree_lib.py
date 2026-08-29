"""
Tests for reference Decision Tree implementation.
"""
import pytest
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import tree_lib as tree


def test_gini_impurity_exact_values():
    # Pure: G = 0.0
    assert tree.compute_gini(np.array([0, 0, 0, 0])) == 0.0
    # 50/50 binary: G = 1 - (0.5^2 + 0.5^2) = 0.50
    assert tree.compute_gini(np.array([0, 1])) == 0.50
    # 3-class equal: G = 1 - 3*(1/3)^2 = 1 - 1/3 = 2/3 = 0.6666...
    assert np.isclose(tree.compute_gini(np.array([0, 1, 2])), 2.0 / 3.0)


def test_entropy_exact_values():
    # Pure: H = 0.0
    assert tree.compute_entropy(np.array([1, 1, 1])) == 0.0
    # 50/50 binary: H = 1.0 bit
    assert np.isclose(tree.compute_entropy(np.array([0, 1])), 1.0)


def test_find_best_split_linear_separation():
    # Feature 0 clearly separates: x <= 5.0 -> class 0, x > 5.0 -> class 1
    X = np.array([[2.0, 10.0], [4.0, 12.0], [6.0, 1.0], [8.0, 3.0]])
    y = np.array([0, 0, 1, 1])
    
    feat, thresh, gini = tree.find_best_split(X, y)
    assert feat == 0
    assert thresh == 5.0
    assert gini == 0.0 # Perfect split


def test_iris_dataset_benchmark():
    iris = load_iris()
    X, y = iris.data, iris.target
    
    scratch_tree = tree.DecisionTreeClassifierScratch(max_depth=3)
    scratch_tree.fit(X, y)
    scratch_preds = scratch_tree.predict(X)
    scratch_acc = np.mean(scratch_preds == y)
    
    sk_tree = DecisionTreeClassifier(max_depth=3, criterion="gini", random_state=42)
    sk_tree.fit(X, y)
    sk_preds = sk_tree.predict(X)
    sk_acc = np.mean(sk_preds == y)
    
    assert scratch_acc >= 0.95
    assert sk_acc >= 0.95
    assert abs(scratch_acc - sk_acc) < 0.05
