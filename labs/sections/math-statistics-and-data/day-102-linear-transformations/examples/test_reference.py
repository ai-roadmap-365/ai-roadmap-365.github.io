"""The reference test suite: real values, real shapes, real exceptions.

Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q -p no:cacheprovider

Every float comparison here states a tolerance and the module docstring of
shapes.py says why that number was chosen. Nothing is compared with == unless
the arithmetic that produced it is exact -- and where it is exact, the test
says == on purpose, because that is a stronger claim.
"""

import math

import numpy as np
import pytest

import shapes
from transforms import (
    SingularMatrix,
    apply,
    columns_of,
    compose,
    determinant,
    from_landings,
    identity,
    inverse,
    is_linear,
    preserves_addition,
    preserves_scaling,
    rank,
    reflection_in_x_axis,
    reflection_in_y_axis,
    rotation,
    scaling,
    shear_x,
    shear_y,
    signed_area,
    transform_polygon,
)

TOL = shapes.TOL


# -- Reading a matrix off its landings ---------------------------------------


def test_from_landings_builds_the_picture_matrix():
    M = from_landings(shapes.PICTURE_E1_LANDS_AT, shapes.PICTURE_E2_LANDS_AT)
    assert M == shapes.PICTURE_MATRIX


def test_columns_are_the_landings_not_the_rows():
    e1, e2 = columns_of(shapes.PICTURE_MATRIX)
    assert e1 == (3.0, 1.0)
    assert e2 == (-1.0, 2.0)
    # The trap this test exists for: row 0 is (3, -1) and is NOT a landing.
    assert tuple(shapes.PICTURE_MATRIX[0]) != e1


def test_the_matrix_sends_2_1_where_hand_arithmetic_says():
    assert apply(shapes.PICTURE_MATRIX, (2.0, 1.0)) == shapes.PICTURE_SENDS_2_1_TO


def test_numpy_agrees_on_the_picture_matrix():
    M = np.array(shapes.PICTURE_MATRIX)
    assert np.allclose(M @ np.array([2.0, 1.0]), np.array([5.0, 4.0]), atol=TOL)
    assert np.allclose(M @ np.array(shapes.E1), np.array([3.0, 1.0]), atol=TOL)
    assert np.allclose(M @ np.array(shapes.E2), np.array([-1.0, 2.0]), atol=TOL)


def test_applying_to_a_basis_vector_just_reads_a_column():
    for M in (shapes.PICTURE_MATRIX, shapes.SCALE_MATRIX, shapes.SHEAR_MATRIX):
        e1, e2 = columns_of(M)
        assert apply(M, shapes.E1) == e1
        assert apply(M, shapes.E2) == e2


# -- The identity -------------------------------------------------------------


def test_identity_leaves_everything_alone():
    I = identity()
    for point in [(0.0, 0.0), (1.0, 0.0), (-3.5, 7.25), (1e6, -1e-6)]:
        assert apply(I, point) == point


def test_identity_matches_numpy_eye():
    assert np.allclose(np.array(identity()), np.eye(2), atol=TOL)


def test_identity_has_determinant_one_and_full_rank():
    assert determinant(identity()) == 1.0
    assert rank(identity()) == 2


# -- The four standard transformations ---------------------------------------


def test_scaling_matrix_is_derived_correctly():
    assert scaling(2.0, 3.0) == shapes.SCALE_MATRIX
    assert apply(scaling(2.0, 3.0), (1.0, 1.0)) == (2.0, 3.0)
    assert apply(scaling(2.0, 3.0), (-4.0, 0.5)) == (-8.0, 1.5)


def test_reflection_in_x_axis_fixes_the_axis_and_flips_the_rest():
    F = reflection_in_x_axis()
    assert F == shapes.FLIP_MATRIX
    assert apply(F, (5.0, 0.0)) == (5.0, 0.0)
    assert apply(F, (2.0, 3.0)) == (2.0, -3.0)


def test_reflection_in_y_axis():
    F = reflection_in_y_axis()
    assert apply(F, (0.0, 5.0)) == (0.0, 5.0)
    assert apply(F, (2.0, 3.0)) == (-2.0, 3.0)


def test_reflecting_twice_is_the_identity():
    F = reflection_in_x_axis()
    assert compose(F, F) == identity()


def test_shear_leaves_the_x_axis_alone_and_slides_the_rest():
    H = shear_x(2.0)
    assert H == shapes.SHEAR_MATRIX
    assert apply(H, (5.0, 0.0)) == (5.0, 0.0)
    assert apply(H, (1.0, 1.0)) == (3.0, 1.0)
    assert apply(H, (0.0, 1.0)) == (2.0, 1.0)


