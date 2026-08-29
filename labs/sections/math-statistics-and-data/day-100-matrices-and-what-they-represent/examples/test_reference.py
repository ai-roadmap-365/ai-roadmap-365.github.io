"""The reference test suite: real values, real shapes, one stated tolerance.

Run from the lab directory:

    .venv/bin/pytest examples

Every float comparison here goes through numpy.allclose with atol=TOL below.
Integer and shape comparisons are exact, because there is nothing to round.
"""

import numpy as np
import pytest

from dataset import (
    COST_PER_BAG_PENCE,
    INGREDIENT_NAMES,
    LITRES_PER_BAG,
    LITRES_PER_INGREDIENT,
    MIX_NAMES,
    PRICE_PER_LITRE,
    RECIPES,
)
from matrix import Matrix, ShapeMismatch

# The stated tolerance. 1e-12 is far tighter than any error these numbers can
# accumulate — they are small integers and exact halves — and stating it is
# the point: a float comparison without a declared tolerance is a guess.
TOL = 1e-12


@pytest.fixture
def M():
    """A fresh (3, 4) array every test, because several tests mutate views."""
    return np.array(RECIPES)


@pytest.fixture
def A():
    return Matrix(RECIPES)


# --------------------------------------------------------------------------
# 1. The from-scratch class, asserted against NumPy
# --------------------------------------------------------------------------


def test_shape_is_rows_then_columns(A, M):
    assert A.shape == (3, 4)
    assert A.shape == M.shape
    assert A.n_rows == 3 and A.n_cols == 4
    assert M.ndim == 2 and M.size == 12


def test_indexing_counts_from_zero(A, M):
    assert A[0, 0] == 2 and M[0, 0] == 2
    assert A[2, 3] == 2 and M[2, 3] == 2
    assert A[1, 3] == 7 and M[1, 3] == 7


def test_indexing_out_of_range_is_an_IndexError(A):
    with pytest.raises(IndexError) as caught:
        A[3, 0]
    assert "shape (3, 4)" in str(caught.value)


def test_indexing_with_a_single_number_is_rejected(A):
    with pytest.raises(TypeError):
        A[0]


def test_rows_and_columns_agree_with_numpy(A, M):
    assert A.row(1) == M[1].tolist() == [0, 5, 2, 7]
    assert A.col(1) == M[:, 1].tolist() == [4, 5, 1]


def test_transpose_swaps_the_axes(A, M):
    assert A.T.shape == (4, 3) == M.T.shape
    assert A.T.to_lists() == M.T.tolist()
    assert A.T.T == A


def test_addition_is_elementwise(A, M):
    B = Matrix([[1, 0, 0, 1], [2, 2, 2, 2], [0, 3, 0, 3]])
    npB = np.array(B.to_lists())
    assert (A + B).to_lists() == (M + npB).tolist()
    assert (A + B)[0, 0] == 3


def test_addition_of_different_shapes_raises(A):
    with pytest.raises(ShapeMismatch):
        A.add(Matrix([[1, 2], [3, 4]]))
    # And, because ShapeMismatch subclasses ValueError, this catches it too —
    # which is the same exception type NumPy raises for the same mistake.
    with pytest.raises(ValueError):
        A.add(Matrix([[1, 2], [3, 4]]))


def test_scalar_multiplication_from_both_sides(A, M):
    assert (A * 3).to_lists() == (M * 3).tolist()
    assert (3 * A).to_lists() == (3 * M).tolist()
    assert (A * 0).to_lists() == Matrix.zeros(3, 4).to_lists()


def test_identity_and_diagonal_match_numpy():
    assert Matrix.identity(3).to_lists() == np.eye(3, dtype=int).tolist()
    assert Matrix.diagonal([2, 5, 1]).to_lists() == np.diag([2, 5, 1]).tolist()


def test_symmetry(A):
    S = Matrix([[1, 7, 3], [7, 4, 0], [3, 0, 9]])
    assert S.is_symmetric()
    assert S.to_lists() == S.T.to_lists()
    assert not A.is_symmetric(), "a (3, 4) matrix is not square, so not symmetric"


def test_identity_leaves_a_vector_alone():
    v = [1.5, -2.0, 0.25]
    assert np.allclose(Matrix.identity(3).apply_to(v), v, atol=TOL)


def test_from_scratch_class_cannot_broadcast(A):
    with pytest.raises(TypeError):
        A.add([100, 200, 300, 400])


# --------------------------------------------------------------------------
# 2. One matrix, three meanings
# --------------------------------------------------------------------------


