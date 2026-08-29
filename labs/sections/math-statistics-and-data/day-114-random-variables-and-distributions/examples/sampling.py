"""Exercises 7 and 8: the inverse-CDF sampling method, written from scratch,
for both a discrete pmf and the exponential distribution -- and a max-gap
statistic to compare two empirical distributions by hand, since scipy is
not installed here.

The idea behind every function in this file is the same one: a single
uniform draw U on (0, 1), pushed through the inverse of a target CDF,
lands on a sample from that target distribution. `numpy.random.Generator`
does exactly this internally for the distributions it knows how to sample;
this file demystifies it by building both halves yourself.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 7: inverse-CDF sampling for an arbitrary discrete distribution
# ---------------------------------------------------------------------------


def sample_discrete_inverse_cdf(
    pmf: dict[int, float], rng: np.random.Generator, size: int
) -> np.ndarray:
    """Sample from an arbitrary discrete distribution using one uniform
    draw per sample.

    Build the cdf as a running total over the sorted values. Draw U from
    Uniform(0, 1). The sample is the smallest value whose cdf is at least
    U -- geometrically, the point where a vertical line at height U first
    crosses the cdf staircase. `numpy.searchsorted` finds that crossing
    point in one vectorised call instead of a Python loop per draw.
    """
    values = sorted(pmf)
    cumulative = np.cumsum([float(pmf[v]) for v in values])
    # Floating-point summation of many fractions can land at 0.999999999999
    # instead of exactly 1.0. Clamping the last entry to 1.0 guarantees
    # every possible U in [0, 1) has somewhere to land.
    cumulative[-1] = 1.0
    draws = rng.random(size)
    indices = np.searchsorted(cumulative, draws, side="right")
    return np.asarray(values, dtype=float)[indices]


# ---------------------------------------------------------------------------
# Exercise 8: the exponential distribution, sampled from scratch
# ---------------------------------------------------------------------------


def sample_exponential_scratch(
    rate: float, rng: np.random.Generator, size: int
) -> np.ndarray:
    """Sample from Exponential(rate) as -ln(U) / rate.

    The exponential's cdf is F(x) = 1 - exp(-rate * x). Setting F(x) = U and
    solving for x gives x = -ln(1 - U) / rate; since U and 1 - U have the
    same distribution on (0, 1), the simpler -ln(U) / rate is used instead
    -- the standard form of this sampler, and the one worth recognising
    when you meet it again inside a library's source.
    """
    draws = rng.random(size)
    return -np.log(draws) / rate


# ---------------------------------------------------------------------------
# A max-gap statistic between two empirical distributions, written by hand
# because scipy.stats.ks_2samp is not available in this environment
# ---------------------------------------------------------------------------


def empirical_cdf_at(sample: np.ndarray, points: np.ndarray) -> np.ndarray:
    """F_n(x) for every x in `points`: the fraction of `sample` at or below
    each point, read off a sorted copy with a binary search."""
    sorted_sample = np.sort(sample)
    return np.searchsorted(sorted_sample, points, side="right") / len(sample)


def max_gap_statistic(sample_a: np.ndarray, sample_b: np.ndarray) -> float:
    """The largest vertical gap between two empirical CDFs, evaluated at
    every point either sample could change value -- the two-sample
    Kolmogorov-Smirnov statistic, without scipy.

    The maximum can only occur at a point where one of the empirical CDFs
    actually jumps, so evaluating both CDFs at every value that appears in
    either sample (the pooled, sorted set of observations) is exact, not an
    approximation on a grid.
    """
    pooled = np.sort(np.concatenate([sample_a, sample_b]))
    cdf_a = empirical_cdf_at(sample_a, pooled)
    cdf_b = empirical_cdf_at(sample_b, pooled)
    return float(np.max(np.abs(cdf_a - cdf_b)))
