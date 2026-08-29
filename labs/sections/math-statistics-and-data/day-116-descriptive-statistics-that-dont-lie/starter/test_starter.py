"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap
rather than guess at it.
"""

import numpy as np
import pytest

import answers
import dataset as D
import descriptive as F
import simulate as S


def need(value, what):
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def attempt(fn, what):
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
    assert len(D.SALARY_LIST) == 9


# ---------------------------------------------------------------------------
# Exercise 1 -- mean, median, mode
# ---------------------------------------------------------------------------


def test_1_mean_matches_statistics_module():
    got = attempt(lambda: F.mean(D.ODD_LIST), "mean")
    import statistics as st

    assert got == st.fmean(D.ODD_LIST)


def test_1_median_odd_length():
    got = attempt(lambda: F.median(D.ODD_LIST), "median")
    assert got == 7.0


def test_1_median_even_length_averages_the_middle_two():
    got = attempt(lambda: F.median(D.EVEN_LIST), "median")
    assert got == 6.0


def test_1_modes_finds_the_single_peak():
    got = attempt(lambda: F.modes(D.ODD_LIST), "modes")
    assert got == [7]


def test_1_modes_finds_every_tied_value():
    got = attempt(lambda: F.modes(D.MULTIMODAL_LIST), "modes")
    assert got == [3, 8]


def test_1_prediction_odd_list_mean():
    predicted = need(answers.ANSWERS["odd_list_mean"], "odd_list_mean prediction")
    close(predicted, 7.444444444444445, 1e-6, "odd_list_mean")


def test_1_prediction_even_list_median():
    predicted = need(answers.ANSWERS["even_list_median"], "even_list_median prediction")
    close(predicted, 6.0, 1e-9, "even_list_median")


# ---------------------------------------------------------------------------
# Exercise 2 -- the breakdown point
# ---------------------------------------------------------------------------


def test_2_mean_moves_far():
    before, after = attempt(
        lambda: F.breakdown_point_mean(D.SALARY_LIST, D.CORRUPTED_SALARY),
        "breakdown_point_mean",
    )
    assert after - before > D.BREAKDOWN_MEAN_SHIFT_FLOOR


def test_2_median_does_not_move_at_all():
    before, after = attempt(
        lambda: F.breakdown_point_median(D.SALARY_LIST, D.CORRUPTED_SALARY),
        "breakdown_point_median",
    )
    assert after == before


def test_2_prediction_mean_breaks_down():
    predicted = need(answers.ANSWERS["mean_breaks_down"], "mean_breaks_down prediction")
    assert predicted is True


def test_2_prediction_median_breaks_down():
    predicted = need(answers.ANSWERS["median_breaks_down"], "median_breaks_down prediction")
    assert predicted is False


# ---------------------------------------------------------------------------
# Exercise 3 -- Bessel's correction
# ---------------------------------------------------------------------------


def test_3_divide_by_n_is_biased_low():
    rng = np.random.default_rng(D.BESSEL_SEED)
    biased, _ = attempt(
        lambda: S.bessel_trial_variances(
            rng,
            D.BESSEL_POPULATION_MEAN,
            D.BESSEL_POPULATION_SIGMA,
            D.BESSEL_SAMPLE_SIZE,
            D.BESSEL_TRIALS,
        ),
        "bessel_trial_variances",
    )
    ratio = float(biased.mean()) / D.BESSEL_TRUE_VARIANCE
    assert ratio < 1.0, "dividing by n should UNDERestimate the true variance"
    assert abs(ratio - D.BESSEL_EXPECTED_BIAS_FACTOR) < D.BESSEL_BIAS_FACTOR_TOLERANCE


def test_3_divide_by_n_minus_1_is_unbiased():
    rng = np.random.default_rng(D.BESSEL_SEED)
    _, unbiased = attempt(
        lambda: S.bessel_trial_variances(
            rng,
            D.BESSEL_POPULATION_MEAN,
            D.BESSEL_POPULATION_SIGMA,
            D.BESSEL_SAMPLE_SIZE,
            D.BESSEL_TRIALS,
        ),
        "bessel_trial_variances",
    )
    mean_unbiased = float(unbiased.mean())
    se = float(unbiased.std(ddof=1)) / (D.BESSEL_TRIALS**0.5)
    assert abs(mean_unbiased - D.BESSEL_TRUE_VARIANCE) < D.BESSEL_UNBIASED_SE_TOLERANCE * se


def test_3_prediction_bias_direction():
    predicted = need(
        answers.ANSWERS["divide_by_n_bias_direction"], "divide_by_n_bias_direction prediction"
    )
    assert predicted == "low"


# ---------------------------------------------------------------------------
# Exercise 4 -- percentile ambiguity
# ---------------------------------------------------------------------------


def test_4_conventions_disagree():
    values = {
        method: attempt(
            lambda method=method: F.percentile_under(
                D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, method
            ),
            "percentile_under",
        )
        for method in D.PERCENTILE_METHODS
    }
    assert len(set(values.values())) >= 2


def test_4_default_linear_matches_documented_value():
    got = attempt(
        lambda: F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, "linear"),
        "percentile_under",
    )
    assert got == 8.25


def test_4_prediction_disagree():
    predicted = need(
        answers.ANSWERS["percentile_methods_disagree"], "percentile_methods_disagree prediction"
    )
    assert predicted is True


def test_4_prediction_linear_value():
    predicted = need(
        answers.ANSWERS["percentile_linear_value"], "percentile_linear_value prediction"
    )
    close(predicted, 8.25, 1e-9, "percentile_linear_value")


# ---------------------------------------------------------------------------
# Exercise 5 -- Pearson versus Spearman
# ---------------------------------------------------------------------------


def test_5_pearson_on_parabola_is_essentially_zero():
    got = attempt(lambda: F.pearson(D.PARABOLA_X, D.PARABOLA_Y), "pearson")
    assert abs(got) < D.PARABOLA_PEARSON_TOLERANCE


def test_5_spearman_on_monotone_cubic_is_exactly_one():
    got = attempt(lambda: F.spearman(D.MONOTONE_X, D.MONOTONE_Y), "spearman")
    assert got == 1.0


def test_5_prediction_parabola_pearson():
    predicted = need(
        answers.ANSWERS["parabola_pearson_magnitude"], "parabola_pearson_magnitude prediction"
    )
    assert predicted == "close_to_zero"


def test_5_prediction_monotone_spearman():
    predicted = need(
        answers.ANSWERS["monotone_spearman_value"], "monotone_spearman_value prediction"
    )
    close(predicted, 1.0, 1e-9, "monotone_spearman_value")


# ---------------------------------------------------------------------------
# Exercise 6 -- Anscombe's quartet
# ---------------------------------------------------------------------------


def test_6_all_four_sets_agree_on_summaries():
    reference = attempt(
        lambda: F.anscombe_summary(*D.ANSCOMBE_SETS["I"]), "anscombe_summary"
    )
    for name in ("II", "III", "IV"):
        s = attempt(lambda name=name: F.anscombe_summary(*D.ANSCOMBE_SETS[name]), "anscombe_summary")
        assert round(s["mean_x"], 1) == round(reference["mean_x"], 1)
        assert round(s["correlation"], 1) == round(reference["correlation"], 1)


def test_6_shape_statistics_separate_set_iv():
    shapes = {
        name: attempt(lambda name=name: F.shape_statistics(*D.ANSCOMBE_SETS[name]), "shape_statistics")
        for name in D.ANSCOMBE_SETS
    }
    assert shapes["IV"]["max_leverage"] > 3.0 * shapes["I"]["max_leverage"]


def test_6_prediction_means_agree():
    predicted = need(answers.ANSWERS["anscombe_means_agree"], "anscombe_means_agree prediction")
    assert predicted is True


def test_6_prediction_set_iv_leverage():
    predicted = need(
        answers.ANSWERS["anscombe_set_iv_leverage_dominant"],
        "anscombe_set_iv_leverage_dominant prediction",
    )
    assert predicted is True


# ---------------------------------------------------------------------------
# Exercise 7 -- Simpson's paradox
# ---------------------------------------------------------------------------


def test_7_a_wins_every_subgroup():
    easy_a = attempt(lambda: F.success_rate(*D.TREATMENT_A_EASY), "success_rate")
    easy_b = attempt(lambda: F.success_rate(*D.TREATMENT_B_EASY), "success_rate")
    hard_a = attempt(lambda: F.success_rate(*D.TREATMENT_A_HARD), "success_rate")
    hard_b = attempt(lambda: F.success_rate(*D.TREATMENT_B_HARD), "success_rate")
    assert easy_a > easy_b
    assert hard_a > hard_b


def test_7_b_wins_overall():
    a_total = attempt(
        lambda: F.combined_rate(D.TREATMENT_A_EASY, D.TREATMENT_A_HARD), "combined_rate"
    )
    b_total = attempt(
        lambda: F.combined_rate(D.TREATMENT_B_EASY, D.TREATMENT_B_HARD), "combined_rate"
    )
    assert b_total > a_total


def test_7_prediction_b_wins_overall():
    predicted = need(answers.ANSWERS["simpson_b_wins_overall"], "simpson_b_wins_overall prediction")
    assert predicted is True


# ---------------------------------------------------------------------------
# Exercise 8 -- robust spread under contamination
# ---------------------------------------------------------------------------


def test_8_std_inflates_a_lot():
    rng = np.random.default_rng(D.CONTAMINATION_SEED)
    clean, contaminated = attempt(
        lambda: S.contaminated_sample(
            rng,
            D.CONTAMINATION_BASE_MEAN,
            D.CONTAMINATION_BASE_SIGMA,
            D.CONTAMINATION_BASE_N,
            D.CONTAMINATION_OUTLIERS,
        ),
        "contaminated_sample",
    )
    std_clean = float(np.std(clean, ddof=1))
    std_contam = float(np.std(contaminated, ddof=1))
    assert std_contam / std_clean > D.CONTAMINATION_STD_MULTIPLIER_FLOOR


def test_8_mad_barely_moves():
    rng = np.random.default_rng(D.CONTAMINATION_SEED)
    clean, contaminated = attempt(
        lambda: S.contaminated_sample(
            rng,
            D.CONTAMINATION_BASE_MEAN,
            D.CONTAMINATION_BASE_SIGMA,
            D.CONTAMINATION_BASE_N,
            D.CONTAMINATION_OUTLIERS,
        ),
        "contaminated_sample",
    )
    mad_clean = attempt(lambda: F.median_absolute_deviation(clean), "median_absolute_deviation")
    mad_contam = attempt(
        lambda: F.median_absolute_deviation(contaminated), "median_absolute_deviation"
    )
    assert mad_contam / mad_clean < D.CONTAMINATION_MAD_MULTIPLIER_CEILING


def test_8_prediction_std_inflates():
    predicted = need(
        answers.ANSWERS["contamination_inflates_std"], "contamination_inflates_std prediction"
    )
    assert predicted is True


def test_8_prediction_mad_stable():
    predicted = need(
        answers.ANSWERS["contamination_mad_stable"], "contamination_mad_stable prediction"
    )
    assert predicted is True


# ---------------------------------------------------------------------------
# Exercise 9 -- standardisation
# ---------------------------------------------------------------------------


def test_9_standardized_mean_and_std():
    rng = np.random.default_rng(D.STANDARDIZATION_SEED)
    x = rng.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
    zx = attempt(lambda: F.zscores(x), "zscores")
    mean_zx = sum(zx) / len(zx)
    std_zx = (sum((v - mean_zx) ** 2 for v in zx) / len(zx)) ** 0.5
    assert abs(mean_zx) < D.STANDARDIZATION_MEAN_TOLERANCE
    assert abs(std_zx - 1.0) < D.STANDARDIZATION_STD_TOLERANCE


def test_9_correlation_unchanged_by_standardizing():
    rng = np.random.default_rng(D.STANDARDIZATION_SEED)
    x = rng.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
    noise = rng.normal(0.0, D.STANDARDIZATION_Y_NOISE_SIGMA, D.STANDARDIZATION_N)
    y = D.STANDARDIZATION_Y_SLOPE * x + noise
    zx = attempt(lambda: F.zscores(x), "zscores")
    zy = attempt(lambda: F.zscores(y), "zscores")
    r_original = attempt(lambda: F.pearson(x, y), "pearson")
    r_standardized = attempt(lambda: F.pearson(zx, zy), "pearson")
    assert abs(r_original - r_standardized) < D.STANDARDIZATION_CORRELATION_TOLERANCE


def test_9_prediction_mean():
    predicted = need(answers.ANSWERS["standardized_mean"], "standardized_mean prediction")
    close(predicted, 0.0, 1e-6, "standardized_mean")


def test_9_prediction_std():
    predicted = need(answers.ANSWERS["standardized_std"], "standardized_std prediction")
    close(predicted, 1.0, 1e-6, "standardized_std")


def test_9_prediction_correlation_unchanged():
    predicted = need(
        answers.ANSWERS["standardizing_changes_correlation"],
        "standardizing_changes_correlation prediction",
    )
    assert predicted is False
