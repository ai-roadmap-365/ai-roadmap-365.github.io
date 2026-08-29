"""Hand-rolled hypothesis-testing and confidence-interval machinery.

Every function here is built from `math.erf` and NumPy array arithmetic
only -- no `scipy.stats`, no `statsmodels`. That is the point of Day 118:
before trusting a library's `ttest_ind`, build the thing it computes.

All functions are pure (no hidden global state) and take an explicit
`numpy.random.Generator` wherever randomness is needed, per the
project's convention of never using an internally reseeded generator.
"""
from __future__ import annotations

import math

import numpy as np


def phi(z: float) -> float:
    """Standard normal CDF, computed from math.erf (no scipy needed)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def p_from_z_two_sided(z: float) -> float:
    """Two-sided p-value for a standard normal test statistic z."""
    return 2.0 * (1.0 - phi(abs(z)))


def z_critical_two_sided(alpha: float) -> float:
    """The z such that P(|Z| > z) = alpha, found by bisection on phi.

    There is no closed form for the normal quantile function in terms of
    erf, so this inverts phi() numerically. 200 bisection steps on a
    [0, 10] bracket resolves z to well under 1e-9, far tighter than any
    tolerance this lab uses.
    """
    target = 1.0 - alpha / 2.0
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if phi(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def two_sample_z_test(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Welch-style two-sample z-test (unpooled variance, large-n normal
    approximation to the sampling distribution of the difference in means).

    Returns (z, p_two_sided). This is the large-sample cousin of Welch's
    t-test (see the lesson's Tools section): it uses each sample's own
    variance rather than assuming the two populations share one variance,
    and it treats the standard error as known rather than estimated,
    which is accurate once each sample has on the order of 30+
    observations.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a, n_b = a.size, b.size
    mean_a, mean_b = a.mean(), b.mean()
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(var_a / n_a + var_b / n_b)
    z = (mean_a - mean_b) / se
    p = p_from_z_two_sided(z)
    return z, p


def confidence_interval_mean(sample: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Normal-approximation (1 - alpha) confidence interval for a mean.

    mean +/- z_(alpha/2) * standard_error, where standard_error is the
    sample standard deviation divided by sqrt(n) -- Day 117's standard
    error, reused rather than re-derived.
    """
    sample = np.asarray(sample, dtype=float)
    n = sample.size
    mean = sample.mean()
    se = sample.std(ddof=1) / math.sqrt(n)
    z = z_critical_two_sided(alpha)
    return mean - z * se, mean + z * se


def ci_excludes(interval: tuple[float, float], value: float) -> bool:
    """True if `value` lies strictly outside the closed interval."""
    lo, hi = interval
    return value < lo or value > hi


def one_sample_z_test_against_value(sample: np.ndarray, null_value: float) -> tuple[float, float]:
    """One-sample z-test of H0: population mean == null_value."""
    sample = np.asarray(sample, dtype=float)
    n = sample.size
    se = sample.std(ddof=1) / math.sqrt(n)
    z = (sample.mean() - null_value) / se
    return z, p_from_z_two_sided(z)


def permutation_test_diff_means(
    a: np.ndarray, b: np.ndarray, n_perm: int, rng: np.random.Generator
) -> tuple[float, float]:
    """Two-sided permutation test for a difference in means.

    No distributional assumption: the null hypothesis is that the group
    label carries no information, so the labels are shuffled `n_perm`
    times, the difference in means is recomputed each time, and the
    p-value is the fraction of shuffles at least as extreme as what was
    actually observed (plus the observed arrangement itself, so the
    p-value can never read as exactly zero).

    Returns (observed_diff, p_two_sided).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a = a.size
    pooled = np.concatenate([a, b])
    observed = a.mean() - b.mean()
    count_as_extreme = 0
    for _ in range(n_perm):
        shuffled = rng.permutation(pooled)
        perm_diff = shuffled[:n_a].mean() - shuffled[n_a:].mean()
        if abs(perm_diff) >= abs(observed):
            count_as_extreme += 1
    p = (count_as_extreme + 1) / (n_perm + 1)
    return observed, p


def power_two_sample_z(effect: float, sigma: float, n_per_group: int, alpha: float = 0.05) -> float:
    """Power of the two-sample z-test above a true mean difference `effect`,
    with a common known standard deviation `sigma`, `n_per_group` in each
    arm, assuming both samples are the same size.

    Derivation: under H1 the test statistic Z = (Xbar_a - Xbar_b)/SE is
    Normal(effect/SE, 1), where SE = sigma * sqrt(2/n_per_group). The test
    rejects when |Z| > z_crit under H0, so power is the probability that a
    Normal(effect/SE, 1) variable falls outside [-z_crit, z_crit].
    """
    se = sigma * math.sqrt(2.0 / n_per_group)
    z_crit = z_critical_two_sided(alpha)
    shift = effect / se
    # P(Z > z_crit) + P(Z < -z_crit) for Z ~ Normal(shift, 1)
    return (1.0 - phi(z_crit - shift)) + phi(-z_crit - shift)


def bonferroni_alpha(alpha: float, m: int) -> float:
    """The per-test alpha that keeps the family-wise error rate at `alpha`
    across `m` independent tests, by the (conservative) Bonferroni bound.
    """
    return alpha / m


def bootstrap_ci(
    sample: np.ndarray,
    statistic,
    n_boot: int,
    alpha: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for an arbitrary statistic.

    Resample `sample` with replacement `n_boot` times, recompute
    `statistic` on each resample, and take the [alpha/2, 1 - alpha/2]
    percentiles of the resulting distribution. Built the same way as Day
    117's bootstrap, reused here for a statistic (a mean) that also has a
    closed-form normal-approximation interval, so the two can be checked
    against each other.
    """
    sample = np.asarray(sample, dtype=float)
    n = sample.size
    replicates = np.empty(n_boot)
    for i in range(n_boot):
        resample = rng.choice(sample, size=n, replace=True)
        replicates[i] = statistic(resample)
    lo = np.percentile(replicates, 100 * alpha / 2)
    hi = np.percentile(replicates, 100 * (1 - alpha / 2))
    return float(lo), float(hi)
