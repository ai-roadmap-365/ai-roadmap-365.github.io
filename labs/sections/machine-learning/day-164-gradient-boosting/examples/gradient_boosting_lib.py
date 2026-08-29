"""
Gradient Boosting reference library implementation.
"""
import numpy as np
from sklearn.tree import DecisionTreeRegressor


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Compute stable sigmoid activation."""
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


def compute_pseudo_residuals_classification(y: np.ndarray, raw_scores: np.ndarray) -> np.ndarray:
    """
    Negative gradient of Binary Cross-Entropy Loss:
    L(y, F) = - [ y * log(p) + (1-y) * log(1-p) ]
    r_i = - dL / dF = y_i - p_i  where p_i = sigmoid(F_i)
    """
    y = np.asarray(y, dtype=float)
    p = sigmoid(raw_scores)
    return y - p


class GradientBoostingRegressorScratch:
    """
    Gradient Boosting Regressor using Squared Error Loss: L(y, F) = 0.5 * (y - F)^2.
    """
    def __init__(self, n_estimators: int = 50, learning_rate: float = 0.1, max_depth: int = 3):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.f0 = 0.0
        self.trees = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        
        # Initial constant prediction: mean of y
        self.f0 = float(np.mean(y))
        f_current = np.full_like(y, self.f0)
        self.trees = []
        
        for _ in range(self.n_estimators):
            # Compute negative gradient (residuals)
            residuals = y - f_current
            
            # Fit shallow regression tree to residuals
            tree = DecisionTreeRegressor(max_depth=self.max_depth, random_state=42)
            tree.fit(X, residuals)
            
            # Update additive model with shrinkage
            update = tree.predict(X)
            f_current += self.learning_rate * update
            self.trees.append(tree)
            
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        f_pred = np.full(len(X), self.f0)
        for tree in self.trees:
            f_pred += self.learning_rate * tree.predict(X)
        return f_pred


class GradientBoostingClassifierScratch:
    """
    Binary Gradient Boosting Classifier using Log-Loss (Binary Cross-Entropy).
    """
    def __init__(self, n_estimators: int = 30, learning_rate: float = 0.1, max_depth: int = 3):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.f0 = 0.0
        self.trees = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        
        # Initial constant log-odds: f0 = log(p / (1-p))
        p_mean = np.clip(np.mean(y), 1e-15, 1.0 - 1e-15)
        self.f0 = float(np.log(p_mean / (1.0 - p_mean)))
        f_current = np.full_like(y, self.f0)
        self.trees = []
        
        for _ in range(self.n_estimators):
            # Compute pseudo-residuals: r_i = y_i - p_i
            p = sigmoid(f_current)
            residuals = y - p
            
            # Fit tree to pseudo-residuals
            tree = DecisionTreeRegressor(max_depth=self.max_depth, random_state=42)
            tree.fit(X, residuals)
            
            # Newton-Raphson leaf value adjustment: gamma = sum(r) / sum(p * (1-p))
            leaf_indices = tree.apply(X)
            leaf_values = {}
            for leaf in np.unique(leaf_indices):
                mask = leaf_indices == leaf
                num = np.sum(residuals[mask])
                den = np.sum(p[mask] * (1.0 - p[mask])) + 1e-15
                leaf_values[leaf] = num / den
                
            # Replace leaf predictions with optimal Newton-Raphson values
            tree_update = np.array([leaf_values[idx] for idx in leaf_indices])
            f_current += self.learning_rate * tree_update
            self.trees.append((tree, leaf_values))
            
        return self

    def _predict_raw(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        f_pred = np.full(len(X), self.f0)
        for tree, leaf_values in self.trees:
            leaf_indices = tree.apply(X)
            update = np.array([leaf_values.get(idx, 0.0) for idx in leaf_indices])
            f_pred += self.learning_rate * update
        return f_pred

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        raw_scores = self._predict_raw(X)
        p1 = sigmoid(raw_scores)
        return np.column_stack([1.0 - p1, p1])

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        probs = self.predict_proba(X)[:, 1]
        return (probs >= threshold).astype(int)
