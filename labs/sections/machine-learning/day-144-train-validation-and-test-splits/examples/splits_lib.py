"""Splitting, measured: what each way of cutting a dataset actually buys.

Three sets, not two, and the reason is arithmetic rather than convention.
A validation set you select on is a set you have fitted to, and this
module measures the resulting optimism directly -- it turns out to be
exactly the expected maximum of K noise draws, which is a quantity you can
compute.

The rest measures the four ways a split goes wrong: not stratifying when
the class is rare, splitting rows when the unit is a person, splitting
randomly when the data has a direction in time, and reading a trend off
one holdout when a holdout's own spread is wider than the trend.

Everything here is deterministic given a seed.
"""

from __future__ import annotations

import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    GroupShuffleSplit,
    StratifiedKFold,
    StratifiedShuffleSplit,
    cross_val_score,
    train_test_split,
)
from sklearn.neighbors import KNeighborsClassifier


def accuracy(y_true, y_pred) -> float:
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


# --------------------------------------------------------------------------
# 1. Why three sets: selecting on a set is fitting to it
# --------------------------------------------------------------------------


def selection_replicate(k_candidates: int, n: int = 500, seed: int = 0):
    """One replication of "pick the best of K, then check it on a fresh set".

    Each candidate is a fixed prediction vector over 2n rows, split into an
    n-row validation set and an n-row test set. Every candidate has exactly
    zero skill by construction, so any validation score above 0.5 is noise
    and any *selected* validation score above 0.5 is noise you chose.

    Returns ``(best_validation_score, that_candidate_s_test_score)``.
    """
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=2 * n)
    predictions = rng.integers(0, 2, size=(k_candidates, 2 * n))
    correct = predictions == y
    validation = correct[:, :n].mean(axis=1)
    test = correct[:, n:].mean(axis=1)
    winner = int(np.argmax(validation))
    return float(validation[winner]), float(test[winner])


def selection_bias_curve(k_values, replications: int = 400, n: int = 500):
    """Mean selected-validation score and its test score, for each K.

    Returns rows of ``(k, mean_validation, mean_test, optimism)``. The test
    column is the control: it must stay at chance for every K, because the
    test set was never selected on.
    """
    rows = []
    for k in k_values:
        pairs = [selection_replicate(k, n=n, seed=r) for r in range(replications)]
        validation = float(np.mean([v for v, _t in pairs]))
        test = float(np.mean([t for _v, t in pairs]))
        rows.append((k, round(validation, 4), round(test, 4), round(validation - test, 4)))
    return rows


def proportion_standard_error(p: float, n: int) -> float:
    """The standard error of an accuracy estimated on n rows."""
    return float(np.sqrt(p * (1.0 - p) / n))


def expected_max_of_normals(k: int, draws: int = 20000, seed: int = 7) -> float:
    """E of the maximum of k standard normals, by simulation.

    This is the quantity the selection optimism should equal, once the
    optimism is expressed in standard errors. Simulated rather than
    approximated, because the usual closed form overestimates it -- which
    exercise 1c measures.
    """
    rng = np.random.default_rng(seed)
    return float(np.mean(np.max(rng.standard_normal((draws, k)), axis=1)))


def sqrt_two_log_k(k: int) -> float:
    """The textbook asymptotic for the expected maximum of k normals."""
    return 0.0 if k <= 1 else float(np.sqrt(2.0 * np.log(k)))


# --------------------------------------------------------------------------
# 2. Stratification: a rare class and a small test set
# --------------------------------------------------------------------------


def rare_class_dataset(n: int = 200, rate: float = 0.05, seed: int = 144):
    """A dataset with a genuinely rare positive class."""
    rng = np.random.default_rng(seed)
    y = np.zeros(n, dtype=int)
    y[: int(n * rate)] = 1
    X = rng.normal(size=(n, 3))
    return X, y


