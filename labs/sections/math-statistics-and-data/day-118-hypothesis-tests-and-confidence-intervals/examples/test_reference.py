"""The reference pytest suite: every function in `inference.py`, checked
against real values from real seeded runs and against hand computations.

Run from the lab directory:

    .venv/bin/pytest examples -q
"""

import math

import numpy as np
import pytest

import dataset as D
import inference as I


# --------------------------------------------------------------------------
# phi / p_from_z_two_sided / z_critical_two_sided
# --------------------------------------------------------------------------


def test_phi_of_zero_is_one_half():
    assert I.phi(0.0) == pytest.approx(0.5)


def test_phi_matches_known_normal_table_values():
    assert I.phi(1.96) == pytest.approx(0.9750, abs=0.0001)
    assert I.phi(-1.96) == pytest.approx(0.0250, abs=0.0001)


def test_z_critical_two_sided_matches_known_constants():
    assert I.z_critical_two_sided(0.05) == pytest.approx(1.959964, abs=1e-5)
    assert I.z_critical_two_sided(0.01) == pytest.approx(2.575829, abs=1e-5)


def test_p_from_z_two_sided_round_trips_with_z_critical():
    z = I.z_critical_two_sided(0.05)
    assert I.p_from_z_two_sided(z) == pytest.approx(0.05, abs=1e-6)


# --------------------------------------------------------------------------
# two_sample_z_test
# --------------------------------------------------------------------------


def test_two_sample_z_test_matches_hand_computation():
    a = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    b = [54, 55, 53, 56, 54, 52, 55, 53, 54, 56]
    z, p = I.two_sample_z_test(a, b)
    import statistics

    mean_a, var_a = statistics.mean(a), statistics.variance(a)
    mean_b, var_b = statistics.mean(b), statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z_hand = (mean_a - mean_b) / se
    assert z == pytest.approx(z_hand, abs=1e-9)
    assert p < 0.001


def test_two_sample_z_test_identical_samples_gives_p_near_one():
    a = [10.0, 20.0, 30.0, 40.0, 50.0]
    z, p = I.two_sample_z_test(a, a)
    assert z == pytest.approx(0.0, abs=1e-9)
    assert p == pytest.approx(1.0, abs=1e-9)


# --------------------------------------------------------------------------
# confidence_interval_mean / ci_excludes
# --------------------------------------------------------------------------


def test_confidence_interval_mean_is_centered_on_the_sample_mean():
    rng = np.random.default_rng(1)
    sample = D.normal_population(rng, 100, D.POP_MEAN, D.POP_STD)
    lo, hi = I.confidence_interval_mean(sample, alpha=0.05)
    assert (lo + hi) / 2 == pytest.approx(sample.mean(), abs=1e-9)
    assert lo < sample.mean() < hi


def test_wider_interval_for_smaller_alpha():
    rng = np.random.default_rng(2)
    sample = D.normal_population(rng, 100, D.POP_MEAN, D.POP_STD)
    lo95, hi95 = I.confidence_interval_mean(sample, alpha=0.05)
    lo99, hi99 = I.confidence_interval_mean(sample, alpha=0.01)
    assert (hi99 - lo99) > (hi95 - lo95)


def test_ci_excludes():
    assert I.ci_excludes((1.0, 2.0), 3.0) is True
    assert I.ci_excludes((1.0, 2.0), 1.5) is False
    assert I.ci_excludes((1.0, 2.0), 1.0) is False  # boundary counts as inside


def test_coverage_is_close_to_nominal():
    rng = np.random.default_rng(42)
    hits = 0
    trials = 2000
    for _ in range(trials):
        sample = D.normal_population(rng, D.COVERAGE_SAMPLE_N, D.POP_MEAN, D.POP_STD)
        lo, hi = I.confidence_interval_mean(sample, alpha=0.05)
        if lo <= D.POP_MEAN <= hi:
            hits += 1
    coverage = hits / trials
    se = math.sqrt(0.95 * 0.05 / trials)
    assert abs(coverage - 0.95) <= 3 * se


# --------------------------------------------------------------------------
# duality: test rejects <=> interval excludes the null value
# --------------------------------------------------------------------------


