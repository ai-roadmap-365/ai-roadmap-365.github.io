"""The reference solutions: what changes once a second predictor joins the first.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np
import pytest

import regression_lib as r


@pytest.fixture(scope="module")
def diabetes():
    return r.load_raw_diabetes()


@pytest.fixture(scope="module")
def bmi_bp(diabetes):
    X, y, names = diabetes
    idx_bmi, idx_bp = names.index("bmi"), names.index("bp")
    return X[:, [idx_bmi, idx_bp]], y


# --- 1. Correlation and variance inflation --------------------------------


def test_01_variance_inflation_factors_flag_the_correlated_serum_measurements(diabetes):
    X, y, names = diabetes
    vifs = r.variance_inflation_factors(X, names)
    assert vifs == {
        "age": 1.2173,
        "sex": 1.2781,
        "bmi": 1.5094,
        "bp": 1.4594,
        "s1": 59.2025,
        "s2": 39.1934,
        "s3": 15.4022,
        "s4": 8.891,
        "s5": 10.076,
        "s6": 1.4846,
    }
    # Every clinical measurement (age, sex, bmi, bp) sits near 1: barely
    # explained by the other nine. Every serum measurement (s1-s5) sits
    # well above the common rule-of-thumb cutoff of 5.
    for name in ("age", "sex", "bmi", "bp"):
        assert vifs[name] < 2.0
    for name in ("s1", "s2", "s3", "s4", "s5"):
        assert vifs[name] > 5.0


def test_01b_s1_and_s2_are_the_most_correlated_predictor_pair(diabetes):
    X, y, names = diabetes
    assert round(r.correlation(X, names, "s1", "s2"), 4) == 0.8967
    assert round(r.correlation(X, names, "s3", "s4"), 4) == -0.7385
    # bmi and bp -- the two clinical measurements -- are nowhere near as
    # entangled with each other.
    assert abs(r.correlation(X, names, "bmi", "bp")) < 0.4


# --- 2. The centrepiece: an exact duplicate column -------------------------


def test_02_an_exact_duplicate_splits_the_coefficient_but_not_the_sum(diabetes):
    X, y, names = diabetes
    idx_s1 = names.index("s1")
    original, coef_a, coef_b, max_diff, r2_orig, r2_dup = r.duplicate_column_exact(X, y, idx_s1)
    assert round(original, 4) == -1.09
    assert round(coef_a, 4) == -0.545
    assert round(coef_b, 4) == -0.545
    # Neither half equals the original coefficient -- but their sum does,
    # to eight decimal places. The normal equations only ever "see" the
    # combined effect of two identical columns.
    assert abs((coef_a + coef_b) - original) < 1e-8


def test_02b_the_exact_duplicate_changes_nothing_about_the_model_itself(diabetes):
    X, y, names = diabetes
    idx_s1 = names.index("s1")
    _original, _a, _b, max_diff, r2_orig, r2_dup = r.duplicate_column_exact(X, y, idx_s1)
    # Every prediction the model makes is unchanged to eleven decimal places.
    assert max_diff < 1e-10
    assert abs(r2_dup - r2_orig) < 1e-10
    assert round(r2_orig, 4) == 0.5177


# --- 3. Breaking the tie with noise makes the split arbitrary --------------


def test_03_a_tiny_amount_of_noise_lets_the_two_coefficients_swing_wildly(diabetes):
    X, y, names = diabetes
    idx_s1 = names.index("s1")
    noise_scale = 0.01 * float(X[:, idx_s1].std())
    coef_a, coef_b, coef_sum, max_diff, r2 = r.duplicate_column_noisy(X, y, idx_s1, noise_scale, seed=0)
    assert round(coef_a, 4) == 0.7592
    assert round(coef_b, 4) == -1.8451
    # A one-percent noise perturbation was enough to send the original
    # -1.09 coefficient POSITIVE. The near-duplicate is no longer tied
    # exactly, so least squares picks a definite -- but essentially
    # arbitrary -- way to split the shared effect.
    assert coef_a > 0
    assert round(coef_sum, 4) == -1.0859
    assert round(r2, 4) == 0.5178


def test_03b_across_many_noise_draws_the_sum_and_the_predictions_hold_steady(diabetes):
    X, y, names = diabetes
    idx_s1 = names.index("s1")
    noise_scale = 0.01 * float(X[:, idx_s1].std())
    result = r.duplicate_noisy_spread(X, y, idx_s1, noise_scale, range(10))
    # The two individual coefficients range over more than twelve units --
    # further apart than the original coefficient is from zero, and they
    # cross zero repeatedly.
    assert result["coef_a"]["sd"] > 4.0
    assert result["coef_b"]["sd"] > 4.0
    assert result["coef_a"]["min"] < 0 < result["coef_a"]["max"]
    # Their sum barely moves: two orders of magnitude steadier than either
    # coefficient alone.
    assert result["sum"]["sd"] < 0.05
    assert round(result["sum"]["mean"], 2) == -1.09
    # And the predictions themselves move by a few units on a target whose
    # own spread is 77 -- noticeable, but nowhere near what the coefficient
    # swings would suggest.
    assert result["max_pred_diff_overall"] < 10.0
    assert result["r2"]["sd"] < 0.001


# --- 4. Instability tracks the VIF, not just the anecdote ------------------


def test_04_bootstrap_resampling_shows_high_vif_predictors_wobble_more(diabetes):
    X, y, names = diabetes
    boot = r.bootstrap_coefficient_spread(X, y, names, reps=500, seed=0)
    high_vif = ["s1", "s2", "s3", "s4"]
    low_vif = ["bmi", "bp", "sex"]
    high_cv = np.mean([boot[name]["cv"] for name in high_vif])
    low_cv = np.mean([boot[name]["cv"] for name in low_vif])
    # age's own coefficient of variation is enormous (4.70) because its
    # mean sits near zero, which inflates the ratio rather than reflecting
    # genuine instability -- excluded from this comparison for that reason.
    assert high_cv > low_cv
    assert boot["s1"]["cv"] > boot["bmi"]["cv"]
    assert boot["s3"]["cv"] > boot["bp"]["cv"]
    assert round(boot["s1"]["cv"], 2) == 0.51
    assert round(boot["bmi"]["cv"], 2) == 0.13


# --- 5. Holding the others constant can flip a sign -------------------------


def test_05_conditioning_on_the_other_nine_predictors_flips_four_signs(diabetes):
    X, y, names = diabetes
    result = r.simple_vs_multiple_coefficients(X, y, names)
    flips = {name for name, values in result.items() if values["sign_flip"]}
    assert flips == {"age", "sex", "s1", "s3"}
    # s1 is the headline: positive alone, negative once s2 is in the model.
    assert result["s1"]["simple"] == 0.4723
    assert result["s1"]["multiple"] == -1.09
    # bmi and s5 do not flip -- their relationship with the target survives
    # conditioning on the other nine predictors.
    assert result["bmi"]["sign_flip"] is False
    assert result["s5"]["sign_flip"] is False


# --- 6. A polynomial fit is linear in its parameters ------------------------


def test_06_polynomialfeatures_plus_linear_regression_matches_the_normal_equations(bmi_bp):
    X2, y = bmi_bp
    names, sk_coefs, sk_intercept, ne_coefs, ne_intercept, coef_diff, intercept_diff = (
        r.polynomial_matches_normal_equations(X2, y, degree=2, feature_names=["bmi", "bp"])
    )
    assert names == ["bmi", "bp", "bmi^2", "bmi bp", "bp^2"]
    assert sk_coefs == ne_coefs
    assert sk_intercept == ne_intercept
    # Two different solution methods for the identical linear system agree
    # to well beyond floating-point noise.
    assert coef_diff < 1e-9
    assert intercept_diff < 1e-9


def test_06b_dropping_the_interaction_term_costs_real_r_squared(bmi_bp):
    X2, y = bmi_bp
    r2_with, r2_without, interaction_coef = r.interaction_term_effect(X2, y)
    assert round(r2_with, 6) == 0.40417
    assert round(r2_without, 6) == 0.399896
    assert round(interaction_coef, 6) == 0.095079
    # bmi^2 and bp^2 describe each predictor curving on its own; only the
    # interaction term describes bmi's effect changing with bp's level --
    # dropping it is a real, measurable loss of fit, not a bookkeeping one.
    assert r2_with > r2_without


# --- 7. R-squared never decreases, even for pure noise ----------------------


def test_07_r_squared_never_decreases_when_you_add_a_predictor_even_noise(diabetes):
    X, y, names = diabetes
    rows = r.r2_with_added_noise_columns(X, y, [1, 2, 5, 10], seed=42)
    assert rows == [
        (1, 0.518064, 0.000316),
        (2, 0.523041, 0.005293),
        (5, 0.527615, 0.009867),
        (10, 0.532455, 0.014707),
    ]
    r2_values = [row[1] for row in rows]
    assert all(a < b for a, b in zip(r2_values, r2_values[1:]))
    # Ten columns of pure numpy noise, with no relationship to the target
    # whatsoever, bought 1.47 points of R2 for free.
    assert rows[-1][2] > 0.01


# --- 8. Scaling changes the coefficients, not the model ---------------------


def test_08_standardizing_changes_the_coefficients_not_the_predictions(diabetes):
    X, y, names = diabetes
    raw_coefs, scaled_coefs, r2_raw, r2_scaled, max_pred_diff = r.scaling_effect(X, y)
    # The two coefficient vectors are nowhere near each other in scale --
    # s1's raw coefficient is -1.09; its scaled coefficient is -37.68.
    idx_s1 = names.index("s1")
    assert raw_coefs[idx_s1] == -1.09
    assert scaled_coefs[idx_s1] == -37.68
    assert max(abs(c) for c in raw_coefs) < 70
    assert max(abs(c) for c in scaled_coefs) < 40
    # But the fit itself -- what it predicts, and how well -- is identical.
    assert r2_raw == r2_scaled
    assert max_pred_diff < 1e-9
