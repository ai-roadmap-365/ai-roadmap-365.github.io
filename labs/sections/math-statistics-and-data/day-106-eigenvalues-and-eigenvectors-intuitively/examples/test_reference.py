"""The reference suite: every claim this lab makes, checked against real values.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider

Every float comparison here names its tolerance in the assertion rather than
relying on a default, and every eigenvector comparison goes through
`abs_cosine` rather than comparing components — because an eigenvector is
defined only up to sign and scale, so a component-wise comparison fails on a
correct answer roughly half the time.
"""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from dataset import (
    A,
    A_EIGEN_ANGLES_DEG,
    A_EIGENVALUES,
    A_EIGENVECTORS,
    CENTRE,
    ELONGATION_DEG,
    N_POINTS,
    PROJECTION_ONTO_X,
    REFLECTION_IN_X,
    ROTATION_60,
    ROTATION_90,
    SHEAR,
    SPREAD_ACROSS,
    SPREAD_ALONG,
    STANDARD_TRANSFORMATIONS,
    SYMMETRIC,
    SYMMETRIC_3X3,
    elongation_direction,
    make_cloud,
    power_method_start,
)
from eigen import (
    abs_cosine,
    characteristic_coefficients,
    covariance_matrix,
    deviation_degrees,
    direction_degrees,
    eigen_lines_by_sweep,
    eigenvalues_2x2,
    eigenvector_2x2,
    power_method,
    principal_components,
    rayleigh_quotient,
    solve_2x2,
    sweep_deviations,
)

#: Tolerances, named once so every test says which one it used.
EXACT = 1e-12
TIGHT = 1e-9
ANGLE = 1e-6
SWEEP = 1e-2  # a sampled sweep cannot beat its own grid spacing


# ==========================================================================
# The fan of vectors: which directions survive
# ==========================================================================


def test_only_two_directions_out_of_twentyfour_keep_their_line():
    kept = []
    for angle in range(0, 360, 15):
        radians = np.radians(angle)
        v = np.array([np.cos(radians), np.sin(radians)])
        if deviation_degrees(v, A @ v) < TIGHT:
            kept.append(angle)
    assert kept == [45, 225]


def test_45_and_225_are_the_same_line():
    up = np.array([np.cos(np.radians(45)), np.sin(np.radians(45))])
    down = np.array([np.cos(np.radians(225)), np.sin(np.radians(225))])
    assert abs_cosine(up, down) == pytest.approx(1.0, abs=EXACT)
    assert np.allclose(down, -up, atol=EXACT)


def test_a_full_sweep_finds_exactly_two_eigen_lines():
    found = eigen_lines_by_sweep(A)
    assert found["verdict"] == "some"
    assert len(found["lines"]) == 2
    assert found["lines"] == pytest.approx(list(A_EIGEN_ANGLES_DEG), abs=SWEEP)


def test_the_eigen_directions_deviate_by_nothing_at_all():
    for angle in A_EIGEN_ANGLES_DEG:
        radians = np.radians(angle)
        v = np.array([np.cos(radians), np.sin(radians)])
        assert deviation_degrees(v, A @ v) < TIGHT


def test_the_stretch_factors_are_the_eigenvalues():
    for angle, expected in zip(A_EIGEN_ANGLES_DEG, A_EIGENVALUES):
        radians = np.radians(angle)
        v = np.array([np.cos(radians), np.sin(radians)])
        stretch = float(np.linalg.norm(A @ v)) / float(np.linalg.norm(v))
        assert stretch == pytest.approx(expected, abs=TIGHT)


def test_a_non_eigen_direction_really_is_knocked_off_its_line():
    v = np.array([1.0, 0.0])
    assert deviation_degrees(v, A @ v) == pytest.approx(26.565051, abs=1e-6)


@pytest.mark.parametrize("vector,eigenvalue", list(zip(A_EIGENVECTORS, A_EIGENVALUES)))
def test_the_integer_eigenvectors_check_out_on_paper(vector, eigenvalue):
    v = np.array(vector)
    assert np.allclose(A @ v, eigenvalue * v, atol=EXACT)


def test_the_zero_vector_satisfies_the_equation_for_every_lambda():
    zero = np.zeros(2)
    for candidate in (5.0, 2.0, 0.0, -3.5, 1000.0):
        assert np.allclose(A @ zero, candidate * zero, atol=EXACT)