def test_shear_y_is_the_same_idea_the_other_way_up():
    V = shear_y(3.0)
    assert apply(V, (0.0, 5.0)) == (0.0, 5.0)
    assert apply(V, (1.0, 0.0)) == (1.0, 3.0)


@pytest.mark.parametrize(
    "degrees, expected_cos, expected_sin",
    [
        (0, 1.0, 0.0),
        (30, math.sqrt(3) / 2, 0.5),
        (45, math.sqrt(2) / 2, math.sqrt(2) / 2),
        (90, 0.0, 1.0),
        (180, -1.0, 0.0),
    ],
)
def test_rotation_columns_are_the_unit_circle_coordinates(
    degrees, expected_cos, expected_sin
):
    R = rotation(math.radians(degrees))
    e1, e2 = columns_of(R)
    assert abs(e1[0] - expected_cos) <= TOL
    assert abs(e1[1] - expected_sin) <= TOL
    assert abs(e2[0] + expected_sin) <= TOL
    assert abs(e2[1] - expected_cos) <= TOL


def test_a_quarter_turn_sends_the_basis_where_the_picture_says():
    Q = rotation(math.pi / 2)
    x, y = apply(Q, shapes.E1)
    assert abs(x - 0.0) <= TOL and abs(y - 1.0) <= TOL
    x, y = apply(Q, shapes.E2)
    assert abs(x + 1.0) <= TOL and abs(y - 0.0) <= TOL


def test_the_quarter_turn_is_NOT_exactly_zero_which_is_why_tolerance_exists():
    """The honest reason this lab never uses == on a rotation.

    cos(pi / 2) is 6.123233995736766e-17 rather than 0.0, because pi cannot be
    stored exactly in binary and the cosine of the stored value is not the
    cosine of pi. This test asserts the inexactness itself, so that if a future
    NumPy or libm ever made it exact, the suite would say so rather than
    silently keeping a comment that had stopped being true.
    """
    assert math.cos(math.pi / 2) != 0.0
    assert 0.0 < abs(math.cos(math.pi / 2)) < 1e-15
    assert apply(rotation(math.pi / 2), shapes.E1) != (0.0, 1.0)


def test_sin_of_thirty_degrees_is_also_not_exactly_a_half():
    assert math.sin(math.radians(30)) != 0.5
    assert abs(math.sin(math.radians(30)) - 0.5) <= TOL


def test_four_quarter_turns_return_to_the_start():
    Q = rotation(math.pi / 2)
    back = compose(Q, compose(Q, compose(Q, Q)))
    for row, want in zip(back, identity()):
        for got, expect in zip(row, want):
            assert abs(got - expect) <= TOL


def test_rotation_preserves_length():
    R = rotation(0.9)
    for point in [(3.0, 4.0), (1.0, 0.0), (-2.0, 7.0)]:
        before = math.hypot(*point)
        after = math.hypot(*apply(R, point))
        assert abs(before - after) <= TOL


def test_all_four_match_numpy():
    theta = math.pi / 2
    pairs = [
        (scaling(2.0, 3.0), np.diag([2.0, 3.0])),
        (reflection_in_x_axis(), np.array([[1.0, 0.0], [0.0, -1.0]])),
        (shear_x(2.0), np.array([[1.0, 2.0], [0.0, 1.0]])),
        (
            rotation(theta),
            np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]),
        ),
    ]
    for mine, theirs in pairs:
        assert np.allclose(np.array(mine), theirs, atol=TOL)


# -- Linearity ----------------------------------------------------------------

U = (1.0, 2.0)
V = (3.0, -1.0)
S = 5.0
B = (1.0, 1.0)


def _linear(point):
    return apply(shapes.SCALE_MATRIX, point)


def _affine(point):
    x, y = apply(shapes.SCALE_MATRIX, point)
    return (x + B[0], y + B[1])


def test_a_matrix_preserves_addition():
    ok, together, separately = preserves_addition(_linear, U, V, TOL)
    assert ok
    assert together == (8.0, 3.0)
    assert separately == (8.0, 3.0)


def test_a_matrix_preserves_scaling():
    ok, first, after = preserves_scaling(_linear, U, S, TOL)
    assert ok
    assert first == (10.0, 30.0)
    assert after == (10.0, 30.0)


def test_a_matrix_is_linear():
    assert is_linear(_linear, U, V, S, TOL)