def split_positive_rates(X, y, splits: int = 500, test_size: float = 0.25):
    """Positive rate in the test half, over many random and stratified splits.

    Returns ``(random_rates, stratified_rates, random_splits_with_no_positives)``.
    """
    random_rates = []
    stratified_rates = []
    empty = 0
    for seed in range(splits):
        _x_tr, _x_te, _y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=seed)
        random_rates.append(float(y_te.mean()))
        if y_te.sum() == 0:
            empty += 1
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        _train, test = next(splitter.split(X, y))
        stratified_rates.append(float(y[test].mean()))
    return random_rates, stratified_rates, empty


def spread(values) -> dict:
    """Mean, standard deviation, minimum and maximum, rounded for reporting."""
    values = np.asarray(values, dtype=float)
    return {
        "mean": round(float(values.mean()), 4),
        "sd": round(float(values.std()), 4),
        "min": round(float(values.min()), 4),
        "max": round(float(values.max()), 4),
    }


# --------------------------------------------------------------------------
# 3. Groups: when the row is not the unit
# --------------------------------------------------------------------------


def grouped_dataset(n_people: int = 50, rows_each: int = 20, seed: int = 5):
    """Twenty rows per person, and the label is a property of the PERSON.

    There is nothing generalisable here at all: each person's label is a
    coin flip, so a model can only score above chance on a person it has
    already seen. Which is exactly what a row-wise split hands it.
    """
    rng = np.random.default_rng(seed)
    groups = np.repeat(np.arange(n_people), rows_each)
    person_signature = rng.normal(size=(n_people, 4)) * 2.0
    X = person_signature[groups] + rng.normal(size=(n_people * rows_each, 4)) * 0.3
    person_label = rng.integers(0, 2, size=n_people)
    return X, person_label[groups], groups


def rowwise_vs_group_split(X, y, groups, splits: int = 20, test_size: float = 0.25):
    """Score a 1-NN under a row-wise split and under a group-aware one."""
    rowwise = []
    grouped = []
    for seed in range(splits):
        train, test = train_test_split(np.arange(len(y)), test_size=test_size, random_state=seed)
        model = KNeighborsClassifier(1).fit(X[train], y[train])
        rowwise.append(accuracy(y[test], model.predict(X[test])))

        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_g, test_g = next(splitter.split(X, y, groups))
        model_g = KNeighborsClassifier(1).fit(X[train_g], y[train_g])
        grouped.append(accuracy(y[test_g], model_g.predict(X[test_g])))
    return float(np.mean(rowwise)), float(np.mean(grouped))


def groups_shared_between_halves(groups, test_size: float = 0.25, seed: int = 0) -> int:
    """How many people appear in BOTH halves of a row-wise split."""
    train, test = train_test_split(np.arange(len(groups)), test_size=test_size, random_state=seed)
    return len(set(groups[train].tolist()) & set(groups[test].tolist()))


# --------------------------------------------------------------------------
# 4. Time: when the data has a direction
# --------------------------------------------------------------------------


