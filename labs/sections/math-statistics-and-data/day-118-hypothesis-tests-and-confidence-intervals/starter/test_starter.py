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
import inference as I


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
    assert D.POP_MEAN > 0


# --------------------------------------------------------------------------
# Exercise 1 -- phi, p_from_z_two_sided, two_sample_z_test
# --------------------------------------------------------------------------


def test_1_phi_of_zero_is_one_half():
    result = attempt(lambda: I.phi(0.0), "phi")
    assert result == pytest.approx(0.5), f"phi(0.0) should be 0.5, got {result}"


def test_1_p_from_z_two_sided_at_1_96_is_near_0_05():
    result = attempt(lambda: I.p_from_z_two_sided(1.959964), "p_from_z_two_sided")
    assert result == pytest.approx(0.05, abs=1e-4), f"expected ~0.05, got {result}"


def test_1_two_sample_z_test_matches_hand_computation():
    a = [50, 52, 49, 51, 53, 48, 50, 52, 51, 49]
    b = [54, 55, 53, 56, 54, 52, 55, 53, 54, 56]
    z, p = attempt(lambda: I.two_sample_z_test(a, b), "two_sample_z_test")
    import statistics

    mean_a, var_a = statistics.mean(a), statistics.variance(a)
    mean_b, var_b = statistics.mean(b), statistics.variance(b)
    se = math.sqrt(var_a / len(a) + var_b / len(b))
    z_hand = (mean_a - mean_b) / se
    assert z == pytest.approx(z_hand, abs=1e-6), f"expected z={z_hand}, got {z}"
    assert p < 0.001, f"these samples are clearly different -- expected p < 0.001, got {p}"


# --------------------------------------------------------------------------
# Exercise 2 -- z_critical_two_sided, confidence_interval_mean, coverage
# --------------------------------------------------------------------------


def test_2_z_critical_two_sided_matches_known_constant():
    result = attempt(lambda: I.z_critical_two_sided(0.05), "z_critical_two_sided")
    assert result == pytest.approx(1.959964, abs=1e-4), f"expected ~1.959964, got {result}"


def test_2_confidence_interval_mean_is_centered_on_the_sample_mean():
    rng = np.random.default_rng(1)
    sample = D.normal_population(rng, 100, D.POP_MEAN, D.POP_STD)
    lo, hi = attempt(lambda: I.confidence_interval_mean(sample, 0.05), "confidence_interval_mean")
    center = (lo + hi) / 2
    assert center == pytest.approx(sample.mean(), abs=1e-6), f"expected center {sample.mean()}, got {center}"


def test_2_coverage_is_close_to_nominal():
    rng = np.random.default_rng(42)

    def run():
        hits = 0
        trials = 2000
        for _ in range(trials):
            sample = D.normal_population(rng, D.COVERAGE_SAMPLE_N, D.POP_MEAN, D.POP_STD)
            lo, hi = I.confidence_interval_mean(sample, alpha=0.05)
            if lo <= D.POP_MEAN <= hi:
                hits += 1
        return hits / trials

    coverage = attempt(run, "confidence_interval_mean (coverage)")
    se = math.sqrt(0.95 * 0.05 / 2000)
    assert abs(coverage - 0.95) <= 3 * se, f"measured coverage {coverage} too far from 0.95"


# --------------------------------------------------------------------------
# Exercise 3 -- ci_excludes, one_sample_z_test_against_value, duality
# --------------------------------------------------------------------------


def test_3_ci_excludes():
    result = attempt(lambda: I.ci_excludes((1.0, 2.0), 3.0), "ci_excludes")
    assert result is True, f"3.0 is outside (1.0, 2.0) -- expected True, got {result}"
    result2 = attempt(lambda: I.ci_excludes((1.0, 2.0), 1.5), "ci_excludes")
    assert result2 is False, f"1.5 is inside (1.0, 2.0) -- expected False, got {result2}"


