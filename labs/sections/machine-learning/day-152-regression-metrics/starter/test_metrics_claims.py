"""Twelve exercises in what a regression metric reports, and what it hides.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`regression_metrics_lib.py` is complete -- it is the machinery, not the
exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import regression_metrics_lib as m  # noqa: F401  (you will need it)


# --- 1. Train R2 is not a quality measure ---------------------------------


def test_01_train_r2_climbs_on_pure_noise_columns():
    pytest.skip(
        "Call m.noise_column_r2_curve() and assert it equals the five rows in "
        "expected-output/measured-values.txt, from (0, 331, 10, 0.5554, 0.5415) "
        "to (100, 331, 110, 0.7403, 0.6104). Then assert the train_r2 column "
        "(index 3 of each row) is strictly increasing, and that it climbs by "
        "more than 0.18 from no noise to 100 noise columns. Every added column "
        "is independent random noise with zero relationship to the target."
    )


def test_01b_adjusted_r2_corrects_the_climb_then_breaks_down_itself():
    pytest.skip(
        "Build a dict keyed by noise count from m.noise_column_r2_curve(). "
        "Assert the adjusted R2 at 20 noise columns is LOWER than the 0-noise "
        "baseline (0.5329 < 0.5415) -- the correction working as intended. "
        "Then assert the adjusted R2 at 100 noise columns is HIGHER than both "
        "the baseline and the 20-noise value (0.6104 > 0.5415 and "
        "0.6104 > 0.5329) -- the correction breaking down once the number of "
        "predictors (110) becomes a large fraction of the sample size (331)."
    )


# --- 2. R2 is not bounded below by zero ------------------------------------


def test_02_the_full_model_beats_a_constant_mean_predictor_on_test():
    pytest.skip(
        "Assert m.full_model_test_r2() equals 0.3594 and that "
        "abs(m.constant_mean_test_r2()) is less than 0.001. A predictor that "
        "always guesses the training mean scores R2 essentially exactly zero "
        "on fresh test data BY CONSTRUCTION -- R2 is defined relative to "
        "exactly that predictor, which is why zero is the number it compares "
        "against, not an accident of this dataset."
    )


def test_02b_r2_has_no_lower_bound():
    pytest.skip(
        "Assert m.bad_predictor_test_r2() equals -4.7009 and is less than "
        "-4.0. A deliberately bad predictor -- always zero -- scores nearly "
        "five FULL UNITS below zero, which is impossible if R2 lived in "
        "[0, 1] the way most people assume it does."
    )


# --- 3. RMSE versus MAE under one outlier ----------------------------------


def test_03_rmse_moves_more_than_mae_when_one_target_is_an_outlier():
    pytest.skip(
        "Call m.rmse_mae_outlier_shift() and assert the four values equal "
        "(2.4801, 1.9833, 28.2569, 5.9448). Compute rmse_ratio = "
        "rmse_after / rmse_before and mae_ratio = mae_after / mae_before. "
        "Assert rmse_ratio > 11.0, mae_ratio < 3.5, and rmse_ratio > "
        "3 * mae_ratio. Same predictions both times; only one target row "
        "moved far away."
    )


# --- 4. MAPE breaking -------------------------------------------------------


def test_04_mape_explodes_silently_at_a_zero_true_value():
    pytest.skip(
        "Call m.mape_at_zero_target() and assert the result is greater than "
        "1.0e10. Note what does NOT happen: no exception, no warning -- "
        "scikit-learn floors the zero denominator at machine epsilon and "
        "returns a number that is off by roughly fourteen orders of "
        "magnitude from anything a percentage error should look like."
    )


def test_04b_mape_explodes_near_zero_while_mae_stays_sane():
    pytest.skip(
        "Call m.mape_near_zero_target() and assert it equals (3.3667, 5.0). "
        "The first value is MAPE, the second is MAE, on the SAME three "
        "predictions. MAE reports a believable 5.0 units of error; MAPE "
        "reports 336.67 percent, because one true value is 0.5 and a "
        "five-unit miss on 0.5 is a factor of ten."
    )


def test_05_mape_is_bounded_under_but_not_over():
    pytest.skip(
        "Call m.mape_asymmetry_bound() and assert it equals (1.0, 10.0). "
        "The first value is the MAPE of the worst possible systematic "
        "under-prediction -- always guessing zero -- which cannot exceed "
        "100 percent. The second is the MAPE of predicting eleven times the "
        "truth, which is 1000 percent, with no ceiling of its own. Assert "
        "ten_x_over > max_under. Being wrong in one direction is capped; "
        "being wrong in the other is not."
    )


# --- 6. A metric ranking inversion ------------------------------------------


def test_06_rmse_and_mae_prefer_different_models():
    pytest.skip(
        "Call m.ranking_inversion_models() and assert the four values equal "
        "(1.947, 1.586, 4.4353, 0.8417) for (rmse_a, mae_a, rmse_b, mae_b). "
        "Then assert rmse_a < rmse_b (RMSE prefers Model A) and mae_b < "
        "mae_a (MAE prefers Model B). Model A makes many small consistent "
        "errors; Model B is nearly perfect except for a handful of large "
        "misses. Reporting only one metric would silently pick a winner the "
        "other metric disagrees with."
    )


# --- 7. RMSE and MAE carry the target's units -------------------------------


def test_07_rmse_and_mae_are_identical_on_raw_and_standardised_features():
    pytest.skip(
        "Call m.raw_and_scaled_metrics() and assert results['scaled'] == "
        "(56.3929, 45.1206, 0.3594) and results['raw'] == the same tuple. "
        "Ordinary least squares is invariant to a per-column affine "
        "rescaling of its inputs, so every metric computed from its "
        "predictions is identical whether the features are standardised or "
        "left in raw units (age in years, bmi, raw blood pressure). Then "
        "state in a comment what unit the RMSE and MAE numbers are actually "
        "in for this dataset."
    )


# --- 8. r2_score: agreement, and the argument-order bug ---------------------


def test_08_r2_score_agrees_with_linearregression_score():
    pytest.skip(
        "Call m.r2_score_vs_model_score() and assert both returned values "
        "equal 0.359409. sklearn.metrics.r2_score(y_true, y_pred) and "
        "LinearRegression.score(X, y) compute the same quantity."
    )


def test_08b_r2_score_argument_order_changes_the_answer():
    pytest.skip(
        "Call m.r2_score_argument_order() and assert it equals "
        "(0.359409, -0.209635). r2_score is NOT symmetric in its two "
        "arguments -- the denominator is the variance of whichever array is "
        "passed FIRST. Assert the swapped value is negative while the "
        "correct-order value is positive: the same predictions, scored with "
        "the arguments the wrong way round, look worse than a constant-mean "
        "baseline."
    )