def test_adding_a_constant_breaks_addition_by_exactly_b():
    ok, together, separately = preserves_addition(_affine, U, V, TOL)
    assert not ok
    assert together == (9.0, 4.0)
    assert separately == (10.0, 5.0)
    gap = (separately[0] - together[0], separately[1] - together[1])
    assert gap == B


def test_adding_a_constant_breaks_scaling_by_exactly_s_minus_one_times_b():
    ok, first, after = preserves_scaling(_affine, U, S, TOL)
    assert not ok
    assert first == (11.0, 31.0)
    assert after == (15.0, 35.0)
    gap = (after[0] - first[0], after[1] - first[1])
    assert gap == ((S - 1) * B[0], (S - 1) * B[1])


def test_an_affine_function_is_not_linear():
    assert not is_linear(_affine, U, V, S, TOL)


def test_linear_fixes_the_origin_and_affine_does_not():
    assert _linear((0.0, 0.0)) == (0.0, 0.0)
    assert _affine((0.0, 0.0)) == B


def test_every_matrix_in_this_lab_fixes_the_origin():
    matrices = [
        identity(),
        scaling(2.0, 3.0),
        shear_x(2.0),
        reflection_in_x_axis(),
        rotation(1.234),
        shapes.PICTURE_MATRIX,
        shapes.COLLAPSE_MATRIX,
    ]
    for M in matrices:
        x, y = apply(M, (0.0, 0.0))
        assert abs(x) <= TOL and abs(y) <= TOL


def test_squaring_a_coordinate_is_not_linear():
    """A second non-linear example, so the point is not just about b."""

    def squarer(point):
        return (point[0] ** 2, point[1])

    assert squarer((0.0, 0.0)) == (0.0, 0.0)  # fixes the origin, yet still not linear
    assert not is_linear(squarer, U, V, S, TOL)


def test_a_linear_map_sends_midpoints_to_midpoints():
    M = compose(rotation(math.radians(30)), shear_x(1.5))
    p, q = (1.0, 3.0), (4.0, -2.0)
    mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    landed_mid = apply(M, mid)
    mid_of_landed = tuple((a + b) / 2 for a, b in zip(apply(M, p), apply(M, q)))
    assert all(abs(a - b) <= TOL for a, b in zip(landed_mid, mid_of_landed))


# -- Composition --------------------------------------------------------------


def test_composition_matches_the_hand_worked_product():
    C = compose(rotation(math.pi / 2), shear_x(2.0))
    for row, want in zip(C, shapes.SHEAR_THEN_ROTATE):
        for got, expect in zip(row, want):
            assert abs(got - expect) <= TOL


def test_the_other_order_is_a_different_transformation():
    A, Bm = shear_x(2.0), rotation(math.pi / 2)
    for row, want in zip(compose(A, Bm), shapes.ROTATE_THEN_SHEAR):
        for got, expect in zip(row, want):
            assert abs(got - expect) <= TOL
    probe = (1.0, 1.0)
    one = apply(compose(Bm, A), probe)
    other = apply(compose(A, Bm), probe)
    assert any(abs(a - b) > TOL for a, b in zip(one, other))


def test_one_matrix_reproduces_the_two_step_sequence_on_every_corner():
    A, Bm = shear_x(2.0), rotation(math.pi / 2)
    two_steps = transform_polygon(Bm, transform_polygon(A, shapes.FLAG))
    at_once = transform_polygon(compose(Bm, A), shapes.FLAG)
    for (x1, y1), (x2, y2) in zip(two_steps, at_once):
        assert abs(x1 - x2) <= TOL and abs(y1 - y2) <= TOL


def test_composition_matches_numpy_matmul_in_both_orders():
    A = np.array(shear_x(2.0))
    Bm = np.array(rotation(math.pi / 2))
    assert np.allclose(Bm @ A, np.array(compose(rotation(math.pi / 2), shear_x(2.0))), atol=TOL)
    assert np.allclose(A @ Bm, np.array(compose(shear_x(2.0), rotation(math.pi / 2))), atol=TOL)
    assert not np.allclose(A @ Bm, Bm @ A, atol=TOL)


def test_composing_with_the_identity_changes_nothing():
    H = shear_x(2.0)
    assert compose(identity(), H) == H
    assert compose(H, identity()) == H


def test_determinants_multiply_under_composition():
    A, Bm = scaling(2.0, 3.0), shear_x(4.0)
    assert abs(determinant(compose(Bm, A)) - determinant(A) * determinant(Bm)) <= TOL


# -- Determinant, area, orientation ------------------------------------------


def test_the_unit_square_starts_with_signed_area_one():
    assert abs(signed_area(shapes.UNIT_SQUARE) - 1.0) <= TOL


