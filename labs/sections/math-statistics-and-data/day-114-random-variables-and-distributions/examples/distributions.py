"""Exercises 1, 2, 3, 4, 5, 6, 9 and 10: random variables as functions on a
sample space, their pmf/cdf, expectation, variance, and two named
distributions checked numerically.

Every function that can return an exact rational answer returns a
`fractions.Fraction`. Only the named-distribution helpers at the bottom --
which exist to compare a Binomial against a Poisson, and a density against
its integral -- return plain floats, because factorials and exponentials are
not rational.
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

    Built by enumerating all 36 equally likely outcomes and counting how
    many land on each sum -- not by looking up a formula.
    """
    from itertools import product

    counts: dict[int, int] = {}
    for a, b in product(range(1, 7), range(1, 7)):
        total = a + b
        counts[total] = counts.get(total, 0) + 1
    return {k: Fraction(v, 36) for k, v in sorted(counts.items())}


# ---------------------------------------------------------------------------
# Exercise 2: the cdf, as the pmf's running total
# ---------------------------------------------------------------------------


def cdf_from_pmf(pmf: dict[int, Fraction]) -> dict[int, Fraction]:
    """The cumulative distribution function: F(k) = P(X <= k), built by
    accumulating the pmf in increasing order of its keys."""
    running = Fraction(0)
    cdf: dict[int, Fraction] = {}
    for key in sorted(pmf):
        running += pmf[key]
        cdf[key] = running
    return cdf


# ---------------------------------------------------------------------------
# Exercises 3, 4, 5, 6: expectation, variance and covariance, computed
# exactly over any equally-weighted finite space
# ---------------------------------------------------------------------------


def expectation_pmf(pmf: dict[int, Fraction]) -> Fraction:
    """E[X] from a pmf: the weighted average of the values."""
    total = Fraction(0)
    for value, prob in pmf.items():
        total += value * prob
    return total


def variance_pmf(pmf: dict[int, Fraction]) -> Fraction:
    """Var[X] from a pmf: E[(X - E[X])^2]."""
    mean = expectation_pmf(pmf)
    total = Fraction(0)
    for value, prob in pmf.items():
        total += prob * (value - mean) ** 2
    return total


def expectation_over(
    outcomes: Iterable[T], weight: Fraction, func: Callable[[T], Fraction]
) -> Fraction:
    """E[func] over an equally-weighted finite space: sum(weight * func(o)).

    This is the general tool exercises 4, 5 and 6 use: pass it a different
    `func` (the identity, X + Y, X squared, ...) over the SAME 36-outcome
    joint space and it computes the expectation of whatever function you
    hand it, exactly.
    """
    total = Fraction(0)
    for outcome in outcomes:
        total += weight * func(outcome)
    return total


def variance_over(
    outcomes: Iterable[T], weight: Fraction, func: Callable[[T], Fraction]
) -> Fraction:
    """Var[func] over an equally-weighted finite space."""
    outcomes = list(outcomes)
    mean = expectation_over(outcomes, weight, func)
    return expectation_over(outcomes, weight, lambda o: (func(o) - mean) ** 2)


def covariance_over(
    outcomes: Iterable[T],
    weight: Fraction,
    f: Callable[[T], Fraction],
    g: Callable[[T], Fraction],
) -> Fraction:
    """Cov[f, g] = E[(f - E[f]) * (g - E[g])], over the same space."""
    outcomes = list(outcomes)
    mean_f = expectation_over(outcomes, weight, f)
    mean_g = expectation_over(outcomes, weight, g)
    return expectation_over(
        outcomes, weight, lambda o: (f(o) - mean_f) * (g(o) - mean_g)
    )


# ---------------------------------------------------------------------------
# Exercise 9: Binomial and Poisson pmfs, and the gap between them
# ---------------------------------------------------------------------------


def binomial_pmf(n: int, p: float, k: int) -> float:
    """P(K = k) for K ~ Binomial(n, p)."""
    if not 0 <= k <= n:
        return 0.0
    return math.comb(n, k) * (p**k) * ((1.0 - p) ** (n - k))


def poisson_pmf(lam: float, k: int) -> float:
    """P(K = k) for K ~ Poisson(lambda)."""
    if k < 0:
        return 0.0
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def max_binomial_poisson_gap(n: int, p: float, lam: float, ks: Iterable[int]) -> float:
    """The largest |Binomial(n, p).pmf(k) - Poisson(lambda).pmf(k)| over the
    given range of k. As n grows with n * p held at lambda, this gap shrinks
    to zero -- that convergence IS the Poisson limit theorem, and this
    function is what measures it."""
    return max(
        abs(binomial_pmf(n, p, k) - poisson_pmf(lam, k)) for k in ks
    )


# ---------------------------------------------------------------------------
# Exercise 10: a density that exceeds 1, and its integral that does not
# ---------------------------------------------------------------------------


def uniform_density(x: float, low: float, high: float) -> float:
    """The pdf of Uniform(low, high) at x: a constant 1 / (high - low) on
    the support, 0 elsewhere. For Uniform(0, 0.5) that constant is 2 -- a
    density greater than 1, which is legal, because a density is not a
    probability."""
    if low <= x <= high:
        return 1.0 / (high - low)
    return 0.0


def numeric_integral(
    f: Callable[[float], float], low: float, high: float, steps: int
) -> float:
    """The trapezoid-rule numeric integral of f over [low, high], used here
    to confirm that a density integrates to exactly 1 even though its value
    everywhere on the support is 2."""
    if steps < 1:
        raise ValueError("steps must be at least 1")
    width = (high - low) / steps
    total = 0.5 * (f(low) + f(high))
    for i in range(1, steps):
        total += f(low + i * width)
    return total * width
