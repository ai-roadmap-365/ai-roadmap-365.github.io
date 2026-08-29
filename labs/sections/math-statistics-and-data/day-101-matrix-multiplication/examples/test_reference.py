"""The reference suite: real values, real shapes, real exception types.

Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q -p no:cacheprovider

Nothing here asserts a duration. Timings live in 05_cost_and_speed.py, where
they are printed as observations from one machine; a test that asserts a
millisecond figure is a test that fails on somebody else's laptop for no good
reason. The one performance claim made here is a wide margin, and it is in
test_the_gap_is_wide_not_marginal at the foot of the file.
"""

import numpy as np
import pytest

from dataset import (
    ANGLE_A,
    ANGLE_A_B,
    ANGLE_B,
    ANGLE_DEGREES,
    BIAS,
    BIG_CHAIN,
    BIG_LEFT_FIRST,
    BIG_RATIO,
    BIG_RIGHT_FIRST,
    DOT_U,
    DOT_U_U,
    DOT_U_V,
    DOT_U_W,
    DOT_V,
    DOT_W,
    FLIP_AFTER_ROT,
    FLIP_AFTER_ROT_V,
    FLIP_V,
    FLIP_X,
    HIGHLIGHT_CELL,
    HIGHLIGHT_COLUMN,
    HIGHLIGHT_ROW,
    HIGHLIGHT_TERMS,
    HIGHLIGHT_VALUE,
    LAYER_OUT,
    P,
    P_AT_Q,
    P_TIMES_Q,
    Q,
    Q_AT_P,
    ROT90,
    ROT_AFTER_FLIP,
    ROT_AFTER_FLIP_V,
    ROT_TIMES_FLIP_ELEMENTWISE,
    ROT_V,
    SHAPE_CASES,
    SMALL_CHAIN,
    SMALL_LEFT_FIRST,
    SMALL_RIGHT_FIRST,
    U,
    V,
    W,
    X,
    X_AT_U,
    X_AT_XT,
    X_TIMES_U,
    XT_AT_X,
    XW,
)
from matmul import (
    ShapeMismatch,
    add_bias,
    chain_costs,
    dot,
    identity,
    matmul_columns,
    matmul_dots,
    matmul_loops,
    matvec,
    multiplication_count,
    shape,
    transpose,
)

TOL = 1e-12

IMPLEMENTATIONS = [matmul_loops, matmul_dots, matmul_columns]


# -- The dot product ---------------------------------------------------------


def test_dot_multiplies_pairwise_and_adds():
    assert dot(DOT_U, DOT_V) == DOT_U_V == 24


def test_dot_of_a_vector_with_itself_is_its_squared_length():
    assert dot(DOT_U, DOT_U) == DOT_U_U == 25
    assert dot(DOT_U, DOT_U) == pytest.approx(float(np.linalg.norm(DOT_U)) ** 2, abs=1e-9)


def test_dot_is_zero_exactly_when_the_vectors_are_perpendicular():
    assert dot(DOT_U, DOT_W) == DOT_U_W == 0
    cosine = dot(DOT_U, DOT_W) / (np.linalg.norm(DOT_U) * np.linalg.norm(DOT_W))
    assert np.degrees(np.arccos(cosine)) == pytest.approx(90.0, abs=1e-9)


def test_dot_agrees_with_the_geometric_formula_on_a_named_angle():
    """|a| |b| cos(theta) and the pairwise sum are the same number."""
    assert dot(ANGLE_A, ANGLE_B) == ANGLE_A_B == 2
    cosine = dot(ANGLE_A, ANGLE_B) / (np.linalg.norm(ANGLE_A) * np.linalg.norm(ANGLE_B))
    assert np.degrees(np.arccos(cosine)) == pytest.approx(ANGLE_DEGREES, abs=1e-9)
    geometric = np.linalg.norm(ANGLE_A) * np.linalg.norm(ANGLE_B) * cosine
    assert geometric == pytest.approx(dot(ANGLE_A, ANGLE_B), abs=1e-9)


def test_dot_is_commutative_even_though_matrix_multiplication_is_not():
    assert dot(DOT_U, DOT_V) == dot(DOT_V, DOT_U)


def test_dot_refuses_mismatched_lengths():
    with pytest.raises(ShapeMismatch):
        dot([1, 2, 3], [1, 2])


