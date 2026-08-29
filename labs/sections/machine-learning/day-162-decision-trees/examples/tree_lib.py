"""
Decision Trees reference library implementation.
"""
import numpy as np


def compute_gini(y: np.ndarray) -> float:
    """
    Compute Gini impurity:
    G = 1 - sum_{k=1}^K p_k^2
    """
    y = np.asarray(y, dtype=int)
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    return float(1.0 - np.sum(probs ** 2))


def compute_entropy(y: np.ndarray, eps: float = 1e-15) -> float:
    """
    Compute Shannon entropy (base 2):
    H = - sum_{k=1}^K p_k * log2(p_k)
    """
    y = np.asarray(y, dtype=int)
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    probs = np.clip(probs, eps, 1.0)
    return float(-np.sum(probs * np.log2(probs)))


def find_best_split(X: np.ndarray, y: np.ndarray) -> tuple[int, float, float]:
    """
    Exhaustively evaluate all features and thresholds to find split minimizing weighted child Gini impurity:
    Returns (best_feature_idx, best_threshold, best_weighted_gini).
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    N, D = X.shape
    
    current_gini = compute_gini(y)
    if current_gini == 0.0 or N < 2:
        return -1, 0.0, current_gini
        
    best_feat = -1
    best_thresh = 0.0
    best_gini = float("inf")
    
    for feat_idx in range(D):
        values = np.unique(X[:, feat_idx])
        if len(values) < 2:
            continue
            
        # Candidate thresholds at midpoints between sorted unique values
        thresholds = (values[:-1] + values[1:]) / 2.0
        
        for t in thresholds:
            left_mask = X[:, feat_idx] <= t
            right_mask = ~left_mask
            
            n_l, n_r = np.sum(left_mask), np.sum(right_mask)
            if n_l == 0 or n_r == 0:
                continue
                
            gini_l = compute_gini(y[left_mask])
            gini_r = compute_gini(y[right_mask])
            weighted_gini = (n_l / N) * gini_l + (n_r / N) * gini_r
            
            if weighted_gini < best_gini:
                best_gini = weighted_gini
                best_feat = feat_idx
                best_thresh = float(t)
                
    return best_feat, best_thresh, float(best_gini)


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


class DecisionTreeClassifierScratch:
    """
    Binary / Multiclass Decision Tree Classifier using CART algorithm.
    """
    def __init__(self, max_depth: int = 3, min_samples_split: int = 2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def _majority_class(self, y: np.ndarray) -> int:
        classes, counts = np.unique(y, return_counts=True)
        return int(classes[np.argmax(counts)])

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> Node:
        N, D = X.shape
        num_classes = len(np.unique(y))
        
        # Base cases: pure node, max depth reached, or too few samples
        if num_classes == 1 or depth >= self.max_depth or N < self.min_samples_split:
            return Node(value=self._majority_class(y))
            
        feat_idx, thresh, best_gini = find_best_split(X, y)
        if feat_idx == -1:
            return Node(value=self._majority_class(y))
            
        left_mask = X[:, feat_idx] <= thresh
        right_mask = ~left_mask
        
        left_child = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return Node(feature=feat_idx, threshold=thresh, left=left_child, right=right_child)

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.root = self._build_tree(X, y, depth=0)
        return self

    def _traverse_single(self, x: np.ndarray, node: Node) -> int:
        if node.is_leaf:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._traverse_single(x, node.left)
        return self._traverse_single(x, node.right)

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return np.array([self._traverse_single(x, self.root) for x in X], dtype=int)
