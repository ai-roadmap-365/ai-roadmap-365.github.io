"""
Complete Classification Project reference library.
"""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, matthews_corrcoef, confusion_matrix
)


class ClassificationProjectPipeline:
    """
    End-to-end disciplined classification project pipeline:
    1. Feature Standardization
    2. Stratified 5-Fold CV model benchmark (LogisticRegression, KNN, GaussianNB)
    3. Asymmetric cost threshold optimization
    4. Gated single test-set evaluation
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.candidates = {
            "logistic_l2": LogisticRegression(C=1.0, class_weight="balanced", random_state=random_state, max_iter=1000),
            "logistic_l1": LogisticRegression(C=0.5, penalty="l1", solver="liblinear", class_weight="balanced", random_state=random_state),
            "knn_5": KNeighborsClassifier(n_neighbors=5, weights="distance"),
            "gaussian_nb": GaussianNB(),
        }
        self.cv_results = {}
        self.best_model_name = None
        self.best_model = None
        self.optimal_threshold = 0.50
        self.test_evaluated = False

    def fit_and_select(self, X_train: np.ndarray, y_train: np.ndarray, cv_folds: int = 5) -> dict[str, float]:
        X_train_scaled = self.scaler.fit_transform(X_train)
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        scores = {}
        for name, model in self.candidates.items():
            f1_list = []
            for train_idx, val_idx in skf.split(X_train_scaled, y_train):
                X_tr, X_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
                y_tr, y_val = y_train[train_idx], y_train[val_idx]
                
                model.fit(X_tr, y_tr)
                preds = model.predict(X_val)
                f1_list.append(f1_score(y_val, preds, zero_division=0))
                
            scores[name] = float(np.mean(f1_list))
            
        self.cv_results = scores
        self.best_model_name = max(scores, key=scores.get)
        self.best_model = self.candidates[self.best_model_name]
        # Fit winner on full training set
        self.best_model.fit(X_train_scaled, y_train)
        return scores

    def calibrate_threshold(self, X_val: np.ndarray, y_val: np.ndarray, cost_fp: float = 10.0, cost_fn: float = 100.0) -> float:
        X_val_scaled = self.scaler.transform(X_val)
        probs = self.best_model.predict_proba(X_val_scaled)[:, 1]
        
        thresholds = np.linspace(0.01, 0.99, 100)
        best_tau = 0.50
        min_cost = float("inf")
        
        for tau in thresholds:
            preds = (probs >= tau).astype(int)
            fp = np.sum((y_val == 0) & (preds == 1))
            fn = np.sum((y_val == 1) & (preds == 0))
            cost = float(cost_fp * fp + cost_fn * fn)
            if cost < min_cost:
                min_cost = cost
                best_tau = float(tau)
                
        self.optimal_threshold = best_tau
        return best_tau

    def evaluate_test(self, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, float]:
        if self.test_evaluated:
            raise RuntimeError("Test set evaluation can only be executed ONCE to prevent leakage!")
        self.test_evaluated = True
        
        X_test_scaled = self.scaler.transform(X_test)
        probs = self.best_model.predict_proba(X_test_scaled)[:, 1]
        preds = (probs >= self.optimal_threshold).astype(int)
        
        cm = confusion_matrix(y_test, preds)
        return {
            "accuracy": float(np.mean(preds == y_test)),
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "recall": float(recall_score(y_test, preds, zero_division=0)),
            "f1": float(f1_score(y_test, preds, zero_division=0)),
            "mcc": float(matthews_corrcoef(y_test, preds)),
            "roc_auc": float(roc_auc_score(y_test, probs)),
            "pr_auc": float(average_precision_score(y_test, probs)),
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1]),
        }
