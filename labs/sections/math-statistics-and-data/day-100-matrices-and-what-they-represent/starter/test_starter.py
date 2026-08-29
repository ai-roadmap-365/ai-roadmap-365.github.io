"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Float comparisons use numpy.allclose with atol=TOL, stated below.
"""

import numpy as np
import pytest

import answers
from matrix import Matrix, ShapeMismatch

TOL = 1e-12

RECIPES = [
    [2, 4, 1, 3],
    [0, 5, 2, 7],
    [6, 1, 4, 2],
]
PRICE_PER_LITRE = [10, 2, 5, 1]


def written(fn, *args, **kwargs):
    """Run part of your Matrix, or skip the test if it is not written yet."""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")


def predicted(name):
    """Read one prediction from answers.py, or skip if it is still None."""
    value = getattr(answers, name)
    if value is None:
        pytest.skip(f"answers.{name} is still unanswered")
    return value


@pytest.fixture
def M():
    return np.array(RECIPES)


@pytest.fixture
def A():
    return Matrix(RECIPES)


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    assert np.__version__, "numpy is importable"
    # The constructor is written for you, and it already refuses a ragged grid:
    # a matrix is rectangular, and that is not a detail you get to skip.
    with pytest.raises(ValueError):
        Matrix([[1, 2, 3], [4, 5]])


# -- Exercise 1: your Matrix ------------------------------------------------


def test_1_1_shape(A):
    assert written(lambda: A.shape) == (3, 4)


def test_1_2_indexing(A):
    assert written(lambda: A[0, 0]) == 2
    assert A[1, 3] == 7
    assert A[2, 3] == 2


def test_1_2_index_errors_name_the_shape(A):
    written(lambda: A[0, 0])
    with pytest.raises(IndexError) as caught:
        A[3, 0]
    assert "shape (3, 4)" in str(caught.value)
    with pytest.raises(IndexError):
        A[0, -1]


def test_1_2_indexing_with_one_number_is_a_TypeError(A):
    written(lambda: A[0, 0])
    with pytest.raises(TypeError):
        A[0]


def test_1_3_transpose(A, M):
    assert written(lambda: A.T.shape) == (4, 3)
    assert A.T.to_lists() == M.T.tolist()
    assert A.T.T == A


def test_1_4_addition(A, M):
    B = Matrix([[1, 0, 0, 1], [2, 2, 2, 2], [0, 3, 0, 3]])
    assert written(lambda: (A + B).to_lists()) == (M + np.array(B.to_lists())).tolist()


def test_1_4_addition_rejects_a_shape_mismatch(A):
    written(lambda: A.add(A))
    with pytest.raises(ShapeMismatch):
        A.add(Matrix([[1, 2], [3, 4]]))
    with pytest.raises(ValueError):
        A.add(Matrix([[1, 2], [3, 4]]))


def test_1_4_addition_refuses_a_plain_list(A):
    written(lambda: A.add(A))
    with pytest.raises(TypeError) as caught:
        A.add([100, 200, 300, 400])
    assert "broadcasting" in str(caught.value)


def test_1_5_scale(A, M):
    assert written(lambda: (A * 3).to_lists()) == (M * 3).tolist()
    assert (3 * A).to_lists() == (M * 3).tolist()


def test_1_6_identity():
    assert written(Matrix.identity, 3).to_lists() == np.eye(3, dtype=int).tolist()
    v = [1.5, -2.0, 0.25]
    assert np.allclose(Matrix.identity(3).apply_to(v), v, atol=TOL)


# -- Exercise 2: shape and the three meanings -------------------------------


def test_2_1_shape_of_M(M):
    assert predicted("SHAPE_OF_M") == M.shape


def test_2_2_shape_of_transpose(M):
    assert predicted("SHAPE_OF_M_T") == M.T.shape


def test_2_3_alpine_row(M):
    assert predicted("ALPINE_ROW") == M[2].tolist()


def test_2_4_grit_column(M):
    assert predicted("GRIT_COLUMN") == M[:, 2].tolist()


def test_2_5_cost_per_bag(M):
    real = (M * np.array(PRICE_PER_LITRE)).sum(axis=1)
    assert predicted("COST_PER_BAG_PENCE") == real.tolist()


def test_2_6_transformed_vector_length(M):
    real = (M * np.array(PRICE_PER_LITRE)).sum(axis=1)
    assert predicted("LENGTH_OF_TRANSFORMED_VECTOR") == len(real)


# -- Exercise 3: views and copies -------------------------------------------


def test_3_1_writing_through_a_reshape(M):
    guess = predicted("M_00_AFTER_WRITING_THROUGH_RESHAPE")
    flat = M.reshape(12)
    flat[0] = 99
    assert guess == M[0, 0]


def test_3_2_writing_through_a_copy(M):
    guess = predicted("M_00_AFTER_WRITING_THROUGH_A_COPY")
    independent = M.copy().reshape(12)
    independent[0] = 99
    assert guess == M[0, 0]


def test_3_3_slice_shares_memory(M):
    assert predicted("SLICE_SHARES_MEMORY") == np.shares_memory(M, M[:, 2])


def test_3_4_fancy_index_shares_memory(M):
    assert predicted("FANCY_INDEX_SHARES_MEMORY") == np.shares_memory(M, M[[0, 2]])


def test_3_5_transpose_shares_memory(M):
    assert predicted("TRANSPOSE_SHARES_MEMORY") == np.shares_memory(M, M.T)


# -- Exercise 4: broadcasting -----------------------------------------------


def _outcome(left, right):
    try:
        return np.broadcast_shapes(left, right)
    except ValueError:
        return "error"


@pytest.mark.parametrize(
    "name, left, right",
    [
        ("BROADCAST_3x4_WITH_4", (3, 4), (4,)),
        ("BROADCAST_3x4_WITH_3", (3, 4), (3,)),
        ("BROADCAST_3x4_WITH_3x1", (3, 4), (3, 1)),
        ("BROADCAST_3x1_WITH_1x4", (3, 1), (1, 4)),
    ],
)
def test_4_broadcast_outcomes(name, left, right):
    assert predicted(name) == _outcome(left, right)


def test_4_5_failure_exception_class(M):
    guess = predicted("BROADCAST_FAILURE_EXCEPTION")
    with pytest.raises(guess):
        M + np.array([100, 200, 300])


# -- Exercise 5: axes -------------------------------------------------------


def test_5_1_shape_of_sum_axis_0(M):
    assert predicted("SHAPE_OF_SUM_AXIS_0") == M.sum(axis=0).shape


def test_5_2_shape_of_sum_axis_1(M):
    assert predicted("SHAPE_OF_SUM_AXIS_1") == M.sum(axis=1).shape


def test_5_3_axis_for_litres_per_bag(M):
    axis = predicted("AXIS_FOR_LITRES_PER_BAG")
    assert M.sum(axis=axis).tolist() == [10, 14, 13]


def test_5_4_axis_for_litres_per_ingredient(M):
    axis = predicted("AXIS_FOR_LITRES_PER_INGREDIENT")
    assert M.sum(axis=axis).tolist() == [8, 10, 7, 12]


def test_5_5_the_two_totals(M):
    assert predicted("LITRES_PER_BAG") == M.sum(axis=1).tolist()
    assert predicted("LITRES_PER_INGREDIENT") == M.sum(axis=0).tolist()


def test_5_6_keepdims_shape(M):
    assert predicted("SHAPE_OF_SUM_AXIS_1_KEEPDIMS") == M.sum(axis=1, keepdims=True).shape