def test_dot_agrees_with_numpy():
    assert dot(DOT_U, DOT_V) == np.dot(DOT_U, DOT_V)
    assert dot(DOT_U, DOT_V) == np.array(DOT_U) @ np.array(DOT_V)


# -- Matrix times vector, as a combination of columns ------------------------


def test_matvec_is_a_weighted_sum_of_the_columns():
    A = [[2, 0], [-1, 1], [0, 4]]
    assert matvec(A, [3, 5]) == [6, 2, 20]


def test_matvec_agrees_with_numpy():
    A = [[2, 0], [-1, 1], [0, 4]]
    assert matvec(A, [3, 5]) == (np.array(A) @ np.array([3, 5])).tolist()


def test_matvec_of_a_basis_vector_returns_that_column():
    """The columns of a matrix ARE the images of the basis vectors."""
    assert matvec(ROT90, [1, 0]) == [0, 1]
    assert matvec(ROT90, [0, 1]) == [-1, 0]
    assert matvec(ROT90, [1, 0]) == [row[0] for row in ROT90]
    assert matvec(ROT90, [0, 1]) == [row[1] for row in ROT90]


def test_matvec_output_length_is_the_row_count():
    A = [[2, 0], [-1, 1], [0, 4]]
    assert shape(A) == (3, 2)
    assert len(matvec(A, [3, 5])) == 3


def test_matvec_refuses_a_vector_of_the_wrong_length():
    with pytest.raises(ShapeMismatch):
        matvec([[2, 0], [-1, 1], [0, 4]], [3, 5, 7])


# -- The three implementations agree with each other and with NumPy ----------


@pytest.mark.parametrize("implementation", IMPLEMENTATIONS)
def test_every_implementation_reproduces_the_hand_worked_product(implementation):
    assert implementation(X, W) == XW


@pytest.mark.parametrize("implementation", IMPLEMENTATIONS)
def test_every_implementation_agrees_with_numpy(implementation):
    assert implementation(X, W) == (np.array(X) @ np.array(W)).tolist()


@pytest.mark.parametrize("m, n, p", [(1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 4), (5, 1, 3), (1, 6, 2)])
def test_all_three_implementations_agree_on_many_shapes(m, n, p):
    rng = np.random.default_rng(m * 100 + n * 10 + p)
    left = rng.integers(-9, 10, size=(m, n)).tolist()
    right = rng.integers(-9, 10, size=(n, p)).tolist()
    expected = (np.array(left) @ np.array(right)).tolist()
    assert matmul_loops(left, right) == expected
    assert matmul_dots(left, right) == expected
    assert matmul_columns(left, right) == expected


def test_the_highlighted_cell_is_row_dotted_with_column():
    i, j = HIGHLIGHT_CELL
    assert [X[i][k] for k in range(3)] == HIGHLIGHT_ROW
    assert [W[k][j] for k in range(3)] == HIGHLIGHT_COLUMN
    assert HIGHLIGHT_TERMS == [X[i][k] * W[k][j] for k in range(3)]
    assert sum(HIGHLIGHT_TERMS) == HIGHLIGHT_VALUE == 13
    assert matmul_loops(X, W)[i][j] == HIGHLIGHT_VALUE


# -- The shape rule ----------------------------------------------------------


@pytest.mark.parametrize("left_shape, right_shape, expected", SHAPE_CASES)
def test_the_shape_rule_predicts_the_result_or_the_failure(left_shape, right_shape, expected):
    rng = np.random.default_rng(sum(left_shape) * 31 + sum(right_shape))
    left = rng.integers(0, 5, size=left_shape)
    right = rng.integers(0, 5, size=right_shape)
    if expected == "error":
        with pytest.raises(ValueError):
            left @ right
        with pytest.raises(ShapeMismatch):
            matmul_loops(left.tolist(), right.tolist())
    else:
        assert (left @ right).shape == expected
        assert shape(matmul_loops(left.tolist(), right.tolist())) == expected


def test_shape_mismatch_is_a_valueerror_so_broad_handlers_still_catch_it():
    assert issubclass(ShapeMismatch, ValueError)
    with pytest.raises(ValueError):
        matmul_loops(X, X)


