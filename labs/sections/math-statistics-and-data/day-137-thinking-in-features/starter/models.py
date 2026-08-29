"""Two classifiers, written from scratch in NumPy.

scikit-learn is not installed in this lab, and that is deliberate: this
course has not taught modelling yet, so every model here is small enough
to read in one sitting. Both are deterministic -- no shuffling, no random
restarts, no early stopping on a random subset -- so a score is a fact
about the features rather than a fact about the run.

`LogisticRegression` is Day 111's gradient descent applied to the
log-loss. `NearestCentroid` is Day 107's distance, applied to two class
means. Neither is state of the art and neither needs to be: the whole
point of the day is that the feature table decides the score long before
the model does.
"""

from __future__ import annotations

import numpy as np


def sigmoid(z: np.ndarray) -> np.ndarray:
    """A numerically stable logistic function."""
    out = np.empty_like(z, dtype=float)
    positive = z >= 0
    out[positive] = 1.0 / (1.0 + np.exp(-z[positive]))
    exp_z = np.exp(z[~positive])
    out[~positive] = exp_z / (1.0 + exp_z)
    return out


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """The fraction of predictions that match the label."""
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    return float(np.mean(y_true == y_pred))


class LogisticRegression:
    """Binary logistic regression trained by full-batch gradient descent.

    The update is exactly Day 111's: subtract the learning rate times the
    gradient of the mean log-loss, `X.T @ (p - y) / n`, and repeat for a
    fixed number of steps. Weights start at zero, so two fits on the same
    data give bit-identical coefficients.
    """

    def __init__(self, learning_rate: float = 0.25, steps: int = 3000, l2: float = 0.0) -> None:
        self.learning_rate = learning_rate
        self.steps = steps
        self.l2 = l2
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()
        n, d = X.shape
        self.weights = np.zeros(d)
        self.bias = 0.0
        for _ in range(self.steps):
            p = sigmoid(X @ self.weights + self.bias)
            error = p - y
            grad_w = X.T @ error / n + self.l2 * self.weights
            grad_b = float(np.mean(error))
            self.weights -= self.learning_rate * grad_w
            self.bias -= self.learning_rate * grad_b
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("fit before predict")
        return sigmoid(np.asarray(X, dtype=float) @ self.weights + self.bias)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) >= 0.5).astype(int)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return accuracy(y, self.predict(X))


class NearestCentroid:
    """Assign each row to the class whose mean it is closest to.

    Distance is the Euclidean norm of Day 107, which is why this model
    cares about scale: a feature measured in thousands dominates the sum
    of squares no matter how little it says about the label.
    """

    def __init__(self) -> None:
        self.classes_: np.ndarray | None = None
        self.centroids_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NearestCentroid":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y).ravel()
        self.classes_ = np.unique(y)
        self.centroids_ = np.vstack([X[y == c].mean(axis=0) for c in self.classes_])
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.centroids_ is None or self.classes_ is None:
            raise RuntimeError("fit before predict")
        X = np.asarray(X, dtype=float)
        distances = np.linalg.norm(X[:, None, :] - self.centroids_[None, :, :], axis=2)
        return self.classes_[np.argmin(distances, axis=1)]

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return accuracy(y, self.predict(X))


def random_split(n: int, test_size: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Row indices for a seeded random train/test split."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    return order[test_size:], order[:test_size]


def time_ordered_split(n: int, test_size: int) -> tuple[np.ndarray, np.ndarray]:
    """Row indices for a split that puts the LAST rows in the test set.

    The rows must already be in time order. This is the split that tells
    you what happens when the model meets a day it has never seen.
    """
    index = np.arange(n)
    return index[: n - test_size], index[n - test_size :]