def regime_series(length: int = 1200, n_regimes: int = 6, seed: int = 9):
    """A series in which the rule mapping features to labels changes.

    Six regimes, each with its own randomly drawn linear rule. A random
    shuffle scatters every regime across both halves, so the model always
    has neighbours from the same regime. A chronological split asks it to
    predict a regime it has never seen -- which is what deployment does.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(length, 4))
    y = np.empty(length, dtype=int)
    block = length // n_regimes
    for r in range(n_regimes):
        rule = rng.normal(size=4)
        window = slice(r * block, (r + 1) * block)
        y[window] = (X[window] @ rule > 0).astype(int)
    return X, y


def shuffled_vs_chronological(X, y, splits: int = 10, test_size: float = 0.25):
    """Score a 5-NN under a shuffled split and under a chronological one.

    Returns ``(mean_shuffled, chronological, majority_baseline_on_the_tail)``.
    """
    shuffled = []
    for seed in range(splits):
        train, test = train_test_split(
            np.arange(len(y)), test_size=test_size, random_state=seed, shuffle=True
        )
        model = KNeighborsClassifier(5).fit(X[train], y[train])
        shuffled.append(accuracy(y[test], model.predict(X[test])))

    cut = int(len(y) * (1.0 - test_size))
    model = KNeighborsClassifier(5).fit(X[:cut], y[:cut])
    chronological = accuracy(y[cut:], model.predict(X[cut:]))
    tail = y[cut:]
    baseline = float(max(tail.mean(), 1.0 - tail.mean()))
    return float(np.mean(shuffled)), chronological, baseline


def temporal_inflation_over_constructions(constructions: int = 20, splits: int = 10):
    """The same comparison over many independently generated series.

    One construction is an anecdote. Reporting the seed that gave the
    largest gap would be the forking-paths problem in a lesson about not
    doing that -- so this returns the whole distribution.
    """
    rows = []
    for seed in range(constructions):
        X, y = regime_series(seed=seed)
        shuffled, chronological, baseline = shuffled_vs_chronological(X, y, splits=splits)
        rows.append((seed, shuffled, chronological, baseline, shuffled - chronological))
    return rows


# --------------------------------------------------------------------------
# 5. One holdout, or many folds
# --------------------------------------------------------------------------


def weak_signal_dataset(n: int = 400, seed: int = 21):
    """A real but modest relationship, so the estimate has something to vary around."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 4))
    y = (X[:, 0] + X[:, 1] * 0.6 + rng.normal(size=n) * 1.2 > 0).astype(int)
    return X, y


def holdout_vs_cross_validation(X, y, repeats: int = 200, test_size: float = 0.25, folds: int = 5):
    """The spread of a single-holdout estimate against a k-fold estimate.

    Same data, same model. The only thing that changes between repeats is
    which rows landed where.
    """
    holdout = []
    cross = []
    for seed in range(repeats):
        train, test = train_test_split(
            np.arange(len(y)), test_size=test_size, random_state=seed, stratify=y
        )
        model = LogisticRegression(max_iter=1000).fit(X[train], y[train])
        holdout.append(accuracy(y[test], model.predict(X[test])))

        cross.append(
            float(
                np.mean(
                    cross_val_score(
                        LogisticRegression(max_iter=1000),
                        X,
                        y,
                        cv=StratifiedKFold(folds, shuffle=True, random_state=seed),
                    )
                )
            )
        )
    return holdout, cross


# --------------------------------------------------------------------------
# 6. How big does the test set need to be?
# --------------------------------------------------------------------------


def test_size_table(sizes, p: float = 0.85, draws: int = 20000, seed: int = 33):
    """Predicted and measured standard error of an accuracy, by test-set size.

    Rows are ``(n, theoretical_se, measured_sd, half_width_of_95_interval)``.
    The theory is Day 117's; this is it arriving where the decisions are.
    """
    rows = []
    for n in sizes:
        theory = proportion_standard_error(p, n)
        sample = np.random.default_rng(seed).binomial(n, p, size=draws) / n
        rows.append((n, round(theory, 4), round(float(sample.std()), 4), round(1.96 * theory, 4)))
    return rows


def rows_needed_for_precision(p: float, half_width: float) -> int:
    """Smallest test set whose 95 percent interval is no wider than requested."""
    n = int(np.ceil(p * (1.0 - p) * (1.96 / half_width) ** 2))
    return n


# --------------------------------------------------------------------------
# 7. The rule, made checkable
# --------------------------------------------------------------------------


class TestSetTouchedTwice(RuntimeError):
    """Raised when the test set is evaluated against more than once."""


class GatedTestSet:
    """A test set that permits exactly one evaluation, then refuses.

    Not a substitute for discipline. It is the discipline made mechanical,
    in the same spirit as Day 143's stage contract: a rule that lives in
    code is a rule somebody can check.
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
        return accuracy(self._y, model.predict(self._X))
