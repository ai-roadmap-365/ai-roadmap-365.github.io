"""
Random Forests reference library implementation.
"""
import numpy as np


def compute_gini(y: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    return float(1.0 - np.sum(probs ** 2))


def bootstrap_sample(X: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Sample N elements uniformly with replacement.
    Returns (X_boot, y_boot, oob_indices).
    """
    N = len(X)
    boot_idx = rng.choice(N, size=N, replace=True)
    oob_mask = np.ones(N, dtype=bool)
    oob_mask[boot_idx] = False
    oob_indices = np.where(oob_mask)[0]
    return X[boot_idx], y[boot_idx], oob_indices


class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    @property
    def is_leaf(self):
        return self.value is not None


class RandomizedDecisionTree:
    def __init__(self, max_depth: int = 5, min_samples_split: int = 2, max_features: str = "sqrt"):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.root = None

    def _get_feature_subset(self, D: int, rng: np.random.Generator) -> np.ndarray:
        if self.max_features == "sqrt":
            k = max(1, int(np.sqrt(D)))
        elif self.max_features == "log2":
            k = max(1, int(np.log2(D)))
        elif isinstance(self.max_features, int):
            k = min(D, self.max_features)
        else:
            k = D
        return rng.choice(D, size=k, replace=False)

    def _find_best_split(self, X: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> tuple[int, float, float]:
        N, D = X.shape
        feature_subset = self._get_feature_subset(D, rng)
        
        best_feat = -1
        best_thresh = 0.0
        best_gini = float("inf")
        
        for feat_idx in feature_subset:
            vals = np.unique(X[:, feat_idx])
            if len(vals) < 2:
                continue
            thresholds = (vals[:-1] + vals[1:]) / 2.0
            for t in thresholds:
                l_mask = X[:, feat_idx] <= t
                r_mask = ~l_mask
                nl, nr = np.sum(l_mask), np.sum(r_mask)
                if nl == 0 or nr == 0:
                    continue
                cost = (nl / N) * compute_gini(y[l_mask]) + (nr / N) * compute_gini(y[r_mask])
                if cost < best_gini:
                    best_gini = cost
                    best_feat = feat_idx
                    best_thresh = float(t)
                    
        return best_feat, best_thresh, best_gini

    def _majority_class(self, y: np.ndarray) -> int:
        classes, counts = np.unique(y, return_counts=True)
        return int(classes[np.argmax(counts)])

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int, rng: np.random.Generator) -> Node:
        N, D = X.shape
        if len(np.unique(y)) == 1 or depth >= self.max_depth or N < self.min_samples_split:
            return Node(value=self._majority_class(y))
            
        feat, thresh, gini = self._find_best_split(X, y, rng)
        if feat == -1:
            return Node(value=self._majority_class(y))
            
        l_mask = X[:, feat] <= thresh
        r_mask = ~l_mask
        
        l_child = self._build_tree(X[l_mask], y[l_mask], depth + 1, rng)
        r_child = self._build_tree(X[r_mask], y[r_mask], depth + 1, rng)
        return Node(feature=feat, threshold=thresh, left=l_child, right=r_child)

    def fit(self, X: np.ndarray, y: np.ndarray, rng: np.random.Generator):
        self.root = self._build_tree(X, y, 0, rng)
        return self

    def _predict_row(self, x: np.ndarray, node: Node) -> int:
        if node.is_leaf:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_row(x, node.left)
        return self._predict_row(x, node.right)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict_row(x, self.root) for x in X], dtype=int)


class RandomForestClassifierScratch:
    """
    Random Forest Classifier combining Bagging, Random Feature Subspaces, and OOB evaluation.
    """
    def __init__(self, n_estimators: int = 15, max_depth: int = 5, max_features: str = "sqrt", random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []
        self.oob_score_ = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        N, D = X.shape
        classes = np.unique(y)
        num_classes = len(classes)
        
        rng = np.random.default_rng(self.random_state)
        self.trees = []
        
        # Track out-of-bag votes for each sample: oob_votes[sample_idx, class_idx]
        oob_votes = np.zeros((N, num_classes), dtype=int)
        oob_counts = np.zeros(N, dtype=int)
        
        for _ in range(self.n_estimators):
            X_boot, y_boot, oob_idx = bootstrap_sample(X, y, rng)
            tree = RandomizedDecisionTree(
                max_depth=self.max_depth,
                max_features=self.max_features
            )
            tree.fit(X_boot, y_boot, rng)
            self.trees.append(tree)
            
            # Predict OOB samples
            if len(oob_idx) > 0:
                preds = tree.predict(X[oob_idx])
                for idx, p in zip(oob_idx, preds):
                    oob_votes[idx, p] += 1
                    oob_counts[idx] += 1
                    
        # Compute OOB score on evaluated samples
        evaluated = oob_counts > 0
        if np.any(evaluated):
            oob_preds = np.argmax(oob_votes[evaluated], axis=1)
            self.oob_score_ = float(np.mean(oob_preds == y[evaluated]))
            
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        tree_preds = np.array([tree.predict(X) for tree in self.trees]) # Shape: (n_trees, N)
        # Majority voting across trees along axis 0
        N = len(X)
        final_preds = np.zeros(N, dtype=int)
        for i in range(N):
            vals, counts = np.unique(tree_preds[:, i], return_counts=True)
            final_preds[i] = vals[np.argmax(counts)]
        return final_preds
