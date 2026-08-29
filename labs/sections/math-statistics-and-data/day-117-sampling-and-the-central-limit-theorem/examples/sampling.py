"""Sampling distributions, the standard error, and the bootstrap -- from
scratch.

Every function here works from first principles: `numpy.random.Generator`
supplies uniform and named draws, and everything else -- the sampling
distribution itself, its standard error, its skewness, the bootstrap, the
naive-versus-true standard error under dependence -- is built on top of that,
not imported from a library that already does it.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np


def sampling_distribution(
    population: np.ndarray, n: int, trials: int, rng: np.random.Generator
) -> np.ndarray:
    """Draw `trials` independent samples of size `n`, with replacement, from
    `population`, and return the array of `trials` sample means.

    This is the central object of the whole lesson: not a single statistic,
    but the distribution *of* a statistic, built by literally repeating the
    experiment.
    """
    idx = rng.integers(0, population.shape[0], size=(trials, n))
    return population[idx].mean(axis=1)


def population_mean_std(population: np.ndarray) -> tuple[float, float]:
    """The population mean and the population standard deviation (divided by
    n, not n-1 -- there is no estimation happening here, the population is
    fully known)."""
    return float(population.mean()), float(population.std(ddof=0))


def theoretical_standard_error(sigma: float, n: int) -> float:
    """The standard error of the sample mean: sigma / sqrt(n)."""
    return sigma / math.sqrt(n)


def skewness(values: np.ndarray) -> float:
    """The sample skewness g1 = m3 / m2^1.5, where mk is the k-th central
    moment. Zero for a symmetric distribution (including the Normal),
    positive for a right-tailed one."""
    values = np.asarray(values, dtype=float)
    centered = values - values.mean()
    m2 = np.mean(centered**2)
    m3 = np.mean(centered**3)
    return float(m3 / m2**1.5)


def iqr(values: np.ndarray) -> float:
    """The interquartile range: a spread measure that stays meaningful even
    when the standard deviation does not, because it depends only on the
    order of the data, not on its moments. A Cauchy-distributed sample has an
    undefined population variance, so its sample standard deviation is not
    an estimate of anything -- the IQR is not affected by that at all."""
    values = np.asarray(values, dtype=float)
    q75, q25 = np.percentile(values, [75, 25])
    return float(q75 - q25)


def exponential_mean_iqr(
    n: int, trials: int, rng: np.random.Generator, scale: float = 1.0
) -> float:
    """The IQR of the sampling distribution of the mean, for `trials`
    samples of size `n` drawn directly from Exponential(scale)."""
    draws = rng.exponential(scale=scale, size=(trials, n))
    return iqr(draws.mean(axis=1))


def cauchy_mean_iqr(n: int, trials: int, rng: np.random.Generator) -> float:
    """The IQR of the sampling distribution of the mean, for `trials`
    samples of size `n` drawn from the standard Cauchy distribution.

    The Cauchy distribution has no defined mean or variance -- its tails are
    too heavy for either integral to converge. Averaging n Cauchy draws
    produces a value that is ITSELF standard-Cauchy distributed, for every n,
    which this function's caller checks by comparing this IQR at two very
    different values of n and finding them the same.
    """
    draws = rng.standard_cauchy(size=(trials, n))
    return iqr(draws.mean(axis=1))


def mean_absolute_error(estimates: np.ndarray, truth: float) -> float:
    """The average absolute distance between a set of estimates and the
    truth they are estimating -- a single number combining bias and
    variance, which is exactly why it is the right thing to track across
    exercise 5."""
    return float(np.mean(np.abs(np.asarray(estimates, dtype=float) - truth)))


def biased_pool(population: np.ndarray) -> np.ndarray:
    """The subset of the population strictly above its own median -- a
    sampling frame that can never produce a draw from the lower half, no
    matter how many draws it makes."""
    threshold = np.median(population)
    return population[population > threshold]


def bootstrap_replicates(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], np.ndarray],
    n_boot: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Resample `data` with replacement `n_boot` times (each resample the
    same size as `data`), apply `statistic` to every resample, and return the
    `n_boot` results.

    `statistic` must accept a 2-D array of shape (n_boot, len(data)) and
    return a 1-D array of shape (n_boot,) -- `lambda a: a.mean(axis=1)` or
    `lambda a: numpy.median(a, axis=1)` are the two used in this lab.
    """
    data = np.asarray(data, dtype=float)
    n = data.shape[0]
    idx = rng.integers(0, n, size=(n_boot, n))
    resamples = data[idx]
    return np.asarray(statistic(resamples), dtype=float)


def bootstrap_standard_error(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], np.ndarray],
    n_boot: int,
    rng: np.random.Generator,
) -> float:
    """The bootstrap estimate of a statistic's standard error: the standard
    deviation of the statistic computed across the bootstrap replicates.
    No formula for the statistic's sampling distribution is used or needed."""
    replicates = bootstrap_replicates(data, statistic, n_boot, rng)
    return float(replicates.std(ddof=1))


def ar1_series(n: int, phi: float, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """A length-n AR(1) series: x[0] ~ Normal(0, sigma), and each later value
    is `phi * previous + innovation`, with the innovation's variance chosen
    so the series' own marginal variance stays sigma^2 throughout (the
    stationary AR(1) variance is innovation_variance / (1 - phi^2))."""
    x = np.empty(n, dtype=float)
    x[0] = rng.normal(0.0, sigma)
    innovation_sigma = sigma * math.sqrt(1.0 - phi**2)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.normal(0.0, innovation_sigma)
    return x


def naive_standard_error(series: np.ndarray) -> float:
    """The textbook formula, sample_std / sqrt(n), applied as if the
    observations were independent -- which is exactly the assumption an
    autocorrelated series violates."""
    series = np.asarray(series, dtype=float)
    n = series.shape[0]
    return float(series.std(ddof=1) / math.sqrt(n))


def true_standard_error_by_replication(
    n: int, phi: float, sigma: float, replications: int, rng: np.random.Generator
) -> float:
    """The actual standard error of the sample mean of an AR(1) series,
    measured the only way that does not assume independence: generate many
    independent length-n series, compute each one's sample mean, and take
    the standard deviation of THOSE means."""
    means = np.array(
        [ar1_series(n, phi, sigma, rng).mean() for _ in range(replications)]
    )
    return float(means.std(ddof=1))


def binomial_standard_error(phat: float, n: int) -> float:
    """The standard error of a sample proportion (equivalently, an accuracy
    measured on n examples): sqrt(phat * (1 - phat) / n)."""
    return math.sqrt(phat * (1.0 - phat) / n)
