"""Machinery for Day 141 -- "What the Number Is Not Telling You".

Nothing in this file is an exercise. It builds the small, fully
deterministic datasets the nine exercises measure, and it contains one
model written by hand in NumPy so you can see that a nearest-neighbour
classifier is eleven lines of arithmetic and no magic at all.

Every dataset constructor takes an explicit integer seed and uses
`numpy.random.default_rng(seed)`, so every number this lab reports is
reproducible on any machine with the pinned versions.
"""

from __future__ import annotations

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier

# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


def accuracy(y_true, y_pred) -> float:
    """Fraction of predictions that match. The whole of "accuracy"."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_true == y_pred))


def mean_absolute_error(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


# --------------------------------------------------------------------------
# A nearest-neighbour classifier, written by hand
# --------------------------------------------------------------------------


class HandwrittenNearestNeighbour:
    """1-nearest-neighbour, from first principles, in NumPy.

    `fit` stores the training set. That is the entire training procedure:
    there is no search, no objective, no parameters. `predict` finds the
    closest stored point to each query and copies its label.

    This class exists to make one fact concrete: predicting a training
    point returns that point's own label, because a point's own distance
    to itself is zero. Training accuracy is therefore 1.000 by
    construction and carries no information whatsoever.
    """

    def __init__(self) -> None:
        self.X_: np.ndarray | None = None
        self.y_: np.ndarray | None = None

    def fit(self, X, y) -> "HandwrittenNearestNeighbour":
        self.X_ = np.asarray(X, dtype=float)
        self.y_ = np.asarray(y)
        return self

    def predict(self, X) -> np.ndarray:
        if self.X_ is None or self.y_ is None:
            raise RuntimeError("call fit before predict")
        X = np.asarray(X, dtype=float)
        # Squared euclidean distance from every query row to every stored
        # row, by broadcasting: (n_query, 1, n_features) - (n_train, n_features)
        diff = X[:, None, :] - self.X_[None, :, :]
        sq_dist = np.sum(diff * diff, axis=2)
        nearest = np.argmin(sq_dist, axis=1)
        return self.y_[nearest]


# --------------------------------------------------------------------------
# Datasets -- every one deterministic given its seed
# --------------------------------------------------------------------------


def pure_noise_dataset(n: int, n_features: int = 4, seed: int = 141):
    """Features from a normal distribution, labels from a coin flip.

    There is no relationship of any kind between X and y. No function
    exists to be approximated, so the best possible test accuracy is
    chance.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, n_features))
    y = rng.integers(0, 2, size=n)
    return X, y


def rule_dataset(n: int, seed: int, offset: float = 0.0):
    """Two uniform features on a square of side 1, labelled by an exact rule.

    The rule is `y = 1 if x1 > x0 else 0` -- the diagonal of the square.
    `offset` translates the whole square without changing the rule, which
    is what makes this dataset usable as a distribution shift: the
    labelling function is identical, only the region the points live in
    has moved.
    """
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.0, 1.0, size=(n, 2)) + offset
    y = exact_rule(X)
    return X, y


def exact_rule(X) -> np.ndarray:
    """The three-line rule that `rule_dataset` labels with.

    It is exactly correct everywhere, for every input, forever, and it
    needs no data, no training and no maintenance.
    """
    X = np.asarray(X, dtype=float)
    return (X[:, 1] > X[:, 0]).astype(int)


def flip_labels(y, noise_rate: float, seed: int):
    """Flip exactly `round(noise_rate * len(y))` labels, chosen at random.

    Exactly, not approximately: the count is fixed so the resulting
    ceiling is an exact arithmetic fact about the data rather than a
    sampled quantity.
    """
    y = np.asarray(y).copy()
    rng = np.random.default_rng(seed)
    n_flip = int(round(noise_rate * len(y)))
    idx = rng.choice(len(y), size=n_flip, replace=False)
    y[idx] = 1 - y[idx]
    return y


def noisy_rule_dataset(n: int, seed: int, noise_rate: float):
    """`rule_dataset` with a known fraction of its labels flipped."""
    X, y_clean = rule_dataset(n, seed=seed)
    y = flip_labels(y_clean, noise_rate=noise_rate, seed=seed + 9000)
    return X, y


def checkerboard_dataset(n: int, seed: int, cells: int = 4):
    """A clean but intricate boundary: a `cells` x `cells` checkerboard.

    The labels contain no noise at all, so nothing limits a model here
    except how much of the boundary the training sample reveals. This is
    the variance-limited problem that more data genuinely fixes.
    """
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.0, 1.0, size=(n, 2))
    y = ((np.floor(X[:, 0] * cells) + np.floor(X[:, 1] * cells)) % 2).astype(int)
    return X, y