def test_the_error_message_names_both_shapes_and_the_inner_dimensions():
    with pytest.raises(ShapeMismatch) as caught:
        matmul_loops(X, X)
    message = str(caught.value)
    assert "(2, 3)" in message
    assert "inner dimensions 3 and 2" in message


def test_numpy_raises_valueerror_for_the_same_mismatch():
    with pytest.raises(ValueError) as caught:
        np.array(X) @ np.array(X)
    assert "size 2 is different from 3" in str(caught.value)


def test_the_two_transpose_repairs_give_different_shapes_and_different_answers():
    npX = np.array(X)
    assert (npX @ npX.T).tolist() == X_AT_XT
    assert (npX.T @ npX).tolist() == XT_AT_X
    assert (npX @ npX.T).shape == (2, 2)
    assert (npX.T @ npX).shape == (3, 3)


def test_both_transpose_repairs_are_symmetric():
    npX = np.array(X)
    for repaired in (npX @ npX.T, npX.T @ npX):
        assert np.array_equal(repaired, repaired.T)


# -- Composition and non-commutativity ---------------------------------------


def test_the_product_is_the_composition_for_a_real_vector():
    step = matvec(FLIP_X, V)
    assert step == FLIP_V
    assert matvec(ROT90, step) == ROT_AFTER_FLIP_V
    assert matmul_loops(ROT90, FLIP_X) == ROT_AFTER_FLIP
    assert matvec(ROT_AFTER_FLIP, V) == ROT_AFTER_FLIP_V


def test_the_rightmost_matrix_acts_on_the_vector_first():
    """A @ (B @ v) equals (A @ B) @ v, which is what fixes the order."""
    two_steps = matvec(ROT90, matvec(FLIP_X, V))
    one_step = matvec(matmul_loops(ROT90, FLIP_X), V)
    assert two_steps == one_step == ROT_AFTER_FLIP_V


def test_the_other_order_gives_a_genuinely_different_matrix():
    assert matmul_loops(FLIP_X, ROT90) == FLIP_AFTER_ROT
    assert matmul_loops(ROT90, FLIP_X) != matmul_loops(FLIP_X, ROT90)


def test_the_other_order_sends_the_same_vector_somewhere_else():
    assert matvec(ROT90, V) == ROT_V
    assert matvec(FLIP_X, matvec(ROT90, V)) == FLIP_AFTER_ROT_V
    assert ROT_AFTER_FLIP_V != FLIP_AFTER_ROT_V


def test_non_commutativity_on_a_second_untidy_pair():
    assert matmul_loops(P, Q) == P_AT_Q == [[19, 22], [43, 50]]
    assert matmul_loops(Q, P) == Q_AT_P == [[23, 34], [31, 46]]
    assert P_AT_Q != Q_AT_P


def test_numpy_agrees_that_the_order_matters():
    npP, npQ = np.array(P), np.array(Q)
    assert (npP @ npQ).tolist() == P_AT_Q
    assert (npQ @ npP).tolist() == Q_AT_P
    assert not np.array_equal(npP @ npQ, npQ @ npP)


def test_associativity_holds_on_integers_exactly():
    rng = np.random.default_rng(7)
    A = rng.integers(-5, 6, size=(4, 7))
    B = rng.integers(-5, 6, size=(7, 2))
    C = rng.integers(-5, 6, size=(2, 6))
    assert np.array_equal((A @ B) @ C, A @ (B @ C))


def test_associativity_holds_for_the_from_scratch_implementation_too():
    C = [[1, 1], [0, 2]]
    assert matmul_loops(matmul_loops(ROT90, FLIP_X), C) == matmul_loops(
        ROT90, matmul_loops(FLIP_X, C)
    )


def test_distributivity_over_addition():
    D = [[2, 0], [1, 1]]
    combined = [[FLIP_X[i][j] + D[i][j] for j in range(2)] for i in range(2)]
    left = matmul_loops(ROT90, combined)
    part_one = matmul_loops(ROT90, FLIP_X)
    part_two = matmul_loops(ROT90, D)
    right = [[part_one[i][j] + part_two[i][j] for j in range(2)] for i in range(2)]
    assert left == right


# -- Elementwise versus matrix multiplication --------------------------------