def test_abs_cosine_refuses_the_zero_vector():
    with pytest.raises(ValueError, match="no direction"):
        abs_cosine(np.zeros(2), np.array([1.0, 1.0]))


# ==========================================================================
# The hand solution
# ==========================================================================


def test_trace_and_determinant_are_the_characteristic_coefficients():
    trace, determinant = characteristic_coefficients(A)
    assert trace == 7.0
    assert determinant == 10.0


def test_the_characteristic_polynomial_really_vanishes_at_both_eigenvalues():
    trace, determinant = characteristic_coefficients(A)
    for eigenvalue in A_EIGENVALUES:
        value = eigenvalue**2 - trace * eigenvalue + determinant
        assert value == pytest.approx(0.0, abs=EXACT)


def test_hand_eigenvalues_match_the_worked_answer():
    values = eigenvalues_2x2(A)
    assert sorted(value.real for value in values) == pytest.approx([2.0, 5.0], abs=TIGHT)
    assert all(abs(value.imag) < EXACT for value in values)


def test_hand_eigenvalues_match_numpy_sorted_with_a_stated_tolerance():
    hand = sorted(value.real for value in eigenvalues_2x2(A))
    theirs = sorted(np.linalg.eig(A)[0].real)
    assert hand == pytest.approx(theirs, abs=TIGHT)


def test_a_minus_lambda_i_has_determinant_zero_at_each_eigenvalue():
    for eigenvalue in A_EIGENVALUES:
        shifted = A - eigenvalue * np.eye(2)
        assert float(np.linalg.det(shifted)) == pytest.approx(0.0, abs=EXACT)


@pytest.mark.parametrize("eigenvalue,expected", list(zip(A_EIGENVALUES, A_EIGENVECTORS)))
def test_hand_eigenvector_lies_on_the_right_line(eigenvalue, expected):
    v = eigenvector_2x2(A, eigenvalue)
    assert abs_cosine(v, expected) == pytest.approx(1.0, abs=TIGHT)


@pytest.mark.parametrize("eigenvalue", A_EIGENVALUES)
def test_hand_eigenvector_satisfies_the_defining_equation(eigenvalue):
    v = eigenvector_2x2(A, eigenvalue)
    assert np.allclose(A @ v, eigenvalue * v, atol=EXACT)


def test_hand_eigenvectors_come_back_as_unit_vectors():
    for eigenvalue in A_EIGENVALUES:
        assert float(np.linalg.norm(eigenvector_2x2(A, eigenvalue))) == pytest.approx(1.0, abs=EXACT)


def test_any_multiple_of_an_eigenvector_is_also_an_eigenvector():
    v = np.array(A_EIGENVECTORS[0])
    for scale in (-7.5, -1.0, 0.25, 3.0, 1000.0):
        scaled = scale * v
        assert np.allclose(A @ scaled, A_EIGENVALUES[0] * scaled, atol=1e-9)


def test_solve_2x2_returns_no_eigenvectors_for_a_rotation():
    values, vectors = solve_2x2(ROTATION_90)
    assert vectors is None
    assert all(abs(value.imag) > 0.5 for value in values)


def test_the_hand_method_rejects_a_non_2x2():
    with pytest.raises(ValueError, match="2x2"):
        characteristic_coefficients(np.eye(3))


# ==========================================================================
# What NumPy actually returns
# ==========================================================================


def test_numpy_eig_returns_complex_even_when_every_eigenvalue_is_real():
    """Observed on numpy 2.5.2, and it contradicts numpy's own docstring.

    The docstring for numpy.linalg.eig says the result "will be of complex
    type, unless the imaginary part is zero in which case it will be cast to a
    real type". On this version the imaginary part IS zero and the cast does
    NOT happen. The measurement is what this test records; if a future version
    changes the behaviour, this test going red is the correct outcome and the
    lesson text needs updating with it.
    """
    values, vectors = np.linalg.eig(A)
    assert values.dtype == np.complex128
    assert vectors.dtype == np.complex128
    assert np.all(values.imag == 0.0)


@pytest.mark.parametrize(
    "matrix",
    [np.eye(2), np.diag([1.0, 2.0, 3.0]), np.array([[2, 0], [0, 3]]), SYMMETRIC],
)
def test_eig_is_complex_for_every_real_eigenvalued_matrix_tried(matrix):
    assert np.linalg.eig(matrix)[0].dtype == np.complex128