def test_meaning_one_table_rows_are_items_columns_are_features(M):
    assert M.shape == (len(MIX_NAMES), len(INGREDIENT_NAMES))
    assert M[MIX_NAMES.index("Alpine")].tolist() == [6, 1, 4, 2]
    assert M[:, INGREDIENT_NAMES.index("grit")].tolist() == [1, 2, 4]


def test_meaning_two_rows_and_columns_are_different_vector_sets(M):
    row_norms = np.linalg.norm(M, axis=1)
    col_norms = np.linalg.norm(M, axis=0)
    assert row_norms.shape == (3,)
    assert col_norms.shape == (4,)
    # Seedling row: sqrt(2^2 + 4^2 + 1^2 + 3^2) = sqrt(30), by hand.
    assert np.allclose(row_norms[0], np.sqrt(30.0), atol=TOL)
    # base column: sqrt(2^2 + 0^2 + 6^2) = sqrt(40), by hand.
    assert np.allclose(col_norms[0], np.sqrt(40.0), atol=TOL)


def test_meaning_three_transformation_consumes_columns_returns_rows(M):
    prices = np.array(PRICE_PER_LITRE)
    out = (M * prices).sum(axis=1)
    assert out.shape == (3,)
    assert out.tolist() == COST_PER_BAG_PENCE == [36, 27, 84]


def test_the_from_scratch_transformation_agrees(M):
    assert Matrix(RECIPES).apply_to(PRICE_PER_LITRE) == COST_PER_BAG_PENCE
    assert np.allclose(
        Matrix(RECIPES).apply_to(PRICE_PER_LITRE),
        (M * np.array(PRICE_PER_LITRE)).sum(axis=1),
        atol=TOL,
    )


def test_a_transformation_rejects_a_vector_of_the_wrong_length():
    with pytest.raises(ShapeMismatch):
        Matrix(RECIPES).apply_to([1, 2, 3])


# --------------------------------------------------------------------------
# 3. Views and copies
# --------------------------------------------------------------------------


def test_reshape_returns_a_view_and_mutation_travels(M):
    flat = M.reshape(12)
    assert flat.tolist() == [2, 4, 1, 3, 0, 5, 2, 7, 6, 1, 4, 2]
    assert np.shares_memory(M, flat)
    assert flat.base is M
    flat[0] = 99
    assert M[0, 0] == 99, "writing through the view changed the original"


def test_copy_breaks_the_link(M):
    independent = M.copy().reshape(12)
    independent[0] = 99
    assert M[0, 0] == 2
    assert not np.shares_memory(M, independent)


def test_base_is_not_the_test_for_independence(M):
    """`.base is None` is False here, and the array is still independent."""
    independent = M.copy().reshape(12)
    assert independent.base is not None, "base points at the anonymous copy"
    assert not np.shares_memory(M, independent)


def test_a_slice_is_a_view(M):
    column = M[:, 2]
    assert column.tolist() == [1, 2, 4]
    assert np.shares_memory(M, column)
    column[0] = 50
    assert M[0, 2] == 50


def test_fancy_indexing_copies(M):
    picked = M[[0, 2]]
    assert picked.shape == (2, 4)
    assert not np.shares_memory(M, picked)
    picked[0, 0] = 77
    assert M[0, 0] == 2


def test_ravel_views_and_flatten_copies(M):
    assert np.shares_memory(M, M.ravel())
    assert not np.shares_memory(M, M.flatten())
    assert M.ravel().tolist() == M.flatten().tolist()


def test_transpose_is_a_view(M):
    t = M.T
    assert np.shares_memory(M, t)
    t[0, 0] = 42
    assert M[0, 0] == 42


def test_impossible_reshape_raises(M):
    with pytest.raises(ValueError):
        M.reshape(5, 3)


def test_minus_one_infers_the_missing_dimension(M):
    assert M.reshape(6, -1).shape == (6, 2)
    assert M.reshape(-1).shape == (12,)


# --------------------------------------------------------------------------
# 4. Broadcasting
# --------------------------------------------------------------------------


def test_broadcasting_a_row_vector_across_every_row(M):
    prices = np.array(PRICE_PER_LITRE)
    scaled = M * prices
    assert scaled.shape == (3, 4)
    assert scaled[0].tolist() == [20, 8, 5, 3]
    assert scaled[1].tolist() == [0, 10, 10, 7]
    assert scaled[2].tolist() == [60, 2, 20, 2]