def test_listing_the_corners_clockwise_flips_the_sign():
    assert abs(signed_area(list(reversed(shapes.UNIT_SQUARE))) + 1.0) <= TOL


@pytest.mark.parametrize(
    "matrix, expected",
    [
        (scaling(2.0, 3.0), 6.0),
        (scaling(0.5, 0.5), 0.25),
        (shear_x(2.0), 1.0),
        (reflection_in_x_axis(), -1.0),
        (reflection_in_y_axis(), -1.0),
        (identity(), 1.0),
        (shapes.PICTURE_MATRIX, 7.0),
        (shapes.COLLAPSE_MATRIX, 0.0),
    ],
)
def test_transformed_area_equals_the_determinant(matrix, expected):
    area = signed_area(transform_polygon(matrix, shapes.UNIT_SQUARE))
    assert abs(area - expected) <= TOL
    assert abs(determinant(matrix) - expected) <= TOL


def test_a_negative_determinant_means_the_orientation_flipped():
    flipped = transform_polygon(reflection_in_x_axis(), shapes.UNIT_SQUARE)
    assert signed_area(flipped) < 0
    assert abs(abs(signed_area(flipped)) - 1.0) <= TOL


def test_a_rotation_never_flips_orientation():
    for degrees in (0, 30, 90, 180, 270, 359):
        assert determinant(rotation(math.radians(degrees))) > 0


def test_rotation_determinant_is_one_which_is_the_pythagorean_identity():
    for degrees in (17, 45, 123, 300):
        theta = math.radians(degrees)
        assert abs(determinant(rotation(theta)) - 1.0) <= TOL
        # det = cos*cos - (-sin)*sin = cos^2 + sin^2, which is 1 by Pythagoras
        assert abs(math.cos(theta) ** 2 + math.sin(theta) ** 2 - 1.0) <= TOL


def test_the_from_scratch_determinant_is_exact_on_whole_numbers():
    assert determinant(shapes.PICTURE_MATRIX) == 7.0
    assert determinant(shapes.COLLAPSE_MATRIX) == 0.0


def test_numpy_determinant_is_close_but_not_always_equal():
    """The honest difference, asserted rather than described.

    numpy.linalg.det factorises the matrix -- the general method that also
    works at 500 by 500 -- and that rounds. The direct a*d - b*c does not. On
    this matrix, on this machine, they differ in the last bit.
    """
    mine = determinant(shapes.PICTURE_MATRIX)
    theirs = float(np.linalg.det(np.array(shapes.PICTURE_MATRIX)))
    assert mine == 7.0
    assert theirs != 7.0
    assert abs(theirs - 7.0) < 1e-14


# -- Rank and collapse --------------------------------------------------------


def test_the_collapse_puts_everything_on_one_line():
    G = shapes.COLLAPSE_MATRIX
    for point in [(1.0, 0.0), (0.0, 1.0), (3.0, -1.0), (7.0, 7.0), (-2.5, 0.25)]:
        x, y = apply(G, point)
        assert abs(y - 2.0 * x) <= TOL


def test_the_collapse_sends_two_different_points_to_the_same_place():
    G = shapes.COLLAPSE_MATRIX
    assert apply(G, (2.0, 0.0)) == apply(G, (0.0, 1.0))


@pytest.mark.parametrize(
    "matrix, expected_rank",
    [
        (identity(), 2),
        (scaling(2.0, 3.0), 2),
        (shear_x(2.0), 2),
        (shapes.PICTURE_MATRIX, 2),
        (shapes.COLLAPSE_MATRIX, 1),
        ([[0.0, 0.0], [0.0, 0.0]], 0),
        ([[1.0, 0.0], [0.0, 0.0]], 1),
    ],
)
def test_rank_matches_numpy(matrix, expected_rank):
    assert rank(matrix) == expected_rank
    assert int(np.linalg.matrix_rank(np.array(matrix))) == expected_rank


def test_scaling_by_zero_in_one_direction_loses_a_dimension():
    flat = scaling(3.0, 0.0)
    assert determinant(flat) == 0.0
    assert rank(flat) == 1
    for point in [(1.0, 5.0), (-2.0, 100.0)]:
        assert apply(flat, point)[1] == 0.0


# -- Inverses ------------------------------------------------------------------


def test_inverse_of_a_shear_is_the_opposite_shear():
    assert inverse(shear_x(2.0)) == shear_x(-2.0)


def test_inverse_of_a_scaling_divides():
    inv = inverse(scaling(2.0, 4.0))
    assert inv == [[0.5, 0.0], [0.0, 0.25]]


