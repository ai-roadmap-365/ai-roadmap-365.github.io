"""The reference pytest suite: real values, real exceptions, run from
inside `examples/` (see `conftest.py`)."""

import statistics as st

import numpy as np
import pytest

import dataset as D
import descriptive as F
import simulate as S


# ---------------------------------------------------------------------------
# Exercise 1: mean, median, mode
# ---------------------------------------------------------------------------


def test_mean_matches_statistics_module():
    assert F.mean(D.ODD_LIST) == st.fmean(D.ODD_LIST)


def test_median_odd_length_matches_statistics_module():
    assert F.median(D.ODD_LIST) == st.median(D.ODD_LIST)


def test_median_even_length_averages_the_two_middle_values():
    assert F.median(D.EVEN_LIST) == st.median(D.EVEN_LIST) == 6.0


def test_mode_single_peak():
    assert F.modes(D.ODD_LIST) == [7]


def test_mode_multimodal_returns_every_tied_value():
    assert F.modes(D.MULTIMODAL_LIST) == sorted(st.multimode(D.MULTIMODAL_LIST)) == [3, 8]


def test_statistics_mode_singular_silently_drops_a_tied_value():
    single = st.mode(D.MULTIMODAL_LIST)
    assert single in F.modes(D.MULTIMODAL_LIST)
    assert len(F.modes(D.MULTIMODAL_LIST)) > 1


# ---------------------------------------------------------------------------
# Exercise 2: the breakdown point
# ---------------------------------------------------------------------------


def test_mean_breakdown_point_is_dragged_far():
    before, after = F.breakdown_point_mean(D.SALARY_LIST, D.CORRUPTED_SALARY)
    assert after - before > D.BREAKDOWN_MEAN_SHIFT_FLOOR


def test_median_breakdown_point_does_not_move_at_all():
    before, after = F.breakdown_point_median(D.SALARY_LIST, D.CORRUPTED_SALARY)
    assert after == before  # exact equality: the median's rank did not change


def test_mean_and_median_agree_on_the_uncorrupted_data():
    ordered = sorted(D.SALARY_LIST)
    assert F.mean(ordered) == pytest.approx(50777.78, abs=0.01)
    assert F.median(ordered) == 50000


# ---------------------------------------------------------------------------
# Exercise 3: Bessel's correction, measured
# ---------------------------------------------------------------------------


def test_bessel_divide_by_n_estimator_is_biased_low_by_n_minus_1_over_n():
    rng = np.random.default_rng(D.BESSEL_SEED)
    biased, _ = S.bessel_trial_variances(
        rng,
        D.BESSEL_POPULATION_MEAN,
        D.BESSEL_POPULATION_SIGMA,
        D.BESSEL_SAMPLE_SIZE,
        D.BESSEL_TRIALS,
    )
    ratio = float(biased.mean()) / D.BESSEL_TRUE_VARIANCE
    assert ratio == pytest.approx(D.BESSEL_EXPECTED_BIAS_FACTOR, abs=D.BESSEL_BIAS_FACTOR_TOLERANCE)


def test_bessel_divide_by_n_minus_1_estimator_is_unbiased_within_tolerance():
    rng = np.random.default_rng(D.BESSEL_SEED)
    _, unbiased = S.bessel_trial_variances(
        rng,
        D.BESSEL_POPULATION_MEAN,
        D.BESSEL_POPULATION_SIGMA,
        D.BESSEL_SAMPLE_SIZE,
        D.BESSEL_TRIALS,
    )
    mean_unbiased = float(unbiased.mean())
    se = float(unbiased.std(ddof=1)) / (D.BESSEL_TRIALS**0.5)
    assert abs(mean_unbiased - D.BESSEL_TRUE_VARIANCE) < D.BESSEL_UNBIASED_SE_TOLERANCE * se