def imbalanced_noise_dataset(n: int, seed: int, minority_rate: float = 0.1):
    """Pure-noise features with an exact minority-class count.

    Exactly `round(minority_rate * n)` rows carry label 1, placed at
    random positions, so the majority-class baseline on this set is an
    exact number rather than an estimate.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 6))
    y = np.zeros(n, dtype=int)
    n_minority = int(round(minority_rate * n))
    y[rng.choice(n, size=n_minority, replace=False)] = 1
    return X, y


def quadratic_curve(n: int, low: float, high: float, seed: int):
    """One feature on [low, high], target y = x squared. No noise."""
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(low, high, size=n))
    X = x.reshape(-1, 1)
    y = x**2
    return X, y


# --------------------------------------------------------------------------
# Model constructors -- fixed hyper-parameters so results never drift
# --------------------------------------------------------------------------


def one_nn() -> KNeighborsClassifier:
    return KNeighborsClassifier(n_neighbors=1)


def shallow_tree(max_depth: int = 3) -> DecisionTreeClassifier:
    return DecisionTreeClassifier(max_depth=max_depth, random_state=141)


def deep_tree() -> DecisionTreeClassifier:
    return DecisionTreeClassifier(random_state=141)


def smooth_knn(k: int = 15) -> KNeighborsClassifier:
    return KNeighborsClassifier(n_neighbors=k)


def linear_classifier() -> LogisticRegression:
    return LogisticRegression(max_iter=1000)


def majority_baseline() -> DummyClassifier:
    return DummyClassifier(strategy="most_frequent")


def knn_regressor(k: int = 5) -> KNeighborsRegressor:
    return KNeighborsRegressor(n_neighbors=k)


def linear_regressor() -> LinearRegression:
    return LinearRegression()


def fit_score(model, X_train, y_train, X_test, y_test) -> float:
    """Fit on the training set, score on the test set. Nothing else."""
    model.fit(X_train, y_train)
    return accuracy(y_test, model.predict(X_test))


# --------------------------------------------------------------------------
# Exercise 9: the decision function
# --------------------------------------------------------------------------

#: The four questions, in the order they must be asked. Cheapness first:
#: a question whose answer disqualifies machine learning outright is
#: worth asking before one that merely constrains it.
ML_DECISION_QUESTIONS = (
    "exact_rule_exists",
    "labels_available",
    "distribution_stable",
    "errors_tolerable",
)


def should_use_ml(problem: dict) -> str:
    """Return one of five verdicts for a described problem.

    `problem` must carry all four keys in `ML_DECISION_QUESTIONS` with
    boolean values. The order of the checks is the argument:

    1. `exact_rule_exists` -- if you can write the rule down, write it.
       A rule is exactly correct, costs nothing to run, needs no labels,
       never drifts and can be reviewed by a person who is not you.
       No model beats that, and a model that merely matches it has cost
       you a data pipeline for nothing.
    2. `labels_available` -- supervised learning approximates a function
       from examples of its output. Without labels there are no examples,
       and no amount of feature work substitutes for them.
    3. `distribution_stable` -- the method assumes future inputs resemble
       training inputs. If the world moves faster than you can retrain,
       the model is wrong by the time it ships.
    4. `errors_tolerable` -- a model is an approximation and will be
       wrong on some inputs. If a single wrong answer is unacceptable and
       cannot be caught downstream, an approximation is the wrong shape
       of tool regardless of its accuracy.
    """
    missing = [q for q in ML_DECISION_QUESTIONS if q not in problem]
    if missing:
        raise KeyError(f"problem is missing: {', '.join(missing)}")
    if problem["exact_rule_exists"]:
        return "write the rule"
    if not problem["labels_available"]:
        return "get labels first"
    if not problem["distribution_stable"]:
        return "not yet: the distribution moves"
    if not problem["errors_tolerable"]:
        return "no: errors are not tolerable"
    return "yes"


def problem(
    exact_rule_exists: bool,
    labels_available: bool,
    distribution_stable: bool,
    errors_tolerable: bool,
) -> dict:
    """Small helper so the case table in the tests reads as prose."""
    return {
        "exact_rule_exists": exact_rule_exists,
        "labels_available": labels_available,
        "distribution_stable": distribution_stable,
        "errors_tolerable": errors_tolerable,
    }