def test_star_and_at_give_different_values_at_the_same_shape():
    npP, npQ = np.array(P), np.array(Q)
    assert (npP * npQ).tolist() == P_TIMES_Q
    assert (npP @ npQ).tolist() == P_AT_Q
    assert (npP * npQ).shape == (npP @ npQ).shape == (2, 2)
    assert not np.array_equal(npP * npQ, npP @ npQ)


def test_star_and_at_give_different_shapes_on_a_matrix_and_a_vector():
    npX, npU = np.array(X), np.array(U)
    assert (npX * npU).shape == (2, 3)
    assert (npX @ npU).shape == (2,)
    assert (npX * npU).tolist() == X_TIMES_U
    assert (npX @ npU).tolist() == X_AT_U


def test_at_is_star_followed_by_a_sum_along_the_last_axis():
    """The one sentence that separates them: `@` sums, `*` does not."""
    npX, npU = np.array(X), np.array(U)
    assert np.array_equal((npX * npU).sum(axis=1), npX @ npU)


def test_the_elementwise_product_of_the_two_transformations_is_all_zeros():
    npA, npB = np.array(ROT90), np.array(FLIP_X)
    assert (npA * npB).tolist() == ROT_TIMES_FLIP_ELEMENTWISE
    assert (npA @ npB).tolist() == ROT_AFTER_FLIP
    assert not np.array_equal(npA * npB, npA @ npB)


def test_dot_matmul_and_the_operator_agree_on_two_dimensional_arrays():
    npX, npW = np.array(X), np.array(W)
    assert np.array_equal(npX @ npW, np.matmul(npX, npW))
    assert np.array_equal(npX @ npW, np.dot(npX, npW))


def test_matmul_and_dot_part_company_on_two_stacks():
    """Checked rather than assumed — they agree on 3-D against 2-D."""
    stack = np.arange(8).reshape(2, 2, 2)
    plain = np.arange(4).reshape(2, 2)
    assert np.matmul(stack, plain).shape == (2, 2, 2)
    assert np.dot(stack, plain).shape == (2, 2, 2)
    assert np.array_equal(np.matmul(stack, plain), np.dot(stack, plain))
    other = np.arange(8).reshape(2, 2, 2)
    assert np.matmul(stack, other).shape == (2, 2, 2)
    assert np.dot(stack, other).shape == (2, 2, 2, 2)


# -- The identity matrix -----------------------------------------------------


