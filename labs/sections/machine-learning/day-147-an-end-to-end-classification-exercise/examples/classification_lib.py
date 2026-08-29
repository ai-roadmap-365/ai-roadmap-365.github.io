"""One classification project, run properly, once.

Days 141-146 each isolated one discipline: what a score means, the three
feedback shapes, the workflow's stage contract, the three sets and the
selection optimism they exist to control, the bias/variance trade, and the
scikit-learn estimator API. This module spends every one of those
disciplines on a single real dataset and produces one defensible verdict.

Frame, baseline, split, pipeline, cross-validate, select, ONE test
evaluation, error analysis, an honest interval. Nothing here is taught for
the first time; everything here is used.
"""

from __future__ import annotations

import time

import numpy as np

from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


# --------------------------------------------------------------------------
# 1. Choosing the dataset -- by measuring, not by assumption
# --------------------------------------------------------------------------


def candidate_summaries():
    """Baseline and headroom for the three datasets bundled in scikit-learn.

    Returns one row per candidate: ``(name, n_samples, n_features,
    n_classes, majority_baseline, n_test_rows_at_20_percent)``. This is the
    evidence the choice of dataset is made from, not a rule of thumb.
    """
    rows = []
    for name, loader in (("iris", load_iris), ("wine", load_wine), ("breast_cancer", load_breast_cancer)):
        d = loader()
        X, y = d.data, d.target
        _x_tr, x_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
        baseline = DummyClassifier(strategy="most_frequent").fit(_x_tr, y_tr)
        rows.append(
            (
                name,
                X.shape[0],
                X.shape[1],
                len(set(y.tolist())),
                round(float(baseline.score(x_te, y_te)), 4),
                x_te.shape[0],
            )
        )
    return rows


def load_chosen_dataset():
    """The dataset this exercise uses: the Wisconsin breast-cancer set.

    Bundled in scikit-learn, fully offline, 569 rows of 30 real-valued
    measurements from a digitised fine-needle aspirate, two classes.
    Chosen over iris and wine because both of those saturate near-perfect
    accuracy on a test set of 30-36 rows, leaving no room for an honest
    interval or a real selection-optimism check; see ``candidate_summaries``.
    """
    d = load_breast_cancer()
    return d.data, d.target, [str(name) for name in d.target_names]


# --------------------------------------------------------------------------
# 2. The frame and the baseline -- before any model
# --------------------------------------------------------------------------


def majority_baseline(x_train, y_train, x_test, y_test) -> float:
    """The accuracy of predicting the majority class every time.

    Every model in this exercise has to beat this number to be worth
    building at all. Day 141's whole point: a score is not evidence until
    you know what it beats.
    """
    dummy = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    return float(dummy.score(x_test, y_test))


# --------------------------------------------------------------------------
# 3. The split -- train for fitting, held for selecting, test for one look
# --------------------------------------------------------------------------


def split_once(X, y, seed: int = 0, test_size: float = 0.2):
    """One stratified train/test split. The test half is touched once, later.

    Day 144's rule: the training portion is for fitting, unlimited looks.
    The test portion's whole value comes from never having influenced a
    choice, so nothing below this call may see ``x_test`` or ``y_test``
    until the single evaluation at the end.
    """
    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)


# --------------------------------------------------------------------------
# 4. The candidate pipelines -- three families, a real sweep
# --------------------------------------------------------------------------

_KNN_NEIGHBORS = list(range(1, 16))
_LOGREG_C = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
_TREE_DEPTHS = list(range(1, 11))


def candidate_configs():
    """36 candidate pipelines: 15 KNN, 11 logistic regression, 10 trees.

    Every candidate is an actual scikit-learn ``Pipeline`` (Day 146),
    scaling folded in wherever the estimator needs it, so cross-validation
    below refits the scaler on each fold's training rows only -- Day 143's
    stage-ordering rule, now enforced by the estimator's own contract
    instead of by discipline.

    Returns a list of ``(family, hyperparameter, make_pipeline)`` where
    ``make_pipeline`` is a zero-argument callable returning a fresh,
    unfitted ``Pipeline`` -- fresh each call, because a fitted estimator is
    not something you cross-validate with.
    """
    configs = []
    for k in _KNN_NEIGHBORS:
        configs.append(
            ("knn", k, lambda k=k: Pipeline([("scale", StandardScaler()), ("clf", KNeighborsClassifier(k))]))
        )
    for c in _LOGREG_C:
        configs.append(
            (
                "logreg",
                c,
                lambda c=c: Pipeline(
                    [("scale", StandardScaler()), ("clf", LogisticRegression(C=c, max_iter=5000))]
                ),
            )
        )
    for depth in _TREE_DEPTHS:
        configs.append(
            ("tree", depth, lambda depth=depth: Pipeline([("clf", DecisionTreeClassifier(max_depth=depth, random_state=0))]))
        )
    return configs


