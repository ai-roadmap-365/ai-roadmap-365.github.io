"""
k-Nearest Neighbors reference library.
"""
import numpy as np
from scipy.spatial.distance import cdist


def compute_distance_matrix(X_train: np.ndarray, X_test: np.ndarray, metric: str = "euclidean") -> np.ndarray:
    """
    Compute pairwise distance matrix between test points (M, d) and training points (N, d).
    Returns (M, N) matrix where element (i, j) is dist(X_test[i], X_train[j]).
    """
    X_train = np.asarray(X_train, dtype=float)
    X_test = np.asarray(X_test, dtype=float)
    if X_train.ndim == 1:
        X_train = X_train[:, None]
    if X_test.ndim == 1:
        X_test = X_test[:, None]
        
    if metric == "euclidean":
        # Vectorized ||x_test - x_train||^2 = ||x_test||^2 + ||x_train||^2 - 2 * x_test * x_train^T
        test_sq = np.sum(X_test**2, axis=1, keepdims=True)
        train_sq = np.sum(X_train**2, axis=1, keepdims=True).T
        cross = np.dot(X_test, X_train.T)
        dists_sq = np.maximum(test_sq + train_sq - 2.0 * cross, 0.0)
        return np.sqrt(dists_sq)
    elif metric == "manhattan":
        return cdist(X_test, X_train, metric="cityblock")
    elif metric == "cosine":
        norm_test = np.linalg.norm(X_test, axis=1, keepdims=True)
        norm_train = np.linalg.norm(X_train, axis=1, keepdims=True).T
        denom = np.maximum(norm_test * norm_train, 1e-12)
        sim = np.dot(X_test, X_train.T) / denom
        return 1.0 - sim
    else:
        raise ValueError(f"Unknown metric: {metric}")


def predict_proba_knn(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    k: int = 5,
    weights: str = "uniform",
    metric: str = "euclidean",
) -> np.ndarray:
    """
    Compute class probability distributions for test points (M, K).
    """
    X_train = np.asarray(X_train, dtype=float)
    y_train = np.asarray(y_train, dtype=int)
    X_test = np.asarray(X_test, dtype=float)
    
    classes = np.unique(y_train)
    num_classes = len(classes)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    
    dists = compute_distance_matrix(X_train, X_test, metric=metric) # (M, N)
    num_test = X_test.shape[0]
    probas = np.zeros((num_test, num_classes), dtype=float)
    
    for i in range(num_test):
        row_dists = dists[i]
        neighbor_indices = np.argsort(row_dists)[:k]
        neighbor_labels = y_train[neighbor_indices]
        neighbor_dists = row_dists[neighbor_indices]
        
        if weights == "uniform":
            for label in neighbor_labels:
                probas[i, class_to_idx[label]] += 1.0 / k
        elif weights == "distance":
            # w = 1 / (d + eps)
            w = 1.0 / (neighbor_dists + 1e-12)
            total_w = np.sum(w)
            for label, weight in zip(neighbor_labels, w):
                probas[i, class_to_idx[label]] += weight / total_w
        else:
            raise ValueError(f"Unknown weights scheme: {weights}")
            
    return probas


def predict_knn(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    k: int = 5,
    weights: str = "uniform",
    metric: str = "euclidean",
) -> np.ndarray:
    """
    Predict discrete class labels for test points (M,).
    """
    classes = np.unique(y_train)
    probas = predict_proba_knn(X_train, y_train, X_test, k=k, weights=weights, metric=metric)
    best_idx = np.argmax(probas, axis=1)
    return classes[best_idx]
