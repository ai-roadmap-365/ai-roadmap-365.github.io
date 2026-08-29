"""Exercises 1, 2, 4, 5, 6, 7 and 9. Write the functions below.

Every function that has an exact answer should avoid floating-point
surprises where possible; every function that depends on an interpolation
convention (the percentile) should make that convention an explicit
argument rather than hiding a default.

Read `00_brief.md` for the exercise-by-exercise instructions, and
`dataset.py` for the exact inputs each exercise is checked against.
"""

from collections import Counter
from typing import Sequence


# ---------------------------------------------------------------------------
# Exercise 1: mean, median, mode, from scratch
# ---------------------------------------------------------------------------


def mean(values: Sequence[float]) -> float:
    """The arithmetic mean: the sum divided by the count."""
    raise NotImplementedError


def median(values: Sequence[float]) -> float:
    """The middle value once sorted; the average of the two middle values
    when the count is even."""
    raise NotImplementedError


def modes(values: Sequence[float]) -> list[float]:
    """Every value that occurs the maximum number of times, sorted."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 2: the breakdown point
# ---------------------------------------------------------------------------


def breakdown_point_mean(values: Sequence[float], corrupted_value: float) -> tuple[float, float]:
    """Replace the largest value with `corrupted_value`; return
    (mean before, mean after)."""
    raise NotImplementedError


def breakdown_point_median(values: Sequence[float], corrupted_value: float) -> tuple[float, float]:
    """The same replacement, but tracking the median instead of the mean."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 4: percentile ambiguity
# ---------------------------------------------------------------------------


def percentile_under(values: Sequence[float], target: float, method: str) -> float:
    """`numpy.percentile` under one named interpolation convention."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 5: Pearson versus Spearman
# ---------------------------------------------------------------------------


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    """Pearson's r: the standardized covariance, measuring LINEAR
    association only. `statistics.correlation` does this correctly."""
    raise NotImplementedError


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman's rank correlation: Pearson's r computed on the RANKS of x
    and y. Rank ties by their AVERAGE rank position."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 6: Anscombe's quartet
# ---------------------------------------------------------------------------


def anscombe_summary(x: Sequence[float], y: Sequence[float]) -> dict[str, float]:
    """mean_x, mean_y, var_x, var_y, correlation, slope, intercept."""
    raise NotImplementedError


def shape_statistics(x: Sequence[float], y: Sequence[float]) -> dict[str, float]:
    """max_leverage, outlier_ratio, residual_sign_changes -- see
    `examples/descriptive.py` for the full explanation of each, once you
    have tried this yourself."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 7: Simpson's paradox
# ---------------------------------------------------------------------------


def success_rate(successes: int, trials: int) -> float:
    raise NotImplementedError


def combined_rate(*subgroups: tuple[int, int]) -> float:
    """The overall success rate across several (successes, trials)
    subgroups -- total successes over total trials, NOT the average of the
    subgroup rates."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8 helper: median absolute deviation
# ---------------------------------------------------------------------------


def median_absolute_deviation(values: Sequence[float]) -> float:
    """The median of the absolute deviations from the median."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9: standardisation and z-scores
# ---------------------------------------------------------------------------


def zscores(values: Sequence[float]) -> list[float]:
    """(x - mean) / population standard deviation, for every value."""
    raise NotImplementedError
