"""
Logistic Regression reference library implementation.
"""
import numpy as np


def sigmoid(z: np.ndarray) -> np.ndarray:
    """
    Compute the logistic sigmoid function in a numerically stable manner:
    sigma(z) = 1 / (1 + exp(-z))
    """
    z = np.asarray(z, dtype=float)
    z_clipped = np.clip(z, -500.0, 500.0)
    return 1.0 / (1.0 + np.exp(-z_clipped))


def predict_proba(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    """
    Compute predicted probabilities P(y=1|X) given weights w and intercept b.
    """
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    z = np.dot(X, w) + b
    return sigmoid(z)


def binary_cross_entropy(y_true: np.ndarray, y_prob: np.ndarray, eps: float = 1e-15) -> float:
    """
    Compute binary cross-entropy (log loss):
    L = - (1/N) * sum(y * log(p) + (1 - y) * log(1 - p))
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)
    y_p_clipped = np.clip(y_p, eps, 1.0 - eps)
    loss = -np.mean(y_t * np.log(y_p_clipped) + (1.0 - y_t) * np.log(1.0 - y_p_clipped))
    return float(loss)


def compute_gradients(X: np.ndarray, y_true: np.ndarray, y_prob: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Compute exact gradients of binary cross-entropy:
    grad_w = (1/N) * X^T (y_prob - y_true)
    grad_b = (1/N) * sum(y_prob - y_true)
    """
    X = np.asarray(X, dtype=float)
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)
    N = len(y_t)
    diff = y_p - y_t
    grad_w = (1.0 / N) * np.dot(X.T, diff)
    grad_b = float((1.0 / N) * np.sum(diff))
    return grad_w, grad_b


def fit_logistic_regression(
    X: np.ndarray,
    y: np.ndarray,
    lr: float = 0.1,
    epochs: int = 1000,
    tol: float = 1e-7
) -> tuple[np.ndarray, float, list[float]]:
    """
    Fit logistic regression model using batch gradient descent.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    N, D = X.shape
    w = np.zeros(D, dtype=float)
    b = 0.0
    history = []

    for epoch in range(epochs):
        probs = predict_proba(X, w, b)
        loss = binary_cross_entropy(y, probs)
        history.append(loss)

        grad_w, grad_b = compute_gradients(X, y, probs)
        w -= lr * grad_w
        b -= lr * grad_b

        if np.linalg.norm(grad_w) < tol and abs(grad_b) < tol:
            break

    return w, b, history


def predict_classes(X: np.ndarray, w: np.ndarray, b: float, threshold: float = 0.5) -> np.ndarray:
    """
    Predict binary class labels (0 or 1) based on decision threshold tau.
    """
    probs = predict_proba(X, w, b)
    return (probs >= threshold).astype(int)
