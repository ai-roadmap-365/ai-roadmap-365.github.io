"""The reference pytest suite: every function in `sampling.py`, checked
against real values from real seeded runs.

Run from the lab directory:

    .venv/bin/pytest examples -q
"""

import math

import numpy as np
import pytest

import dataset as D
import sampling as S


# --------------------------------------------------------------------------
# sampling_distribution / theoretical_standard_error
# --------------------------------------------------------------------------


def test_sampling_distribution_returns_one_mean_per_trial():
    rng = np.random.default_rng(101)
    means = S.sampling_distribution(D.SKEWED_POP, n=20, trials=500, rng=rng)
    assert means.shape == (500,)


def test_sampling_distribution_mean_is_close_to_population_mean():
    rng = np.random.default_rng(102)
    pop_mean, pop_sigma = S.population_mean_std(D.SKEWED_POP)
    n, trials = 50, 20_000
    means = S.sampling_distribution(D.SKEWED_POP, n, trials, rng)
    se_of_mean = S.theoretical_standard_error(pop_sigma, n) / math.sqrt(trials)
    assert abs(means.mean() - pop_mean) < 4.0 * se_of_mean


def test_theoretical_standard_error_scales_as_inverse_sqrt_n():
    assert S.theoretical_standard_error(10.0, 100) == pytest.approx(1.0)
    assert S.theoretical_standard_error(10.0, 400) == pytest.approx(0.5)


# --------------------------------------------------------------------------
# skewness / iqr
# --------------------------------------------------------------------------


def test_skewness_of_a_symmetric_sample_is_near_zero():
    rng = np.random.default_rng(103)
    symmetric = rng.normal(0.0, 1.0, size=200_000)
    assert abs(S.skewness(symmetric)) < 0.02


def test_skewness_of_an_exponential_population_is_positive_and_near_two():
    # The Exponential distribution's population skewness is exactly 2,
    # regardless of scale. This checks the from-scratch estimator against
    # that known constant on a large sample.
    assert S.skewness(D.SKEWED_POP) == pytest.approx(2.0, abs=0.05)


def test_iqr_of_a_known_uniform_sample():
    values = np.arange(0, 101)  # 0..100, IQR should be exactly 50
    assert S.iqr(values) == pytest.approx(50.0)


def test_iqr_ignores_a_single_extreme_outlier():
    values = np.concatenate([np.arange(0, 99), [1_000_000.0]])
    assert S.iqr(values) < 100.0  # unaffected by the one wild value


# --------------------------------------------------------------------------
# exponential_mean_iqr / cauchy_mean_iqr
# --------------------------------------------------------------------------


def test_exponential_mean_iqr_shrinks_with_more_data():
    rng = np.random.default_rng(104)
    small = S.exponential_mean_iqr(10, 5_000, rng, scale=1.0)
    large = S.exponential_mean_iqr(1_000, 5_000, rng, scale=1.0)
    assert small / large > 5.0


def test_cauchy_mean_iqr_does_not_shrink_with_more_data():
    rng = np.random.default_rng(105)
    small = S.cauchy_mean_iqr(10, 5_000, rng)
    large = S.cauchy_mean_iqr(1_000, 5_000, rng)
    assert 0.3 < small / large < 3.0


# --------------------------------------------------------------------------
# mean_absolute_error / biased_pool
# --------------------------------------------------------------------------


def test_mean_absolute_error_is_zero_for_exact_estimates():
    assert S.mean_absolute_error(np.array([5.0, 5.0, 5.0]), 5.0) == 0.0


def test_mean_absolute_error_is_positive_for_biased_estimates():
    assert S.mean_absolute_error(np.array([6.0, 7.0, 8.0]), 5.0) == pytest.approx(2.0)


def test_biased_pool_contains_only_values_above_the_median():
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    pool = S.biased_pool(values)
    assert (pool > np.median(values)).all()
    assert len(pool) < len(values)


# --------------------------------------------------------------------------
# bootstrap_replicates / bootstrap_standard_error
# --------------------------------------------------------------------------


def test_bootstrap_replicates_shape():
    rng = np.random.default_rng(106)
    data = np.arange(50, dtype=float)
    reps = S.bootstrap_replicates(data, lambda a: a.mean(axis=1), 300, rng)
    assert reps.shape == (300,)


def test_bootstrap_se_of_the_mean_agrees_with_the_formula():
    rng = np.random.default_rng(107)
    data = rng.normal(0.0, 5.0, size=300)
    sigma_hat = data.std(ddof=1)
    theoretical = sigma_hat / math.sqrt(len(data))
    boot_se = S.bootstrap_standard_error(data, lambda a: a.mean(axis=1), 4_000, rng)
    assert abs(boot_se - theoretical) / theoretical < 0.15


# --------------------------------------------------------------------------
# ar1_series / naive_standard_error / true_standard_error_by_replication
# --------------------------------------------------------------------------


def test_ar1_series_has_the_right_length():
    rng = np.random.default_rng(108)
    series = S.ar1_series(n=50, phi=0.5, sigma=1.0, rng=rng)
    assert series.shape == (50,)


def test_ar1_series_is_independent_when_phi_is_zero():
    rng = np.random.default_rng(109)
    naive = np.mean(
        [S.naive_standard_error(S.ar1_series(300, 0.0, 1.0, rng)) for _ in range(200)]
    )
    true_se = S.true_standard_error_by_replication(300, 0.0, 1.0, 600, rng)
    # With phi = 0, there is no dependence, so naive and true should agree
    # closely -- this is the control case for exercise 7's main result.
    assert abs(naive - true_se) / true_se < 0.25


def test_dependence_makes_naive_se_understate_the_true_se():
    rng = np.random.default_rng(110)
    naive = np.mean(
        [S.naive_standard_error(S.ar1_series(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, rng)) for _ in range(200)]
    )
    true_se = S.true_standard_error_by_replication(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, 1_500, rng)
    assert true_se > naive


# --------------------------------------------------------------------------
# binomial_standard_error
# --------------------------------------------------------------------------


def test_binomial_standard_error_matches_the_brief():
    se_pct = S.binomial_standard_error(0.914, 500) * 100.0
    assert se_pct == pytest.approx(1.25, abs=0.05)


def test_binomial_standard_error_is_largest_at_p_one_half():
    se_half = S.binomial_standard_error(0.5, 100)
    se_extreme = S.binomial_standard_error(0.99, 100)
    assert se_half > se_extreme
