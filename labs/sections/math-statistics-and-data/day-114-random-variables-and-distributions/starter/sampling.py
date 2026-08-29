"""Exercises 7 and 8: the inverse-CDF sampling method, written from scratch,
for both a discrete pmf and the exponential distribution -- and a max-gap
statistic to compare two empirical distributions by hand, since scipy is
not installed here.

Fill in every function below.
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

    Build the cdf as a running total over the sorted values (clamp the last
    entry to exactly 1.0 to guard against floating-point summation landing
    a hair below it). Draw `size` values from `rng.random(size)`. Use
    `numpy.searchsorted(cumulative, draws, side="right")` to find, for each
    draw, the index of the smallest cdf value at least as large as the
    draw. Index into the sorted values with that array of indices.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8: the exponential distribution, sampled from scratch
# ---------------------------------------------------------------------------


def sample_exponential_scratch(
    rate: float, rng: np.random.Generator, size: int
) -> np.ndarray:
    """Sample from Exponential(rate) as -ln(U) / rate, where U is drawn
    from `rng.random(size)`."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# A max-gap statistic between two empirical distributions, written by hand
# because scipy.stats.ks_2samp is not available in this environment
# ---------------------------------------------------------------------------


def empirical_cdf_at(sample: np.ndarray, points: np.ndarray) -> np.ndarray:
    """F_n(x) for every x in `points`: the fraction of `sample` at or below
    each point. Sort a copy of `sample`, then use
    `numpy.searchsorted(sorted_sample, points, side="right") / len(sample)`.
    """
    raise NotImplementedError


def max_gap_statistic(sample_a: np.ndarray, sample_b: np.ndarray) -> float:
    """The largest vertical gap between two empirical CDFs, evaluated at
    every point either sample could change value: pool and sort both
    samples, evaluate both empirical cdfs at every pooled point with
    `empirical_cdf_at`, and return the maximum absolute difference."""
    raise NotImplementedError