def test_duality_holds_exactly_across_many_datasets():
    rng = np.random.default_rng(9)
    for _ in range(200):
        n = int(rng.integers(15, 60))
        shift = 0.0 if rng.random() < 0.5 else rng.uniform(-6.0, 6.0)
        sample = D.normal_population(rng, n, D.POP_MEAN + shift, D.POP_STD)
        _, p = I.one_sample_z_test_against_value(sample, D.POP_MEAN)
        interval = I.confidence_interval_mean(sample, 0.05)
        assert (p < 0.05) == I.ci_excludes(interval, D.POP_MEAN)


# --------------------------------------------------------------------------
# permutation_test_diff_means
# --------------------------------------------------------------------------


def test_permutation_test_returns_valid_probability():
    rng = np.random.default_rng(3)
    a = D.normal_population(rng, 30, D.POP_MEAN, D.POP_STD)
    b = D.normal_population(rng, 30, D.POP_B_MEAN, D.POP_B_STD)
    _, p = I.permutation_test_diff_means(a, b, 500, rng)
    assert 0.0 <= p <= 1.0


def test_permutation_test_p_is_small_for_a_large_true_difference():
    rng = np.random.default_rng(4)
    a = D.normal_population(rng, 50, 0.0, 1.0)
    b = D.normal_population(rng, 50, 20.0, 1.0)
    _, p = I.permutation_test_diff_means(a, b, 500, rng)
    assert p < 0.01


# --------------------------------------------------------------------------
# power_two_sample_z
# --------------------------------------------------------------------------


def test_power_is_between_alpha_and_one():
    power = I.power_two_sample_z(effect=5.0, sigma=12.7, n_per_group=50)
    assert 0.05 < power < 1.0


def test_power_increases_with_n():
    p1 = I.power_two_sample_z(effect=3.0, sigma=12.7, n_per_group=20)
    p2 = I.power_two_sample_z(effect=3.0, sigma=12.7, n_per_group=200)
    assert p2 > p1


def test_power_increases_with_effect_size():
    p1 = I.power_two_sample_z(effect=1.0, sigma=12.7, n_per_group=100)
    p2 = I.power_two_sample_z(effect=10.0, sigma=12.7, n_per_group=100)
    assert p2 > p1


def test_power_at_zero_effect_equals_alpha():
    # With no true effect, "power" is just the false-positive rate: alpha.
    power = I.power_two_sample_z(effect=0.0, sigma=12.7, n_per_group=100, alpha=0.05)
    assert power == pytest.approx(0.05, abs=1e-6)


# --------------------------------------------------------------------------
# bonferroni_alpha
# --------------------------------------------------------------------------


def test_bonferroni_alpha_divides_by_m():
    assert I.bonferroni_alpha(0.05, 20) == pytest.approx(0.0025)


def test_exact_family_wise_error_rate_for_twenty_tests():
    exact = 1 - (1 - 0.05) ** 20
    assert exact == pytest.approx(0.6415, abs=0.0001)


def test_exact_bonferroni_corrected_rate_for_twenty_tests():
    corrected = 1 - (1 - 0.05 / 20) ** 20
    assert corrected == pytest.approx(0.0488, abs=0.0001)


# --------------------------------------------------------------------------
# bootstrap_ci
# --------------------------------------------------------------------------


def test_bootstrap_ci_contains_the_sample_mean_region():
    rng = np.random.default_rng(5)
    sample = D.normal_population(rng, 200, D.POP_MEAN, D.POP_STD)
    lo, hi = I.bootstrap_ci(sample, np.mean, 1000, 0.05, rng)
    assert lo < sample.mean() < hi


def test_bootstrap_ci_agrees_with_normal_ci_for_the_mean():
    rng = np.random.default_rng(6)
    sample = D.normal_population(rng, 200, D.POP_MEAN, D.POP_STD)
    normal_lo, normal_hi = I.confidence_interval_mean(sample, 0.05)
    boot_lo, boot_hi = I.bootstrap_ci(sample, np.mean, 3000, 0.05, rng)
    normal_center = (normal_lo + normal_hi) / 2
    boot_center = (boot_lo + boot_hi) / 2
    se = sample.std(ddof=1) / math.sqrt(200)
    assert abs(normal_center - boot_center) / se < 1.0
    width_ratio = (boot_hi - boot_lo) / (normal_hi - normal_lo)
    assert 0.7 < width_ratio < 1.3
