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
from matmul import ShapeMismatch, shape, transpose

TOL = 1e-12

X = [[1, 2, 0], [0, 1, 3]]
W = [[2, 0], [-1, 1], [0, 4]]
BIAS = [5, -2]
U = [10, 2, 5]
P = [[1, 2], [3, 4]]
Q = [[5, 6], [7, 8]]
ROT90 = [[0, -1], [1, 0]]
FLIP_X = [[1, 0], [0, -1]]
V = [3, 1]


def written(fn, *args, **kwargs):
    """Run part of your work, or skip the test if it is not written yet."""
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


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    assert np.__version__, "numpy is importable"
    # Written for you, and already refusing a ragged grid: a matrix is
    # rectangular, and that is not a detail you get to skip.
    with pytest.raises(ValueError):
        shape([[1, 2, 3], [4, 5]])
    assert transpose(X) == np.array(X).T.tolist()
    assert issubclass(ShapeMismatch, ValueError)


# -- Exercise 1.1: the dot product -------------------------------------------


def test_1_1_dot_multiplies_pairwise_and_adds():
    from matmul import dot

    assert written(dot, [3, 4], [4, 3]) == 24
    assert dot([3, 4], [3, 4]) == 25
    assert dot([3, 4], [-4, 3]) == 0


def test_1_1_dot_agrees_with_numpy_on_longer_vectors():
    from matmul import dot

    written(dot, [1], [1])
    rng = np.random.default_rng(3)
    for _ in range(5):
        a = rng.integers(-9, 10, size=7)
        b = rng.integers(-9, 10, size=7)
        assert dot(a.tolist(), b.tolist()) == int(np.dot(a, b))


def test_1_1_dot_refuses_mismatched_lengths():
    from matmul import dot

    written(dot, [1], [1])
    with pytest.raises(ShapeMismatch):
        dot([1, 2, 3], [1, 2])


# -- Exercise 1.2: the shape rule --------------------------------------------


def test_1_2_check_multipliable_returns_m_n_p():
    from matmul import check_multipliable

    assert written(check_multipliable, X, W) == (2, 3, 2)
    assert check_multipliable(W, X) == (3, 2, 3)


def test_1_2_check_multipliable_rejects_a_mismatch():
    from matmul import check_multipliable

    written(check_multipliable, X, W)
    with pytest.raises(ShapeMismatch):
        check_multipliable(X, X)


def test_1_2_the_message_names_both_shapes_and_the_inner_dimensions():
    from matmul import check_multipliable

    written(check_multipliable, X, W)
    with pytest.raises(ShapeMismatch) as caught:
        check_multipliable(X, X)
    message = str(caught.value)
    assert "(2, 3)" in message, "the message should name the shapes"
    assert "inner dimensions 3 and 2" in message, "and the two numbers that disagreed"


# -- Exercise 1.3: three nested loops ----------------------------------------


def test_1_3_matmul_loops_reproduces_the_hand_worked_product():
    from matmul import matmul_loops

    assert written(matmul_loops, X, W) == [[0, 2], [-1, 13]]


def test_1_3_matmul_loops_agrees_with_numpy_on_six_shapes():
    from matmul import matmul_loops

    written(matmul_loops, X, W)
    for m, n, p in [(1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 4), (5, 1, 3), (1, 6, 2)]:
        rng = np.random.default_rng(m * 100 + n * 10 + p)
        left = rng.integers(-9, 10, size=(m, n)).tolist()
        right = rng.integers(-9, 10, size=(n, p)).tolist()
        assert matmul_loops(left, right) == (np.array(left) @ np.array(right)).tolist(), (
            f"disagreed on ({m}, {n}) @ ({n}, {p})"
        )


def test_1_3_the_rows_of_the_result_are_independent_objects():
    """Catches `[[0] * p] * m`, which makes m references to ONE row."""
    from matmul import matmul_loops

    result = written(matmul_loops, X, W)
    assert result[0] is not result[1], (
        "the two rows are the same object — you built the grid with "
        "[[0] * p] * m, which repeats one row rather than making m of them"
    )


