"""Hypothesis-testing and confidence-interval machinery -- from scratch.

Work through `starter/00_brief.md` in order, filling in the functions below.
Check your progress with:

    .venv/bin/pytest starter -q

Unattempted work reports as skipped, never failed. Every function currently
returns None -- replace the body, not just the return statement.
"""
from __future__ import annotations

import math

import numpy as np


def phi(z: float) -> float:
    """Exercise 1. Standard normal CDF, computed from math.erf. No scipy.

    Hint: math.erf(z / math.sqrt(2)) is the piece you need; phi(z) is
    0.5 * (1 + that).
    """
    return None


def p_from_z_two_sided(z: float) -> float:
    """Exercise 1. Two-sided p-value for a standard normal statistic z."""
    return None


def z_critical_two_sided(alpha: float) -> float:
    """Exercise 2. The z such that P(|Z| > z) = alpha, found by bisecting
    phi() on the interval [0, 10] until phi(mid) is within reach of
    1 - alpha/2. 200 iterations is far more than enough precision.
    """
    return None


def two_sample_z_test(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Exercise 1. Two-sample z-test using each sample's own variance
    (unpooled): z = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b).
    Return (z, p_two_sided).
    """
    return None


def confidence_interval_mean(sample: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Exercise 2 / 3. Normal-approximation (1 - alpha) confidence interval
    for a mean: mean +/- z_(alpha/2) * (sample_std / sqrt(n)).
    """
    return None


def ci_excludes(interval: tuple[float, float], value: float) -> bool:
    """Exercise 3. True if value lies strictly outside the closed interval."""
    return None


def one_sample_z_test_against_value(sample: np.ndarray, null_value: float) -> tuple[float, float]:
    """Exercise 3 / 8. One-sample z-test of H0: population mean == null_value."""
    return None


def permutation_test_diff_means(
    a: np.ndarray, b: np.ndarray, n_perm: int, rng: np.random.Generator
) -> tuple[float, float]:
    """Exercise 4. Shuffle the pooled labels n_perm times, recompute the
    difference in means each time, and count how many shuffles are at
    least as extreme (in absolute value) as the real observed difference.
    p = (count_at_least_as_extreme + 1) / (n_perm + 1) -- the "+1"s avoid a
    p-value of exactly zero. Return (observed_diff, p_two_sided).
    """
    return None


def power_two_sample_z(effect: float, sigma: float, n_per_group: int, alpha: float = 0.05) -> float:
    """Exercise 6. Power of the two-sample z-test given a true mean
    difference `effect`, common known std `sigma`, and `n_per_group` per
    arm. SE = sigma * sqrt(2/n_per_group); under H1 the test statistic is
    Normal(effect/SE, 1); power is the probability that variable falls
    outside [-z_crit, z_crit].
    """
    return None


def bonferroni_alpha(alpha: float, m: int) -> float:
    """Exercise 5. The per-test alpha that keeps the family-wise error rate
    at `alpha` across `m` independent tests."""
    return None


def bootstrap_ci(
    sample: np.ndarray,
    statistic,
    n_boot: int,
    alpha: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Exercise 9. Percentile bootstrap interval: resample `sample` with
    replacement `n_boot` times, recompute `statistic` on each resample, and
    take the [alpha/2, 1 - alpha/2] percentiles of the results.
    """
    return None
