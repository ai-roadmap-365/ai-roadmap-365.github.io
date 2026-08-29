"""Your running score. Run from the lab directory:

    .venv/bin/pytest starter -q

A SKIP means "not attempted yet". A FAILURE means "attempted and wrong", and
it prints your answer beside the real one. On an untouched checkout this is
1 passed, 52 skipped. When it says 53 passed, you are finished.

Every float comparison here names its tolerance. Every eigenvector comparison
goes through abs_cosine, because an eigenvector is defined only up to sign and
scale — so if your (1, -2) comes back as (-1, 2), or as (0.447, -0.894), all
three are correct and the tests treat them as equal.
"""

from __future__ import annotations

import numpy as np
import pytest

import answers
import eigen
from dataset import (
    A,
    CENTRE,
    ELONGATION_DEG,
    N_POINTS,
    PROJECTION_ONTO_X,
    REFLECTION_IN_X,
    ROTATION_90,
    SHEAR,
    SPREAD_ALONG,
    SYMMETRIC,
    elongation_direction,
    make_cloud,
    power_method_start,
)

EXACT = 1e-12
TIGHT = 1e-9

#: The known-correct facts, used to check your predictions. Reading this list
#: is of course possible, and equally of course misses the entire point.
TRUE_EIGENVALUES = (5.0, 2.0)
TRUE_EIGENVECTORS = ((1.0, 1.0), (1.0, -2.0))


def written(function):
    """Skip cleanly if the exercise has not been attempted yet."""
    try:
        result = function()
    except NotImplementedError:
        result = NotImplemented
    if result is NotImplemented:
        pytest.skip("not attempted yet — write this function in starter/eigen.py")
    return result


def answered(name):
    """Skip cleanly if this prediction is still None."""
    value = getattr(answers, name)
    if value is None:
        pytest.skip(f"not attempted yet — set {name} in starter/answers.py")
    return value


def test_the_environment_is_ready():
    """The one test that passes on an untouched checkout."""
    assert np.__version__.split(".")[0] >= "2"
    assert A.shape == (2, 2)
    assert make_cloud().shape == (N_POINTS, 2)


# ==========================================================================
# Exercise 1 — the six functions
# ==========================================================================


def test_1a_abs_cosine_on_the_same_line():
    fn = written(lambda: eigen.abs_cosine([1.0, 1.0], [1.0, 1.0]))
    assert fn == pytest.approx(1.0, abs=EXACT)


def test_1a_abs_cosine_ignores_a_sign_flip():
    value = written(lambda: eigen.abs_cosine([1.0, -2.0], [-1.0, 2.0]))
    assert value == pytest.approx(1.0, abs=EXACT), (
        "the sign must not matter: (1, -2) and (-1, 2) name the same line. "
        "Did you take the ABSOLUTE value of the dot product?"
    )


def test_1a_abs_cosine_ignores_scale():
    value = written(lambda: eigen.abs_cosine([1.0, 1.0], [37.5, 37.5]))
    assert value == pytest.approx(1.0, abs=EXACT)


def test_1a_abs_cosine_at_right_angles():
    value = written(lambda: eigen.abs_cosine([1.0, 0.0], [0.0, 1.0]))
    assert value == pytest.approx(0.0, abs=EXACT)


def test_1a_abs_cosine_refuses_the_zero_vector():
    written(lambda: eigen.abs_cosine([1.0, 1.0], [1.0, 1.0]))
    with pytest.raises(ValueError, match="no direction"):
        eigen.abs_cosine([0.0, 0.0], [1.0, 1.0])


def test_1b_characteristic_coefficients():
    value = written(lambda: eigen.characteristic_coefficients(A))
    assert tuple(value) == pytest.approx((7.0, 10.0), abs=EXACT)


def test_1b_characteristic_coefficients_rejects_a_3x3():
    written(lambda: eigen.characteristic_coefficients(A))
    with pytest.raises(ValueError, match="2x2"):
        eigen.characteristic_coefficients(np.eye(3))


def test_1c_eigenvalues_of_a():
    values = written(lambda: eigen.eigenvalues_2x2(A))
    assert sorted(complex(v).real for v in values) == pytest.approx([2.0, 5.0], abs=TIGHT)


