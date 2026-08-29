"""Twelve exercises in what changes once a second predictor joins the first.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`regression_lib.py` is complete -- it is the machinery, not the exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import regression_lib as r  # noqa: F401  (you will need it)


@pytest.fixture(scope="module")
def diabetes():
    return r.load_raw_diabetes()


@pytest.fixture(scope="module")
def bmi_bp(diabetes):
    X, y, names = diabetes
    idx_bmi, idx_bp = names.index("bmi"), names.index("bp")
    return X[:, [idx_bmi, idx_bp]], y


def test_01_variance_inflation_factors_flag_the_correlated_serum_measurements(diabetes):
    pytest.skip(
        "Assert r.variance_inflation_factors(X, names) equals the ten-entry "
        "dict in expected-output/measured-values.txt: age 1.2173, sex "
        "1.2781, bmi 1.5094, bp 1.4594, s1 59.2025, s2 39.1934, s3 15.4022, "
        "s4 8.891, s5 10.076, s6 1.4846. Then assert every one of age, sex, "
        "bmi, bp is under 2.0, and every one of s1-s5 is over 5.0 -- the "
        "usual VIF rule-of-thumb cutoff."
    )


def test_01b_s1_and_s2_are_the_most_correlated_predictor_pair(diabetes):
    pytest.skip(
        "Assert r.correlation(X, names, 's1', 's2') rounds to 0.8967 and "
        "r.correlation(X, names, 's3', 's4') rounds to -0.7385. Then assert "
        "abs(r.correlation(X, names, 'bmi', 'bp')) is under 0.4 -- the two "
        "clinical measurements are nowhere near as entangled as the serum "
        "measurements are with each other."
    )


def test_02_an_exact_duplicate_splits_the_coefficient_but_not_the_sum(diabetes):
    pytest.skip(
        "Call r.duplicate_column_exact(X, y, names.index('s1')). Assert the "
        "original coefficient rounds to -1.09 and the two duplicate "
        "coefficients each round to -0.545. Then assert their SUM equals "
        "the original coefficient to within 1e-8 -- neither half matches "
        "the original alone, but the combined effect is conserved exactly."
    )


def test_02b_the_exact_duplicate_changes_nothing_about_the_model_itself(diabetes):
    pytest.skip(
        "From the same call, assert the maximum absolute difference in "
        "predictions is under 1e-10 and the R2 values agree to within "
        "1e-10, with R2 rounding to 0.5177. Adding a column that carries no "
        "new information changes the model's arithmetic without changing "
        "what it predicts."
    )


def test_03_a_tiny_amount_of_noise_lets_the_two_coefficients_swing_wildly(diabetes):
    pytest.skip(
        "With noise_scale = 0.01 * X[:, s1_index].std(), call "
        "r.duplicate_column_noisy(X, y, s1_index, noise_scale, seed=0). "
        "Assert the first coefficient rounds to 0.7592 (POSITIVE -- the "
        "original was -1.09) and the second to -1.8451. Assert their sum "
        "rounds to -1.0859 and R2 rounds to 0.5178. Breaking the exact tie "
        "with a one-percent perturbation was enough to send the sign the "
        "wrong way."
    )


def test_03b_across_many_noise_draws_the_sum_and_the_predictions_hold_steady(diabetes):
    pytest.skip(
        "Call r.duplicate_noisy_spread(X, y, s1_index, noise_scale, "
        "range(10)). Assert both individual coefficients have a standard "
        "deviation over 4.0 and cross zero (min negative, max positive). "
        "Then assert the SUM's standard deviation is under 0.05 and its "
        "mean rounds to -1.09 at 2 decimals. Assert max_pred_diff_overall "
        "is under 10.0 and the R2 standard deviation is under 0.001. Wild "
        "coefficients, stable predictions -- that contrast is the lesson."
    )


def test_04_bootstrap_resampling_shows_high_vif_predictors_wobble_more(diabetes):
    pytest.skip(
        "Call r.bootstrap_coefficient_spread(X, y, names, reps=500, "
        "seed=0). Average the 'cv' (coefficient of variation) for "
        "['s1','s2','s3','s4'] and separately for ['bmi','bp','sex'], and "
        "assert the high-VIF average exceeds the low-VIF average. Then "
        "assert boot['s1']['cv'] rounds to 0.51 and boot['bmi']['cv'] "
        "rounds to 0.13 -- a predictor's VIF predicts how much its own "
        "coefficient wobbles under resampling."
    )


def test_05_conditioning_on_the_other_nine_predictors_flips_four_signs(diabetes):
    pytest.skip(
        "Call r.simple_vs_multiple_coefficients(X, y, names). Collect the "
        "names whose 'sign_flip' is True and assert the set equals "
        "{'age', 'sex', 's1', 's3'}. Then assert result['s1']['simple'] == "
        "0.4723 and result['s1']['multiple'] == -1.09 -- positive alone, "
        "negative once s2 (its correlated partner) is held constant."
    )


def test_06_polynomialfeatures_plus_linear_regression_matches_the_normal_equations(bmi_bp):
    pytest.skip(
        "Call r.polynomial_matches_normal_equations(X2, y, degree=2, "
        "feature_names=['bmi', 'bp']). Assert the feature names are "
        "['bmi', 'bp', 'bmi^2', 'bmi bp', 'bp^2'], the sklearn coefficients "
        "equal the normal-equations coefficients exactly (they were both "
        "rounded to 6 places), and both difference values are under 1e-9. "
        "A polynomial fit is linear in ITS parameters, and this is the "
        "proof: two different solvers on the identical design matrix agree."
    )


def test_06b_dropping_the_interaction_term_costs_real_r_squared(bmi_bp):
    pytest.skip(
        "Call r.interaction_term_effect(X2, y). Assert r2_with rounds to "
        "0.40417 and r2_without rounds to 0.399896, with r2_with strictly "
        "greater. Assert the interaction coefficient rounds to 0.095079. "
        "bmi^2 and bp^2 describe each predictor curving on its own; only "
        "'bmi bp' describes bmi's effect changing with bp's level."
    )


def test_07_r_squared_never_decreases_when_you_add_a_predictor_even_noise(diabetes):
    pytest.skip(
        "Call r.r2_with_added_noise_columns(X, y, [1, 2, 5, 10], seed=42) "
        "and assert it equals the four rows in "
        "expected-output/measured-values.txt, from (1, 0.518064, 0.000316) "
        "to (10, 0.532455, 0.014707). Assert the R2 column is strictly "
        "increasing. Every added column is pure numpy noise with no "
        "relationship to the target at all."
    )


def test_08_standardizing_changes_the_coefficients_not_the_predictions(diabetes):
    pytest.skip(
        "Call r.scaling_effect(X, y). Assert raw_coefs[s1_index] == -1.09 "
        "and scaled_coefs[s1_index] == -37.68 -- more than 30 times larger "
        "in magnitude. Then assert r2_raw == r2_scaled exactly and "
        "max_pred_diff is under 1e-9. Standardising changes what one unit "
        "of a predictor means, and therefore every coefficient's size -- "
        "and changes nothing about what the model predicts."
    )
