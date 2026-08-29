"""
Support Vector Machines reference library implementation.
"""
import numpy as np


def compute_rbf_kernel(X1: np.ndarray, X2: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Compute pairwise RBF kernel Gram matrix K in R^(N1 x N2):
    K[i, j] = exp(-gamma * ||x1_i - x2_j||^2)
    Using Euclidean distance expansion: ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a^T b
    """
    X1 = np.asarray(X1, dtype=float)
    X2 = np.asarray(X2, dtype=float)
    
    sq_norm1 = np.sum(X1**2, axis=1)[:, np.newaxis] # (N1, 1)
    sq_norm2 = np.sum(X2**2, axis=1)[np.newaxis, :] # (1, N2)
    
    sq_dists = sq_norm1 + sq_norm2 - 2 * np.dot(X1, X2.T)
    sq_dists = np.maximum(sq_dists, 0.0) # Numerical stability
    
    return np.exp(-gamma * sq_dists)


class LinearSVMScratch:
    """
    Soft-margin linear SVM trained via Pegasos subgradient descent on Hinge Loss:
    min_w (1/2)||w||^2 + C * sum max(0, 1 - y_i(w^T x_i + b))
    Labels y must be in {-1, +1}.
    """
    def __init__(self, C: float = 1.0, learning_rate: float = 0.01, max_iter: int = 1000, random_state: int = 42):
        self.C = C
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.random_state = random_state
        self.w = None
        self.b = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        
        # Convert {0, 1} to {-1, +1} if needed
        if set(np.unique(y)) == {0, 1}:
            y = np.where(y == 0, -1.0, 1.0)
            
        n_samples, n_features = X.shape
        rng = np.random.default_rng(self.random_state)
        
        self.w = np.zeros(n_features)
        self.b = 0.0
        
        for epoch in range(1, self.max_iter + 1):
            lr = self.learning_rate / (1.0 + 0.001 * epoch) # Decaying step size
            indices = rng.permutation(n_samples)
            
            for idx in indices:
                x_i = X[idx]
                y_i = y[idx]
                
                margin = y_i * (np.dot(self.w, x_i) + self.b)
                
                if margin < 1.0:
                    # Misclassified or inside margin: subgradient of Hinge Loss is -y_i * x_i
                    self.w = (1.0 - lr) * self.w + lr * self.C * y_i * x_i
                    self.b = self.b + lr * self.C * y_i
                else:
                    # Correctly classified outside margin: gradient is just L2 weight decay
                    self.w = (1.0 - lr) * self.w
                    
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        return np.dot(X, self.w) + self.b

    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.decision_function(X)
        return np.where(scores >= 0, 1, 0)