def test_1c_eigenvalues_of_a_have_no_imaginary_part():
    values = written(lambda: eigen.eigenvalues_2x2(A))
    assert all(abs(complex(v).imag) < EXACT for v in values)


def test_1c_a_rotation_gives_complex_eigenvalues():
    values = written(lambda: eigen.eigenvalues_2x2(ROTATION_90))
    assert all(abs(complex(v).imag) > 0.5 for v in values), (
        "a 90-degree rotation has NO real eigenvalues. Did you use "
        "numpy.emath.sqrt rather than numpy.sqrt?"
    )


def test_1c_matches_numpy():
    values = written(lambda: eigen.eigenvalues_2x2(A))
    mine = sorted(complex(v).real for v in values)
    theirs = sorted(np.linalg.eig(A)[0].real)
    assert mine == pytest.approx(theirs, abs=TIGHT)


@pytest.mark.parametrize("eigenvalue,expected", list(zip(TRUE_EIGENVALUES, TRUE_EIGENVECTORS)))
def test_1d_eigenvector_lies_on_the_right_line(eigenvalue, expected):
    v = written(lambda: eigen.eigenvector_2x2(A, eigenvalue))
    cosine = abs(float(np.dot(v, expected))) / (
        float(np.linalg.norm(v)) * float(np.linalg.norm(expected))
    )
    assert cosine == pytest.approx(1.0, abs=TIGHT), (
        f"for lambda = {eigenvalue} you returned {np.asarray(v).tolist()}, which is not "
        f"on the same line as {list(expected)}"
    )


@pytest.mark.parametrize("eigenvalue", TRUE_EIGENVALUES)
def test_1d_eigenvector_satisfies_the_equation(eigenvalue):
    v = written(lambda: eigen.eigenvector_2x2(A, eigenvalue))
    assert np.allclose(A @ np.asarray(v), eigenvalue * np.asarray(v), atol=TIGHT)


def test_1d_eigenvector_is_unit_length():
    v = written(lambda: eigen.eigenvector_2x2(A, 5.0))
    assert float(np.linalg.norm(v)) == pytest.approx(1.0, abs=TIGHT)


def test_1e_power_method_converges():
    result = written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    assert result["converged"] is True
    assert result["iterations"] == 25, (
        f"expected 25 iterations to reach 1e-10, got {result['iterations']}. "
        "Check that you normalise BEFORE measuring the change, and that you "
        "align the signs."
    )


def test_1e_power_method_finds_the_dominant_line():
    result = written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    v = np.asarray(result["vector"], dtype=float)
    cosine = abs(float(np.dot(v, [1.0, 1.0]))) / (float(np.linalg.norm(v)) * np.sqrt(2.0))
    assert cosine == pytest.approx(1.0, abs=1e-10)


def test_1e_power_method_finds_the_dominant_eigenvalue():
    result = written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    assert float(result["eigenvalue"]) == pytest.approx(5.0, abs=TIGHT)


def test_1e_power_method_works_from_many_starts():
    written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    rng = np.random.default_rng(99)
    for _ in range(6):
        result = eigen.power_method(A, rng.normal(size=2), tol=1e-10)
        v = np.asarray(result["vector"], dtype=float)
        cosine = abs(float(np.dot(v, [1.0, 1.0]))) / (float(np.linalg.norm(v)) * np.sqrt(2.0))
        assert cosine == pytest.approx(1.0, abs=1e-10)


def test_1e_power_method_handles_a_negative_dominant_eigenvalue():
    """[[-5, 0], [0, 2]] has dominant eigenvalue -5, so the raw iteration
    flips sign every step. Without the sign alignment this never converges."""
    written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    result = eigen.power_method(np.diag([-5.0, 2.0]), np.array([0.6, 0.8]), tol=1e-10)
    assert result["converged"] is True, (
        "the dominant eigenvalue is negative, so w flips sign every step. "
        "Negate w when numpy.dot(w, v) < 0."
    )
    assert float(result["eigenvalue"]) == pytest.approx(-5.0, abs=TIGHT)


def test_1e_power_method_refuses_the_zero_vector():
    written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    with pytest.raises(ValueError, match="zero vector"):
        eigen.power_method(A, np.zeros(2))


def test_1e_power_method_reports_failure_rather_than_lying():
    written(lambda: eigen.power_method(A, power_method_start(), tol=1e-10))
    result = eigen.power_method(A, power_method_start(), tol=1e-16, max_iter=5)
    assert result["converged"] is False


