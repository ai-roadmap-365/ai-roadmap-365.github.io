"""Fourteen exercises in what a penalty actually does.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
exactly what to build and what to assert; replace the skip with real code.
`regularization_lib.py` is complete -- it is the machinery, not the
exercise.

Run this suite on its own:

    .venv/bin/pytest starter -q

Never run `pytest starter examples` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np  # noqa: F401  (you will need it)
import pytest

import regularization_lib as r  # noqa: F401  (you will need it)

ALPHA_GRID = [0.001, 0.01, 0.1, 1.0]
PATH_ALPHAS = np.logspace(-3, 2, 60)


def test_01_ridge_never_zeros_lasso_progressively_zeros():
    pytest.skip(
        "Call r.zero_counts_and_r2(ALPHA_GRID) and assert it equals the four "
        "rows in expected-output/measured-values.txt, from "
        "(0.001, 0, 0.3588, 0, 0.3586) to (1.0, 8, 0.2782, 0, 0.357). Then "
        "assert the ridge-zeros column is [0, 0, 0, 0] and the lasso-zeros "
        "column never decreases as alpha grows. Ridge shrinks; lasso "
        "shrinks and selects."
    )


def test_01b_lasso_cv_picks_alpha_and_six_features():
    pytest.skip(
        "Call r.lasso_cv_selection() and assert alpha rounds to 0.07874, "
        "zeros == 4, kept == ['sex', 'bmi', 'bp', 's1', 's3', 's5'], and "
        "r2 == 0.3562. Cross-validation, not eyeballing a curve, is how "
        "alpha actually gets chosen in practice."
    )


def test_02_the_coefficient_path_lasso_hits_exact_zeros_ridge_never_does():
    pytest.skip(
        "Call r.alpha_where_each_lasso_coefficient_first_hits_zero(PATH_ALPHAS), "
        "which returns (zero_at, ridge_ever_zero). Assert every one of the "
        "ten lasso coefficients has a non-None zero_at value, and assert "
        "ridge_ever_zero is False across the same 60-point sweep. A circle "
        "has no corners; a diamond has one on every axis."
    )


def test_02b_the_weakest_coefficients_zero_out_first():
    pytest.skip(
        "From the same zero_at dict, assert the feature with the smallest "
        "zero_at value is 's3' (it rounds to alpha=0.0032) and the feature "
        "with the largest is 'bmi' (alpha=2.4538). The coefficients lasso "
        "can least afford to shrink are the ones it keeps longest."
    )


def test_03_lasso_recovers_the_right_features_at_low_noise():
    pytest.skip(
        "Call r.sparse_recovery(alpha=1.0, noise=1.0, seed=0) against a "
        "known sparse ground truth (5 informative of 20 features) and "
        "assert precision == 1.0, recall == 1.0, n_selected == 5. Repeat at "
        "alpha=0.1, noise=0.1 and assert the same three values. At low "
        "noise, lasso finds exactly the right features -- not merely some "
        "features that predict well."
    )


def test_03b_recovery_degrades_with_noise_and_too_much_penalty():
    pytest.skip(
        "Call r.sparse_recovery(alpha=80.0, noise=30.0, seed=0) and assert "
        "recall == 0.2, n_selected == 1. Call it again at noise=10.0 and "
        "assert recall == 0.0, n_selected == 0 -- too much penalty on noisy "
        "data can zero out the truth entirely. Then call "
        "r.sparse_recovery_across_seeds at (alpha=1.0, noise=1.0) and at "
        "(alpha=1.0, noise=10.0), and assert the second call's mean "
        "precision (0.6792) is lower than the first's (1.0). This is not "
        "one unlucky seed."
    )


def test_04_regularization_requires_scaled_features():
    pytest.skip(
        "Call r.scale_dependence(alpha=1.0). Assert the 'raw' result keeps "
        "all 10 features, 'standardized' keeps 7 "
        "(['sex','bmi','bp','s1','s3','s5','s6']), and 'sklearn_unit_norm' "
        "keeps 3 (['bmi','bp','s5']) -- three different answers, same data, "
        "same alpha. The penalty is applied in whatever units the "
        "coefficients happen to be in, and 'scaled' is not even one "
        "convention: unit-variance and unit-norm disagree too."
    )


def test_05_elasticnet_interpolates_between_ridge_and_lasso():
    pytest.skip(
        "Call r.elasticnet_sweep(alpha=0.1, l1_ratios=[0.0, 0.1, 0.3, 0.5, "
        "0.7, 0.9, 1.0]) and assert it equals the captured rows, ending "
        "(1.0, 3, 0.355). Then assert that row's zero count matches plain "
        "Lasso's own zero count at the same alpha "
        "(r.zero_counts_and_r2([0.1])[0]). l1_ratio=1.0 is not an "
        "approximation to lasso; it is lasso."
    )


def test_05b_ridge_and_elasticnet_do_not_share_an_alpha_scale():
    pytest.skip(
        "Call r.ridge_elasticnet_equivalence(alpha=0.1), which fits "
        "Ridge at alpha * n_train against ElasticNet(alpha=0.1, "
        "l1_ratio=0.0) directly. Assert max_diff < 0.001. Ridge's objective "
        "sums the squared error; ElasticNet's averages it over n_samples -- "
        "so the same alpha means two different penalty strengths until you "
        "correct for it."
    )


def test_06_ridge_splits_the_weight_between_near_duplicates():
    pytest.skip(
        "Get correlation from r.near_duplicate_dataset() and assert it "
        "exceeds 0.999. Call r.ridge_vs_lasso_on_duplicates([1.0]) and, "
        "from the one row, assert the two ridge coefficients differ by "
        "less than 0.15 and sum to within 0.2 of 6.0 -- ridge splits the "
        "true combined weight roughly evenly. Assert lasso's second "
        "coefficient is exactly 0.0 and its first exceeds 5.0 -- lasso "
        "picks one and drops the other."
    )


def test_06b_enough_penalty_zeros_both_duplicates_in_lasso_but_ridge_still_splits():
    pytest.skip(
        "Call r.ridge_vs_lasso_on_duplicates([10.0]). Assert both lasso "
        "coefficients are exactly 0.0. Assert both ridge coefficients "
        "still exceed 2.5 and still differ from each other by less than "
        "0.15. Ridge never produces the corner; more penalty just shrinks "
        "both halves together."
    )


def test_07_ridge_has_a_closed_form_lasso_needs_iterations():
    pytest.skip(
        "Call r.ridge_has_no_iteration_count() and assert "
        "ridge_has_n_iter is False and lasso_has_n_iter is True. Call "
        "r.lasso_iteration_counts(ALPHA_GRID) and assert it equals "
        "{0.001: 368, 0.01: 62, 0.1: 135, 1.0: 6}. Ridge is one "
        "linear-algebra call; lasso is solved iteratively because its "
        "penalty is not differentiable at zero."
    )


def test_08_the_corner_two_correlated_features_and_a_lasso_zero():
    pytest.skip(
        "Call r.two_feature_corner_demo([0.001, 0.5, 1.0, 3.0, 8.0]). At "
        "alpha=3.0, assert lasso's coefficients equal [0.8919, 0.0] exactly "
        "-- it has landed on the axis -- while ridge's second coefficient "
        "still exceeds 1.5 in magnitude. This is the geometry: a diamond's "
        "corner sits on an axis; a circle's does not."
    )


def test_08b_at_a_tiny_alpha_both_models_agree_with_ols():
    pytest.skip(
        "From the same two_feature_corner_demo call (use alphas [0.001, "
        "8.0]), assert both ridge's and lasso's coefficients at alpha=0.001 "
        "are within 0.01 of the OLS coefficients [1.9564, 1.9381]. Then "
        "assert that at alpha=8.0, lasso's coefficients are both exactly "
        "0.0 while ridge's are both still nonzero. As alpha shrinks toward "
        "zero, both penalties vanish and agree with plain least squares."
    )
