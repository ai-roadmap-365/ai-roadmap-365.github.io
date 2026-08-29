"""Exercises 3 and 8: the two places this lab draws random numbers.

Both use `numpy.random.default_rng(seed)`, an independent generator object
rather than the legacy global-state `numpy.random.seed()` -- so the same
seed gives byte-identical results regardless of what else has run.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Exercise 3: Bessel's correction, measured by simulation
# ---------------------------------------------------------------------------


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
    samples = rng.normal(
        loc=population_mean, scale=population_sigma, size=(trials, sample_size)
    )
    sample_means = samples.mean(axis=1, keepdims=True)
    squared_deviations = (samples - sample_means) ** 2
    sum_sq = squared_deviations.sum(axis=1)
    biased = sum_sq / sample_size
    unbiased = sum_sq / (sample_size - 1)
    return biased, unbiased


# ---------------------------------------------------------------------------
# Exercise 8: robust spread under contamination
# ---------------------------------------------------------------------------


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
    clean = rng.normal(loc=clean_mean, scale=clean_sigma, size=clean_n)
    contaminated = np.concatenate([clean, np.asarray(outliers, dtype=float)])
    return clean, contaminated
