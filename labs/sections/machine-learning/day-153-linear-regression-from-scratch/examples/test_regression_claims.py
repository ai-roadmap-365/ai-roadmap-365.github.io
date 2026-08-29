"""Ten exercises in what a linear-regression library was doing for you.

Reference solutions. Read `starter/00_brief.md` and
`starter/test_regression_claims.py` for the exercise version, where each of
these bodies is a `pytest.skip` naming exactly what to build.

Run this suite on its own:

    .venv/bin/pytest examples -q

Never run `pytest examples starter` in one invocation: both directories
define modules with the same names and pytest aborts on the collision.
"""

import numpy as np
import pytest

import regression_lib as r


@pytest.fixture(scope="module")
def diabetes():
    return r.load_diabetes_data(scaled=True)


@pytest.fixture(scope="module")
def diabetes_raw():
    return r.load_diabetes_data(scaled=False)


def test_01_lstsq_agrees_with_sklearn_a_hundred_times_more_closely_than_the_normal_equations(diabetes):
    X, y = diabetes
    A = r.add_intercept_column(X)
    beta_ne = r.fit_normal_equations(A, y)
    beta_lstsq = r.fit_lstsq(A, y)
    beta_sk = r.sklearn_reference_fit(X, y)

    gap_ne = r.max_abs_difference(beta_ne, beta_sk)
    gap_lstsq = r.max_abs_difference(beta_lstsq, beta_sk)

    assert gap_ne == pytest.approx(1.2153e-10, rel=0.05)
    assert gap_lstsq == pytest.approx(1.199e-12, rel=0.05)
    # lstsq is roughly a hundred times closer to sklearn's own answer
    assert 50 < gap_ne / gap_lstsq < 200


def test_01b_the_normal_equations_condition_number_is_exactly_the_square(diabetes):
    X, y = diabetes
    A = r.add_intercept_column(X)
    cond_a, cond_ata = r.condition_numbers(A)

    assert cond_a == pytest.approx(227.2248, rel=1e-4)
    assert cond_ata == pytest.approx(51631.1119, rel=1e-4)
    # cond(A'A) is the square of cond(A), to numerical precision here
    assert cond_ata / cond_a**2 == pytest.approx(1.0, abs=1e-8)


def test_02_a_near_duplicate_column_makes_the_normal_equations_explode():
    X, y, true_coef = r.make_dramatic_collinear_dataset(n=100, seed=0)
    A = r.add_intercept_column(X)
    beta_ne = r.fit_normal_equations(A, y)
    beta_lstsq = r.fit_lstsq(A, y)
    beta_sk = r.sklearn_reference_fit(X, y)

    # the true coefficients for the two duplicated columns are 1 and 4;
    # both from-scratch closed forms split that weight into something
    # unrecognisable, in opposite directions
    assert beta_ne[1] > 1e5
    assert beta_ne[4] < -1e5
    assert beta_lstsq[1] > 1e5
    assert beta_lstsq[4] < -1e5

    # sklearn's own LinearRegression -- an SVD-based minimum-norm solve --
    # stays sane and splits the weight evenly between the near-duplicates
    assert beta_sk[1] == pytest.approx(2.5, abs=0.05)
    assert beta_sk[4] == pytest.approx(2.5, abs=0.05)
    # and it recovers the two non-duplicated coefficients accurately
    assert beta_sk[2] == pytest.approx(2.0, abs=0.05)
    assert beta_sk[3] == pytest.approx(3.0, abs=0.05)


def test_02b_even_the_squaring_relationship_becomes_hard_to_verify_here():
    X, y, _true_coef = r.make_dramatic_collinear_dataset(n=100, seed=0)
    A = r.add_intercept_column(X)
    cond_a, cond_ata = r.condition_numbers(A)

    # several orders of magnitude worse than the diabetes case above
    assert cond_a > 1e6
    assert cond_ata > 1e13

    # the theoretical relationship is exact, but computing the smallest
    # singular value of an already near-singular matrix is itself
    # imprecise, so the measured ratio drifts noticeably from 1.0 -- unlike
    # the clean diabetes case, where it held to twelve decimal places
    ratio = cond_ata / cond_a**2
    assert 0.9 < ratio < 1.0
    assert abs(ratio - 1.0) > 1e-4


def test_03_gradient_descent_reaches_the_closed_form_at_three_six_and_nine_decimals(diabetes):
    X, y = diabetes
    Xs = r.standardize(X)
    yc = y - y.mean()
    target = r.fit_normal_equations(Xs, yc)

    threshold = r.stability_threshold(Xs)
    assert threshold == pytest.approx(0.2485, rel=1e-3)

    learning_rate = 0.2  # about 80 percent of the stability threshold
    iters_3, _ = r.iters_to_tolerance(Xs, yc, learning_rate, target, 5e-4, 200_000)
    iters_6, _ = r.iters_to_tolerance(Xs, yc, learning_rate, target, 5e-7, 200_000)
    iters_9, _ = r.iters_to_tolerance(Xs, yc, learning_rate, target, 5e-10, 200_000)

    assert iters_3 == 3263
    assert iters_6 == 5277
    assert iters_9 == 7291
    # each extra three decimal places costs a comparable number of further
    # iterations, not an exponentially larger one -- linear convergence
    assert iters_6 - iters_3 < iters_3
    assert iters_9 - iters_6 < iters_6


