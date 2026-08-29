"""Your running score. Unattempted work SKIPS; wrong work FAILS with both values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap
rather than guess at it.

Nothing in here checks that a function exists or that a file is present.
Every test runs your code and compares a value.
"""

from fractions import Fraction

import numpy as np
import pytest

import answers
import dataset as D
import distributions as dist
import sampling as samp

# --------------------------------------------------------------------------
# The skip machinery
# --------------------------------------------------------------------------


def need(value, what):
    """Skip if the exercise has not been attempted, otherwise hand it back."""
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except (TypeError, AttributeError, NotImplementedError):
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def close(got, want, tol, what):
    assert abs(float(got) - float(want)) < tol, (
        f"{what}: your answer {got!r}, expected {want!r} "
        f"(difference {abs(float(got) - float(want)):.3e}, tolerance {tol:g})"
    )


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from
    a collection error that quietly ran nothing at all."""
    assert len(D.TWO_DICE_SPACE) == 36


# --------------------------------------------------------------------------
# Exercise 1 -- the pmf of a sum
# --------------------------------------------------------------------------


def test_1_pmf_has_eleven_entries():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    assert set(pmf) == set(range(2, 13))


def test_1_pmf_of_seven_is_exactly_one_sixth():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    assert pmf[7] == Fraction(1, 6), "pmf[7] must be exactly Fraction(1, 6)"


def test_1_pmf_returns_fractions():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    assert all(isinstance(p, Fraction) for p in pmf.values()), (
        "every pmf value must be a Fraction, not a float"
    )


def test_1_seven_is_six_times_two():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    assert pmf[7] == 6 * pmf[2]


# --------------------------------------------------------------------------
# Exercise 2 -- the cdf
# --------------------------------------------------------------------------


def test_2_cdf_is_monotone():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    cdf = attempt(lambda: dist.cdf_from_pmf(pmf), "cdf_from_pmf")
    values = [cdf[k] for k in sorted(cdf)]
    assert all(a <= b for a, b in zip(values, values[1:]))


def test_2_cdf_ends_at_one():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    cdf = attempt(lambda: dist.cdf_from_pmf(pmf), "cdf_from_pmf")
    assert cdf[max(cdf)] == 1


def test_2_cdf_difference_equals_pmf():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    cdf = attempt(lambda: dist.cdf_from_pmf(pmf), "cdf_from_pmf")
    assert cdf[7] - cdf[6] == pmf[7]


# --------------------------------------------------------------------------
# Exercise 3 -- expectation and variance
# --------------------------------------------------------------------------


def test_3_expectation_of_sum_is_seven():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    got = attempt(lambda: dist.expectation_pmf(pmf), "expectation_pmf")
    assert got == 7


def test_3_variance_of_sum_is_35_over_6():
    pmf = attempt(dist.dice_sum_pmf, "dice_sum_pmf")
    got = attempt(lambda: dist.variance_pmf(pmf), "variance_pmf")
    assert got == Fraction(35, 6)


# --------------------------------------------------------------------------
# Exercise 4 -- linearity with a dependent pair
# --------------------------------------------------------------------------


def test_4_linearity_holds_for_the_dependent_pair():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    e_x = attempt(lambda: dist.expectation_over(outcomes, weight, D.first_die), "expectation_over")
    e_y = attempt(lambda: dist.expectation_over(outcomes, weight, D.dice_sum), "expectation_over")
    e_sum = attempt(
        lambda: dist.expectation_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o)),
        "expectation_over",
    )
    assert e_sum == e_x + e_y, "E[X + Y] must equal E[X] + E[Y] EXACTLY, even though X and Y are dependent"


# --------------------------------------------------------------------------
# Exercise 5 -- variance is not additive
# --------------------------------------------------------------------------


def test_5_variance_of_sum_is_not_the_naive_sum():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    var_x = attempt(lambda: dist.variance_over(outcomes, weight, D.first_die), "variance_over")
    var_y = attempt(lambda: dist.variance_over(outcomes, weight, D.dice_sum), "variance_over")
    var_sum = attempt(
        lambda: dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o)),
        "variance_over",
    )
    assert var_sum != var_x + var_y


def test_5_variance_of_sum_matches_the_full_covariance_formula():
    outcomes, weight = D.TWO_DICE_SPACE, D.TWO_DICE_WEIGHT
    var_x = attempt(lambda: dist.variance_over(outcomes, weight, D.first_die), "variance_over")
    var_y = attempt(lambda: dist.variance_over(outcomes, weight, D.dice_sum), "variance_over")
    cov_xy = attempt(
        lambda: dist.covariance_over(outcomes, weight, D.first_die, D.dice_sum), "covariance_over"
    )
    var_sum = attempt(
        lambda: dist.variance_over(outcomes, weight, lambda o: D.first_die(o) + D.dice_sum(o)),
        "variance_over",
    )
    assert var_sum == var_x + var_y + 2 * cov_xy


# --------------------------------------------------------------------------
# Exercise 6 -- Jensen's inequality
# --------------------------------------------------------------------------


def test_6_jensen_strict_for_a_die():
    outcomes, weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
    e_x2 = attempt(lambda: dist.expectation_over(outcomes, weight, lambda x: x * x), "expectation_over")
    e_x = attempt(lambda: dist.expectation_over(outcomes, weight, lambda x: x), "expectation_over")
    assert e_x2 > e_x**2


def test_6_jensen_gap_equals_variance():
    outcomes, weight = D.DIE_FACES, D.ONE_DIE_WEIGHT
    e_x2 = attempt(lambda: dist.expectation_over(outcomes, weight, lambda x: x * x), "expectation_over")
    e_x = attempt(lambda: dist.expectation_over(outcomes, weight, lambda x: x), "expectation_over")
    var_x = attempt(lambda: dist.variance_over(outcomes, weight, lambda x: x), "variance_over")
    assert e_x2 - e_x**2 == var_x


# --------------------------------------------------------------------------
# Exercise 7 -- inverse-CDF discrete sampling
# --------------------------------------------------------------------------


def test_7_sampler_draws_only_pmf_values():
    pmf = {k: float(v) for k, v in D_pmf_for_starter()}
    rng = np.random.default_rng(0)
    draws = attempt(
        lambda: samp.sample_discrete_inverse_cdf(pmf, rng, 2_000), "sample_discrete_inverse_cdf"
    )
    assert set(draws.astype(int).tolist()) <= set(pmf)


def test_7_sampler_matches_pmf_within_tolerance():
    pmf = {k: float(v) for k, v in D_pmf_for_starter()}
    rng = np.random.default_rng(1)
    n = 100_000
    draws = attempt(
        lambda: samp.sample_discrete_inverse_cdf(pmf, rng, n), "sample_discrete_inverse_cdf"
    )
    values, counts = np.unique(draws, return_counts=True)
    empirical = dict(zip(values.astype(int), counts / n))
    for k, p in pmf.items():
        se = D.standard_error_of_proportion(p, n)
        close(empirical.get(k, 0.0), p, 4.0 * se, f"P(Y={k})")


def test_7_sampler_same_seed_is_reproducible():
    pmf = {k: float(v) for k, v in D_pmf_for_starter()}
    a = attempt(
        lambda: samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(7), 500),
        "sample_discrete_inverse_cdf",
    )
    b = attempt(
        lambda: samp.sample_discrete_inverse_cdf(pmf, np.random.default_rng(7), 500),
        "sample_discrete_inverse_cdf",
    )
    assert np.array_equal(a, b)


def D_pmf_for_starter():
    # A helper that does not itself depend on the reader's dice_sum_pmf,
    # so exercise 7's tests can run even before exercise 1 is solved.
    from itertools import product

    counts: dict[int, int] = {}
    for a, b in product(range(1, 7), range(1, 7)):
        total = a + b
        counts[total] = counts.get(total, 0) + 1
    return {k: Fraction(v, 36) for k, v in counts.items()}.items()


# --------------------------------------------------------------------------
# Exercise 8 -- exponential from scratch
# --------------------------------------------------------------------------


def test_8_exponential_scratch_is_nonnegative():
    rng = np.random.default_rng(3)
    draws = attempt(
        lambda: samp.sample_exponential_scratch(1.0, rng, 5_000), "sample_exponential_scratch"
    )
    assert (draws >= 0).all()


def test_8_exponential_scratch_mean_is_close_to_one_over_rate():
    rate = 2.0
    rng = np.random.default_rng(4)
    n = 100_000
    draws = attempt(
        lambda: samp.sample_exponential_scratch(rate, rng, n), "sample_exponential_scratch"
    )
    tol = 3.0 * D.standard_error_of_mean((1.0 / rate) ** 2, n)
    close(draws.mean(), 1.0 / rate, tol, "exponential sample mean")


def test_8_max_gap_of_identical_samples_is_zero():
    sample = np.array([1.0, 2.0, 3.0])
    got = attempt(lambda: samp.max_gap_statistic(sample, sample), "max_gap_statistic")
    assert got == 0.0


# --------------------------------------------------------------------------
# Exercise 9 -- Poisson as a Binomial limit
# --------------------------------------------------------------------------


def test_9_binomial_pmf_sums_to_one():
    total = 0.0
    for k in range(11):
        total += attempt(lambda k=k: dist.binomial_pmf(10, 0.3, k), "binomial_pmf")
    assert abs(total - 1.0) < 1e-9


def test_9_poisson_pmf_at_zero_matches_exp_of_minus_lambda():
    import math

    got = attempt(lambda: dist.poisson_pmf(2.0, 0), "poisson_pmf")
    assert abs(got - math.exp(-2.0)) < 1e-12


def test_9_gap_decreases_monotonically():
    lam = D.POISSON_LAMBDA
    gaps = [
        attempt(
            lambda n=n: dist.max_binomial_poisson_gap(n, lam / n, lam, D.POISSON_COMPARISON_KS),
            "max_binomial_poisson_gap",
        )
        for n in D.POISSON_LIMIT_NS
    ]
    assert all(a > b for a, b in zip(gaps, gaps[1:]))


# --------------------------------------------------------------------------
# Exercise 10 -- density above 1
# --------------------------------------------------------------------------


def test_10_uniform_density_is_two():
    got = attempt(lambda: dist.uniform_density(0.25, 0.0, 0.5), "uniform_density")
    assert got == 2.0


def test_10_numeric_integral_of_density_is_one():
    got = attempt(
        lambda: dist.numeric_integral(lambda x: dist.uniform_density(x, 0.0, 0.5), 0.0, 0.5, 50_000),
        "numeric_integral",
    )
    close(got, 1.0, 1e-6, "integral of the Uniform(0, 0.5) density")


# --------------------------------------------------------------------------
# The eighteen predictions
# --------------------------------------------------------------------------

EXPECTED: dict[str, object] = {
    "p_sum_seven": float(Fraction(1, 6)),
    "ratio_seven_to_two": 6,
    "cdf_at_twelve": 1.0,
    "cdf_difference_seven_six": float(Fraction(1, 6)),
    "expectation_of_sum": 7.0,
    "variance_of_sum": float(Fraction(35, 6)),
    "expectation_x_plus_y": float(Fraction(21, 2)),
    "linearity_holds_for_dependent_pair": True,
    "variance_naive_sum_holds": False,
    "variance_x_plus_y": float(Fraction(175, 12)),
    "jensen_strict_for_die": True,
    "jensen_gap_equals_variance": True,
    "discrete_sampler_reproducible": True,
    "exponential_scratch_nonnegative": True,
    "poisson_gap_decreases_monotonically": True,
    "uniform_density_value": 2.0,
    "uniform_density_exceeds_one": True,
    "uniform_integral_equals_one": True,
}

HINTS: dict[str, str] = {
    "ratio_seven_to_two": (
        "P(sum=7) = 6/36 and P(sum=2) = 1/36. Divide one by the other."
    ),
    "variance_naive_sum_holds": (
        "X and Y are dependent, and Var[X+Y] = Var[X] + Var[Y] + 2*Cov(X,Y). "
        "The covariance term here is not zero."
    ),
    "expectation_x_plus_y": (
        "Linearity holds regardless of dependence: E[X+Y] = E[X] + E[Y] = "
        "3.5 + 7."
    ),
}


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_predictions(key):
    got = need(answers.ANSWERS.get(key), f"answers.ANSWERS[{key!r}]")
    want = EXPECTED[key]
    hint = HINTS.get(key, "")
    if isinstance(want, bool) or isinstance(want, int):
        assert got == want, f"{key}: your answer {got!r}, expected {want!r}. {hint}"
    else:
        assert abs(float(got) - want) < 1e-6, (
            f"{key}: your answer {got!r}, expected {want!r}. {hint}"
        )


def test_every_answer_key_is_still_present():
    missing = sorted(set(EXPECTED) - set(answers.ANSWERS))
    assert not missing, f"answers.py is missing these keys: {missing}"