def test_casting_those_eigenvalues_to_float_warns():
    values = np.linalg.eig(A)[0]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        values.astype(float)
    assert [item.category.__name__ for item in caught] == ["ComplexWarning"]


def test_taking_real_without_checking_destroys_a_rotations_answer():
    values = np.linalg.eig(ROTATION_90)[0]
    assert np.allclose(np.abs(values), 1.0, atol=TIGHT)
    assert np.allclose(values.real, 0.0, atol=TIGHT)


def test_eigh_returns_real_sorted_values_on_symmetric_input():
    values = np.linalg.eigh(SYMMETRIC)[0]
    assert values.dtype == np.float64
    assert np.all(np.diff(values) >= 0)
    assert values == pytest.approx([1.0, 3.0], abs=TIGHT)


def test_eigh_silently_answers_a_different_question_on_non_symmetric_input():
    wrong = np.linalg.eigh(A)[0]
    lower_triangle_mirrored = np.array([[4.0, 2.0], [2.0, 3.0]])
    assert np.allclose(wrong, np.linalg.eigvalsh(lower_triangle_mirrored), atol=EXACT)
    assert not np.allclose(np.sort(wrong), sorted(A_EIGENVALUES), atol=1e-6)


def test_every_returned_pair_satisfies_a_v_equals_lambda_v():
    for matrix in [A, SYMMETRIC, SHEAR, REFLECTION_IN_X, PROJECTION_ONTO_X]:
        values, vectors = np.linalg.eig(matrix)
        for index in range(len(values)):
            left = matrix @ vectors[:, index]
            right = values[index] * vectors[:, index]
            assert float(np.abs(left - right).max()) < EXACT


def test_eigenvectors_from_numpy_are_unit_length():
    for matrix in [A, SYMMETRIC, SYMMETRIC_3X3]:
        vectors = np.linalg.eig(matrix)[1]
        assert np.allclose(np.linalg.norm(vectors, axis=0), 1.0, atol=EXACT)


def test_the_sign_ambiguity_is_real_and_component_comparison_fails():
    """The trap, pinned down. Do not 'fix' this test by flipping a sign."""
    values, vectors = np.linalg.eig(A)
    index = int(np.argmin(values.real))  # the lambda = 2 column
    mine = np.array(A_EIGENVECTORS[1], dtype=float)
    mine = mine / np.linalg.norm(mine)
    theirs = vectors.real[:, index]
    assert not np.allclose(mine, theirs, atol=1e-6)
    assert np.allclose(mine, -theirs, atol=TIGHT)
    assert abs_cosine(mine, theirs) == pytest.approx(1.0, abs=EXACT)


# ==========================================================================
# The standard transformations
# ==========================================================================


def test_a_shear_has_exactly_one_eigen_line():
    found = eigen_lines_by_sweep(SHEAR)
    assert len(found["lines"]) == 1
    line = found["lines"][0]
    assert min(line, 180.0 - line) < 0.05


def test_a_shear_returns_two_columns_that_are_the_same_direction():
    values, vectors = np.linalg.eig(SHEAR)
    assert np.allclose(values.real, [1.0, 1.0], atol=TIGHT)
    assert abs_cosine(vectors.real[:, 0], vectors.real[:, 1]) == pytest.approx(1.0, abs=1e-8)


@pytest.mark.parametrize("rotation", [ROTATION_90, ROTATION_60])
def test_a_plane_rotation_has_no_real_eigenvalues(rotation):
    values = np.linalg.eig(rotation)[0]
    assert np.all(np.abs(values.imag) > 0.5)
    assert np.allclose(np.abs(values), 1.0, atol=TIGHT)


@pytest.mark.parametrize("rotation", [ROTATION_90, ROTATION_60])
def test_a_plane_rotation_leaves_no_direction_on_its_own_line(rotation):
    found = eigen_lines_by_sweep(rotation)
    assert found["verdict"] == "none"
    assert found["lines"] == []


def test_the_rotations_negative_discriminant_is_the_geometry_speaking():
    trace, determinant = characteristic_coefficients(ROTATION_90)
    assert trace == 0.0
    assert determinant == pytest.approx(1.0, abs=EXACT)
    assert trace * trace - 4.0 * determinant < 0.0