def test_1_3_matmul_loops_refuses_a_shape_mismatch():
    from matmul import matmul_loops

    written(matmul_loops, X, W)
    with pytest.raises(ShapeMismatch):
        matmul_loops(X, X)


# -- Exercise 1.4: a matrix applied to a vector ------------------------------


def test_1_4_matvec_is_a_weighted_sum_of_the_columns():
    from matmul import matvec

    A = [[2, 0], [-1, 1], [0, 4]]
    assert written(matvec, A, [3, 5]) == [6, 2, 20]


def test_1_4_matvec_of_a_basis_vector_returns_that_column():
    from matmul import matvec

    written(matvec, ROT90, [1, 0])
    assert matvec(ROT90, [1, 0]) == [0, 1], "column 0 of ROT90"
    assert matvec(ROT90, [0, 1]) == [-1, 0], "column 1 of ROT90"


def test_1_4_matvec_agrees_with_numpy():
    from matmul import matvec

    written(matvec, X, U)
    assert matvec(X, U) == (np.array(X) @ np.array(U)).tolist()


def test_1_4_matvec_refuses_a_vector_of_the_wrong_length():
    from matmul import matvec

    written(matvec, X, U)
    with pytest.raises(ShapeMismatch):
        matvec(X, [1, 2])


# -- Exercise 1.5: the same product as a list of dot products ----------------


def test_1_5_matmul_dots_agrees_with_matmul_loops():
    from matmul import matmul_dots, matmul_loops

    assert written(matmul_dots, X, W) == [[0, 2], [-1, 13]]
    for m, n, p in [(1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 4), (5, 1, 3), (1, 6, 2)]:
        rng = np.random.default_rng(m * 100 + n * 10 + p)
        left = rng.integers(-9, 10, size=(m, n)).tolist()
        right = rng.integers(-9, 10, size=(n, p)).tolist()
        expected = (np.array(left) @ np.array(right)).tolist()
        assert matmul_dots(left, right) == expected, f"({m}, {n}) @ ({n}, {p})"
        assert matmul_loops(left, right) == expected


# -- Exercise 1.6 and 1.7: identity and bias ---------------------------------