def test_1f_covariance_matches_numpy():
    cloud = make_cloud()
    mine = written(lambda: eigen.covariance_matrix(cloud))
    assert np.allclose(mine, np.cov(cloud, rowvar=False), atol=EXACT), (
        "if this is close but not equal, check that you divided by (n - 1) "
        "and not by n; if it is far out, check that you subtracted the mean"
    )


def test_1f_covariance_is_symmetric():
    mine = written(lambda: eigen.covariance_matrix(make_cloud()))
    assert np.allclose(mine, np.asarray(mine).T, atol=1e-15)


def test_1f_covariance_rejects_a_1d_array():
    written(lambda: eigen.covariance_matrix(make_cloud()))
    with pytest.raises(ValueError, match="2-D"):
        eigen.covariance_matrix(np.array([1.0, 2.0, 3.0]))


# ==========================================================================
# Exercise 2 — the hand solution
# ==========================================================================


def test_2a_trace():
    assert answered("TRACE_OF_A") == 7


def test_2b_determinant():
    assert answered("DETERMINANT_OF_A") == 10


def test_2c_characteristic_coefficients():
    assert tuple(answered("CHARACTERISTIC_COEFFICIENTS")) == (7, 10)


def test_2d_discriminant():
    assert answered("DISCRIMINANT") == 9


def test_2e_eigenvalues():
    assert tuple(answered("EIGENVALUES_LARGEST_FIRST")) == (5, 2)


def test_2f_eigenvector_for_the_larger_eigenvalue():
    v = np.asarray(answered("EIGENVECTOR_FOR_LARGER"), dtype=float)
    assert np.allclose(A @ v, 5.0 * v, atol=TIGHT), (
        f"A @ {v.tolist()} is {(A @ v).tolist()}, which is not 5 times {v.tolist()}"
    )


def test_2g_eigenvector_for_the_smaller_eigenvalue():
    v = np.asarray(answered("EIGENVECTOR_FOR_SMALLER"), dtype=float)
    assert np.allclose(A @ v, 2.0 * v, atol=TIGHT), (
        f"A @ {v.tolist()} is {(A @ v).tolist()}, which is not 2 times {v.tolist()}"
    )


# ==========================================================================
# Exercise 3 — the standard transformations
# ==========================================================================


def test_3a_shear_has_one_eigen_line():
    assert answered("SHEAR_EIGEN_LINE_COUNT") == 1, (
        "numpy.linalg.eig returns two COLUMNS for the shear, but check whether "
        "they point along different lines"
    )
    values, vectors = np.linalg.eig(SHEAR)
    cosine = abs(float(np.dot(vectors.real[:, 0], vectors.real[:, 1])))
    assert cosine == pytest.approx(1.0, abs=1e-8)


def test_3b_rotation_eigenvalues_are_not_real():
    assert answered("ROTATION_EIGENVALUES_ARE_REAL") is False
    assert np.all(np.abs(np.linalg.eig(ROTATION_90)[0].imag) > 0.5)


def test_3c_rotation_eigenvalue_magnitude():
    assert float(answered("ROTATION_EIGENVALUE_MAGNITUDE")) == pytest.approx(1.0, abs=TIGHT)


def test_3d_eig_dtype_on_a_real_matrix():
    predicted = answered("EIG_DTYPE_ON_A")
    observed = str(np.linalg.eig(A)[0].dtype)
    assert predicted == observed, (
        f"you predicted {predicted!r}; numpy {np.__version__} on this machine "
        f"returned {observed!r}. Both eigenvalues are real and it still handed "
        "back complex. Its own docstring says otherwise. When documentation "
        "and measurement disagree, the measurement wins."
    )


def test_3e_projection_determinant_and_smallest_eigenvalue():
    pair = tuple(float(x) for x in answered("PROJECTION_DET_AND_SMALLEST_EIGENVALUE"))
    assert pair == pytest.approx((0.0, 0.0), abs=TIGHT)
    assert float(np.linalg.det(PROJECTION_ONTO_X)) == pytest.approx(0.0, abs=EXACT)
    assert float(np.min(np.linalg.eig(PROJECTION_ONTO_X)[0].real)) == pytest.approx(0.0, abs=TIGHT)