def test_3_duality_holds_exactly():
    rng = np.random.default_rng(9)

    def run():
        mismatches = 0
        for _ in range(200):
            n = int(rng.integers(15, 60))
            shift = 0.0 if rng.random() < 0.5 else rng.uniform(-6.0, 6.0)
            sample = D.normal_population(rng, n, D.POP_MEAN + shift, D.POP_STD)
            _, p = I.one_sample_z_test_against_value(sample, D.POP_MEAN)
            interval = I.confidence_interval_mean(sample, 0.05)
            if (p < 0.05) != I.ci_excludes(interval, D.POP_MEAN):
                mismatches += 1
        return mismatches

    mismatches = attempt(run, "one_sample_z_test_against_value / duality")
    assert mismatches == 0, f"expected zero test/interval disagreements, got {mismatches}"


# --------------------------------------------------------------------------
# Exercise 4 -- permutation_test_diff_means
# --------------------------------------------------------------------------


def test_4_permutation_test_returns_valid_probability():
    rng = np.random.default_rng(3)
    a = D.normal_population(rng, 30, D.POP_MEAN, D.POP_STD)
    b = D.normal_population(rng, 30, D.POP_B_MEAN, D.POP_B_STD)
    _, p = attempt(lambda: I.permutation_test_diff_means(a, b, 500, rng), "permutation_test_diff_means")
    assert 0.0 <= p <= 1.0, f"a p-value must be in [0, 1], got {p}"


def test_4_permutation_test_p_is_small_for_a_large_true_difference():
    rng = np.random.default_rng(4)
    a = D.normal_population(rng, 50, 0.0, 1.0)
    b = D.normal_population(rng, 50, 20.0, 1.0)
    _, p = attempt(lambda: I.permutation_test_diff_means(a, b, 500, rng), "permutation_test_diff_means")
    assert p < 0.01, f"a 20-sigma separation should be obviously significant, got p={p}"


# --------------------------------------------------------------------------
# Exercise 5 -- bonferroni_alpha
# --------------------------------------------------------------------------


def test_5_bonferroni_alpha_divides_by_m():
    result = attempt(lambda: I.bonferroni_alpha(0.05, 20), "bonferroni_alpha")
    assert result == pytest.approx(0.0025), f"expected 0.05/20=0.0025, got {result}"


# --------------------------------------------------------------------------
# Exercise 6 -- power_two_sample_z
# --------------------------------------------------------------------------


def test_6_power_increases_with_n():
    p1 = attempt(lambda: I.power_two_sample_z(3.0, 12.7, 20), "power_two_sample_z")
    p2 = attempt(lambda: I.power_two_sample_z(3.0, 12.7, 200), "power_two_sample_z")
    assert p2 > p1, f"power should rise with n, got power(20)={p1}, power(200)={p2}"


def test_6_power_at_zero_effect_equals_alpha():
    result = attempt(lambda: I.power_two_sample_z(0.0, 12.7, 100, alpha=0.05), "power_two_sample_z")
    assert result == pytest.approx(0.05, abs=1e-4), f"with no true effect, power should equal alpha, got {result}"


# --------------------------------------------------------------------------
# Exercise 9 -- bootstrap_ci
# --------------------------------------------------------------------------


def test_9_bootstrap_ci_contains_the_sample_mean():
    rng = np.random.default_rng(5)
    sample = D.normal_population(rng, 200, D.POP_MEAN, D.POP_STD)
    lo, hi = attempt(lambda: I.bootstrap_ci(sample, np.mean, 1000, 0.05, rng), "bootstrap_ci")
    assert lo < sample.mean() < hi, f"the sample mean {sample.mean()} should fall inside [{lo}, {hi}]"


def test_9_bootstrap_ci_agrees_with_normal_ci():
    rng = np.random.default_rng(6)
    sample = D.normal_population(rng, 200, D.POP_MEAN, D.POP_STD)
    normal_lo, normal_hi = attempt(
        lambda: I.confidence_interval_mean(sample, 0.05), "confidence_interval_mean"
    )
    boot_lo, boot_hi = attempt(lambda: I.bootstrap_ci(sample, np.mean, 3000, 0.05, rng), "bootstrap_ci")
    width_ratio = (boot_hi - boot_lo) / (normal_hi - normal_lo)
    assert 0.7 < width_ratio < 1.3, f"bootstrap and normal interval widths should roughly agree, ratio={width_ratio}"
