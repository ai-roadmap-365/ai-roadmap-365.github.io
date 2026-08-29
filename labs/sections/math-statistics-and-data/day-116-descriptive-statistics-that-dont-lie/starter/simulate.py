"""Exercises 3 and 8: the two places this lab draws random numbers.

Use `numpy.random.default_rng(seed)` -- an independent generator object,
never the legacy global-state `numpy.random.seed()`.
"""

import numpy as np


def bessel_trial_variances(
    rng: np.random.Generator,
    population_mean: float,
    population_sigma: float,
    sample_size: int,
    trials: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw `trials` independent samples of size `sample_size` from a
    normal population, and compute both the biased (divide-by-n) and
    unbiased (divide-by-(n-1)) sample variance for every one of them.

    Returns (biased_variances, unbiased_variances), one value per trial.
    """
    raise NotImplementedError


def contaminated_sample(
    rng: np.random.Generator,
    clean_mean: float,
    clean_sigma: float,
    clean_n: int,
    outliers: tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray]:
    """A clean sample from a normal distribution, and the same sample with
    a handful of extreme values appended.

    Returns (clean, contaminated).
    """
    raise NotImplementedError