def test_3f_reflection_eigenvalues():
    assert tuple(answered("REFLECTION_EIGENVALUES")) == (1, -1)
    assert np.sort(np.linalg.eig(REFLECTION_IN_X)[0].real) == pytest.approx([-1.0, 1.0], abs=TIGHT)


def test_3g_symmetric_eigenvectors_are_perpendicular():
    assert float(answered("SYMMETRIC_EIGENVECTOR_ANGLE_DEG")) == pytest.approx(90.0, abs=TIGHT)
    vectors = np.linalg.eigh(SYMMETRIC)[1]
    assert float(np.dot(vectors[:, 0], vectors[:, 1])) == pytest.approx(0.0, abs=EXACT)


# ==========================================================================
# Exercise 4 — the power method
# ==========================================================================


def test_4a_which_eigenvalue():
    assert float(answered("POWER_METHOD_FINDS_EIGENVALUE")) == pytest.approx(5.0, abs=TIGHT)


def test_4b_which_direction():
    assert float(answered("POWER_METHOD_FINDS_DIRECTION_DEG")) == pytest.approx(45.0, abs=1e-6)


def test_4c_convergence_ratio():
    assert float(answered("CONVERGENCE_RATIO")) == pytest.approx(0.4, abs=1e-6), (
        "the surviving error is the second eigenvector's share, which shrinks "
        "relative to the first by |lambda2 / lambda1| every round"
    )


def test_4d_close_eigenvalues_are_slower():
    assert answered("CLOSE_EIGENVALUES_NEED") == "more"


def test_4e_unnormalised_length():
    assert answered("UNNORMALISED_LENGTH_BEHAVIOUR") == "overflows to inf"
    v = power_method_start()
    with np.errstate(over="ignore"):
        for _ in range(600):
            v = A @ v
    assert not np.all(np.isfinite(v))


# ==========================================================================
# Exercise 5 — PCA
# ==========================================================================


def test_5a_covariance_shape():
    assert tuple(answered("COVARIANCE_SHAPE")) == (2, 2)


def test_5b_covariance_is_symmetric():
    assert answered("COVARIANCE_IS_SYMMETRIC") is True


def test_5c_top_component_direction():
    predicted = float(answered("TOP_COMPONENT_DIRECTION_DEG"))
    assert predicted == pytest.approx(ELONGATION_DEG, abs=1.0)


def test_5d_sqrt_of_the_top_eigenvalue():
    predicted = float(answered("SQRT_OF_TOP_EIGENVALUE"))
    assert predicted == pytest.approx(SPREAD_ALONG, abs=0.5)


def test_5e_right_routine_for_a_covariance_matrix():
    assert answered("RIGHT_ROUTINE_FOR_COVARIANCE") == "eigh", (
        "a covariance matrix is symmetric by construction, and eigh is the "
        "routine written for symmetric input: real dtype, sorted values, and "
        "measurably faster"
    )


def test_5f_allclose_says_false_on_a_correct_answer():
    assert answered("ALLCLOSE_ON_THE_CORRECT_COMPONENT") is False, (
        "the answer is correct and numpy.allclose still says False, because "
        "eigh returned the reversed sign. An eigenvector names an AXIS, not "
        "an arrow. This is the trap the whole lab is built around."
    )
    cloud = make_cloud()
    centred = cloud - cloud.mean(axis=0)
    covariance = (centred.T @ centred) / (N_POINTS - 1)
    values, vectors = np.linalg.eigh(covariance)
    top = vectors[:, int(np.argmax(values))]
    truth = elongation_direction()
    assert not np.allclose(top, truth, atol=1e-3)
    assert abs(float(np.dot(top, truth))) > 0.999


def test_5g_forgetting_to_centre_is_not_survivable():
    assert answered("UNCENTRED_STILL_CORRECT") is False
    cloud = make_cloud()
    uncentred = (cloud.T @ cloud) / (N_POINTS - 1)
    values, vectors = np.linalg.eigh(uncentred)
    top = vectors[:, int(np.argmax(values))]
    angle = float(np.degrees(np.arctan2(top[1], top[0])) % 180.0)
    assert abs(angle - ELONGATION_DEG) > 5.0
    assert np.allclose(cloud.mean(axis=0), CENTRE, atol=0.2)