@pytest.mark.parametrize("matrix", [np.eye(2), 2.0 * np.eye(2)])
def test_a_uniform_scaling_keeps_every_direction(matrix):
    found = eigen_lines_by_sweep(matrix)
    assert found["verdict"] == "every direction"
    assert found["fraction"] == pytest.approx(1.0, abs=EXACT)


def test_a_reflection_has_a_negative_eigenvalue_and_still_keeps_both_lines():
    values = np.sort(np.linalg.eig(REFLECTION_IN_X)[0].real)
    assert values == pytest.approx([-1.0, 1.0], abs=TIGHT)
    found = eigen_lines_by_sweep(REFLECTION_IN_X)
    assert len(found["lines"]) == 2


def test_a_projection_has_eigenvalue_zero_and_determinant_zero():
    values = np.sort(np.linalg.eig(PROJECTION_ONTO_X)[0].real)
    assert values == pytest.approx([0.0, 1.0], abs=TIGHT)
    assert float(np.linalg.det(PROJECTION_ONTO_X)) == pytest.approx(0.0, abs=EXACT)


def test_the_collapsed_direction_has_no_angle_to_measure():
    deviations, collapsed = sweep_deviations(PROJECTION_ONTO_X, [0.0, 45.0, 90.0])
    assert collapsed.tolist() == [False, False, True]
    assert np.isnan(deviations[2])
    assert deviations[0] == pytest.approx(0.0, abs=ANGLE)


@pytest.mark.parametrize("name", list(STANDARD_TRANSFORMATIONS))
def test_eigenvalues_multiply_to_the_determinant(name):
    matrix = STANDARD_TRANSFORMATIONS[name][0]
    product = complex(np.prod(np.linalg.eig(matrix)[0]))
    assert product.real == pytest.approx(float(np.linalg.det(matrix)), abs=TIGHT)
    assert abs(product.imag) < TIGHT


@pytest.mark.parametrize("name", list(STANDARD_TRANSFORMATIONS))
def test_eigenvalues_add_to_the_trace(name):
    matrix = STANDARD_TRANSFORMATIONS[name][0]
    total = complex(np.sum(np.linalg.eig(matrix)[0]))
    assert total.real == pytest.approx(float(np.trace(matrix)), abs=TIGHT)
    assert abs(total.imag) < TIGHT


@pytest.mark.parametrize("matrix", [SYMMETRIC, SYMMETRIC_3X3])
def test_a_symmetric_matrix_has_real_eigenvalues_and_orthogonal_eigenvectors(matrix):
    assert np.allclose(matrix, matrix.T, atol=EXACT)
    values, vectors = np.linalg.eigh(matrix)
    assert values.dtype == np.float64
    assert float(np.abs(vectors.T @ vectors - np.eye(len(values))).max()) < EXACT


def test_diagonalisation_reconstructs_the_original_matrix():
    """A = V D V-inverse: change basis, scale, change back."""
    values, vectors = np.linalg.eig(A)
    rebuilt = vectors @ np.diag(values) @ np.linalg.inv(vectors)
    assert np.allclose(rebuilt.real, A, atol=TIGHT)
    assert float(np.abs(rebuilt.imag).max()) < TIGHT


def test_the_shear_cannot_be_diagonalised_and_fails_silently():
    """The shear has one eigen-line, so its eigenvector matrix is singular and
    V D V-inverse cannot rebuild it.

    What is worth recording is HOW it fails. numpy.linalg.inv does not raise:
    the determinant is 2.2e-16 rather than exactly 0, so LAPACK inverts it and
    returns entries around 4.5e15. The reconstruction then comes back as the
    identity matrix — a clean, plausible, completely wrong answer, with no
    exception and no warning anywhere.

    The reliable check is the condition number, not an exception.
    """
    values, vectors = np.linalg.eig(SHEAR)
    vectors = vectors.real
    assert abs(float(np.linalg.det(vectors))) < 1e-15
    assert float(np.linalg.cond(vectors)) > 1e15

    inverse = np.linalg.inv(vectors)  # does NOT raise
    rebuilt = vectors @ np.diag(values.real) @ inverse
    assert not np.allclose(rebuilt, SHEAR, atol=1e-6)
    assert np.allclose(rebuilt, np.eye(2), atol=1e-9)