def test_bessel_unbiased_estimator_is_closer_to_truth_than_biased_on_average():
    rng = np.random.default_rng(D.BESSEL_SEED)
    biased, unbiased = S.bessel_trial_variances(
        rng,
        D.BESSEL_POPULATION_MEAN,
        D.BESSEL_POPULATION_SIGMA,
        D.BESSEL_SAMPLE_SIZE,
        D.BESSEL_TRIALS,
    )
    assert abs(float(unbiased.mean()) - D.BESSEL_TRUE_VARIANCE) < abs(
        float(biased.mean()) - D.BESSEL_TRUE_VARIANCE
    )


# ---------------------------------------------------------------------------
# Exercise 4: percentile ambiguity
# ---------------------------------------------------------------------------


def test_percentile_conventions_disagree():
    values = {
        method: F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, method)
        for method in D.PERCENTILE_METHODS
    }
    assert len(set(values.values())) >= 2


def test_percentile_default_linear_method_matches_the_documented_value():
    assert F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, "linear") == 8.25


def test_percentile_lower_and_higher_land_on_different_real_data_points():
    lower = F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, "lower")
    higher = F.percentile_under(D.PERCENTILE_ARRAY, D.PERCENTILE_TARGET, "higher")
    assert lower != higher
    assert lower in D.PERCENTILE_ARRAY
    assert higher in D.PERCENTILE_ARRAY


# ---------------------------------------------------------------------------
# Exercise 5: Pearson versus Spearman
# ---------------------------------------------------------------------------


def test_pearson_on_a_symmetric_parabola_is_essentially_zero():
    r = F.pearson(D.PARABOLA_X, D.PARABOLA_Y)
    assert abs(r) < D.PARABOLA_PEARSON_TOLERANCE


def test_spearman_on_a_monotone_cubic_is_exactly_one():
    assert F.spearman(D.MONOTONE_X, D.MONOTONE_Y) == 1.0


def test_pearson_on_the_same_cubic_is_strong_but_not_perfect():
    r = F.pearson(D.MONOTONE_X, D.MONOTONE_Y)
    assert 0.0 < r < 1.0


# ---------------------------------------------------------------------------
# Exercise 6: Anscombe's quartet
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["I", "II", "III", "IV"])
def test_anscombe_summaries_agree_to_documented_precision(name):
    reference = F.anscombe_summary(*D.ANSCOMBE_SETS["I"])
    summary = F.anscombe_summary(*D.ANSCOMBE_SETS[name])
    dec = D.ANSCOMBE_AGREEMENT_DECIMALS
    assert round(summary["mean_x"], dec) == round(reference["mean_x"], dec)
    assert round(summary["mean_y"], dec) == round(reference["mean_y"], dec)
    assert round(summary["var_x"], dec) == round(reference["var_x"], dec)
    assert round(summary["var_y"], dec) == round(reference["var_y"], dec)
    assert round(summary["correlation"], 1) == round(reference["correlation"], 1)
    assert round(summary["slope"], 1) == round(reference["slope"], 1)


def test_anscombe_set_iv_has_dramatically_higher_leverage():
    shapes = {name: F.shape_statistics(x, y) for name, (x, y) in D.ANSCOMBE_SETS.items()}
    assert shapes["IV"]["max_leverage"] > 3.0 * shapes["I"]["max_leverage"]
    assert shapes["I"]["max_leverage"] == shapes["II"]["max_leverage"] == shapes["III"]["max_leverage"]


def test_anscombe_set_iii_has_a_dominant_outlier_residual():
    shapes = {name: F.shape_statistics(x, y) for name, (x, y) in D.ANSCOMBE_SETS.items()}
    assert shapes["III"]["outlier_ratio"] > 2.0 * shapes["I"]["outlier_ratio"]


def test_anscombe_set_ii_residuals_change_sign_less_often_than_set_i():
    shapes = {name: F.shape_statistics(x, y) for name, (x, y) in D.ANSCOMBE_SETS.items()}
    assert shapes["II"]["residual_sign_changes"] < shapes["I"]["residual_sign_changes"]


# ---------------------------------------------------------------------------
# Exercise 7: Simpson's paradox
# ---------------------------------------------------------------------------


