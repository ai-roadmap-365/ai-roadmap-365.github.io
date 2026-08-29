"""Exercises 1, 2, 3, 4, 5, 6, 9 and 10: random variables as functions on a
sample space, their pmf/cdf, expectation, variance, and two named
distributions checked numerically.

Fill in every function below. Read `dataset.py` first -- nothing in it
needs to change. Every function that can return an exact rational answer
should return a `fractions.Fraction`.
"""

import math
from fractions import Fraction
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Exercise 1: the two-dice sum as a random variable, and its pmf
# ---------------------------------------------------------------------------


def dice_sum_pmf() -> dict[int, Fraction]:
    """The probability mass function of Y = sum of two fair dice.

    Enumerate all 36 equally likely (first die, second die) outcomes with
    `itertools.product(range(1, 7), range(1, 7))`, count how many land on
    each sum, and return {sum: Fraction(count, 36)}.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 2: the cdf, as the pmf's running total
# ---------------------------------------------------------------------------


def cdf_from_pmf(pmf: dict[int, Fraction]) -> dict[int, Fraction]:
    """F(k) = P(X <= k), built by accumulating the pmf in increasing order
    of its keys."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercises 3, 4, 5, 6: expectation, variance and covariance, computed
# exactly over any equally-weighted finite space
# ---------------------------------------------------------------------------


def expectation_pmf(pmf: dict[int, Fraction]) -> Fraction:
    """E[X] from a pmf: the weighted average of the values."""
    raise NotImplementedError


def variance_pmf(pmf: dict[int, Fraction]) -> Fraction:
    """Var[X] from a pmf: E[(X - E[X])^2]."""
    raise NotImplementedError


def expectation_over(
    outcomes: Iterable[T], weight: Fraction, func: Callable[[T], Fraction]
) -> Fraction:
    """E[func] over an equally-weighted finite space: sum(weight * func(o))
    over every outcome o. `weight` is the same Fraction for every outcome,
    since the space is equally likely."""
    raise NotImplementedError


def variance_over(
    outcomes: Iterable[T], weight: Fraction, func: Callable[[T], Fraction]
) -> Fraction:
    """Var[func] over an equally-weighted finite space. Compute the mean
    with `expectation_over` first, then the expectation of the squared
    deviation from it."""
    raise NotImplementedError


def covariance_over(
    outcomes: Iterable[T],
    weight: Fraction,
    f: Callable[[T], Fraction],
    g: Callable[[T], Fraction],
) -> Fraction:
    """Cov[f, g] = E[(f - E[f]) * (g - E[g])], over the same space."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9: Binomial and Poisson pmfs, and the gap between them
# ---------------------------------------------------------------------------


def binomial_pmf(n: int, p: float, k: int) -> float:
    """P(K = k) for K ~ Binomial(n, p). Return 0.0 if k is outside [0, n].
    `math.comb(n, k)` gives the binomial coefficient."""
    raise NotImplementedError


def poisson_pmf(lam: float, k: int) -> float:
    """P(K = k) for K ~ Poisson(lambda). Return 0.0 if k < 0."""
    raise NotImplementedError


def max_binomial_poisson_gap(n: int, p: float, lam: float, ks: Iterable[int]) -> float:
    """The largest |Binomial(n, p).pmf(k) - Poisson(lambda).pmf(k)| over the
    given range of k."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 10: a density that exceeds 1, and its integral that does not
# ---------------------------------------------------------------------------


def uniform_density(x: float, low: float, high: float) -> float:
    """The pdf of Uniform(low, high) at x: 1 / (high - low) on the
    support, 0 elsewhere."""
    raise NotImplementedError


def numeric_integral(
    f: Callable[[float], float], low: float, high: float, steps: int
) -> float:
    """The trapezoid-rule numeric integral of f over [low, high]. Raise
    ValueError if steps < 1. The trapezoid rule: split [low, high] into
    `steps` equal-width panels, weight the two endpoint evaluations by 0.5,
    weight every interior evaluation by 1, and multiply the total by the
    panel width."""
    raise NotImplementedError