# ==========================================================================
# The power method
# ==========================================================================


def test_power_method_converges_in_25_iterations_to_the_stated_tolerance():
    result = power_method(A, power_method_start(), tol=1e-10)
    assert result["converged"] is True
    assert result["iterations"] == 25
    assert result["change"] < 1e-10


def test_power_method_finds_the_dominant_eigen_line():
    result = power_method(A, power_method_start(), tol=1e-10)
    assert abs_cosine(result["vector"], A_EIGENVECTORS[0]) == pytest.approx(1.0, abs=EXACT)
    assert direction_degrees(result["vector"]) == pytest.approx(45.0, abs=ANGLE)


def test_power_method_finds_the_dominant_eigenvalue():
    result = power_method(A, power_method_start(), tol=1e-10)
    assert result["eigenvalue"] == pytest.approx(5.0, abs=TIGHT)


def test_power_method_agrees_with_numpy():
    result = power_method(A, power_method_start(), tol=1e-10)
    values, vectors = np.linalg.eig(A)
    top = int(np.argmax(np.abs(values.real)))
    assert result["eigenvalue"] == pytest.approx(float(values.real[top]), abs=TIGHT)
    assert abs_cosine(result["vector"], vectors.real[:, top]) == pytest.approx(1.0, abs=EXACT)


def test_the_convergence_rate_equals_the_eigenvalue_ratio():
    history = power_method(A, power_method_start(), tol=1e-10)["history"]
    ratio = history[13] / history[12]
    assert ratio == pytest.approx(A_EIGENVALUES[1] / A_EIGENVALUES[0], abs=1e-3)


def test_close_eigenvalues_make_the_power_method_crawl():
    fast = power_method(A, power_method_start(), tol=1e-10)
    slow = power_method(np.diag([5.0, 4.9]), np.array([0.6, 0.8]), tol=1e-10)
    assert slow["iterations"] > 10 * fast["iterations"]


def test_power_method_works_from_several_different_starts():
    rng = np.random.default_rng(99)
    for _ in range(8):
        start = rng.normal(size=2)
        result = power_method(A, start, tol=1e-10)
        assert result["converged"] is True
        assert abs_cosine(result["vector"], A_EIGENVECTORS[0]) == pytest.approx(1.0, abs=1e-10)


def test_power_method_refuses_the_zero_vector():
    with pytest.raises(ValueError, match="zero vector"):
        power_method(A, np.zeros(2))


def test_power_method_reports_failure_rather_than_lying():
    result = power_method(A, power_method_start(), tol=1e-16, max_iter=5)
    assert result["converged"] is False
    assert result["iterations"] == 5


def test_the_rayleigh_quotient_is_exact_on_a_true_eigenvector():
    for vector, eigenvalue in zip(A_EIGENVECTORS, A_EIGENVALUES):
        assert rayleigh_quotient(A, vector) == pytest.approx(eigenvalue, abs=EXACT)


def _quotient_error_ratios(matrix, target, eigenvalue, steps=8):
    """(angle error, quotient error) after each of `steps` power iterations."""
    v = power_method_start()
    out = []
    for _ in range(steps):
        w = matrix @ v
        v = w / np.linalg.norm(w)
        angle = float(np.arccos(min(1.0, abs_cosine(v, target))))
        out.append((angle, abs(rayleigh_quotient(matrix, v) - eigenvalue)))
    return out


def test_the_rayleigh_quotient_is_quadratic_only_for_a_symmetric_matrix():
    """The textbook says the Rayleigh quotient converges twice as fast as the
    vector. Measured here, that is true for a SYMMETRIC matrix and false for
    this lab's non-symmetric one.

    On SYMMETRIC the quotient error divided by the squared angle settles on
    2.0 — dead-on quadratic. On A the quotient error divided by the angle
    itself settles on 1.0 — merely linear, the same rate as the vector.

    The quadratic result depends on the eigenvectors being orthogonal, which
    symmetry guarantees and A does not have.
    """
    symmetric = _quotient_error_ratios(SYMMETRIC, np.array([1.0, 1.0]), 3.0)
    angle, quotient = symmetric[-1]
    assert quotient / angle**2 == pytest.approx(2.0, abs=1e-3)

    unsymmetric = _quotient_error_ratios(A, np.array(A_EIGENVECTORS[0]), 5.0)
    angle, quotient = unsymmetric[-1]
    assert quotient / angle == pytest.approx(1.0, abs=1e-2)
    assert quotient / angle**2 > 100.0  # nowhere near quadratic


