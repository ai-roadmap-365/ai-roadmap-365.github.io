"""The reference solutions: what each regression metric reports, and hides.

Every number here was captured from a real run of this file on the
authoring machine. If a number changes, the claim in the lesson is wrong
and one of the two must be fixed.
"""

import numpy as np

import regression_metrics_lib as m


# --- 1. Train R2 is not a quality measure ---------------------------------


def test_01_train_r2_climbs_on_pure_noise_columns():
    rows = m.noise_column_r2_curve()
    assert rows == [
        (0, 331, 10, 0.5554, 0.5415),
        (1, 331, 11, 0.5555, 0.5402),
        (5, 331, 15, 0.5648, 0.5441),
        (20, 331, 30, 0.5754, 0.5329),
        (100, 331, 110, 0.7403, 0.6104),
    ]
    train_r2 = [row[3] for row in rows]
    # Every added column is pure noise, independent of the target, and
    # yet the training R2 climbs anyway -- by more as more columns are
    # added, because more predictors can only help a training-set fit.
    assert all(a < b for a, b in zip(train_r2, train_r2[1:]))
    assert train_r2[-1] - train_r2[0] > 0.18


def test_01b_adjusted_r2_corrects_the_climb_then_breaks_down_itself():
    rows = m.noise_column_r2_curve()
    by_noise = {row[0]: row for row in rows}
    baseline_adj = by_noise[0][4]
    # At a modest number of noise columns, adjusted R2 does its job: it
    # falls below the no-noise baseline, correctly reporting that these
    # columns did not earn their place.
    assert by_noise[20][4] < baseline_adj
    # But at p=110 predictors on n=331 rows -- a third of the sample size
    # spent on predictors -- the penalty term itself becomes unstable, and
    # adjusted R2 climbs back ABOVE the baseline even though every one of
    # those 100 extra columns is still pure noise. The correction is not
    # a cure; it has its own failure mode.
    assert by_noise[100][4] > baseline_adj
    assert by_noise[100][4] > by_noise[20][4]


# --- 2. R2 is not bounded below by zero ------------------------------------


def test_02_the_full_model_beats_a_constant_mean_predictor_on_test():
    full = m.full_model_test_r2()
    constant = m.constant_mean_test_r2()
    assert full == 0.3594
    # A constant-mean predictor scores R2 essentially exactly zero on a
    # fresh test set, by construction: R2 is defined relative to that
    # exact predictor, so this is the thing R2 compares against, not an
    # incidental fact about this dataset.
    assert abs(constant) < 0.001
    assert full > constant


def test_02b_r2_has_no_lower_bound():
    bad = m.bad_predictor_test_r2()
    # A deliberately bad predictor -- zero, always -- is not merely worse
    # than the constant-mean baseline; it is worse by nearly five full
    # units of R2, which is impossible if R2 lived in [0, 1] the way most
    # readers assume.
    assert bad == -4.7009
    assert bad < -4.0


# --- 3. RMSE versus MAE under one outlier ----------------------------------


def test_03_rmse_moves_more_than_mae_when_one_target_is_an_outlier():
    rmse_before, mae_before, rmse_after, mae_after = m.rmse_mae_outlier_shift()
    assert (rmse_before, mae_before, rmse_after, mae_after) == (2.4801, 1.9833, 28.2569, 5.9448)
    rmse_ratio = rmse_after / rmse_before
    mae_ratio = mae_after / mae_before
    # Squaring the error in RMSE means one very wrong prediction dominates
    # the sum; MAE, which never squares anything, moves by far less.
    assert rmse_ratio > 11.0
    assert mae_ratio < 3.5
    assert rmse_ratio > 3 * mae_ratio


# --- 4. MAPE breaking -------------------------------------------------------


def test_04_mape_explodes_silently_at_a_zero_true_value():
    value = m.mape_at_zero_target()
    # scikit-learn does not raise or warn on a zero true value: it floors
    # the denominator at machine epsilon and returns a number. The result
    # is not a small mistake -- it is off by roughly fourteen orders of
    # magnitude from anything a percentage error should look like.
    assert value > 1.0e10


