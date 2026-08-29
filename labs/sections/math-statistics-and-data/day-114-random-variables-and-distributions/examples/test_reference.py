"""The reference test suite: real values, real exceptions, no mocking."""

import math
from fractions import Fraction

import numpy as np
import pytest

import dataset as D
import distributions as dist
import sampling as samp

# ---------------------------------------------------------------------------
# dice_sum_pmf
# ---------------------------------------------------------------------------


def test_pmf_has_eleven_entries():
    pmf = dist.dice_sum_pmf()
    assert set(pmf) == set(range(2, 13))


def test_pmf_sums_to_one():
    pmf = dist.dice_sum_pmf()
    assert sum(pmf.values()) == 1


def test_pmf_of_seven_is_one_sixth():
    pmf = dist.dice_sum_pmf()
    assert pmf[7] == Fraction(1, 6)


def test_pmf_returns_fractions():
    pmf = dist.dice_sum_pmf()
    assert all(isinstance(p, Fraction) for p in pmf.values())


def test_pmf_is_symmetric_around_seven():
    pmf = dist.dice_sum_pmf()
    for offset in range(1, 6):
        assert pmf[7 - offset] == pmf[7 + offset]


def test_seven_is_six_times_two():
    pmf = dist.dice_sum_pmf()
    assert pmf[7] == 6 * pmf[2]


def test_the_distribution_is_not_uniform():
    pmf = dist.dice_sum_pmf()
    assert len(set(pmf.values())) > 1


# ---------------------------------------------------------------------------
# cdf_from_pmf
# ---------------------------------------------------------------------------


def test_cdf_is_monotone_non_decreasing():
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    values = [cdf[k] for k in sorted(cdf)]
    assert all(a <= b for a, b in zip(values, values[1:]))


def test_cdf_ends_at_exactly_one():
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    assert cdf[max(cdf)] == 1


def test_cdf_starts_at_the_first_pmf_value():
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    assert cdf[2] == pmf[2]


def test_cdf_difference_equals_pmf_value():
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    assert cdf[7] - cdf[6] == pmf[7]


@pytest.mark.parametrize("k", range(3, 13))
def test_cdf_difference_equals_pmf_at_every_k(k):
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    assert cdf[k] - cdf[k - 1] == pmf[k]


def test_cdf_of_an_interval_matches_a_direct_sum():
    pmf = dist.dice_sum_pmf()
    cdf = dist.cdf_from_pmf(pmf)
    direct = sum((pmf[k] for k in range(5, 10)), Fraction(0))
    assert cdf[9] - cdf[4] == direct


# ---------------------------------------------------------------------------
# expectation_pmf / variance_pmf
# ---------------------------------------------------------------------------


def test_expectation_of_dice_sum_is_seven():
    pmf = dist.dice_sum_pmf()
    assert dist.expectation_pmf(pmf) == 7


def test_variance_of_dice_sum_is_35_over_6():
    pmf = dist.dice_sum_pmf()
    assert dist.variance_pmf(pmf) == Fraction(35, 6)


def test_expectation_of_a_single_die_is_three_point_five():
    pmf = {k: Fraction(1, 6) for k in range(1, 7)}
    assert dist.expectation_pmf(pmf) == Fraction(7, 2)


def test_expectation_need_not_be_an_attainable_value():
    pmf = {k: Fraction(1, 6) for k in range(1, 7)}
    mean = dist.expectation_pmf(pmf)
    assert mean not in pmf


# ---------------------------------------------------------------------------
# expectation_over / variance_over / covariance_over: linearity and its limit
# ---------------------------------------------------------------------------


def test_linearity_holds_for_the_dependent_pair():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    e_x = dist.expectation_over(outcomes, weight, D.first_die)
    e_y = dist.expectation_over(outcomes, weight, D.dice_sum)
    e_sum = dist.expectation_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))
    assert e_sum == e_x + e_y


def test_e_x_is_three_point_five():
    e_x = dist.expectation_over(D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT, D.first_die)
    assert e_x == Fraction(7, 2)


def test_e_y_is_seven():
    e_y = dist.expectation_over(D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT, D.dice_sum)
    assert e_y == 7


def test_variance_of_sum_is_not_the_naive_sum():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    var_x = dist.variance_over(outcomes, weight, D.first_die)
    var_y = dist.variance_over(outcomes, weight, D.dice_sum)
    var_sum = dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))
    assert var_sum != var_x + var_y


def test_variance_of_sum_equals_the_full_covariance_formula():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    var_x = dist.variance_over(outcomes, weight, D.first_die)
    var_y = dist.variance_over(outcomes, weight, D.dice_sum)
    cov_xy = dist.covariance_over(outcomes, weight, D.first_die, D.dice_sum)
    var_sum = dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o))
    assert var_sum == var_x + var_y + 2 * cov_xy


def test_covariance_of_x_and_y_is_nonzero():
    cov_xy = dist.covariance_over(D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT, D.first_die, D.dice_sum)
    assert cov_xy != 0
    assert cov_xy == Fraction(35, 12)