def test_unnormalised_iteration_overflows_to_infinity():
    v = power_method_start()
    with np.errstate(over="ignore"):
        for _ in range(600):
            v = A @ v
    assert not np.all(np.isfinite(v))


# ==========================================================================
# PCA
# ==========================================================================


def test_the_cloud_is_reproducible_from_the_seed():
    first = make_cloud()
    second = make_cloud()
    assert np.array_equal(first, second)
    assert first.shape == (N_POINTS, 2)


def test_the_cloud_sits_where_it_was_built_to_sit():
    assert make_cloud().mean(axis=0) == pytest.approx(CENTRE, abs=0.2)


def test_covariance_from_scratch_matches_numpy_cov():
    cloud = make_cloud()
    assert np.allclose(covariance_matrix(cloud), np.cov(cloud, rowvar=False), atol=EXACT)


def test_a_covariance_matrix_is_always_symmetric():
    covariance = covariance_matrix(make_cloud())
    assert np.allclose(covariance, covariance.T, atol=1e-15)


def test_covariance_refuses_a_1d_array():
    with pytest.raises(ValueError, match="2-D"):
        covariance_matrix(np.array([1.0, 2.0, 3.0]))


def test_the_top_principal_component_lies_along_the_known_elongation():
    _variances, directions = principal_components(make_cloud())
    similarity = abs_cosine(directions[:, 0], elongation_direction())
    assert similarity > 0.999
    assert similarity == pytest.approx(0.9999984422, abs=1e-9)


def test_the_top_component_is_within_a_fifth_of_a_degree_of_the_truth():
    _variances, directions = principal_components(make_cloud())
    error = abs(direction_degrees(directions[:, 0]) - ELONGATION_DEG)
    assert error < 0.2


def test_the_returned_top_component_points_the_other_way_along_that_line():
    """The sign ambiguity, in the artifact that matters. Not a defect."""
    _variances, directions = principal_components(make_cloud())
    truth = elongation_direction()
    assert float(np.dot(directions[:, 0], truth)) < 0.0
    assert not np.allclose(directions[:, 0], truth, atol=1e-3)
    assert abs_cosine(directions[:, 0], truth) > 0.999


def test_the_eigenvalues_recover_the_spreads_the_cloud_was_built_with():
    variances, _directions = principal_components(make_cloud())
    assert float(np.sqrt(variances[0])) == pytest.approx(SPREAD_ALONG, abs=0.2)
    assert float(np.sqrt(variances[1])) == pytest.approx(SPREAD_ACROSS, abs=0.1)


def test_the_first_component_carries_almost_all_the_variance():
    variances, _directions = principal_components(make_cloud())
    assert float(variances[0] / variances.sum()) > 0.97


def test_the_components_come_back_largest_first():
    variances, _directions = principal_components(make_cloud())
    assert np.all(np.diff(variances) <= 0)


def test_the_two_principal_components_are_perpendicular():
    _variances, directions = principal_components(make_cloud())
    assert float(np.dot(directions[:, 0], directions[:, 1])) == pytest.approx(0.0, abs=EXACT)


def test_projections_onto_the_components_are_uncorrelated():
    _variances, directions = principal_components(make_cloud())
    cloud = make_cloud()
    projected = (cloud - cloud.mean(axis=0)) @ directions
    assert abs(float(np.corrcoef(projected.T)[0, 1])) < EXACT


def test_skipping_the_centring_gives_a_confidently_wrong_answer():
    cloud = make_cloud()
    uncentred = (cloud.T @ cloud) / (N_POINTS - 1)
    values, vectors = np.linalg.eigh(uncentred)
    top = vectors[:, int(np.argmax(values))]
    assert abs(direction_degrees(top) - ELONGATION_DEG) > 5.0


def test_eig_and_eigh_agree_on_the_covariance_matrix():
    covariance = covariance_matrix(make_cloud())
    assert np.allclose(
        np.sort(np.linalg.eig(covariance)[0].real),
        np.sort(np.linalg.eigh(covariance)[0]),
        atol=EXACT,
    )