def test_04b_mape_explodes_near_zero_while_mae_stays_sane():
    mape_value, mae_value = m.mape_near_zero_target()
    assert (mape_value, mae_value) == (3.3667, 5.0)
    # The same three rows: MAE reports a modest, believable 5.0 units of
    # error. MAPE reports 336.67 percent -- a number nobody would present
    # to a stakeholder -- because one of the three true values is 0.5 and
    # a five-unit miss on 0.5 is a factor of ten.
    assert mape_value > 3.0
    assert mae_value < 10.0


def test_05_mape_is_bounded_under_but_not_over():
    max_under, ten_x_over = m.mape_asymmetry_bound()
    assert (max_under, ten_x_over) == (1.0, 10.0)
    # The worst possible systematic under-prediction -- always guessing
    # zero -- cannot exceed 100 percent MAPE, because the error can never
    # exceed the true value once the prediction floor of zero is hit.
    # Over-prediction has no such ceiling: predicting eleven times the
    # truth reports 1000 percent, and there is no larger multiple that
    # would not report a correspondingly larger number. The two directions
    # of being wrong are not scored on the same scale.
    assert max_under == 1.0
    assert ten_x_over > max_under


# --- 6. A metric ranking inversion ------------------------------------------


def test_06_rmse_and_mae_prefer_different_models():
    rmse_a, mae_a, rmse_b, mae_b = m.ranking_inversion_models()
    assert (rmse_a, mae_a, rmse_b, mae_b) == (1.947, 1.586, 4.4353, 0.8417)
    # Model A makes many small, consistent errors. Model B is right almost
    # everywhere and badly wrong on a handful of rows. RMSE, which squares
    # every error, is dominated by Model B's few large misses and prefers
    # A. MAE, which weighs every error equally, is dominated by the
    # ninety-five rows Model B gets almost exactly right and prefers B.
    assert rmse_a < rmse_b
    assert mae_b < mae_a


# --- 7. RMSE and MAE carry the target's units -------------------------------


def test_07_rmse_and_mae_are_identical_on_raw_and_standardised_features():
    results = m.raw_and_scaled_metrics()
    assert results["scaled"] == (56.3929, 45.1206, 0.3594)
    assert results["raw"] == (56.3929, 45.1206, 0.3594)
    # Ordinary least squares is invariant to a per-column affine rescaling
    # of its inputs, so the predictions -- and every metric computed from
    # them -- are identical whether the features are standardised or left
    # in their original units (age in years, bmi, raw blood pressure).
    assert results["scaled"] == results["raw"]
    # RMSE and MAE are stated in the target's own units. The diabetes
    # target has no physical unit -- it is a composite disease-progression
    # score running 25 to 346 -- so a mean absolute error of 45.12 means
    # "45.12 points on that 25-346 scale", not "45.12 of anything you
    # could hand a doctor". A metric you cannot state a unit for is a
    # metric you cannot explain.


# --- 8. r2_score: agreement, and the argument-order bug ---------------------


def test_08_r2_score_agrees_with_linearregression_score():
    from_metric, from_model = m.r2_score_vs_model_score()
    assert from_metric == from_model == 0.359409


def test_08b_r2_score_argument_order_changes_the_answer():
    correct_order, swapped_order = m.r2_score_argument_order()
    assert correct_order == 0.359409
    # Swapping the two arguments is not a harmless typo: r2_score is not
    # symmetric in y_true and y_pred, because the denominator is the
    # variance of whichever array is passed FIRST. Swapped, the same
    # predictions score negative -- a model that looked genuinely useful
    # now looks worse than a constant-mean baseline, from one call written
    # the wrong way round.
    assert swapped_order == -0.209635
    assert swapped_order != correct_order
    assert swapped_order < 0 < correct_order
