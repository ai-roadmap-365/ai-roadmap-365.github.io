"""Feature builders, every one of them split into `fit` and `transform`.

The split is the whole discipline of this lab. `fit` looks at data and
learns a statistic -- a mean, a standard deviation, a category's average
outcome, a vocabulary. `transform` applies a statistic that has already
been learned and looks at nothing. Once the two are separate functions
you can point `fit` at the training rows only, and the question "did the
test set influence this number?" has an answer you can read off the call
site instead of guessing at it.

Nothing here imports scikit-learn -- it is not installed in this lab.
Everything is NumPy and pandas, small enough to read.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

TOKEN = re.compile(r"[a-z0-9]+")


# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------


class Standardiser:
    """Subtract a mean and divide by a standard deviation (Day 107).

    `fit` records the two statistics. `transform` applies them. Fitting on
    rows you will later score is the second kind of leakage, and the only
    thing stopping you is which rows you hand to `fit`.
    """

    def __init__(self) -> None:
        self.mean_: np.ndarray | None = None
        self.scale_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "Standardiser":
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        scale = X.std(axis=0)
        # A constant column has zero spread; dividing by it would produce
        # infinities, so it is left alone rather than exploded.
        self.scale_ = np.where(scale == 0.0, 1.0, scale)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("fit before transform")
        return (np.asarray(X, dtype=float) - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class GroupMeanImputer:
    """Fill a missing value with the mean of its group (Day 125).

    `fit` records one mean per group, plus a global fallback for groups
    it never saw. Like every other statistic in this file it reads rows,
    so which rows it reads is a decision -- and with small groups it is
    the most consequential decision in this lab.
    """

    def __init__(self) -> None:
        self.means_: dict[str, float] = {}
        self.default_: float = 0.0

    def fit(self, groups, values) -> "GroupMeanImputer":
        frame = pd.DataFrame(
            {"group": pd.Series(groups).astype("str"), "value": np.asarray(values, dtype=float)}
        ).dropna(subset=["value"])
        self.means_ = {
            str(k): float(v) for k, v in frame.groupby("group")["value"].mean().items()
        }
        self.default_ = float(frame["value"].mean()) if len(frame) else 0.0
        return self

    def transform(self, groups, values) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        filled = values.copy()
        for i, (group, value) in enumerate(zip(pd.Series(groups).astype("str"), values)):
            if np.isnan(value):
                filled[i] = self.means_.get(str(group), self.default_)
        return filled


# ---------------------------------------------------------------------------
# Categorical encodings
# ---------------------------------------------------------------------------


def one_hot(values, categories: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    """One column of 0/1 per category, in a fixed, explicit category order.

    The category list is returned so the caller can reuse it at transform
    time. A test row carrying a category the training data never held
    becomes an all-zero row rather than a crash or a new column.
    """
    values = pd.Series(values).astype("str")
    if categories is None:
        categories = sorted(values.unique().tolist())
    matrix = np.zeros((len(values), len(categories)), dtype=float)
    position = {name: i for i, name in enumerate(categories)}
    for row, name in enumerate(values):
        column = position.get(name)
        if column is not None:
            matrix[row, column] = 1.0
    return matrix, list(categories)


def ordinal_encode(values, order: list[str]) -> np.ndarray:
    """Replace each category with its position in `order`.

    Honest when the order is real (small, medium, large). A trap when it
    is not: the code is a number, and a model reading it as a number can
    and will interpolate between categories that have no midpoint.
    """
    position = {name: float(i) for i, name in enumerate(order)}
    return np.array([position[str(v)] for v in values], dtype=float)


def target_encode_fit(categories, y) -> tuple[dict[str, float], float]:
    """Learn the mean outcome per category, plus the global mean.

    Returns the map and the fallback. Call this on TRAINING rows only:
    it reads the target, so fitting it on everything hands each test row
    a number computed partly from its own answer.
    """
    frame = pd.DataFrame({"category": pd.Series(categories).astype("str"), "y": np.asarray(y, dtype=float)})
    means = frame.groupby("category")["y"].mean()
    return {str(k): float(v) for k, v in means.items()}, float(frame["y"].mean())


def target_encode_transform(categories, mapping: dict[str, float], default: float) -> np.ndarray:
    """Apply a learned target encoding; unseen categories get the prior."""
    return np.array([mapping.get(str(c), default) for c in categories], dtype=float)


def target_encode_out_of_fold(categories, y, n_folds: int = 5, seed: int = 0) -> np.ndarray:
    """Encode each training row from the folds that do NOT contain it.

    This is the fix, and it is worth stating precisely what it fixes: a
    row's own target never contributes to its own feature value. The
    encoding is still built from training data only; out-of-fold does not
    excuse fitting on the test set.
    """
    categories = pd.Series(categories).astype("str").to_numpy()
    y = np.asarray(y, dtype=float)
    n = len(y)
    rng = np.random.default_rng(seed)
    fold_of = rng.permutation(n) % n_folds
    encoded = np.empty(n, dtype=float)
    for fold in range(n_folds):
        held_out = fold_of == fold
        mapping, default = target_encode_fit(categories[~held_out], y[~held_out])
        encoded[held_out] = target_encode_transform(categories[held_out], mapping, default)
    return encoded


# ---------------------------------------------------------------------------
# Datetime, cyclical, binning, interactions
# ---------------------------------------------------------------------------


def calendar_features(timestamps: pd.Series) -> pd.DataFrame:
    """The obvious datetime parts, pulled out as separate columns."""
    ts = pd.to_datetime(timestamps)
    return pd.DataFrame(
        {
            "hour": ts.dt.hour.astype(float),
            "day_of_week": ts.dt.dayofweek.astype(float),
            "day_of_month": ts.dt.day.astype(float),
            "month": ts.dt.month.astype(float),
            "is_weekend": (ts.dt.dayofweek >= 5).astype(float),
        }
    )


def cyclical_encode(values, period: float) -> np.ndarray:
    """Map a wrapping quantity onto a circle: two columns, sine and cosine.

    Hour 23 and hour 0 are one hour apart in the world and 23 apart as
    integers. On the circle they are neighbours again, and every pair of
    adjacent hours sits exactly the same distance apart.
    """
    angle = 2.0 * np.pi * np.asarray(values, dtype=float) / float(period)
    return np.column_stack([np.sin(angle), np.cos(angle)])


def equal_width_bins(values, bins: int) -> np.ndarray:
    """Bin edges, from NumPy's own edge calculator (Day 130's bin width)."""
    return np.histogram_bin_edges(np.asarray(values, dtype=float), bins=bins)


def bin_index(values, edges: np.ndarray) -> np.ndarray:
    """Which bin each value falls in, given edges learned elsewhere.

    Values below the first edge or above the last are clamped into the
    end bins rather than dropped: a bin boundary is a decision, and the
    decision has to cover values the training data never contained.
    """
    idx = np.digitize(np.asarray(values, dtype=float), edges[1:-1], right=False)
    return idx.astype(float)


def ratio_feature(numerator, denominator, epsilon: float = 1e-12) -> np.ndarray:
    """One column divided by another, with a guard against a zero divisor."""
    denominator = np.asarray(denominator, dtype=float)
    return np.asarray(numerator, dtype=float) / np.where(
        np.abs(denominator) < epsilon, epsilon, denominator
    )


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------


def tokenize(document: str) -> list[str]:
    return TOKEN.findall(str(document).lower())


@dataclass
class Vocabulary:
    """A bag-of-words vocabulary, chosen by association with the target.

    `top_k` words are kept: the ones whose presence correlates most
    strongly with the label. That selection reads the target, so which
    rows you fit it on is exactly as consequential as it is for a target
    encoding. `min_docs` drops words too rare to estimate anything from.
    """

    top_k: int = 20
    min_docs: int = 3
    words: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    def fit(self, documents, y) -> "Vocabulary":
        y = np.asarray(y, dtype=float)
        tokenized = [set(tokenize(d)) for d in documents]
        counts: Counter[str] = Counter()
        for bag in tokenized:
            counts.update(bag)
        candidates = [w for w, c in counts.items() if c >= self.min_docs]
        scored: list[tuple[float, str]] = []
        for word in candidates:
            present = np.array([1.0 if word in bag else 0.0 for bag in tokenized])
            if present.std() == 0.0 or y.std() == 0.0:
                continue
            correlation = float(np.corrcoef(present, y)[0, 1])
            scored.append((abs(correlation), word))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        self.words = [word for _, word in scored[: self.top_k]]
        self.scores = {word: score for score, word in scored[: self.top_k]}
        return self

    def transform(self, documents) -> np.ndarray:
        position = {word: i for i, word in enumerate(self.words)}
        matrix = np.zeros((len(documents), len(self.words)), dtype=float)
        for row, document in enumerate(documents):
            for token in tokenize(document):
                column = position.get(token)
                if column is not None:
                    matrix[row, column] += 1.0
        return matrix

    def unseen_words(self, documents) -> set[str]:
        """Tokens in these documents that the vocabulary does not carry."""
        known = set(self.words)
        seen: set[str] = set()
        for document in documents:
            seen.update(tokenize(document))
        return seen - known


# ---------------------------------------------------------------------------
# The audit
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Flag:
    """One suspicious feature, with the reason it was flagged."""

    column: str
    rule: str
    detail: str


def leakage_audit(
    frame: pd.DataFrame,
    target: str,
    corr_threshold: float = 0.90,
) -> list[Flag]:
    """Flag columns that look like they already know the answer.

    Three rules, and each one has a name so a flag can be argued with:

    * `correlation` -- a numeric column whose absolute Pearson
      correlation with the target is at or above `corr_threshold`.
    * `separable` -- a numeric column where a single threshold splits the
      classes perfectly, which catches leaks a linear correlation misses.
    * `pure_category` -- a non-numeric column where every category occurs
      with exactly one target value, so the column is the target wearing
      different words.

    What this cannot do is the point of the exercise. It reads one table
    at one moment, so it cannot see a scaler fitted on the wrong rows, it
    cannot see that a column will be unavailable at prediction time, and
    it cannot see a value that was backfilled from the future. It catches
    the loud leaks. The quiet ones are still your job.
    """
    y = frame[target].to_numpy()
    flags: list[Flag] = []
    for column in frame.columns:
        if column == target:
            continue
        series = frame[column]
        if pd.api.types.is_numeric_dtype(series):
            values = series.to_numpy(dtype=float)
            if values.std() == 0.0:
                continue
            correlation = float(np.corrcoef(values, y.astype(float))[0, 1])
            if abs(correlation) >= corr_threshold:
                flags.append(
                    Flag(column, "correlation", f"|r| = {abs(correlation):.3f} with {target!r}")
                )
                continue
            if _perfectly_separable(values, y):
                flags.append(
                    Flag(column, "separable", f"one threshold splits {target!r} without error")
                )
        else:
            grouped = frame.groupby(series.astype("str"))[target].nunique()
            if len(grouped) > 1 and int(grouped.max()) == 1:
                flags.append(
                    Flag(column, "pure_category", f"every category maps to one {target!r} value")
                )
    return flags


def _perfectly_separable(values: np.ndarray, y: np.ndarray) -> bool:
    """True when some threshold on `values` classifies `y` with no error."""
    classes = np.unique(y)
    if len(classes) != 2:
        return False
    order = np.argsort(values)
    sorted_y = y[order]
    positives = np.cumsum(sorted_y == classes[1])
    negatives = np.cumsum(sorted_y == classes[0])
    total_positive = positives[-1]
    total_negative = negatives[-1]
    for i in range(len(sorted_y) - 1):
        if values[order][i] == values[order][i + 1]:
            continue
        left_correct = negatives[i] + (total_positive - positives[i])
        right_correct = positives[i] + (total_negative - negatives[i])
        if left_correct == len(sorted_y) or right_correct == len(sorted_y):
            return True
    return False