def test_broadcasting_copies_nothing():
    prices = np.array(PRICE_PER_LITRE)
    stretched = np.broadcast_to(prices, (3, 4))
    assert stretched.shape == (3, 4)
    assert np.shares_memory(stretched, prices)
    assert stretched.flags.writeable is False


def test_broadcasting_failure_is_a_ValueError(M):
    with pytest.raises(ValueError) as caught:
        M + np.array([100, 200, 300])
    assert "could not be broadcast together" in str(caught.value)


def test_the_failure_is_fixed_by_naming_the_axis(M):
    column = np.array([100, 200, 300]).reshape(3, 1)
    result = M + column
    assert result.shape == (3, 4)
    assert result[0].tolist() == [102, 104, 101, 103]
    assert result[2].tolist() == [306, 301, 304, 302]


def test_broadcast_shapes_predicts_both_outcomes():
    assert np.broadcast_shapes((3, 4), (4,)) == (3, 4)
    assert np.broadcast_shapes((3, 4), (3, 1)) == (3, 4)
    assert np.broadcast_shapes((3, 1), (1, 4)) == (3, 4)
    with pytest.raises(ValueError):
        np.broadcast_shapes((3, 4), (3,))


def test_the_square_matrix_trap_is_silent_and_wrong():
    S = np.array(
        [
            [1.0, 2.0, 3.0, 4.0],
            [10.0, 20.0, 30.0, 40.0],
            [100.0, 200.0, 300.0, 400.0],
            [1000.0, 2000.0, 3000.0, 4000.0],
        ]
    )
    wrong = S - S.mean(axis=1)
    right = S - S.mean(axis=1, keepdims=True)
    # Both have the same shape. Only one is what was meant.
    assert wrong.shape == right.shape == (4, 4)
    assert not np.allclose(wrong, right, atol=TOL)
    # Row-centred data must have every ROW summing to zero.
    assert np.allclose(right.sum(axis=1), np.zeros(4), atol=1e-9)
    assert not np.allclose(wrong.sum(axis=1), np.zeros(4), atol=1e-9)
    # Concretely: the silent version subtracted ROW j's mean from COLUMN j.
    # Row 0's mean is 2.5, so the whole of column 0 lost 2.5.
    assert np.allclose(S.mean(axis=1), [2.5, 25.0, 250.0, 2500.0], atol=TOL)
    assert np.allclose(wrong[2, 0], 100.0 - 2.5, atol=TOL)
    assert np.allclose(right[2, 0], 100.0 - 250.0, atol=TOL)


def test_the_same_mistake_on_a_non_square_matrix_is_loud(M):
    with pytest.raises(ValueError):
        M - M.mean(axis=1)


# --------------------------------------------------------------------------
# 5. Axes
# --------------------------------------------------------------------------


def test_axis_zero_collapses_the_rows(M):
    total = M.sum(axis=0)
    assert total.shape == (4,)
    assert total.tolist() == LITRES_PER_INGREDIENT == [8, 10, 7, 12]


def test_axis_one_collapses_the_columns(M):
    total = M.sum(axis=1)
    assert total.shape == (3,)
    assert total.tolist() == LITRES_PER_BAG == [10, 14, 13]


def test_no_axis_collapses_everything(M):
    assert M.sum() == 37
    assert M.sum(axis=0).sum() == M.sum(axis=1).sum() == 37
    assert np.shape(M.sum()) == ()


def test_means_along_each_axis(M):
    assert np.allclose(M.mean(axis=0), [8 / 3, 10 / 3, 7 / 3, 4.0], atol=TOL)
    assert np.allclose(M.mean(axis=1), [2.5, 3.5, 3.25], atol=TOL)


def test_argmax_returns_positions_not_values(M):
    assert np.argmax(M, axis=0).tolist() == [2, 1, 2, 1]
    assert np.argmax(M, axis=1).tolist() == [1, 3, 0]
    assert INGREDIENT_NAMES[np.argmax(M, axis=1)[2]] == "base"


def test_keepdims_leaves_a_one_where_the_axis_was(M):
    assert M.sum(axis=0, keepdims=True).shape == (1, 4)
    assert M.sum(axis=1, keepdims=True).shape == (3, 1)


def test_keepdims_is_what_makes_row_normalisation_work(M):
    share = M / M.sum(axis=1, keepdims=True)
    assert share.shape == (3, 4)
    assert np.allclose(share.sum(axis=1), np.ones(3), atol=TOL)
    # Seedling is 2 of 10 litres base, so exactly 0.2.
    assert np.allclose(share[0, 0], 0.2, atol=TOL)