def test_identity_is_ones_on_the_diagonal():
    assert identity(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert identity(3) == np.eye(3, dtype=int).tolist()


def test_identity_leaves_a_matrix_alone_from_either_side():
    assert matmul_loops(identity(2), X) == X
    assert matmul_loops(X, identity(3)) == X


def test_the_identity_that_fits_depends_on_the_side():
    """X is (2, 3), so it takes a 2x2 on the left and a 3x3 on the right."""
    with pytest.raises(ShapeMismatch):
        matmul_loops(identity(3), X)
    with pytest.raises(ShapeMismatch):
        matmul_loops(X, identity(2))


def test_identity_leaves_a_vector_alone():
    v = [1.5, -2.0, 0.25]
    assert np.allclose(matvec(identity(3), v), v, atol=TOL)


def test_identity_rejects_a_size_below_one():
    with pytest.raises(ValueError):
        identity(0)


# -- One layer of a neural network -------------------------------------------


def test_the_layer_reproduces_the_hand_worked_output():
    assert (np.array(X) @ np.array(W) + np.array(BIAS)).tolist() == LAYER_OUT


def test_the_layer_from_scratch_matches_the_numpy_version():
    assert add_bias(matmul_loops(X, W), BIAS) == LAYER_OUT


def test_the_bias_is_broadcast_across_rows_not_columns():
    product = np.array(X) @ np.array(W)
    assert product.shape == (2, 2)
    with_bias = product + np.array(BIAS)
    for row in with_bias.tolist():
        assert [row[j] - BIAS[j] for j in range(2)] in product.tolist()


def test_a_bias_of_the_wrong_length_raises():
    product = np.array(X) @ np.array(W)
    with pytest.raises(ValueError) as caught:
        product + np.array([5, -2, 7])
    assert "could not be broadcast" in str(caught.value)
    with pytest.raises(ShapeMismatch):
        add_bias(XW, [5, -2, 7])


def test_growing_the_batch_leaves_the_earlier_rows_unchanged():
    bigger = np.array([[1, 2, 0], [0, 1, 3], [2, 0, 1], [1, 1, 1]])
    out = bigger @ np.array(W) + np.array(BIAS)
    assert out.shape == (4, 2)
    assert out[:2].tolist() == LAYER_OUT


def test_two_layers_without_a_nonlinearity_collapse_into_one():
    npX, npW, npB = np.array(X), np.array(W), np.array(BIAS)
    W2 = np.array([[1, 0, 2], [3, 1, 0]])
    b2 = np.array([0, 1, -1])
    two_layers = (npX @ npW + npB) @ W2 + b2
    collapsed = npX @ (npW @ W2) + (npB @ W2 + b2)
    assert np.array_equal(two_layers, collapsed)


# -- Cost -------------------------------------------------------------------


def test_the_multiplication_count_is_m_times_n_times_p():
    assert multiplication_count(2, 3, 2) == 12
    assert multiplication_count(200, 200, 200) == 8_000_000
    assert multiplication_count(1024, 4096, 4096) == 17_179_869_184


def test_the_small_chain_costs_what_the_hand_count_said():
    assert chain_costs(*SMALL_CHAIN) == (SMALL_LEFT_FIRST, SMALL_RIGHT_FIRST)
    assert SMALL_RIGHT_FIRST // SMALL_LEFT_FIRST == 10


def test_the_adapter_chain_costs_what_the_hand_count_said():
    assert chain_costs(*BIG_CHAIN) == (BIG_LEFT_FIRST, BIG_RIGHT_FIRST)
    assert BIG_RIGHT_FIRST // BIG_LEFT_FIRST == BIG_RATIO == 258


def test_both_associations_of_the_adapter_chain_give_the_same_answer():
    """Cheap and expensive are the same computation, on shapes small enough to run."""
    rng = np.random.default_rng(11)
    batch = rng.integers(0, 4, size=(6, 12))
    down = rng.integers(0, 4, size=(12, 2))
    up = rng.integers(0, 4, size=(2, 12))
    assert np.array_equal((batch @ down) @ up, batch @ (down @ up))


# -- Utilities the rest of the lab leans on ----------------------------------


def test_numpy_integer_products_overflow_silently():
    """NumPy int64 wraps; Python's own integers do not. NumPy is the wrong one.

    Asserted rather than described, including the absence of a warning, because
    "it fails silently" is exactly the kind of claim that rots when a library
    changes. If NumPy ever starts warning here, this test says so.
    """
    import warnings

    big = [[3037000500, 0], [0, 1]]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        wrapped = (np.array(big) @ np.array(big)).tolist()
    exact = matmul_loops(big, big)

    assert exact[0][0] == 3037000500**2 == 9223372037000250000
    assert wrapped[0][0] == -9223372036709301616
    assert wrapped[0][0] < 0 < exact[0][0]
    assert caught == [], "NumPy raised no warning — that is the dangerous part"


def test_shape_rejects_a_ragged_grid():
    with pytest.raises(ValueError):
        shape([[1, 2, 3], [4, 5]])


def test_transpose_swaps_the_shape_and_undoes_itself():
    assert shape(transpose(X)) == (3, 2)
    assert transpose(transpose(X)) == X
    assert transpose(X) == np.array(X).T.tolist()


# -- The one performance claim, stated as a wide margin ----------------------


def test_the_gap_is_wide_not_marginal():
    """No duration is asserted. Only that the loop loses by a large factor.

    The threshold is deliberately far below what was measured while writing
    this lab, so that a slow or busy machine still passes. If this ever fails,
    the interesting question is not the number but why NumPy is not reaching
    BLAS on your installation.
    """
    import time

    rng = np.random.default_rng(2026)
    size = 120
    left = rng.integers(0, 10, size=(size, size)).astype(np.float64)
    right = rng.integers(0, 10, size=(size, size)).astype(np.float64)
    left_lists, right_lists = left.tolist(), right.tolist()

    start = time.perf_counter()
    loop_answer = matmul_loops(left_lists, right_lists)
    loop_seconds = time.perf_counter() - start

    best = float("inf")
    for _ in range(5):
        start = time.perf_counter()
        numpy_answer = left @ right
        best = min(best, time.perf_counter() - start)

    assert np.allclose(np.array(loop_answer), numpy_answer, atol=1e-9)
    assert loop_seconds / best > 50
