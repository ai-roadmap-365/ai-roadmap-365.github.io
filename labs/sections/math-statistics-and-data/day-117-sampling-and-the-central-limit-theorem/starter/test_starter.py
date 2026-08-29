"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap rather
than guess at it.
"""

import math

import numpy as np
import pytest

import dataset as D
import sampling as S


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except (TypeError, AttributeError, NotImplementedError):
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from a
    collection error that quietly ran nothing at all."""
    assert D.POP_SIZE > 0


# --------------------------------------------------------------------------
# Exercise 1 -- the sampling distribution itself
# --------------------------------------------------------------------------


def test_1_sampling_distribution_has_one_mean_per_trial():
    rng = np.random.default_rng(201)
    means = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, n=20, trials=300, rng=rng),
        "sampling_distribution",
    )
    assert means.shape == (300,)


def test_1_sampling_distribution_mean_is_close_to_population_mean():
    rng = np.random.default_rng(202)
    pop_mean, pop_sigma = attempt(
        lambda: S.population_mean_std(D.SKEWED_POP), "population_mean_std"
    )
    n, trials = 50, 20_000
    means = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, n, trials, rng), "sampling_distribution"
    )
    se_theory = attempt(
        lambda: S.theoretical_standard_error(pop_sigma, n), "theoretical_standard_error"
    )
    se_of_mean = se_theory / math.sqrt(trials)
    assert abs(means.mean() - pop_mean) < 4.0 * se_of_mean


# --------------------------------------------------------------------------
# Exercise 2 -- the sqrt(n) law
# --------------------------------------------------------------------------


def test_2_standard_error_halves_when_n_quadruples():
    rng = np.random.default_rng(203)
    ses = {}
    for n in D.SQRT_N_LAW_NS:
        means = attempt(
            lambda n=n: S.sampling_distribution(D.SKEWED_POP, n, D.SQRT_N_LAW_TRIALS, rng),
            "sampling_distribution",
        )
        ses[n] = means.std(ddof=1)
    for smaller, larger in zip(D.SQRT_N_LAW_NS, D.SQRT_N_LAW_NS[1:]):
        ratio = ses[smaller] / ses[larger]
        assert abs(ratio - 2.0) < D.SQRT_N_LAW_RATIO_TOLERANCE, (
            f"SE(n={smaller})/SE(n={larger}) = {ratio:.3f}, expected near 2.0"
        )


# --------------------------------------------------------------------------
# Exercise 3 -- CLT from a skewed population
# --------------------------------------------------------------------------


def test_3_skewness_of_the_sampling_distribution_decreases_monotonically():
    rng = np.random.default_rng(204)
    skews = []
    for n in D.SKEW_DEMO_NS:
        means = attempt(
            lambda n=n: S.sampling_distribution(D.SKEWED_POP, n, D.SKEW_DEMO_TRIALS, rng),
            "sampling_distribution",
        )
        skews.append(attempt(lambda means=means: S.skewness(means), "skewness"))
    for a, b in zip(skews, skews[1:]):
        assert b < a, f"skewness did not decrease: {skews}"


# --------------------------------------------------------------------------
# Exercise 4 -- the Cauchy counterexample
# --------------------------------------------------------------------------


def test_4_exponential_mean_shrinks_but_cauchy_mean_does_not():
    rng = np.random.default_rng(205)
    exp_small = attempt(
        lambda: S.exponential_mean_iqr(D.CAUCHY_DEMO_N_SMALL, D.CAUCHY_DEMO_TRIALS, rng, D.EXPONENTIAL_SCALE),
        "exponential_mean_iqr",
    )
    exp_large = attempt(
        lambda: S.exponential_mean_iqr(D.CAUCHY_DEMO_N_LARGE, D.CAUCHY_DEMO_TRIALS, rng, D.EXPONENTIAL_SCALE),
        "exponential_mean_iqr",
    )
    cauchy_small = attempt(
        lambda: S.cauchy_mean_iqr(D.CAUCHY_DEMO_N_SMALL, D.CAUCHY_DEMO_TRIALS, rng), "cauchy_mean_iqr"
    )
    cauchy_large = attempt(
        lambda: S.cauchy_mean_iqr(D.CAUCHY_DEMO_N_LARGE, D.CAUCHY_DEMO_TRIALS, rng), "cauchy_mean_iqr"
    )
    assert exp_small / exp_large > D.EXPONENTIAL_SHRINK_FLOOR
    assert D.CAUCHY_NO_SHRINK_LOW < cauchy_small / cauchy_large < D.CAUCHY_NO_SHRINK_HIGH


# --------------------------------------------------------------------------
# Exercise 5 -- bias does not shrink
# --------------------------------------------------------------------------