def test_03b_the_same_setup_on_unscaled_features_barely_moves(diabetes, diabetes_raw):
    X, y = diabetes
    Xraw, yraw = diabetes_raw
    Xs = r.standardize(X)

    eig_scaled = r.hessian_eigenvalues(Xs, Xs.shape[0])
    Xrc, yrc, _, _ = r.center(Xraw, yraw)
    eig_raw = r.hessian_eigenvalues(Xrc, Xrc.shape[0])

    ratio_scaled = float(eig_scaled.max() / eig_scaled.min())
    ratio_raw = float(eig_raw.max() / eig_raw.min())

    assert ratio_scaled == pytest.approx(470.08, rel=0.01)
    assert ratio_raw == pytest.approx(76278.96, rel=0.01)
    # the raw features are over a hundred times worse conditioned, in the
    # Hessian-eigenvalue sense Day 111 already established
    assert ratio_raw / ratio_scaled > 100

    raw_threshold = r.stability_threshold(Xrc)
    target_raw = r.fit_normal_equations(Xrc, yrc)
    status, coef = r.iters_to_tolerance(Xrc, yrc, raw_threshold * 0.95, target_raw, 5e-4, 200_000)

    # a learning rate at 95 percent of ITS OWN stability threshold --
    # stable in principle -- still has not reached even one decimal place
    # of agreement after 200,000 iterations, because the slowest direction
    # is governed by the smallest eigenvalue, not the largest
    assert status is None
    assert r.max_abs_difference(coef, target_raw) > 0.1


def test_04_the_day_111_stability_threshold_predicts_divergence_exactly(diabetes):
    X, y = diabetes
    Xs = r.standardize(X)
    yc = y - y.mean()
    target = r.fit_normal_equations(Xs, yc)
    threshold = r.stability_threshold(Xs)

    # comfortably below threshold: converges
    below_status, below_coef = r.iters_to_tolerance(Xs, yc, threshold * 0.8, target, 1e-9, 20_000)
    assert below_status == 7132

    # just past threshold: diverges to non-finite values
    above_status, above_coef = r.iters_to_tolerance(Xs, yc, threshold * 1.02, target, 1e-9, 20_000)
    assert above_status == "diverged"
    assert not np.all(np.isfinite(above_coef))


def test_05_the_closed_form_needs_a_thousand_times_fewer_operations(diabetes):
    X, _y = diabetes
    n, p = X.shape

    ops_normal = r.normal_equation_op_count(n, p + 1)  # +1 for the intercept column
    ops_gd = r.gradient_descent_op_count(n, p, iterations=7291)  # 9-decimal convergence, exercise 3

    assert ops_normal == 54813
    assert ops_gd == 64_452_440
    ratio = ops_gd / ops_normal
    assert 1000 < ratio < 1300


def test_06_the_estimator_matches_sklearn_and_check_estimator_names_two_failures(diabetes):
    from sklearn.linear_model import LinearRegression

    X, y = diabetes
    Xs = r.standardize(X)
    sk = LinearRegression().fit(Xs, y)

    normal_est = r.OLSRegressor(method="normal").fit(Xs, y)
    lstsq_est = r.OLSRegressor(method="lstsq").fit(Xs, y)
    gd_est = r.OLSRegressor(method="gd", lr=0.2, n_iter=8000).fit(Xs, y)

    assert r.max_abs_difference(normal_est.coef_, sk.coef_) < 1e-9
    assert r.max_abs_difference(lstsq_est.coef_, sk.coef_) < 1e-9
    assert r.max_abs_difference(gd_est.coef_, sk.coef_) < 1e-8

    passed, failed, skipped = r.run_check_estimator(r.OLSRegressor())
    failed_names = {name for name, _msg in failed}
    skipped_names = {name for name, _msg in skipped}

    assert len(passed) == 48
    assert failed_names == {"check_n_features_in_after_fitting", "check_dtype_object"}
    assert skipped_names == {"check_array_api_input", "check_regressor_data_not_an_array"}
    assert len(passed) + len(failed) + len(skipped) == 52


def test_07_centring_and_appending_a_column_agree_to_ten_decimal_places(diabetes):
    X, y = diabetes
    coef_col, intercept_col, coef_centred, intercept_centred = r.fit_intercept_two_ways(X, y)

    assert r.max_abs_difference(coef_col, coef_centred) < 1e-9
    assert abs(intercept_col - intercept_centred) < 1e-9
