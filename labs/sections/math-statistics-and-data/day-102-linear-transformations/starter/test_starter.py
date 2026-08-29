"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Float comparisons use a tolerance of TOL, stated below, and `shapes.py`
explains why that number and not equality.
"""

import math

import numpy as np
import pytest

import answers
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
    reflection_in_x_axis,
    rotation,
    scaling,
    shear_x,
    signed_area,
    transform_polygon,
)

TOL = shapes.TOL


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


def close(a, b, tol=TOL):
    """Elementwise closeness for points and for 2 by 2 matrices."""
    if isinstance(a[0], (list, tuple)):
        return all(close(ra, rb, tol) for ra, rb in zip(a, b))
    return all(abs(x - y) <= tol for x, y in zip(a, b))


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    assert np.__version__, "numpy is importable"
    assert identity() == [[1.0, 0.0], [0.0, 1.0]], "the written-for-you helpers load"
    assert abs(signed_area(shapes.UNIT_SQUARE) - 1.0) <= TOL


# -- Exercise 1: your transforms.py ------------------------------------------
#
# Every test below runs its whole body inside `written(...)`, so a test is
# skipped if ANY function it needs is still unwritten -- not just the first
# one. Arguments in Python are evaluated before the call, so gating on one
# function while calling another inside the arguments would let a
# NotImplementedError escape and be reported as a failure. It would say
# "attempted and wrong" about work you had not attempted, which is precisely
# the lie this suite exists to avoid.


def test_1_1_from_landings():
    M = written(lambda: from_landings((3.0, 1.0), (-1.0, 2.0)))
    assert M == [[3.0, -1.0], [1.0, 2.0]], (
        "the landing places are the COLUMNS, so they read downwards"
    )


def test_1_2_columns_of():
    e1, e2 = written(lambda: columns_of([[3.0, -1.0], [1.0, 2.0]]))
    assert tuple(e1) == (3.0, 1.0)
    assert tuple(e2) == (-1.0, 2.0)


def test_1_2_columns_of_undoes_from_landings():
    def check():
        for a, b in [((2.0, -5.0), (0.5, 7.0)), ((0.0, 1.0), (1.0, 0.0))]:
            got_a, got_b = columns_of(from_landings(a, b))
            assert tuple(got_a) == a and tuple(got_b) == b

    written(check)


def test_1_3_apply():
    assert written(lambda: apply([[3.0, -1.0], [1.0, 2.0]], (2.0, 1.0))) == (5.0, 4.0)


def test_1_3_apply_to_a_basis_vector_reads_a_column():
    M = [[3.0, -1.0], [1.0, 2.0]]
    assert tuple(written(lambda: apply(M, shapes.E1))) == (3.0, 1.0)
    assert tuple(apply(M, shapes.E2)) == (-1.0, 2.0)


def test_1_3_apply_matches_numpy():
    def check():
        M = [[3.0, -1.0], [1.0, 2.0]]
        for point in [(2.0, 1.0), (-1.5, 4.0), (0.0, 0.0)]:
            assert close(apply(M, point), (np.array(M) @ np.array(point)).tolist())

    written(check)


def test_1_4_scaling():
    assert written(lambda: scaling(2.0, 3.0)) == [[2.0, 0.0], [0.0, 3.0]]
    assert tuple(written(lambda: apply(scaling(2.0, 3.0), (1.0, 1.0)))) == (2.0, 3.0)


def test_1_5_reflection():
    assert written(reflection_in_x_axis) == [[1.0, 0.0], [0.0, -1.0]]
    assert tuple(written(lambda: apply(reflection_in_x_axis(), (5.0, 0.0)))) == (
        5.0,
        0.0,
    ), "a point on the mirror line cannot move"


def test_1_6_shear():
    assert written(lambda: shear_x(2.0)) == [[1.0, 2.0], [0.0, 1.0]]
    assert tuple(written(lambda: apply(shear_x(2.0), (5.0, 0.0)))) == (5.0, 0.0), (
        "height 0 means no sideways push at all"
    )
    assert tuple(apply(shear_x(2.0), (1.0, 1.0))) == (3.0, 1.0)


def test_1_7_rotation_quarter_turn():
    Q = written(lambda: rotation(math.pi / 2))
    assert close(Q, [[0.0, -1.0], [1.0, 0.0]]), (
        "compared with a tolerance, because cos(pi / 2) is not exactly 0.0"
    )


def test_1_7_rotation_thirty_degrees():
    R = written(lambda: rotation(math.radians(30)))
    assert close(R, [[math.sqrt(3) / 2, -0.5], [0.5, math.sqrt(3) / 2]])


def test_1_7_rotation_preserves_length():
    def check():
        for point in [(3.0, 4.0), (-2.0, 7.0)]:
            turned = apply(rotation(0.9), point)
            assert abs(math.hypot(*point) - math.hypot(*turned)) <= TOL

    written(check)


def test_1_8_compose_matches_the_hand_worked_product():
    C = written(lambda: compose(rotation(math.pi / 2), shear_x(2.0)))
    assert close(C, [[0.0, -1.0], [1.0, 2.0]])


def test_1_8_compose_reproduces_two_separate_steps():
    def check():
        A, B = shear_x(2.0), rotation(math.pi / 2)
        two_steps = transform_polygon(B, transform_polygon(A, shapes.FLAG))
        at_once = transform_polygon(compose(B, A), shapes.FLAG)
        for p, q in zip(two_steps, at_once):
            assert close(p, q)

    written(check)


def test_1_8_compose_matches_numpy_matmul():
    def check():
        A, B = shear_x(2.0), rotation(math.pi / 2)
        assert close(compose(B, A), (np.array(B) @ np.array(A)).tolist())

    written(check)


def test_1_9_determinant():
    assert written(lambda: determinant([[3.0, -1.0], [1.0, 2.0]])) == 7.0, (
        "compute a*d - b*c directly; on whole numbers it should be exact"
    )
    assert determinant([[1.0, 2.0], [2.0, 4.0]]) == 0.0
    assert determinant(identity()) == 1.0


def test_1_9_determinant_is_the_area_factor():
    def check():
        for M, expected in [(scaling(2.0, 3.0), 6.0), (reflection_in_x_axis(), -1.0)]:
            area = signed_area(transform_polygon(M, shapes.UNIT_SQUARE))
            assert abs(area - expected) <= TOL
            assert abs(determinant(M) - expected) <= TOL

    written(check)


def test_1_10_inverse():
    assert written(lambda: inverse([[1.0, 2.0], [0.0, 1.0]])) == [[1.0, -2.0], [0.0, 1.0]]


def test_1_10_inverse_undoes_the_original():
    def check():
        for M in [shear_x(2.0), scaling(2.0, 3.0), [[3.0, -1.0], [1.0, 2.0]]]:
            assert close(compose(inverse(M), M), identity())

    written(check)


def test_1_10_inverse_refuses_a_collapse():
    written(lambda: inverse(identity()))
    with pytest.raises(SingularMatrix):
        inverse(shapes.COLLAPSE_MATRIX)


def test_1_10_that_refusal_is_catchable_as_a_ValueError():
    written(lambda: inverse(identity()))
    with pytest.raises(ValueError):
        inverse(shapes.COLLAPSE_MATRIX)


def test_1_10_inverse_matches_numpy():
    def check():
        for M in [shear_x(2.0), scaling(2.0, 3.0), [[3.0, -1.0], [1.0, 2.0]]]:
            assert close(inverse(M), np.linalg.inv(np.array(M)).tolist())

    written(check)


# -- Exercise 2: reading a matrix off a picture ------------------------------


def test_2_1_picture_matrix():
    assert predicted("PICTURE_MATRIX") == [[3.0, -1.0], [1.0, 2.0]]


def test_2_2_where_2_1_lands():
    assert tuple(predicted("PICTURE_SENDS_2_1_TO")) == (5.0, 4.0)


def test_2_3_neither_row_is_a_landing():
    assert predicted("WHICH_ROW_IS_A_LANDING") == "neither"


# -- Exercise 3: the four standard transformations ---------------------------


def test_3_1_scaling():
    assert tuple(predicted("SCALE_SENDS_1_1_TO")) == (2.0, 3.0)


def test_3_2_reflection():
    assert tuple(predicted("FLIP_SENDS_2_3_TO")) == (2.0, -3.0)


def test_3_3_shear():
    assert tuple(predicted("SHEAR_SENDS_1_1_TO")) == (3.0, 1.0)


def test_3_4_shear_on_the_axis():
    assert tuple(predicted("SHEAR_SENDS_5_0_TO")) == (5.0, 0.0)


def test_3_5_quarter_turn():
    assert close(tuple(predicted("QUARTER_TURN_SENDS_1_0_TO")), (0.0, 1.0))


def test_3_6_cosine_is_not_exactly_zero():
    assert predicted("COS_OF_QUARTER_TURN_IS_EXACTLY_ZERO") is False
    assert math.cos(math.pi / 2) != 0.0


def test_3_7_the_origin_is_fixed_by_every_matrix():
    assert tuple(predicted("THE_POINT_NO_MATRIX_CAN_MOVE")) == (0.0, 0.0)


# -- Exercise 4: linearity ----------------------------------------------------


def test_4_1_T_of_u_plus_v():
    assert tuple(predicted("T_OF_U_PLUS_V")) == (8.0, 3.0)


def test_4_2_T_of_u_plus_T_of_v():
    assert tuple(predicted("T_OF_U_PLUS_T_OF_V")) == (8.0, 3.0)


def test_4_3_f_of_u_plus_v():
    assert tuple(predicted("F_OF_U_PLUS_V")) == (9.0, 4.0)


def test_4_4_f_of_u_plus_f_of_v():
    assert tuple(predicted("F_OF_U_PLUS_F_OF_V")) == (10.0, 5.0)


def test_4_5_the_gap_is_exactly_b():
    assert tuple(predicted("THE_GAP_BETWEEN_THEM")) == (1.0, 1.0)


def test_4_6_f_is_not_linear():
    assert predicted("F_IS_LINEAR") is False


def test_4_7_f_moves_the_origin():
    assert tuple(predicted("F_OF_THE_ORIGIN")) == (1.0, 1.0)


# -- Exercise 5: composition and order ---------------------------------------


def test_5_1_which_order():
    assert predicted("SHEAR_THEN_ROTATE_IS") == "compose(B, A)"


def test_5_2_the_composite_matrix():
    assert close(predicted("SHEAR_THEN_ROTATE_MATRIX"), [[0.0, -1.0], [1.0, 2.0]])


def test_5_3_order_matters():
    assert predicted("BOTH_ORDERS_AGREE") is False


def test_5_4_determinants_multiply():
    assert abs(predicted("DET_OF_THE_COMPOSITE") - 1.0) <= TOL


# -- Exercise 6: determinant, rank and the inverse ---------------------------


def test_6_1_area_after_scaling():
    assert abs(predicted("AREA_AFTER_SCALING") - 6.0) <= TOL


def test_6_2_signed_area_after_reflection():
    assert abs(predicted("SIGNED_AREA_AFTER_REFLECTION") + 1.0) <= TOL


def test_6_3_what_a_negative_determinant_means():
    assert predicted("A_NEGATIVE_DETERMINANT_MEANS") == "the plane was flipped over"


def test_6_4_shear_preserves_area():
    assert abs(predicted("DET_OF_SHEAR") - 1.0) <= TOL


def test_6_5_determinant_of_the_collapse():
    assert abs(predicted("DET_OF_COLLAPSE")) <= TOL


def test_6_6_rank_of_the_collapse():
    assert predicted("RANK_OF_COLLAPSE") == 1
    assert int(np.linalg.matrix_rank(np.array(shapes.COLLAPSE_MATRIX))) == 1


def test_6_7_the_line_everything_lands_on():
    m = predicted("COLLAPSE_LANDS_EVERYTHING_ON_THE_LINE_Y_EQUALS")
    M = np.array(shapes.COLLAPSE_MATRIX)
    for point in [(1.0, 0.0), (0.0, 1.0), (3.0, -1.0)]:
        x, y = (M @ np.array(point)).tolist()
        assert abs(y - m * x) <= TOL


def test_6_8_the_exception_numpy_raises():
    cls = predicted("COLLAPSE_INVERSE_EXCEPTION")
    assert cls is np.linalg.LinAlgError
    with pytest.raises(cls):
        np.linalg.inv(np.array(shapes.COLLAPSE_MATRIX))


def test_6_9_inverse_of_a_shear():
    assert abs(predicted("INVERSE_OF_SHEAR_IS_SHEAR_WITH_K") + 2.0) <= TOL


def test_6_10_inverse_of_a_scaling():
    assert close(predicted("INVERSE_OF_SCALING_2_4"), [[0.5, 0.0], [0.0, 0.25]])
