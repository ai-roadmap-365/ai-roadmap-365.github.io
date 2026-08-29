"""Fourteen exercises in what a penalty actually does, measured.

Read `00_brief.md` first. Each function below is solved here and is a
`pytest.skip` in `starter/` naming exactly what to build and what to
assert. `regularization_lib.py` is complete -- it is the machinery, not the
exercise.

Run this suite on its own:

    .venv/bin/pytest examples -q

Never run `pytest examples starter` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np

import regularization_lib as r

ALPHA_GRID = [0.001, 0.01, 0.1, 1.0]
PATH_ALPHAS = np.logspace(-3, 2, 60)


def test_01_ridge_never_zeros_lasso_progressively_zeros():
    rows = r.zero_counts_and_r2(ALPHA_GRID)
    assert rows == [
        (0.001, 0, 0.3588, 0, 0.3586),
        (0.01, 1, 0.3541, 0, 0.3567),
        (0.1, 3, 0.355, 0, 0.369),
        (1.0, 8, 0.2782, 0, 0.357),
    ]
    ridge_zeros = [row[3] for row in rows]
    lasso_zeros = [row[1] for row in rows]
    assert ridge_zeros == [0, 0, 0, 0]
    # lasso's zero count never goes down as the penalty grows
    assert all(a <= b for a, b in zip(lasso_zeros, lasso_zeros[1:]))
    assert lasso_zeros[-1] > lasso_zeros[0]


def test_01b_lasso_cv_picks_alpha_and_six_features():
    result = r.lasso_cv_selection()
    assert round(result["alpha"], 5) == 0.07874
    assert result["zeros"] == 4
    assert result["kept"] == ["sex", "bmi", "bp", "s1", "s3", "s5"]
    assert result["r2"] == 0.3562


def test_02_the_coefficient_path_lasso_hits_exact_zeros_ridge_never_does():
    zero_at, ridge_ever_zero = r.alpha_where_each_lasso_coefficient_first_hits_zero(PATH_ALPHAS)
    # every lasso coefficient hits exactly zero somewhere in this sweep
    assert all(value is not None for value in zero_at.values())
    assert ridge_ever_zero is False


def test_02b_the_weakest_coefficients_zero_out_first():
    zero_at, _ridge_ever_zero = r.alpha_where_each_lasso_coefficient_first_hits_zero(PATH_ALPHAS)
    # s3 is the first coefficient lasso can afford to drop; bmi is the last
    weakest_first = min(zero_at, key=zero_at.get)
    strongest_last = max(zero_at, key=zero_at.get)
    assert weakest_first == "s3"
    assert strongest_last == "bmi"
    assert round(zero_at["s3"], 4) == 0.0032
    assert round(zero_at["bmi"], 4) == 2.4538


def test_03_lasso_recovers_the_right_features_at_low_noise():
    precision, recall, n_selected = r.sparse_recovery(alpha=1.0, noise=1.0, seed=0)
    assert precision == 1.0
    assert recall == 1.0
    assert n_selected == 5
    precision2, recall2, n_selected2 = r.sparse_recovery(alpha=0.1, noise=0.1, seed=0)
    assert precision2 == 1.0
    assert recall2 == 1.0
    assert n_selected2 == 5


def test_03b_recovery_degrades_with_noise_and_too_much_penalty():
    # honest failure: at high noise AND a heavy penalty, lasso can miss
    # most of the true informative set, or all of it
    precision, recall, n_selected = r.sparse_recovery(alpha=80.0, noise=30.0, seed=0)
    assert recall == 0.2
    assert n_selected == 1
    precision0, recall0, n_selected0 = r.sparse_recovery(alpha=80.0, noise=10.0, seed=0)
    assert recall0 == 0.0
    assert n_selected0 == 0
    # and this is not one unlucky seed: averaged over ten dataset seeds,
    # recovery is excellent at moderate noise and degrades at high noise
    mean_precision_low, mean_recall_low = r.sparse_recovery_across_seeds(alpha=1.0, noise=1.0)
    assert mean_precision_low == 1.0
    assert mean_recall_low == 0.98
    mean_precision_high, mean_recall_high = r.sparse_recovery_across_seeds(alpha=1.0, noise=10.0)
    assert mean_precision_high < mean_precision_low
    assert mean_precision_high == 0.6792


def test_04_regularization_requires_scaled_features():
    result = r.scale_dependence(alpha=1.0)
    assert result["raw"]["kept"] == [
        "age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6",
    ]
    assert result["raw"]["n_kept"] == 10
    assert result["standardized"]["kept"] == ["sex", "bmi", "bp", "s1", "s3", "s5", "s6"]
    assert result["standardized"]["n_kept"] == 7
    assert result["sklearn_unit_norm"]["kept"] == ["bmi", "bp", "s5"]
    assert result["sklearn_unit_norm"]["n_kept"] == 3
    # three different answers, same data, same alpha -- only the units differ
    counts = {result[key]["n_kept"] for key in result}
    assert len(counts) == 3


def test_05_elasticnet_interpolates_between_ridge_and_lasso():
    rows = r.elasticnet_sweep(alpha=0.1, l1_ratios=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    assert rows == [
        (0.0, 0, 0.0555),
        (0.1, 0, 0.0605),
        (0.3, 0, 0.0741),
        (0.5, 0, 0.0963),
        (0.7, 1, 0.1389),
        (0.9, 0, 0.2511),
        (1.0, 3, 0.355),
    ]
    # pure L1 (l1_ratio=1.0) is the only setting that matches plain Lasso's
    # own zero count at the same alpha
    lasso_only = r.zero_counts_and_r2([0.1])[0]
    assert rows[-1][1] == lasso_only[1]


def test_05b_ridge_and_elasticnet_do_not_share_an_alpha_scale():
    ridge_head, elastic_head, max_diff = r.ridge_elasticnet_equivalence(alpha=0.1)
    # naively comparing Ridge(alpha=0.1) to ElasticNet(alpha=0.1, l1_ratio=0)
    # would NOT agree -- Ridge sums the squared error, ElasticNet averages
    # it, so the alphas differ by a factor of n_train. Once that correction
    # is applied (Ridge fitted at alpha * n_train), the two match closely.
    assert max_diff < 0.001
    assert ridge_head == [6.3098, 1.229, 22.6076]
    assert elastic_head == [6.3097, 1.229, 22.6076]


def test_06_ridge_splits_the_weight_between_near_duplicates():
    _X, _y, correlation = r.near_duplicate_dataset()
    assert correlation > 0.999
    rows = r.ridge_vs_lasso_on_duplicates([1.0])
    _alpha, ridge_coefs, lasso_coefs = rows[0]
    ridge_x1, ridge_x2, _ridge_x3 = ridge_coefs
    lasso_x1, lasso_x2, _lasso_x3 = lasso_coefs
    # ridge splits the true combined weight of 6.0 roughly evenly
    assert abs(ridge_x1 - ridge_x2) < 0.15
    assert abs((ridge_x1 + ridge_x2) - 6.0) < 0.2
    # lasso picks one and drives the other to exactly zero
    assert lasso_x2 == 0.0
    assert lasso_x1 > 5.0


def test_06b_enough_penalty_zeros_both_duplicates_in_lasso_but_ridge_still_splits():
    rows = r.ridge_vs_lasso_on_duplicates([10.0])
    _alpha, ridge_coefs, lasso_coefs = rows[0]
    ridge_x1, ridge_x2, _ridge_x3 = ridge_coefs
    assert lasso_coefs[0] == 0.0
    assert lasso_coefs[1] == 0.0
    # ridge, at the same alpha, still has both near-duplicate coefficients
    # alive and still close to each other
    assert ridge_x1 > 2.5
    assert ridge_x2 > 2.5
    assert abs(ridge_x1 - ridge_x2) < 0.15


def test_07_ridge_has_a_closed_form_lasso_needs_iterations():
    info = r.ridge_has_no_iteration_count()
    assert info["ridge_has_n_iter"] is False
    assert info["lasso_has_n_iter"] is True
    counts = r.lasso_iteration_counts(ALPHA_GRID)
    assert counts == {0.001: 368, 0.01: 62, 0.1: 135, 1.0: 6}
    # every count is real work, and none of them hit the ceiling
    assert all(0 < n < 50000 for n in counts.values())


def test_08_the_corner_two_correlated_features_and_a_lasso_zero():
    ols, rows = r.two_feature_corner_demo([0.001, 0.5, 1.0, 3.0, 8.0])
    assert ols == [1.9564, 1.9381]
    by_alpha = {alpha: (ridge, lasso) for alpha, ridge, lasso in rows}
    # at alpha=3.0, lasso's solution has landed exactly on the axis --
    # the second coefficient is exactly zero -- while ridge's has not
    ridge_at_3, lasso_at_3 = by_alpha[3.0]
    assert lasso_at_3 == [0.8919, 0.0]
    assert ridge_at_3[0] != 0.0 and ridge_at_3[1] != 0.0
    assert abs(ridge_at_3[1]) > 1.5


def test_08b_at_a_tiny_alpha_both_models_agree_with_ols():
    ols, rows = r.two_feature_corner_demo([0.001, 8.0])
    by_alpha = {alpha: (ridge, lasso) for alpha, ridge, lasso in rows}
    ridge_tiny, lasso_tiny = by_alpha[0.001]
    for ols_coef, ridge_coef in zip(ols, ridge_tiny):
        assert abs(ols_coef - ridge_coef) < 0.01
    for ols_coef, lasso_coef in zip(ols, lasso_tiny):
        assert abs(ols_coef - lasso_coef) < 0.01
    # and at a large enough alpha, lasso has zeroed everything while
    # ridge, which never zeros, has merely shrunk
    ridge_big, lasso_big = by_alpha[8.0]
    assert lasso_big == [0.0, 0.0]
    assert ridge_big[0] != 0.0 and ridge_big[1] != 0.0
