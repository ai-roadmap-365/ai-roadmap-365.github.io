"""
Class Imbalance reference library.
"""
import numpy as np
from scipy.spatial.distance import cdist


def compute_balanced_weights(y: np.ndarray) -> dict[int, float]:
    """
    Compute balanced class weights:
    w_c = N / (K * N_c)
    """
    y = np.asarray(y, dtype=int)
    classes, counts = np.unique(y, return_counts=True)
    num_classes = len(classes)
    total_samples = len(y)
    
    weights = {}
    for c, count in zip(classes, counts):
        weights[int(c)] = float(total_samples / (num_classes * count))
    return weights


def random_undersample(X: np.ndarray, y: np.ndarray, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    Undersample majority class to match minority class sample count.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    rng = np.random.RandomState(random_state)
    
    classes, counts = np.unique(y, return_counts=True)
    min_count = np.min(counts)
    
    sampled_indices = []
    for c in classes:
        c_indices = np.where(y == c)[0]
        chosen = rng.choice(c_indices, size=min_count, replace=False)
        sampled_indices.extend(chosen)
        
    rng.shuffle(sampled_indices)
    return X[sampled_indices], y[sampled_indices]


def random_oversample(X: np.ndarray, y: np.ndarray, random_state: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """
    Oversample minority class with replacement to match majority sample count.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    rng = np.random.RandomState(random_state)
    
    classes, counts = np.unique(y, return_counts=True)
    max_count = np.max(counts)
    
    sampled_indices = []
    for c in classes:
        c_indices = np.where(y == c)[0]
        chosen = rng.choice(c_indices, size=max_count, replace=True)
        sampled_indices.extend(chosen)
        
    rng.shuffle(sampled_indices)
    return X[sampled_indices], y[sampled_indices]


def smote_synthetic_points(
    X_minority: np.ndarray,
    n_samples: int,
    k_neighbors: int = 5,
    random_state: int = 42,
) -> np.ndarray:
    """
    Generate synthetic minority points via k-NN line segment interpolation:
    x_syn = x_i + lambda * (x_neighbor - x_i), where lambda in [0, 1].
    """
    X_minority = np.asarray(X_minority, dtype=float)
    N, d = X_minority.shape
    if N < 2:
        raise ValueError("SMOTE requires at least 2 minority samples")
        
    rng = np.random.RandomState(random_state)
    actual_k = min(k_neighbors, N - 1)
    
    # Compute pairwise distance matrix among minority samples
    dists = cdist(X_minority, X_minority, metric="euclidean")
    np.fill_diagonal(dists, np.inf)
    
    # Find k nearest neighbors for each minority sample
    neighbor_indices = np.argsort(dists, axis=1)[:, :actual_k] # (N, actual_k)
    
    synthetic = np.zeros((n_samples, d), dtype=float)
    for i in range(n_samples):
        # Pick random base sample
        base_idx = rng.randint(0, N)
        base_point = X_minority[base_idx]
        
        # Pick random neighbor
        chosen_neighbor_idx = rng.choice(neighbor_indices[base_idx])
        neighbor_point = X_minority[chosen_neighbor_idx]
        
        # Random step lambda in [0, 1]
        lam = rng.uniform(0.0, 1.0)
        synthetic[i] = base_point + lam * (neighbor_point - base_point)
        
    return synthetic
