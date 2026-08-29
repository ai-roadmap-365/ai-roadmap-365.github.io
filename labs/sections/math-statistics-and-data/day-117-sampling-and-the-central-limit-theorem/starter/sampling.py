"""Sampling distributions, the standard error, and the bootstrap -- from
scratch.

Work through `starter/00_brief.md` in order, filling in the functions below.
Check your progress with:

    .venv/bin/pytest starter -q

Unattempted work reports as skipped, never failed. Every function currently
returns None -- replace the body, not just the return statement.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np


def sampling_distribution(
    population: np.ndarray, n: int, trials: int, rng: np.random.Generator
) -> np.ndarray:
    """Exercise 1. Draw `trials` independent samples of size `n`, with
    replacement, from `population`, and return the array of `trials` sample
    means.

    Hint: `rng.integers(0, population.shape[0], size=(trials, n))` gives you
    every sample's indices in one call; index `population` with that array
    and take `.mean(axis=1)`.
    """
    return None


def population_mean_std(population: np.ndarray) -> tuple[float, float]:
    """The population mean and the population standard deviation (ddof=0,
    since the whole population is known -- there is no estimation here)."""
    return None


def theoretical_standard_error(sigma: float, n: int) -> float:
    """Exercise 1 / 2. The standard error of the sample mean: sigma / sqrt(n)."""
    return None


def skewness(values: np.ndarray) -> float:
    """Exercise 3. The sample skewness g1 = m3 / m2^1.5, where mk is the k-th
    central moment: mk = mean((x - mean(x))**k)."""
    return None


def iqr(values: np.ndarray) -> float:
    """Exercise 4. The interquartile range: the 75th percentile minus the
    25th. Use `numpy.percentile`."""
    return None


def exponential_mean_iqr(
    n: int, trials: int, rng: np.random.Generator, scale: float = 1.0
) -> float:
    """Exercise 4. The IQR of the sampling distribution of the mean, for
    `trials` samples of size `n` drawn directly from Exponential(scale) via
    `rng.exponential`."""
    return None


def cauchy_mean_iqr(n: int, trials: int, rng: np.random.Generator) -> float:
    """Exercise 4. The same idea, drawing from `rng.standard_cauchy` instead."""
    return None


def mean_absolute_error(estimates: np.ndarray, truth: float) -> float:
    """Exercise 5. The average absolute distance between a set of estimates
    and the truth they are estimating."""
    return None


def biased_pool(population: np.ndarray) -> np.ndarray:
    """Exercise 5. The subset of `population` strictly above its own median.
    Use `numpy.median` and boolean indexing."""
    return None


def bootstrap_replicates(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], np.ndarray],
    n_boot: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Exercise 6. Resample `data` with replacement `n_boot` times (each
    resample the same size as `data`), apply `statistic` to every resample,
    and return the `n_boot` results.

    Hint: build an index array of shape (n_boot, len(data)) with
    `rng.integers`, index `data` with it to get all the resamples at once,
    and pass that 2-D array straight to `statistic`.
    """
    return None


def bootstrap_standard_error(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], np.ndarray],
    n_boot: int,
    rng: np.random.Generator,
) -> float:
    """Exercise 6. The standard deviation (ddof=1) of `bootstrap_replicates`."""
    return None


def ar1_series(n: int, phi: float, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Exercise 7. A length-n AR(1) series: x[0] ~ Normal(0, sigma), and each
    later value is `phi * previous + innovation`, where the innovation's own
    standard deviation is `sigma * sqrt(1 - phi**2)` -- chosen so the
    series' marginal variance stays sigma**2 throughout."""
    return None


def naive_standard_error(series: np.ndarray) -> float:
    """Exercise 7. sample_std(ddof=1) / sqrt(n) -- the textbook formula,
    applied as if the observations were independent."""
    return None


def true_standard_error_by_replication(
    n: int, phi: float, sigma: float, replications: int, rng: np.random.Generator
) -> float:
    """Exercise 7. Generate `replications` independent length-n AR(1) series,
    compute each one's sample mean, and return the standard deviation
    (ddof=1) of those means."""
    return None


def binomial_standard_error(phat: float, n: int) -> float:
    """Exercise 8. sqrt(phat * (1 - phat) / n)."""
    return None