def test_covariance_of_independent_like_pair_can_be_zero():
    # First die and "is the second die a 6" behave independently in
    # covariance, since the second die's value is unrelated to the first.
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    cov = dist.covariance_over(outcomes, weight, lambda o: o[0], lambda o: o[1])
    assert cov == 0


# ---------------------------------------------------------------------------
# Jensen's inequality
# ---------------------------------------------------------------------------


def test_jensen_strict_for_a_die():
    outcomes, weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
    e_x2 = dist.expectation_over(outcomes, weight, lambda x: x * x)
    e_x = dist.expectation_over(outcomes, weight, lambda x: x)
    assert e_x2 > e_x**2


def test_jensen_gap_equals_variance():
    outcomes, weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
    e_x2 = dist.expectation_over(outcomes, weight, lambda x: x * x)
    e_x = dist.expectation_over(outcomes, weight, lambda x: x)
    var_x = dist.variance_over(outcomes, weight, lambda x: x)
    assert e_x2 - e_x**2 == var_x


def test_jensen_is_equality_for_a_constant():
    outcomes, weight = (5, 5, 5), Fraction(1, 3)
    e_x2 = dist.expectation_over(outcomes, weight, lambda x: x * x)
    e_x = dist.expectation_over(outcomes, weight, lambda x: x)
    assert e_x2 == e_x**2


# ---------------------------------------------------------------------------
# Var[aX + b]
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("a,b", [(2, 0), (2, 100), (-3, 7), (0.5, -4)])
def test_variance_of_affine_transform(a, b):
    outcomes, weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
    var_x = dist.variance_over(outcomes, weight, lambda x: x)
    var_ax_b = dist.variance_over(outcomes, weight, lambda x: a * x + b)
    assert var_ax_b == a**2 * var_x


# ---------------------------------------------------------------------------
# binomial_pmf / poisson_pmf
# ---------------------------------------------------------------------------


def test_binomial_pmf_sums_to_one():
    n, p = 10, 0.3
    total = sum(dist.binomial_pmf(n, p, k) for k in range(n + 1))
    assert abs(total - 1.0) < 1e-9


def test_binomial_pmf_out_of_range_is_zero():
    assert dist.binomial_pmf(10, 0.3, -1) == 0.0
    assert dist.binomial_pmf(10, 0.3, 11) == 0.0


def test_binomial_pmf_at_zero_successes():
    n, p = 10, 0.3
    assert abs(dist.binomial_pmf(n, p, 0) - (1 - p) ** n) < 1e-12


def test_poisson_pmf_sums_close_to_one_over_a_wide_range():
    lam = 2.0
    total = sum(dist.poisson_pmf(lam, k) for k in range(0, 40))
    assert abs(total - 1.0) < 1e-9


def test_poisson_pmf_negative_k_is_zero():
    assert dist.poisson_pmf(2.0, -1) == 0.0


def test_poisson_pmf_at_zero():
    lam = 2.0
    assert abs(dist.poisson_pmf(lam, 0) - math.exp(-lam)) < 1e-12


# ---------------------------------------------------------------------------
# max_binomial_poisson_gap: the Poisson-as-Binomial-limit convergence
# ---------------------------------------------------------------------------


def test_poisson_limit_gap_shrinks_monotonically():
    lam = D.POISSON_LAMBDA
    gaps = [
        dist.max_binomial_poisson_gap(n, lam / n, lam, D.POISSON_COMPARISON_KS)
        for n in D.POISSON_LIMIT_NS
    ]
    assert all(a > b for a, b in zip(gaps, gaps[1:]))


def test_poisson_limit_gap_at_largest_n_is_tiny():
    lam = D.POISSON_LAMBDA
    n = D.POISSON_LIMIT_NS[-1]
    gap = dist.max_binomial_poisson_gap(n, lam / n, lam, D.POISSON_COMPARISON_KS)
    assert gap < 1e-3


# ---------------------------------------------------------------------------
# uniform_density / numeric_integral
# ---------------------------------------------------------------------------


def test_uniform_density_is_two_on_the_support():
    assert dist.uniform_density(0.25, 0.0, 0.5) == 2.0


def test_uniform_density_exceeds_one():
    assert dist.uniform_density(0.1, 0.0, 0.5) > 1.0


def test_uniform_density_is_zero_outside_support():
    assert dist.uniform_density(0.6, 0.0, 0.5) == 0.0
    assert dist.uniform_density(-0.1, 0.0, 0.5) == 0.0


def test_numeric_integral_of_the_density_is_one():
    integral = dist.numeric_integral(lambda x: dist.uniform_density(x, 0.0, 0.5), 0.0, 0.5, 50_000)
    assert abs(integral - 1.0) < 1e-6


def test_numeric_integral_of_a_constant_one():
    integral = dist.numeric_integral(lambda x: 1.0, 0.0, 1.0, 1000)
    assert abs(integral - 1.0) < 1e-9


def test_numeric_integral_rejects_zero_steps():
    with pytest.raises(ValueError):
        dist.numeric_integral(lambda x: 1.0, 0.0, 1.0, 0)


# ---------------------------------------------------------------------------
# sample_discrete_inverse_cdf
# ---------------------------------------------------------------------------


