"""
Decision Boundaries reference library.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression


def compute_linear_boundary_2d(w: np.ndarray, b: float, x1: np.ndarray) -> np.ndarray:
    """
    Compute x2 coordinates for linear decision boundary w1*x1 + w2*x2 + b = 0:
    x2 = - (w1*x1 + b) / w2
    """
    w = np.asarray(w, dtype=float)
    x1 = np.asarray(x1, dtype=float)
    if abs(w[1]) < 1e-12:
        raise ZeroDivisionError("w2 is zero; boundary is vertical line x1 = -b/w1")
    return -(w[0] * x1 + b) / w[1]


def signed_distance_to_boundary(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    """
    Compute signed perpendicular distance from points to linear boundary:
    d = (w^T x + b) / ||w||_2
    """
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    norm_w = np.linalg.norm(w)
    if norm_w < 1e-12:
        raise ValueError("Weight vector norm is zero")
    return (np.dot(X, w) + b) / norm_w


def polynomial_features_2d(X: np.ndarray, degree: int = 2) -> np.ndarray:
    """
    Expand 2D feature matrix [x1, x2] into polynomial features up to degree.
    For degree=2: [x1, x2, x1^2, x1*x2, x2^2]
    """
    X = np.asarray(X, dtype=float)
    if X.shape[1] != 2:
        raise ValueError("X must have exactly 2 columns")
    x1 = X[:, 0]
    x2 = X[:, 1]
    
    if degree == 1:
        return X.copy()
    elif degree == 2:
        return np.column_stack([x1, x2, x1**2, x1 * x2, x2**2])
    else:
        # General expansion
        cols = []
        for d in range(1, degree + 1):
            for i in range(d + 1):
                cols.append((x1 ** (d - i)) * (x2 ** i))
        return np.column_stack(cols)


def fit_ovr_classifier(X: np.ndarray, y: np.ndarray, C: float = 1e9) -> list[tuple[np.ndarray, float]]:
    """
    Fit One-vs-Rest binary logistic regression models for multiclass classification.
    Returns list of (w, b) tuples for each class.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    classes = np.unique(y)
    models = []

    for c in classes:
        # Binary target: 1 if class c else 0
        y_binary = (y == c).astype(int)
        clf = LogisticRegression(C=C, solver="lbfgs", max_iter=1000)
        clf.fit(X, y_binary)
        w = clf.coef_[0]
        b = float(clf.intercept_[0])
        models.append((w, b))

    return models


def predict_ovr(X: np.ndarray, models: list[tuple[np.ndarray, float]]) -> np.ndarray:
    """
    Predict class labels using One-vs-Rest decision rule (argmax score z_k = w_k^T x + b_k).
    """
    X = np.asarray(X, dtype=float)
    scores = []
    for w, b in models:
        z = np.dot(X, w) + b
        scores.append(z)
    scores_matrix = np.column_stack(scores)
    return np.argmax(scores_matrix, axis=1)