def test_1_6_identity_is_ones_on_the_diagonal():
    from matmul import identity

    assert written(identity, 3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert identity(1) == [[1]]


def test_1_6_identity_does_nothing_from_either_side():
    from matmul import identity, matmul_loops

    written(identity, 2)
    written(matmul_loops, X, W)
    assert matmul_loops(identity(2), X) == X
    assert matmul_loops(X, identity(3)) == X


def test_1_6_the_identity_that_fits_depends_on_the_side():
    from matmul import identity, matmul_loops

    written(identity, 2)
    written(matmul_loops, X, W)
    with pytest.raises(ShapeMismatch):
        matmul_loops(identity(3), X)
    with pytest.raises(ShapeMismatch):
        matmul_loops(X, identity(2))


def test_1_6_identity_rejects_a_size_below_one():
    from matmul import identity

    written(identity, 1)
    with pytest.raises(ValueError):
        identity(0)


def test_1_7_add_bias_adds_the_same_vector_to_every_row():
    from matmul import add_bias

    assert written(add_bias, [[0, 2], [-1, 13]], BIAS) == [[5, 0], [4, 11]]


def test_1_7_add_bias_matches_numpy_broadcasting():
    from matmul import add_bias

    written(add_bias, [[0, 2]], BIAS)
    product = np.array(X) @ np.array(W)
    assert add_bias(product.tolist(), BIAS) == (product + np.array(BIAS)).tolist()


def test_1_7_add_bias_refuses_a_bias_of_the_wrong_length():
    from matmul import add_bias

    written(add_bias, [[0, 2]], BIAS)
    with pytest.raises(ShapeMismatch):
        add_bias([[0, 2], [-1, 13]], [5, -2, 7])


# -- Exercise 1.8 and 1.9: counting the work ---------------------------------


def test_1_8_multiplication_count():
    from matmul import multiplication_count

    assert written(multiplication_count, 2, 3, 2) == 12
    assert multiplication_count(200, 200, 200) == 8_000_000
    assert multiplication_count(1024, 4096, 4096) == 17_179_869_184


def test_1_9_chain_costs():
    from matmul import chain_costs

    assert written(chain_costs, 10, 100, 5, 50) == (7_500, 75_000)
    assert chain_costs(1024, 4096, 8, 4096) == (67_108_864, 17_314_086_912)


# -- Exercise 2: the shape rule ----------------------------------------------


def test_2_1_shape_of_X_at_W():
    assert predicted("SHAPE_OF_X_AT_W") == (np.array(X) @ np.array(W)).shape


def test_2_2_shape_of_W_at_X():
    assert predicted("SHAPE_OF_W_AT_X") == (np.array(W) @ np.array(X)).shape


def test_2_3_X_at_X_is_an_error():
    guess = predicted("SHAPE_OF_X_AT_X")
    assert guess == "error", "the inner dimensions are 3 and 2"


def test_2_4_shape_of_X_at_X_transposed():
    assert predicted("SHAPE_OF_X_AT_X_T") == (np.array(X) @ np.array(X).T).shape


def test_2_5_shape_of_X_transposed_at_X():
    assert predicted("SHAPE_OF_X_T_AT_X") == (np.array(X).T @ np.array(X)).shape


def test_2_6_shape_of_P_at_Q():
    assert predicted("SHAPE_OF_P_AT_Q") == (np.array(P) @ np.array(Q)).shape


def test_2_7_shape_of_matrix_times_vector():
    assert predicted("SHAPE_OF_X_AT_U") == (np.array(X) @ np.array(U)).shape


def test_2_8_the_exception_class():
    guess = predicted("SHAPE_ERROR_EXCEPTION")
    assert isinstance(guess, type), "give the class itself, not its name as a string"
    with pytest.raises(guess):
        np.array(X) @ np.array(X)


# -- Exercise 3: composition and order ---------------------------------------


def test_3_1_B_times_v():
    assert predicted("B_TIMES_V") == (np.array(FLIP_X) @ np.array(V)).tolist()


def test_3_2_A_times_B_times_v():
    expected = (np.array(ROT90) @ (np.array(FLIP_X) @ np.array(V))).tolist()
    assert predicted("A_TIMES_B_TIMES_V") == expected


def test_3_3_A_at_B():
    assert predicted("A_AT_B") == (np.array(ROT90) @ np.array(FLIP_X)).tolist()


def test_3_4_B_at_A():
    assert predicted("B_AT_A") == (np.array(FLIP_X) @ np.array(ROT90)).tolist()


def test_3_5_composition_matches():
    two_steps = np.array(ROT90) @ (np.array(FLIP_X) @ np.array(V))
    one_step = (np.array(ROT90) @ np.array(FLIP_X)) @ np.array(V)
    assert predicted("COMPOSITION_MATCHES") == bool(np.array_equal(two_steps, one_step))


def test_3_6_order_does_not_matter_is_false():
    same = np.array_equal(np.array(ROT90) @ np.array(FLIP_X), np.array(FLIP_X) @ np.array(ROT90))
    assert predicted("ORDER_DOES_NOT_MATTER") == bool(same)


def test_3_7_which_matrix_acts_first():
    guess = predicted("WHICH_ACTS_FIRST")
    assert guess in ("A", "B"), 'answer with the string "A" or "B"'
    assert guess == "B", "the rightmost matrix is the one standing next to the vector"


# -- Exercise 4: `*` against `@` ---------------------------------------------


def test_4_1_P_star_Q():
    assert predicted("P_STAR_Q") == (np.array(P) * np.array(Q)).tolist()


def test_4_2_P_at_Q():
    assert predicted("P_AT_Q") == (np.array(P) @ np.array(Q)).tolist()


def test_4_3_star_and_at_have_the_same_shape_here():
    same = (np.array(P) * np.array(Q)).shape == (np.array(P) @ np.array(Q)).shape
    assert predicted("P_STAR_AND_AT_SAME_SHAPE") == bool(same)


def test_4_4_X_star_u_shape():
    assert predicted("X_STAR_U_SHAPE") == (np.array(X) * np.array(U)).shape


def test_4_5_X_at_u_shape_and_values():
    assert predicted("X_AT_U_SHAPE") == (np.array(X) @ np.array(U)).shape
    assert predicted("X_AT_U_VALUES") == (np.array(X) @ np.array(U)).tolist()


def test_4_6_the_axis_that_turns_star_into_at():
    axis = predicted("AXIS_THAT_TURNS_STAR_INTO_AT")
    summed = (np.array(X) * np.array(U)).sum(axis=axis)
    assert np.array_equal(summed, np.array(X) @ np.array(U))


# -- Exercise 5: one layer of a neural network -------------------------------


def test_5_1_X_at_W():
    assert predicted("X_AT_W") == (np.array(X) @ np.array(W)).tolist()


def test_5_2_layer_output():
    assert predicted("LAYER_OUTPUT") == (np.array(X) @ np.array(W) + np.array(BIAS)).tolist()


def test_5_3_the_bias_is_one_per_output():
    guess = predicted("BIAS_IS_ONE_PER")
    assert guess in ("example", "output"), 'answer "example" or "output"'
    assert guess == "output", (
        "the bias has as many entries as the layer has output units; grow the "
        "batch and it does not change"
    )


def test_5_4_only_the_batch_shape_changes():
    guess = predicted("SHAPES_THAT_CHANGE_WITH_THE_BATCH")
    assert isinstance(guess, list), "give a list of names"
    assert guess == ["X"], "W and the bias belong to the layer, not to the batch"


def test_5_5_two_linear_layers_collapse():
    npX, npW, npB = np.array(X), np.array(W), np.array(BIAS)
    W2 = np.array([[1, 0, 2], [3, 1, 0]])
    b2 = np.array([0, 1, -1])
    two_layers = (npX @ npW + npB) @ W2 + b2
    collapsed = npX @ (npW @ W2) + (npB @ W2 + b2)
    assert predicted("TWO_LINEAR_LAYERS_COLLAPSE") == bool(np.array_equal(two_layers, collapsed))


# -- Exercise 6: cost --------------------------------------------------------


def test_6_1_cost_of_the_small_layer():
    assert predicted("COST_OF_THE_SMALL_LAYER") == 2 * 3 * 2


def test_6_2_cost_of_200_squared():
    assert predicted("COST_OF_200_SQUARED") == 200 * 200 * 200


def test_6_3_the_two_associations():
    assert predicted("CHAIN_LEFT_FIRST") == 10 * 100 * 5 + 10 * 5 * 50
    assert predicted("CHAIN_RIGHT_FIRST") == 100 * 5 * 50 + 10 * 100 * 50


def test_6_4_which_association_is_cheaper():
    guess = predicted("CHEAPER_ASSOCIATION")
    assert guess in ("(AB)C", "A(BC)"), 'answer "(AB)C" or "A(BC)"'
    left = 10 * 100 * 5 + 10 * 5 * 50
    right = 100 * 5 * 50 + 10 * 100 * 50
    assert guess == ("(AB)C" if left < right else "A(BC)")


def test_6_5_the_associations_agree_on_the_answer():
    rng = np.random.default_rng(11)
    A = rng.integers(0, 4, size=(6, 12))
    B = rng.integers(0, 4, size=(12, 2))
    C = rng.integers(0, 4, size=(2, 12))
    assert predicted("ASSOCIATIONS_AGREE") == bool(np.array_equal((A @ B) @ C, A @ (B @ C)))


def test_6_6_why_float_beats_int():
    guess = predicted("WHY_FLOAT_BEATS_INT")
    assert guess == "BLAS only implements floating point", (
        "BLAS has no integer matrix-multiply routine, so an int64 `@` falls "
        "back to NumPy's own compiled loop. That loop is still far faster than "
        "interpreted Python and still far slower than BLAS."
    )
