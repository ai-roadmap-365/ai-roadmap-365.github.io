"""Ten exercises in what a linear-regression library was doing for you.

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
    return r.load_diabetes_data(scaled=True)


@pytest.fixture(scope="module")
def diabetes_raw():
    return r.load_diabetes_data(scaled=False)


def test_01_lstsq_agrees_with_sklearn_a_hundred_times_more_closely_than_the_normal_equations(diabetes):
    pytest.skip(
        "Prepend an intercept column with r.add_intercept_column, fit "
        "r.fit_normal_equations and r.fit_lstsq on it, and fit "
        "r.sklearn_reference_fit on the raw X. Assert "
        "r.max_abs_difference(normal_equations, sklearn) is about 1.2153e-10 "
        "and the lstsq gap is about 1.199e-12 -- roughly a hundred times "
        "closer to sklearn's own answer, on the SAME well-conditioned data."
    )


def test_01b_the_normal_equations_condition_number_is_exactly_the_square(diabetes):
    pytest.skip(
        "Call r.condition_numbers on the intercept-augmented design matrix. "
        "Assert cond(A) is about 227.2248 and cond(A'A) is about 51631.1119, "
        "and that cond(A'A) / cond(A)**2 is within 1e-8 of 1.0. This is the "
        "textbook reason the normal equations lose precision that a direct "
        "solve of A does not."
    )


def test_02_a_near_duplicate_column_makes_the_normal_equations_explode():
    pytest.skip(
        "Build r.make_dramatic_collinear_dataset(n=100, seed=0): three "
        "random columns plus a fourth that is column 0 plus a sliver of "
        "noise, true coefficients [1, 2, 3, 4]. Fit both closed forms and "
        "sklearn's own LinearRegression. Assert the normal-equation and "
        "lstsq coefficients for the duplicated pair explode past 1e5 in "
        "opposite directions, while sklearn's stay near 2.5 and 2.5 -- an "
        "SVD-based minimum-norm solve splitting the weight evenly -- and "
        "sklearn recovers the other two coefficients near 2.0 and 3.0."
    )


def test_02b_even_the_squaring_relationship_becomes_hard_to_verify_here():
    pytest.skip(
        "On the same dramatic dataset, assert cond(A) exceeds 1e6 and "
        "cond(A'A) exceeds 1e13 -- several orders of magnitude worse than "
        "the diabetes case. Then assert cond(A'A) / cond(A)**2 lies strictly "
        "between 0.9 and 1.0 but differs from 1.0 by MORE than 1e-4: at this "
        "level of ill-conditioning, computing the smallest singular value of "
        "an already near-singular matrix is itself imprecise, so even the "
        "squaring relationship's own verification degrades."
    )


def test_03_gradient_descent_reaches_the_closed_form_at_three_six_and_nine_decimals(diabetes):
    pytest.skip(
        "Standardize X with r.standardize, centre y, and fit the closed "
        "form as the target. Compute r.stability_threshold and assert it is "
        "about 0.2485 (Day 111's condition applied to this Hessian). At a "
        "learning rate of 0.2 -- about 80 percent of that threshold -- "
        "assert r.iters_to_tolerance needs exactly 3263 iterations for 3 "
        "decimals, 5277 for 6, and 7291 for 9. Then assert the growth is "
        "roughly linear, not exponential: iters_6 - iters_3 < iters_3."
    )


def test_03b_the_same_setup_on_unscaled_features_barely_moves(diabetes, diabetes_raw):
    pytest.skip(
        "Compute r.hessian_eigenvalues for the standardized diabetes data "
        "and for the RAW (scaled=False), centred diabetes data. Assert the "
        "max/min eigenvalue ratio is about 470.08 standardized and about "
        "76278.96 raw -- over a hundred times worse conditioned, in exactly "
        "the sense Day 111 defined. Then, at 95 percent of the raw data's "
        "own stability threshold, assert r.iters_to_tolerance has NOT "
        "converged after 200,000 iterations and the remaining gap from the "
        "closed form still exceeds 0.1 -- a learning rate that is stable in "
        "principle can still be catastrophically slow."
    )


def test_04_the_day_111_stability_threshold_predicts_divergence_exactly(diabetes):
    pytest.skip(
        "At 80 percent of r.stability_threshold, assert "
        "r.iters_to_tolerance converges (to 1e-9) in exactly 7132 "
        "iterations. At 102 percent of the same threshold, assert it "
        "returns the string 'diverged' and the returned coefficients are "
        "no longer all finite. The formula from Day 111, "
        "|1 - eta * a| < 1, predicts exactly where that line falls."
    )


def test_05_the_closed_form_needs_a_thousand_times_fewer_operations(diabetes):
    pytest.skip(
        "Using the diabetes shape (n=442, p=10), compute "
        "r.normal_equation_op_count(442, 11) -- the +1 is the intercept "
        "column -- and assert it equals 54813. Compute "
        "r.gradient_descent_op_count(442, 10, 7291) using exercise 3's "
        "9-decimal iteration count and assert it equals 64452440. Assert "
        "the ratio is between 1000 and 1300: over a thousand times more "
        "multiply-adds for gradient descent to match what the closed form "
        "gets in one solve. No wall-clock timing anywhere -- count "
        "operations instead."
    )


def test_06_the_estimator_matches_sklearn_and_check_estimator_names_two_failures(diabetes):
    pytest.skip(
        "Fit r.OLSRegressor with method='normal', 'lstsq' and 'gd' "
        "(lr=0.2, n_iter=8000) on standardized diabetes data, and assert "
        "each one's coef_ matches sklearn's own LinearRegression to within "
        "1e-8 or better. Then call r.run_check_estimator(r.OLSRegressor()) "
        "and assert exactly 48 of 52 checks pass, that the two failures are "
        "named check_n_features_in_after_fitting and check_dtype_object, "
        "and that the two skips are check_array_api_input and "
        "check_regressor_data_not_an_array -- do not suppress or hide "
        "either list."
    )


def test_07_centring_and_appending_a_column_agree_to_ten_decimal_places(diabetes):
    pytest.skip(
        "Call r.fit_intercept_two_ways on the diabetes data and assert the "
        "max coefficient difference between the column-append approach and "
        "the centring approach is below 1e-9, and the intercept difference "
        "is below 1e-9 as well. Two routes to the same intercept, agreeing "
        "to nine decimal places or better."
    )