def test_5_biased_sampler_error_stays_flat_while_unbiased_shrinks():
    rng = np.random.default_rng(206)
    true_mean = float(D.SKEWED_POP.mean())
    pool = attempt(lambda: S.biased_pool(D.SKEWED_POP), "biased_pool")

    def err(population, n):
        means = S.sampling_distribution(population, n, D.BIAS_DEMO_TRIALS, rng)
        return attempt(lambda: S.mean_absolute_error(means, true_mean), "mean_absolute_error")

    unbiased_small = err(D.SKEWED_POP, D.BIAS_DEMO_N_SMALL)
    unbiased_large = err(D.SKEWED_POP, D.BIAS_DEMO_N_LARGE)
    biased_small = err(pool, D.BIAS_DEMO_N_SMALL)
    biased_large = err(pool, D.BIAS_DEMO_N_LARGE)

    assert unbiased_small / unbiased_large > D.UNBIASED_SHRINK_FLOOR
    assert D.BIASED_FLAT_LOW < biased_small / biased_large < D.BIASED_FLAT_HIGH


# --------------------------------------------------------------------------
# Exercise 6 -- the bootstrap, from scratch
# --------------------------------------------------------------------------


def test_6_bootstrap_se_of_mean_agrees_with_formula():
    rng = np.random.default_rng(207)
    data = rng.normal(D.BOOTSTRAP_SAMPLE_MEAN, D.BOOTSTRAP_SAMPLE_STD, D.BOOTSTRAP_SAMPLE_SIZE)
    theoretical = data.std(ddof=1) / math.sqrt(len(data))
    boot_se = attempt(
        lambda: S.bootstrap_standard_error(data, lambda a: a.mean(axis=1), D.BOOTSTRAP_N_BOOT, rng),
        "bootstrap_standard_error",
    )
    assert abs(boot_se - theoretical) / theoretical < D.BOOTSTRAP_MEAN_RELATIVE_TOLERANCE


def test_6_bootstrap_se_of_median_is_sane():
    rng = np.random.default_rng(208)
    data = rng.normal(D.BOOTSTRAP_SAMPLE_MEAN, D.BOOTSTRAP_SAMPLE_STD, D.BOOTSTRAP_SAMPLE_SIZE)
    boot_se_median = attempt(
        lambda: S.bootstrap_standard_error(data, lambda a: np.median(a, axis=1), D.BOOTSTRAP_N_BOOT, rng),
        "bootstrap_standard_error",
    )
    fresh = rng.normal(
        D.BOOTSTRAP_SAMPLE_MEAN, D.BOOTSTRAP_SAMPLE_STD, size=(D.FRESH_MEDIAN_REPLICATIONS, D.BOOTSTRAP_SAMPLE_SIZE)
    )
    fresh_se = np.median(fresh, axis=1).std(ddof=1)
    ratio = boot_se_median / fresh_se
    assert D.BOOTSTRAP_MEDIAN_SANITY_LOW < ratio < D.BOOTSTRAP_MEDIAN_SANITY_HIGH


# --------------------------------------------------------------------------
# Exercise 7 -- dependence inflates the true standard error
# --------------------------------------------------------------------------


def test_7_naive_se_understates_the_true_se_under_dependence():
    rng = np.random.default_rng(209)
    naive_ses = [
        attempt(
            lambda: S.naive_standard_error(S.ar1_series(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, rng)),
            "naive_standard_error / ar1_series",
        )
        for _ in range(300)
    ]
    naive_avg = float(np.mean(naive_ses))
    true_se = attempt(
        lambda: S.true_standard_error_by_replication(D.AR1_N, D.AR1_PHI, D.AR1_SIGMA, D.AR1_REPLICATIONS, rng),
        "true_standard_error_by_replication",
    )
    assert true_se / naive_avg > D.AR1_INFLATION_FLOOR


# --------------------------------------------------------------------------
# Exercise 8 -- the evaluation-margin calculation
# --------------------------------------------------------------------------


def test_8_binomial_se_matches_the_brief_and_the_margin_is_noise():
    se = attempt(lambda: S.binomial_standard_error(D.EVAL_ACCURACY, D.EVAL_N), "binomial_standard_error")
    se_pct = se * 100.0
    assert abs(se_pct - D.EVAL_EXPECTED_SE_PCT) < D.EVAL_SE_TOLERANCE_PCT
    assert D.EVAL_MARGIN_PCT / se_pct < 1.0


# --------------------------------------------------------------------------
# Exercise 9 -- reproducibility (depends only on exercise 1)
# --------------------------------------------------------------------------


def test_9_same_seed_reproduces_identical_results():
    a1 = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, np.random.default_rng(D.REPRO_SEED_A)),
        "sampling_distribution",
    )
    a2 = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, np.random.default_rng(D.REPRO_SEED_A)),
        "sampling_distribution",
    )
    assert np.array_equal(a1, a2)


def test_9_different_seed_gives_a_different_but_compatible_result():
    a = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, np.random.default_rng(D.REPRO_SEED_A)),
        "sampling_distribution",
    )
    b = attempt(
        lambda: S.sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, np.random.default_rng(D.REPRO_SEED_B)),
        "sampling_distribution",
    )
    assert not np.array_equal(a, b)
    pop_mean, pop_sigma = attempt(lambda: S.population_mean_std(D.SKEWED_POP), "population_mean_std")
    se_theory = attempt(lambda: S.theoretical_standard_error(pop_sigma, D.REPRO_N), "theoretical_standard_error")
    se_of_mean = se_theory / math.sqrt(D.REPRO_TRIALS)
    assert abs(a.mean() - b.mean()) < 5.0 * se_of_mean