def test_inverse_composed_with_the_original_is_the_identity():
    for M in [shear_x(2.0), scaling(2.0, 3.0), shapes.PICTURE_MATRIX, rotation(0.7)]:
        back = compose(inverse(M), M)
        for row, want in zip(back, identity()):
            for got, expect in zip(row, want):
                assert abs(got - expect) <= TOL


def test_a_round_trip_returns_the_original_point():
    M = shapes.PICTURE_MATRIX
    for point in [(1.0, 1.0), (-3.0, 2.5), (0.0, 0.0)]:
        there = apply(M, point)
        home = apply(inverse(M), there)
        assert abs(home[0] - point[0]) <= TOL
        assert abs(home[1] - point[1]) <= TOL


def test_the_inverse_determinant_is_the_reciprocal():
    M = scaling(2.0, 3.0)
    assert abs(determinant(inverse(M)) - 1.0 / determinant(M)) <= TOL


def test_inverting_a_collapse_raises():
    with pytest.raises(SingularMatrix):
        inverse(shapes.COLLAPSE_MATRIX)


def test_the_from_scratch_refusal_is_catchable_as_a_ValueError():
    with pytest.raises(ValueError):
        inverse(shapes.COLLAPSE_MATRIX)


def test_numpy_raises_LinAlgError_for_the_same_matrix():
    with pytest.raises(np.linalg.LinAlgError) as caught:
        np.linalg.inv(np.array(shapes.COLLAPSE_MATRIX))
    assert "Singular matrix" in str(caught.value)


def test_numpys_error_is_also_a_ValueError():
    assert issubclass(np.linalg.LinAlgError, ValueError)
    with pytest.raises(ValueError):
        np.linalg.inv(np.array(shapes.COLLAPSE_MATRIX))


def test_numpy_inverse_agrees_with_the_from_scratch_one():
    for M in [shear_x(2.0), scaling(2.0, 3.0), shapes.PICTURE_MATRIX]:
        assert np.allclose(np.linalg.inv(np.array(M)), np.array(inverse(M)), atol=TOL)


# -- The limit of linear -------------------------------------------------------


def test_a_stack_of_twenty_layers_is_one_matrix():
    import random

    random.seed(102)
    stack = [
        [[random.uniform(-2, 2) for _ in range(2)] for _ in range(2)]
        for _ in range(20)
    ]
    point = (0.7, -0.4)
    stepwise = point
    for layer in stack:
        stepwise = apply(layer, stepwise)

    combined = stack[0]
    for layer in stack[1:]:
        combined = compose(layer, combined)
    at_once = apply(combined, point)

    # A relative tolerance, because twenty layers of rounding on entries that
    # are not small whole numbers is a real accumulation and pretending
    # otherwise would be dishonest.
    for a, b in zip(stepwise, at_once):
        assert abs(a - b) <= 1e-9 * max(1.0, abs(a))


def test_a_stack_still_fixes_the_origin_and_still_makes_a_parallelogram():
    M = compose(compose(rotation(0.4), shear_x(3.0)), scaling(2.0, -1.0))
    corners = transform_polygon(M, shapes.UNIT_SQUARE)
    assert abs(corners[0][0]) <= TOL and abs(corners[0][1]) <= TOL
    # Opposite sides of the image are still parallel and equal, which is what
    # "still a parallelogram" means numerically.
    side_a = (corners[1][0] - corners[0][0], corners[1][1] - corners[0][1])
    side_c = (corners[2][0] - corners[3][0], corners[2][1] - corners[3][1])
    assert abs(side_a[0] - side_c[0]) <= TOL
    assert abs(side_a[1] - side_c[1]) <= TOL


def test_relu_after_a_matrix_is_not_linear():
    M = compose(rotation(math.radians(30)), shear_x(1.5))

    def relu_layer(point):
        return tuple(max(0.0, c) for c in apply(M, point))

    assert not is_linear(relu_layer, (1.0, -1.0), (0.5, 2.0), 3.0, TOL)


def test_the_area_factor_of_a_stack_is_the_product_of_its_factors():
    layers = [scaling(2.0, 3.0), shear_x(4.0), reflection_in_x_axis()]
    combined = layers[0]
    for layer in layers[1:]:
        combined = compose(layer, combined)
    expected = 1.0
    for layer in layers:
        expected *= determinant(layer)
    assert abs(determinant(combined) - expected) <= TOL
    assert abs(expected + 6.0) <= TOL  # 6 * 1 * -1, and the sign says it flipped
