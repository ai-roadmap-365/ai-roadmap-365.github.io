"""Exercises 1, 2, 4, 5, 6, 7 and 9: statistics computed from scratch, and
checked against a second, independent way of getting the same number.

Every function that has an exact answer avoids floating-point surprises
where it can (the mean and mode use exact arithmetic on the inputs given
here); every function that depends on an interpolation convention (the
percentile) makes that convention an explicit argument rather than hiding a
default.
"""

import math
from collections import Counter
from typing import Sequence


# ---------------------------------------------------------------------------
# Exercise 1: mean, median, mode, from scratch
# ---------------------------------------------------------------------------


def mean(values: Sequence[float]) -> float:
    """The arithmetic mean: the sum divided by the count."""
    values = list(values)
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """The middle value once sorted; the average of the two middle values
    when the count is even."""
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def modes(values: Sequence[float]) -> list[float]:
    """Every value that occurs the maximum number of times. A list, not a
    single value, because a distribution can be multimodal."""
    counts = Counter(values)
    top = max(counts.values())
    return sorted(v for v, c in counts.items() if c == top)


# ---------------------------------------------------------------------------
# Exercise 2: the breakdown point
# ---------------------------------------------------------------------------


def breakdown_point_mean(values: Sequence[float], corrupted_value: float) -> tuple[float, float]:
    """Replace the largest value with `corrupted_value`; return
    (mean before, mean after)."""
    ordered = sorted(values)
    before = mean(ordered)
    corrupted = ordered[:-1] + [corrupted_value]
    after = mean(corrupted)
    return before, after


def breakdown_point_median(values: Sequence[float], corrupted_value: float) -> tuple[float, float]:
    """The same replacement, but tracking the median instead of the mean."""
    ordered = sorted(values)
    before = median(ordered)
    corrupted = ordered[:-1] + [corrupted_value]
    after = median(corrupted)
    return before, after


# ---------------------------------------------------------------------------
# Exercise 4: percentile ambiguity -- deliberately NOT resolved to one
# function. The point of this exercise is that "the" 75th percentile does
# not exist; this helper just calls NumPy with an explicit method, so every
# call site is forced to say which convention it means.
# ---------------------------------------------------------------------------


def percentile_under(values: Sequence[float], target: float, method: str) -> float:
    """`numpy.percentile` under one named interpolation convention."""
    import numpy as np

    return float(np.percentile(np.asarray(values, dtype=float), target, method=method))


# ---------------------------------------------------------------------------
# Exercise 5: Pearson versus Spearman
# ---------------------------------------------------------------------------


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    """Pearson's r: the standardized covariance, measuring LINEAR
    association only."""
    import statistics as st

    return st.correlation(list(x), list(y))


def _rank(values: Sequence[float]) -> list[float]:
    """Fractional (average) ranks, so tied values share the mean of the
    rank positions they occupy -- the standard convention Spearman's
    correlation uses."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = average_rank
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman's rank correlation: Pearson's r computed on the RANKS of x
    and y, measuring monotone association regardless of shape."""
    return pearson(_rank(list(x)), _rank(list(y)))


# ---------------------------------------------------------------------------
# Exercise 6: Anscombe's quartet
# ---------------------------------------------------------------------------


def anscombe_summary(x: Sequence[float], y: Sequence[float]) -> dict[str, float]:
    """The five classic summary statistics: mean x, mean y, variance x,
    variance y, Pearson correlation, and the fitted regression slope."""
    import statistics as st

    x, y = list(x), list(y)
    slope, intercept = st.linear_regression(x, y)
    return {
        "mean_x": st.fmean(x),
        "mean_y": st.fmean(y),
        "var_x": st.variance(x),
        "var_y": st.variance(y),
        "correlation": st.correlation(x, y),
        "slope": slope,
        "intercept": intercept,
    }


def shape_statistics(x: Sequence[float], y: Sequence[float]) -> dict[str, float]:
    """Three diagnostics the five classic summary numbers do NOT capture --
    each one, on its own, is unremarkable for an ordinary linear
    relationship, and each one is exactly what makes one Anscombe set
    different from the other three, for three different structural
    reasons.

    - ``max_leverage``: how much a single x-value alone (before y is even
      considered) could determine the fitted line. Depends only on the x
      values, so it is identical for any two datasets that share an x
      column -- and dramatically different for a dataset whose x values
      are not spread out the same way.
    - ``outlier_ratio``: the largest single residual, divided by the sum
      of every OTHER residual's magnitude. Large when one point's
      deviation from the fitted line dwarfs everyone else's combined.
    - ``residual_sign_changes``: walking the residuals in x-order, how
      many times the sign flips. Scattered, honestly linear noise flips
      sign often; one smooth systematic curve (a fitted line failing to
      follow a genuine bend) flips rarely.
    """
    import statistics as st

    x, y = list(x), list(y)
    n = len(x)
    slope, intercept = st.linear_regression(x, y)
    residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]

    mean_x = st.fmean(x)
    ss_x = sum((xi - mean_x) ** 2 for xi in x)
    leverages = [1.0 / n + (xi - mean_x) ** 2 / ss_x for xi in x]

    abs_residuals = sorted((abs(r) for r in residuals), reverse=True)
    largest, rest = abs_residuals[0], sum(abs_residuals[1:])
    outlier_ratio = largest / rest if rest > 0 else math.inf

    order = sorted(range(n), key=lambda i: x[i])
    ordered_residuals = [residuals[i] for i in order]
    sign_changes = sum(
        1
        for i in range(n - 1)
        if ordered_residuals[i] * ordered_residuals[i + 1] < 0
    )

    return {
        "max_leverage": max(leverages),
        "outlier_ratio": outlier_ratio,
        "residual_sign_changes": float(sign_changes),
    }


# ---------------------------------------------------------------------------
# Exercise 7: Simpson's paradox
# ---------------------------------------------------------------------------


def success_rate(successes: int, trials: int) -> float:
    return successes / trials


def combined_rate(*subgroups: tuple[int, int]) -> float:
    """The overall success rate across several (successes, trials)
    subgroups -- NOT the average of the subgroup rates, but the total
    successes over the total trials, which is what "overall rate" means and
    exactly where Simpson's paradox hides."""
    total_successes = sum(s for s, _ in subgroups)
    total_trials = sum(t for _, t in subgroups)
    return total_successes / total_trials


# ---------------------------------------------------------------------------
# Exercise 8 helper: median absolute deviation (the simulation itself lives
# in simulate.py, since it draws random contamination)
# ---------------------------------------------------------------------------


def median_absolute_deviation(values: Sequence[float]) -> float:
    """MAD: the median of the absolute deviations from the median. A
    robust measure of spread -- corrupting a small fraction of the data
    moves it far less than it moves the standard deviation."""
    values = list(values)
    m = median(values)
    return median([abs(v - m) for v in values])


def population_std(values: Sequence[float]) -> float:
    """The (ddof=0) standard deviation, used for the clean/contaminated
    comparison in exercise 8 -- either ddof gives the same qualitative
    story, this lab's tests use the sample (ddof=1) version via NumPy for
    consistency with `numpy.std(ddof=1)`."""
    import statistics as st

    return st.pstdev(values)


# ---------------------------------------------------------------------------
# Exercise 9: standardisation and z-scores
# ---------------------------------------------------------------------------


def zscores(values: Sequence[float]) -> list[float]:
    """(x - mean) / population standard deviation, for every value."""
    import statistics as st

    values = list(values)
    m = st.fmean(values)
    s = st.pstdev(values)
    return [(v - m) / s for v in values]