def candidate_count() -> int:
    """K, the number of configurations this exercise actually tries.

    The number nobody remembers, Day 144 said -- so this project counts it.
    """
    return len(candidate_configs())


# --------------------------------------------------------------------------
# 5. Cross-validate, then select -- the honest way to spend the train rows
# --------------------------------------------------------------------------


def cross_validate_configs(x_train, y_train, seed: int = 0, folds: int = 5):
    """5-fold stratified CV accuracy for every candidate, on train rows only.

    Returns rows of ``(family, hyperparameter, cv_mean, cv_std)``, sorted
    best first. This plays the role Day 144 gave the validation set --
    many looks, and every look is spent here, never on the test rows.
    """
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    rows = []
    for family, param, make in candidate_configs():
        scores = cross_val_score(make(), x_train, y_train, cv=splitter)
        rows.append((family, param, round(float(scores.mean()), 4), round(float(scores.std()), 4)))
    rows.sort(key=lambda r: -r[2])
    return rows


def select_best(x_train, y_train, seed: int = 0, folds: int = 5):
    """Fit the winner of the sweep on the full training set.

    Returns ``(family, hyperparameter, cv_mean, fitted_pipeline)``. This is
    the one moment of choice in the whole exercise -- everything before it
    explores, everything after it is committed.
    """
    rows = cross_validate_configs(x_train, y_train, seed=seed, folds=folds)
    winner_family, winner_param, winner_cv, _sd = rows[0]
    for family, param, make_fn in candidate_configs():
        if family == winner_family and param == winner_param:
            fitted = make_fn().fit(x_train, y_train)
            return winner_family, winner_param, winner_cv, fitted
    raise RuntimeError("winning configuration vanished between sweep and refit")


# --------------------------------------------------------------------------
# 6. The predicted optimism, from Day 144's formula -- and what it misses
# --------------------------------------------------------------------------


def proportion_standard_error(p: float, n: int) -> float:
    """The standard error of an accuracy estimated on n rows. Day 117's formula."""
    return float(np.sqrt(p * (1.0 - p) / n))


def expected_max_of_normals(k: int, draws: int = 20000, seed: int = 7) -> float:
    """E of the maximum of k standard normals, by simulation. Day 144's quantity."""
    rng = np.random.default_rng(seed)
    return float(np.mean(np.max(rng.standard_normal((draws, k)), axis=1)))


def predicted_selection_optimism(best_cv: float, n_train: int, k: int, folds: int = 5) -> float:
    """The optimism Day 144's formula predicts for this sweep.

    Standard error of an accuracy measured on one CV fold's worth of rows,
    times the expected maximum of K standard normal draws. Both are known
    before the sweep runs, which is the entire point of the formula: it is
    a number you can compute in advance, not a warning you discover after.
    """
    n_fold = n_train // folds
    se = proportion_standard_error(best_cv, n_fold)
    return se * expected_max_of_normals(k)


def selection_optimism_over_seeds(X, y, seeds=range(20), folds: int = 5):
    """The formula's prediction against what actually happened, at each seed.

    Returns rows of ``(seed, best_cv, test_acc, measured_drop,
    predicted_optimism)``. One seed is an anecdote -- Day 144's own
    lesson about the forking-paths problem -- so this returns the whole
    distribution rather than the seed used as the headline.
    """
    k = candidate_count()
    rows = []
    for seed in seeds:
        x_train, x_test, y_train, y_test = split_once(X, y, seed=seed)
        _family, _param, cv_mean, fitted = select_best(x_train, y_train, seed=seed, folds=folds)
        test_acc = float(fitted.score(x_test, y_test))
        drop = round(cv_mean - test_acc, 4)
        predicted = round(predicted_selection_optimism(cv_mean, len(y_train), k, folds=folds), 4)
        rows.append((seed, cv_mean, round(test_acc, 4), drop, predicted))
    return rows


# --------------------------------------------------------------------------
# 7. The test set -- one look, enforced mechanically
# --------------------------------------------------------------------------


class TestSetTouchedTwice(RuntimeError):
    """Raised when the test set is evaluated against more than once."""


class GatedTestSet:
    """A test set that permits exactly one evaluation, then refuses.

    Day 144's discipline, made mechanical again: the counter does not
    advance on a refused attempt, so a caller that never succeeds cannot
    drain the budget by retrying.
    """

    def __init__(self, X, y):
        self._X = X
        self._y = y
        self.evaluations = 0

    def evaluate(self, model) -> float:
        if self.evaluations >= 1:
            raise TestSetTouchedTwice(
                "the test set has already been used once; any further score is a "
                "validation score, not a test score"
            )
        self.evaluations += 1
        return float(model.score(self._X, self._y))