def test_treatment_a_wins_every_subgroup():
    assert F.success_rate(*D.TREATMENT_A_EASY) > F.success_rate(*D.TREATMENT_B_EASY)
    assert F.success_rate(*D.TREATMENT_A_HARD) > F.success_rate(*D.TREATMENT_B_HARD)


def test_treatment_b_wins_overall():
    a_total = F.combined_rate(D.TREATMENT_A_EASY, D.TREATMENT_A_HARD)
    b_total = F.combined_rate(D.TREATMENT_B_EASY, D.TREATMENT_B_HARD)
    assert b_total > a_total


def test_overall_rate_is_the_pooled_total_not_the_average_of_subgroup_rates():
    a_total = F.combined_rate(D.TREATMENT_A_EASY, D.TREATMENT_A_HARD)
    naive_average = (
        F.success_rate(*D.TREATMENT_A_EASY) + F.success_rate(*D.TREATMENT_A_HARD)
    ) / 2
    # The pooled rate is dominated by the much larger hard subgroup, so it
    # sits far closer to the hard-subgroup rate than a naive 50/50 average
    # of the two subgroup rates would.
    assert abs(a_total - F.success_rate(*D.TREATMENT_A_HARD)) < abs(a_total - naive_average)


# ---------------------------------------------------------------------------
# Exercise 8: robust spread under contamination
# ---------------------------------------------------------------------------


def test_contamination_inflates_standard_deviation_a_lot():
    rng = np.random.default_rng(D.CONTAMINATION_SEED)
    clean, contaminated = S.contaminated_sample(
        rng,
        D.CONTAMINATION_BASE_MEAN,
        D.CONTAMINATION_BASE_SIGMA,
        D.CONTAMINATION_BASE_N,
        D.CONTAMINATION_OUTLIERS,
    )
    std_clean = float(np.std(clean, ddof=1))
    std_contam = float(np.std(contaminated, ddof=1))
    assert std_contam / std_clean > D.CONTAMINATION_STD_MULTIPLIER_FLOOR


def test_contamination_barely_moves_the_median_absolute_deviation():
    rng = np.random.default_rng(D.CONTAMINATION_SEED)
    clean, contaminated = S.contaminated_sample(
        rng,
        D.CONTAMINATION_BASE_MEAN,
        D.CONTAMINATION_BASE_SIGMA,
        D.CONTAMINATION_BASE_N,
        D.CONTAMINATION_OUTLIERS,
    )
    mad_clean = F.median_absolute_deviation(clean)
    mad_contam = F.median_absolute_deviation(contaminated)
    assert mad_contam / mad_clean < D.CONTAMINATION_MAD_MULTIPLIER_CEILING


# ---------------------------------------------------------------------------
# Exercise 9: standardisation
# ---------------------------------------------------------------------------


def test_standardized_sample_has_mean_zero_and_std_one():
    rng = np.random.default_rng(D.STANDARDIZATION_SEED)
    x = rng.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
    zx = F.zscores(x)
    mean_zx = sum(zx) / len(zx)
    std_zx = (sum((v - mean_zx) ** 2 for v in zx) / len(zx)) ** 0.5
    assert abs(mean_zx) < D.STANDARDIZATION_MEAN_TOLERANCE
    assert abs(std_zx - 1.0) < D.STANDARDIZATION_STD_TOLERANCE


def test_standardizing_does_not_change_pearson_correlation():
    rng = np.random.default_rng(D.STANDARDIZATION_SEED)
    x = rng.normal(D.STANDARDIZATION_X_MEAN, D.STANDARDIZATION_X_SIGMA, D.STANDARDIZATION_N)
    noise = rng.normal(0.0, D.STANDARDIZATION_Y_NOISE_SIGMA, D.STANDARDIZATION_N)
    y = D.STANDARDIZATION_Y_SLOPE * x + noise
    zx, zy = F.zscores(x), F.zscores(y)
    r_original = F.pearson(x, y)
    r_standardized = F.pearson(zx, zy)
    assert abs(r_original - r_standardized) < D.STANDARDIZATION_CORRELATION_TOLERANCE