def test_discrete_sampler_returns_only_values_in_the_pmf():
    pmf = {k: float(v) for k, v in dist.dice_sum_pmf().items()}
    rng = np.random.default_rng(0)
    draws = samp.sample_discrete_inverse_cdf(pmf, rng, 2_000)
    assert set(draws.astype(int).tolist()) <= set(pmf)


def test_discrete_sampler_empirical_frequencies_are_close():
    pmf = {k: float(v) for k, v in dist.dice_sum_pmf().items()}
    rng = np.random.default_rng(1)
    n = 100_000
    draws = samp.sample_discrete_inverse_cdf(pmf, rng, n)
    values, counts = np.unique(draws, return_counts=True)
    empirical = dict(zip(values.astype(int), counts / n))
    for k, p in pmf.items():
        se = D.standard_error_of_proportion(p, n)
        assert abs(empirical.get(k, 0.0) - p) < 4.0 * se


def test_discrete_sampler_same_seed_is_reproducible():
    pmf = {k: float(v) for k, v in dist.dice_sum_pmf().items()}
    a = samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(7), 500)
    b = samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(7), 500)
    assert np.array_equal(a, b)


def test_discrete_sampler_different_seed_differs():
    pmf = {k: float(v) for k, v in dist.dice_sum_pmf().items()}
    a = samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(7), 500)
    b = samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(8), 500)
    assert not np.array_equal(a, b)


def test_discrete_sampler_handles_a_skewed_two_point_pmf():
    pmf = {0: 0.9, 1: 0.1}
    rng = np.random.default_rng(2)
    n = 50_000
    draws = samp.sample_discrete_inverse_cdf(pmf, rng, n)
    empirical_one = (draws == 1).mean()
    se = D.standard_error_of_proportion(0.1, n)
    assert abs(empirical_one - 0.1) < 4.0 * se


# ---------------------------------------------------------------------------
# sample_exponential_scratch
# ---------------------------------------------------------------------------


def test_exponential_scratch_mean_near_one_over_rate():
    rate = 2.0
    rng = np.random.default_rng(3)
    n = 100_000
    draws = samp.sample_exponential_scratch(rate, rng, n)
    tol = 3.0 * D.standard_error_of_mean((1.0 / rate) ** 2, n)
    assert abs(draws.mean() - 1.0 / rate) < tol


def test_exponential_scratch_is_never_negative():
    rng = np.random.default_rng(4)
    draws = samp.sample_exponential_scratch(1.0, rng, 10_000)
    assert (draws >= 0).all()


def test_exponential_scratch_matches_builtin_mean_within_tolerance():
    rate = 2.0
    n = 50_000
    rng = np.random.default_rng(5)
    scratch = samp.sample_exponential_scratch(rate, rng, n)
    built_in = rng.exponential(scale=1.0 / rate, size=n)
    tol = 3.0 * D.standard_error_of_mean((1.0 / rate) ** 2, n)
    assert abs(scratch.mean() - built_in.mean()) < 2 * tol


# ---------------------------------------------------------------------------
# empirical_cdf_at / max_gap_statistic
# ---------------------------------------------------------------------------


def test_empirical_cdf_is_between_zero_and_one():
    sample = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    points = np.array([0.0, 2.5, 10.0])
    cdf_vals = samp.empirical_cdf_at(sample, points)
    assert (cdf_vals >= 0).all() and (cdf_vals <= 1).all()
    assert cdf_vals[0] == 0.0
    assert cdf_vals[-1] == 1.0


def test_max_gap_is_zero_for_identical_samples():
    sample = np.array([1.0, 2.0, 3.0, 4.0])
    assert samp.max_gap_statistic(sample, sample) == 0.0


def test_max_gap_is_one_for_disjoint_supports():
    a = np.array([0.0, 0.0, 0.0])
    b = np.array([100.0, 100.0, 100.0])
    assert samp.max_gap_statistic(a, b) == 1.0


def test_max_gap_between_two_exponential_samples_is_small():
    rng = np.random.default_rng(9)
    n = 30_000
    a = samp.sample_exponential_scratch(2.0, rng, n)
    b = rng.exponential(scale=0.5, size=n)
    gap = samp.max_gap_statistic(a, b)
    threshold = D.dkw_two_sample_threshold(n, n)
    assert gap < threshold


# ---------------------------------------------------------------------------
# dkw_two_sample_threshold / standard_error helpers
# ---------------------------------------------------------------------------


def test_dkw_threshold_shrinks_as_n_grows():
    small = D.dkw_two_sample_threshold(1_000, 1_000)
    large = D.dkw_two_sample_threshold(100_000, 100_000)
    assert large < small


def test_standard_error_of_mean_scales_as_inverse_sqrt_n():
    se_100 = D.standard_error_of_mean(4.0, 100)
    se_10000 = D.standard_error_of_mean(4.0, 10_000)
    assert abs(se_100 / se_10000 - 10.0) < 1e-9


def test_standard_error_of_proportion_is_symmetric_in_p():
    assert D.standard_error_of_proportion(0.3, 1000) == D.standard_error_of_proportion(0.7, 1000)