# --------------------------------------------------------------------------
# 8. Error analysis -- what the confusion matrix says, once you look
# --------------------------------------------------------------------------


def confusion_and_errors(y_true, y_pred, target_names):
    """The confusion matrix, plus the two counts that matter clinically.

    Returns ``(matrix, false_negatives, false_positives)`` where a false
    negative is a malignant case predicted benign -- the costlier mistake
    in this domain, and a number worth reporting even though accuracy
    alone would hide it.
    """
    matrix = confusion_matrix(y_true, y_pred)
    malignant_index = target_names.index("malignant")
    benign_index = target_names.index("benign")
    false_negatives = int(matrix[malignant_index, benign_index])
    false_positives = int(matrix[benign_index, malignant_index])
    return matrix, false_negatives, false_positives


# --------------------------------------------------------------------------
# 9. The verdict -- an interval, not a point
# --------------------------------------------------------------------------


def verdict_interval(test_acc: float, n_test: int):
    """The 95 percent interval around the one test score this project spent.

    Returns ``(se, half_width, lower, upper)``. Day 144's sizing table
    arriving at the actual decision: is the model distinguishable from the
    baseline, given how few rows the test set actually has.
    """
    se = proportion_standard_error(test_acc, n_test)
    half_width = round(1.96 * se, 4)
    return round(se, 4), half_width, round(test_acc - half_width, 4), round(test_acc + half_width, 4)


def distinguishable_from_baseline(test_acc: float, baseline_acc: float, n_test: int) -> bool:
    """Whether the improvement over baseline exceeds the test set's own interval.

    An honest verdict may be "cannot distinguish" -- Day 144's whole point
    about test-set sizing. Here it does not come to that, and this function
    is how you would find out if it had.
    """
    _se, half_width, _lo, _hi = verdict_interval(test_acc, n_test)
    return (test_acc - baseline_acc) > half_width


# --------------------------------------------------------------------------
# 10. The leaky version -- selecting by peeking at the test set
# --------------------------------------------------------------------------


def leaky_selection_test_score(x_train, y_train, x_test, y_test):
    """Select the winner by fitting every candidate and scoring it on TEST.

    This is the mistake this whole exercise has spent nine days learning
    not to make: using the held-out set as if it were a validation set.
    Returns the winning test score -- not a validation score followed by
    one look, but K looks disguised as one.
    """
    best_score = -1.0
    for _family, _param, make in candidate_configs():
        pipe = make().fit(x_train, y_train)
        score = float(pipe.score(x_test, y_test))
        if score > best_score:
            best_score = score
    return round(best_score, 4)


def leaky_vs_honest_over_seeds(X, y, seeds=range(20), folds: int = 5):
    """The gap between peeking at the test set and looking at it once.

    Returns rows of ``(seed, honest_test, leaky_test, gap)``. Honest is
    Day 144's discipline: select on cross-validated train rows, evaluate
    the winner on test exactly once. Leaky is the mistake: fit every
    candidate and let the test set itself do the selecting.
    """
    rows = []
    for seed in seeds:
        x_train, x_test, y_train, y_test = split_once(X, y, seed=seed)
        _family, _param, _cv, fitted = select_best(x_train, y_train, seed=seed, folds=folds)
        honest_test = round(float(fitted.score(x_test, y_test)), 4)
        leaky_test = leaky_selection_test_score(x_train, y_train, x_test, y_test)
        rows.append((seed, honest_test, leaky_test, round(leaky_test - honest_test, 4)))
    return rows


# --------------------------------------------------------------------------
# 11. What the whole thing costs
# --------------------------------------------------------------------------


def timed_full_run(seed: int = 0):
    """Run frame-to-verdict once, and time it.

    Returns ``(elapsed_seconds, test_acc)``. Not asserted anywhere as a
    threshold -- machines differ -- but reported, because "how long does
    this take" is part of an honest verdict about whether the protocol is
    usable day to day.
    """
    start = time.perf_counter()
    X, y, _names = load_chosen_dataset()
    x_train, x_test, y_train, y_test = split_once(X, y, seed=seed)
    majority_baseline(x_train, y_train, x_test, y_test)
    _family, _param, _cv, fitted = select_best(x_train, y_train, seed=seed)
    gate = GatedTestSet(x_test, y_test)
    test_acc = gate.evaluate(fitted)
    elapsed = time.perf_counter() - start
    return round(elapsed, 4), round(test_acc, 4)
