"""
Feature Scaling and Encoding reference library implementation.
"""
import numpy as np
from sklearn.model_selection import KFold


class StandardScalerScratch:
    """
    Standardize features: z = (x - mu) / sigma
    """
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray):
        X = np.asarray(X, dtype=float)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        # Avoid division by zero for constant features
        self.scale_ = np.where(self.scale_ < 1e-9, 1.0, self.scale_)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class RobustScalerScratch:
    """
    Robust scaling using median and Interquartile Range (IQR = Q75 - Q25):
    z = (x - median) / IQR
    """
    def __init__(self):
        self.center_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray):
        X = np.asarray(X, dtype=float)
        self.center_ = np.median(X, axis=0)
        q25 = np.percentile(X, 25, axis=0)
        q75 = np.percentile(X, 75, axis=0)
        iqr = q75 - q25
        self.scale_ = np.where(iqr < 1e-9, 1.0, iqr)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return (X - self.center_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


def out_of_fold_target_encode(
    categories: np.ndarray, target: np.ndarray, cv: int = 5, smoothing: float = 10.0, random_state: int = 42
) -> np.ndarray:
    """
    Compute leak-free Out-of-Fold smoothed target encoding:
    S_c = (n_c * mean_c + smoothing * global_mean) / (n_c + smoothing)
    """
    categories = np.asarray(categories)
    target = np.asarray(target, dtype=float)
    n_samples = len(categories)
    encoded = np.zeros(n_samples, dtype=float)
    
    kf = KFold(n_splits=cv, shuffle=True, random_state=random_state)
    
    for train_idx, val_idx in kf.split(categories, target):
        cat_tr, y_tr = categories[train_idx], target[train_idx]
        cat_va = categories[val_idx]
        
        global_mean = np.mean(y_tr)
        
        # Compute category statistics on training fold ONLY
        unique_cats, counts = np.unique(cat_tr, return_counts=True)
        cat_sums = {c: np.sum(y_tr[cat_tr == c]) for c in unique_cats}
        cat_counts = dict(zip(unique_cats, counts))
        
        # Apply smoothed formula to validation fold
        val_encoded = np.zeros(len(cat_va))
        for i, c in enumerate(cat_va):
            if c in cat_counts:
                n_c = cat_counts[c]
                sum_c = cat_sums[c]
                val_encoded[i] = (sum_c + smoothing * global_mean) / (n_c + smoothing)
            else:
                # Unseen category gets global training mean
                val_encoded[i] = global_mean
                
        encoded[val_idx] = val_encoded
        
    return encoded
