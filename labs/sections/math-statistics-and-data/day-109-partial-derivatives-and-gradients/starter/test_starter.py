"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure message
prints both your answer and the real one.

Every test that exercises your code runs its whole body inside `written(...)`,
so a test is skipped if ANY function it needs is still unwritten -- not just
the first one. Python evaluates arguments before the call, so gating on one
function while calling another inside the arguments would let a
NotImplementedError escape and be reported as a failure. It would say
"attempted and wrong" about work you had not attempted, which is precisely the
lie this suite exists to avoid.
"""

import math

import numpy as np
import pytest

import answers
import surfaces as S
from gradients import (
    angle_degrees,
    angular_gap_degrees,
    contour_chord,
    directional_derivative,
    directional_derivative_direct,
    forward_partial,
    gradient,
    magnitude,
    partial,
    sweep_directions,
    unit,
)


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
    assert int(np.__version__.split(".")[0]) >= 2, "numpy 2 or later is importable"
    assert S.bowl((2.0, 1.0)) == 7.0, "surfaces.py loads and the bowl is the bowl"
    assert S.model_loss(S.START_PARAMS) == 22.5, "the model data is intact"


# -- Exercise 1: your gradients.py -------------------------------------------


def test_1_1_partial_on_the_bowl_in_x():
    got = written(lambda: partial(S.bowl, (2.0, 1.0), 0))
    assert got == pytest.approx(4.0, abs=S.GRADIENT_TOL)


def test_1_1_partial_on_the_bowl_in_y():
    got = written(lambda: partial(S.bowl, (2.0, 1.0), 1))
    assert got == pytest.approx(6.0, abs=S.GRADIENT_TOL)


def test_1_1_partial_divides_by_two_h_not_by_h():
    """The most common bug: an answer exactly twice too big."""
    got = written(lambda: partial(S.plane, (0.0, 0.0), 0))
    assert got != pytest.approx(6.0, abs=1e-6), "divide by 2h, not by h"
    assert got == pytest.approx(3.0, abs=S.GRADIENT_TOL)


def test_1_1_partial_holds_the_other_coordinate_completely_still():
    seen = []

    def spy(p):
        seen.append(tuple(float(v) for v in p))
        return S.product(p)

    written(lambda: partial(spy, (2.0, 5.0), 0))
    assert len(seen) == 2, "a central difference evaluates f exactly twice"
    assert {p[1] for p in seen} == {5.0}, "y must be identical in both calls"


def test_1_1_partial_does_not_mutate_the_point_it_was_given():
    point = np.array([1.0, 2.0])
    written(lambda: partial(S.bowl, point, 0))
    assert point.tolist() == [1.0, 2.0], "copy the point before nudging it"


def test_1_1_partial_returns_a_plain_float():
    got = written(lambda: partial(S.bowl, (1.0, 1.0), 0))
    assert isinstance(got, float), "wrap the result in float(...)"


@pytest.mark.parametrize("name", sorted(S.SURFACES))
@pytest.mark.parametrize("point", S.PROBE_POINTS)
@pytest.mark.parametrize("index", (0, 1))
def test_1_1_partial_on_every_surface_and_point(name, point, index):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    got = written(lambda: partial(f, point, index))
    assert got == pytest.approx(exact_gradient(point)[index], abs=S.GRADIENT_TOL)


def test_1_2_gradient_of_the_bowl():
    got = written(lambda: gradient(S.bowl, (1.0, 1.0)))
    assert got == pytest.approx([2.0, 6.0], abs=S.GRADIENT_TOL)


def test_1_2_gradient_returns_a_numpy_array():
    got = written(lambda: gradient(S.bowl, (1.0, 1.0)))
    assert isinstance(got, np.ndarray), "return an array, not a list or a tuple"


def test_1_2_gradient_has_one_entry_per_INPUT():
    got = written(lambda: gradient(S.bowl, (1.0, 1.0)))
    assert got.size == 2, "two inputs, two partials -- not three"


def test_1_2_gradient_works_on_a_function_of_three_inputs():
    got = written(lambda: gradient(S.model_loss, S.START_PARAMS))
    assert got.size == 3, "do not hard-code two coordinates"
    assert got == pytest.approx([-17.0, -18.0, -8.0], abs=S.GRADIENT_TOL)


@pytest.mark.parametrize("name", sorted(S.SURFACES))
@pytest.mark.parametrize("point", S.PROBE_POINTS)
def test_1_2_gradient_on_every_surface_and_point(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    got = written(lambda: gradient(f, point))
    assert got == pytest.approx(exact_gradient(point), abs=S.GRADIENT_TOL)


def test_1_3_magnitude_of_a_three_four_five_triangle():
    assert written(lambda: magnitude([3.0, 4.0])) == 5.0


def test_1_3_magnitude_of_the_zero_vector_is_zero():
    assert written(lambda: magnitude([0.0, 0.0])) == 0.0


def test_1_3_magnitude_returns_a_plain_float():
    assert isinstance(written(lambda: magnitude([1.0, 1.0])), float)


def test_1_3_magnitude_of_the_bowl_gradient_at_one_one():
    got = written(lambda: magnitude(gradient(S.bowl, (1.0, 1.0))))
    assert got == pytest.approx(math.sqrt(40.0), abs=1e-9)


def test_1_4_unit_scales_to_length_one():
    got = written(lambda: unit([3.0, 4.0]))
    assert got == pytest.approx([0.6, 0.8], abs=1e-15)


def test_1_4_unit_keeps_the_bearing():
    got = written(lambda: unit([2.0, 6.0]))
    assert angle_degrees(got) == pytest.approx(angle_degrees([2.0, 6.0]), abs=1e-9)


def test_1_4_unit_of_a_long_and_a_short_arrow_agree():
    a = written(lambda: unit([1.0, 2.0]))
    b = written(lambda: unit([50.0, 100.0]))
    assert a == pytest.approx(b, abs=1e-15)


def test_1_4_unit_raises_value_error_on_the_zero_vector():
    def call():
        with pytest.raises(ValueError, match="no direction"):
            unit([0.0, 0.0])
        return True

    assert written(call) is True


def test_1_5_directional_derivative_due_east_is_the_x_partial():
    got = written(lambda: directional_derivative(S.bowl, (1.0, 1.0), (1.0, 0.0)))
    assert got == pytest.approx(2.0, abs=S.GRADIENT_TOL)


def test_1_5_directional_derivative_due_north_is_the_y_partial():
    got = written(lambda: directional_derivative(S.bowl, (1.0, 1.0), (0.0, 1.0)))
    assert got == pytest.approx(6.0, abs=S.GRADIENT_TOL)


def test_1_5_directional_derivative_normalises_the_direction():
    """A longer arrow must not give a bigger answer."""
    short = written(lambda: directional_derivative(S.bowl, (1.0, 1.0), (1.0, 2.0)))
    long = written(lambda: directional_derivative(S.bowl, (1.0, 1.0), (1000.0, 2000.0)))
    assert short == pytest.approx(long, abs=1e-9), "normalise before dotting"


def test_1_5_a_direction_perpendicular_to_the_gradient_gives_zero():
    got = written(lambda: directional_derivative(S.bowl, (1.0, 1.0), (3.0, -1.0)))
    assert got == pytest.approx(0.0, abs=S.GRADIENT_TOL)


def test_1_6_direct_measurement_agrees_with_the_dot_product():
    """The most important test in the lab: two routes, one answer."""
    for direction in ((1.0, 1.0), (-1.0, 2.0), (7.0, 0.5), (-2.0, -5.0)):
        via = written(lambda d=direction: directional_derivative(S.bowl, (1.0, 1.0), d))
        direct = written(
            lambda d=direction: directional_derivative_direct(S.bowl, (1.0, 1.0), d)
        )
        assert via == pytest.approx(direct, abs=S.GRADIENT_TOL)


def test_1_6_direct_measurement_never_forms_a_gradient():
    """f must be evaluated exactly twice, not once per axis plus twice more."""
    calls = []

    def counted(p):
        calls.append(1)
        return S.bowl(p)

    written(lambda: directional_derivative_direct(counted, (1.0, 1.0), (1.0, 1.0)))
    assert len(calls) == 2, "two evaluations: one forward, one back"


def test_1_6_walking_backwards_negates_the_rate():
    forward = written(
        lambda: directional_derivative_direct(S.cubic, (2.0, -1.0), (1.0, 3.0))
    )
    backward = written(
        lambda: directional_derivative_direct(S.cubic, (2.0, -1.0), (-1.0, -3.0))
    )
    assert forward == pytest.approx(-backward, abs=1e-9)


def test_1_7_sweep_returns_two_arrays_of_the_right_length():
    angles, rates = written(lambda: sweep_directions(S.bowl, (1.0, 1.0), n=8))
    assert len(angles) == 8 and len(rates) == 8


def test_1_7_sweep_excludes_the_endpoint():
    """Sampling both 0 and 2*pi would count the same bearing twice."""
    angles, _rates = written(lambda: sweep_directions(S.bowl, (1.0, 1.0), n=4))
    assert float(angles[0]) == 0.0
    assert float(angles[-1]) == pytest.approx(1.5 * math.pi, abs=1e-12)


def test_1_7_sweep_of_four_gives_the_two_partials_and_their_negatives():
    _angles, rates = written(lambda: sweep_directions(S.bowl, (1.0, 1.0), n=4))
    assert rates == pytest.approx([2.0, 6.0, -2.0, -6.0], abs=S.GRADIENT_TOL)


def test_1_7_sweep_defaults_to_the_documented_number_of_directions():
    _angles, rates = written(lambda: sweep_directions(S.bowl, (1.0, 1.0)))
    assert len(rates) == S.N_DIRECTIONS


def test_1_8_forward_partial_on_a_square():
    got = written(lambda: forward_partial(S.bowl, (2.0, 1.0), 0, 0.1))
    assert got == pytest.approx(4.1, abs=1e-9), "((2.1)^2 - 2^2) / 0.1 = 4.1"


def test_1_8_forward_partial_evaluates_f_only_twice():
    calls = []

    def counted(p):
        calls.append(1)
        return S.bowl(p)

    written(lambda: forward_partial(counted, (1.0, 1.0), 0))
    assert len(calls) == 2


def test_1_8_forward_is_worse_than_central_at_the_default_step():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    c = written(lambda: abs(partial(S.cubic, (2.0, 1.0), 0) - exact))
    f = written(lambda: abs(forward_partial(S.cubic, (2.0, 1.0), 0) - exact))
    assert f > 1000 * c


# -- Exercise 1 (applied): the two facts the day exists for -------------------


@pytest.mark.parametrize("name,point", (
    ("bowl", (1.0, 1.0)),
    ("bowl", (0.25, 0.75)),
    ("product", (2.0, -1.0)),
    ("saddle", (1.5, 0.5)),
    ("cubic", (1.0, 1.0)),
))
def test_applied_the_gradient_wins_the_sweep(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    angles, rates = written(lambda: sweep_directions(f, point))
    best = int(np.argmax(rates))
    gap = angular_gap_degrees(
        float(np.degrees(angles[best])), angle_degrees(exact_gradient(point))
    )
    assert gap <= S.ANGLE_TOL_DEGREES


@pytest.mark.parametrize("name,point", (
    ("bowl", (1.0, 1.0)),
    ("product", (2.0, -1.0)),
    ("cubic", (1.0, 1.0)),
))
def test_applied_no_direction_beats_the_gradients_magnitude(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    _angles, rates = written(lambda: sweep_directions(f, point))
    assert float(np.max(rates)) <= magnitude(exact_gradient(point)) + S.GRADIENT_TOL


@pytest.mark.parametrize("name", sorted(S.CONTOURS))
@pytest.mark.parametrize("t", (0.4, 0.9, 1.4, 1.9))
def test_applied_the_gradient_is_perpendicular_to_the_contour(name, t):
    f, contour, level, _t0 = S.CONTOURS[name]
    result = written(lambda: contour_chord(f, contour, level, t, S.CONTOUR_DELTA))
    chord, p = result[0], result[1]
    g = written(lambda: unit(gradient(f, p)))
    assert abs(float(np.dot(g, chord))) < S.CONTOUR_DOT_TOL


@pytest.mark.parametrize("name", sorted(S.CONTOURS))
def test_applied_the_dot_product_shrinks_with_the_step(name):
    f, contour, level, t0 = S.CONTOURS[name]
    previous = None
    for k in (2, 3, 4, 5):
        delta = 10.0 ** (-k)
        result = written(lambda d=delta: contour_chord(f, contour, level, t0, d))
        chord, p = result[0], result[1]
        dot = abs(float(np.dot(written(lambda: unit(gradient(f, p))), chord)))
        if previous is not None:
            assert 9.0 < previous / dot < 11.0
        previous = dot


def test_applied_the_plane_has_the_same_gradient_everywhere():
    seen = [written(lambda p=p: gradient(S.plane, p))
            for p in ((0.0, 0.0), (1.0, 1.0), (-40.0, 17.5))]
    assert float(np.max(np.abs(np.array(seen) - seen[0]))) < S.GRADIENT_TOL


def test_applied_the_bowls_gradient_points_away_from_its_minimum():
    for point in ((0.5, 0.5), (1.0, 1.0), (2.0, 2.0), (-3.0, 1.0)):
        g = written(lambda p=point: unit(gradient(S.bowl, p)))
        assert float(np.dot(g, unit(np.array(point)))) > 0.0


@pytest.mark.parametrize("name,_kind,_why", S.STATIONARY_AT_ORIGIN)
def test_applied_all_three_stationary_points_have_a_zero_gradient(name, _kind, _why):
    g = written(lambda: gradient(S.SURFACES[name][0], (0.0, 0.0)))
    assert magnitude(g) < S.GRADIENT_TOL


def test_applied_the_cubics_truncation_error_is_exactly_h_squared():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    for h in (1e-1, 1e-2, 1e-3):
        error = written(lambda hh=h: partial(S.cubic, (2.0, 1.0), 0, hh) - exact)
        assert error == pytest.approx(h * h, rel=1e-5)


def test_applied_the_error_curve_is_u_shaped():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    errors = {k: written(lambda kk=k: abs(partial(S.cubic, (2.0, 1.0), 0, 10.0 ** -kk) - exact))
              for k in range(0, 15)}
    best = min(errors, key=errors.get)
    assert 0 < best < 14
    assert 10.0 ** -best == S.H_DEFAULT


def test_applied_a_numerical_gradient_costs_two_evaluations_per_parameter():
    calls = []

    def counted(p):
        calls.append(1)
        return S.model_loss(p)

    written(lambda: gradient(counted, S.START_PARAMS))
    assert len(calls) == 6


def test_applied_a_step_against_the_gradient_reduces_the_loss():
    g = written(lambda: gradient(S.model_loss, S.START_PARAMS))
    before = S.model_loss(S.START_PARAMS)
    assert S.model_loss(np.array(S.START_PARAMS) - 0.01 * g) < before


# -- Exercise 2: partial derivatives by hand ---------------------------------


def test_2_1_bowl_df_dx():
    assert predicted("BOWL_DF_DX_AT_2_1") == pytest.approx(4.0)


def test_2_2_bowl_df_dy():
    assert predicted("BOWL_DF_DY_AT_2_1") == pytest.approx(6.0)


def test_2_3_product_df_dx_at_1_0():
    assert predicted("PRODUCT_DF_DX_AT_1_0") == pytest.approx(0.0)


def test_2_4_product_df_dy_at_1_0():
    assert predicted("PRODUCT_DF_DY_AT_1_0") == pytest.approx(1.0)


def test_2_5_the_product_is_not_flat_there():
    assert predicted("IS_THE_PRODUCT_FLAT_AT_1_0") == "no"


def test_2_6_cubic_df_dx():
    assert predicted("CUBIC_DF_DX_AT_2_1") == pytest.approx(13.0)


def test_2_7_cubic_df_dy():
    assert predicted("CUBIC_DF_DY_AT_2_1") == pytest.approx(4.0)


def test_2_8_why_the_rounded_d():
    assert predicted("WHY_THE_ROUNDED_D") == (
        "it signals that the function has other inputs being held fixed"
    )


# -- Exercise 3: the gradient as a vector ------------------------------------


def test_3_1_bowl_gradient():
    assert predicted("BOWL_GRADIENT_AT_2_1") == pytest.approx([4.0, 6.0])


def test_3_2_gradient_length():
    assert predicted("BOWL_GRADIENT_LENGTH") == 2


def test_3_3_plane_gradient_far_away():
    assert predicted("PLANE_GRADIENT_FAR_AWAY") == pytest.approx([3.0, -2.0])


def test_3_4_bowl_gradient_magnitude():
    assert predicted("BOWL_GRADIENT_MAGNITUDE_AT_1_1") == pytest.approx(
        math.sqrt(40.0), abs=1e-3
    )


def test_3_5_what_the_magnitude_means():
    assert predicted("WHAT_THE_MAGNITUDE_MEANS") == (
        "the rate of climb in the steepest direction, per unit of distance"
    )


def test_3_6_one_partial_per_parameter():
    assert predicted("GRADIENT_LENGTH_FOR_500_PARAMETERS") == 500


# -- Exercise 4: directional derivatives -------------------------------------


def test_4_1_rate_due_east():
    assert predicted("BOWL_RATE_DUE_EAST") == pytest.approx(2.0)


def test_4_2_rate_due_north():
    assert predicted("BOWL_RATE_DUE_NORTH") == pytest.approx(6.0)


def test_4_3_rate_along_a_perpendicular():
    assert predicted("BOWL_RATE_ALONG_3_MINUS_1") == pytest.approx(0.0, abs=1e-9)


def test_4_4_largest_possible_rate():
    assert predicted("BOWL_LARGEST_POSSIBLE_RATE") == pytest.approx(
        math.sqrt(40.0), abs=1e-3
    )


def test_4_5_smallest_possible_rate():
    assert predicted("BOWL_SMALLEST_POSSIBLE_RATE") == pytest.approx(
        -math.sqrt(40.0), abs=1e-3
    )


def test_4_6_the_sweep_falls_just_short():
    assert predicted("WILL_THE_SWEEP_HIT_THE_MAXIMUM") == "no, slightly smaller"


def test_4_7_which_trig_function():
    assert predicted("WHICH_TRIG_FUNCTION") == "cos"


# -- Exercise 5: contours ----------------------------------------------------


def test_5_1_bowl_contours_are_ellipses():
    assert predicted("BOWL_CONTOUR_SHAPE") == "ellipses"


def test_5_2_plane_contours_are_straight_lines():
    assert predicted("PLANE_CONTOUR_SHAPE") == "straight lines"


def test_5_3_the_angle_is_ninety_degrees():
    assert predicted("ANGLE_BETWEEN_GRADIENT_AND_CONTOUR") == pytest.approx(90.0)


def test_5_4_nothing_happens_along_a_contour():
    assert predicted("WHAT_HAPPENS_ALONG_A_CONTOUR") == (
        "essentially nothing, to first order"
    )


def test_5_5_the_dot_product_is_first_order_in_delta():
    assert predicted("HOW_THE_DOT_PRODUCT_SHRINKS") == "it is divided by about 10"


def test_5_6_why_not_rotate_the_gradient():
    assert predicted("WHY_NOT_ROTATE_THE_GRADIENT") == (
        "rotating would make the result true by construction and prove nothing"
    )


# -- Exercise 6: step size ---------------------------------------------------


def test_6_1_central_difference_on_a_square():
    assert predicted("CENTRAL_DIFFERENCE_ON_A_SQUARE") == "2x"


def test_6_2_central_difference_error_on_a_cube():
    assert predicted("CENTRAL_DIFFERENCE_ERROR_ON_A_CUBE") == "h^2"


def test_6_3_second_order_means_a_hundredfold():
    assert predicted("TRUNCATION_ERROR_IMPROVEMENT_PER_DECADE") == 100


def test_6_4_what_goes_wrong_for_tiny_h():
    assert predicted("WHAT_GOES_WRONG_FOR_TINY_H") == (
        "subtracting two nearly equal floats loses the digits they shared"
    )


def test_6_5_best_h_for_central():
    assert predicted("BEST_H_FOR_CENTRAL") == pytest.approx(1e-05)


def test_6_6_best_h_for_forward():
    assert predicted("BEST_H_FOR_FORWARD") == pytest.approx(1e-08)


def test_6_7_tiny_h_is_much_worse():
    assert predicted("CENTRAL_AT_TINY_H_VERSUS_MODERATE_H") == "much worse"


# -- Exercise 7: the zero gradient -------------------------------------------


def test_7_1_bowl_gradient_at_origin():
    assert predicted("BOWL_GRADIENT_AT_ORIGIN") == pytest.approx([0.0, 0.0])


def test_7_2_saddle_gradient_at_origin():
    assert predicted("SADDLE_GRADIENT_AT_ORIGIN") == pytest.approx([0.0, 0.0])


def test_7_3_dome_gradient_at_origin():
    assert predicted("DOME_GRADIENT_AT_ORIGIN") == pytest.approx([0.0, 0.0])


def test_7_4_the_gradient_cannot_tell_them_apart():
    assert predicted("CAN_THE_GRADIENT_TELL_THEM_APART") == "no"


def test_7_5_the_name_is_stationary_point():
    assert predicted("NAME_FOR_A_ZERO_GRADIENT_POINT") == "stationary point"


def test_7_6_you_would_need_the_hessian():
    assert predicted("WHAT_YOU_NEED_INSTEAD") == "Hessian"


def test_7_7_the_saddle_rises_going_east():
    assert predicted("SADDLE_CHANGE_WALKING_EAST") == pytest.approx(0.25)


def test_7_8_and_falls_going_north():
    assert predicted("SADDLE_CHANGE_WALKING_NORTH") == pytest.approx(-0.25)


# -- Exercise 8: models and cost ---------------------------------------------


def test_8_1_model_loss():
    assert predicted("MODEL_LOSS_AT_ONES") == pytest.approx(22.5)


def test_8_2_dl_dw1():
    assert predicted("MODEL_DL_DW1") == pytest.approx(-17.0)


def test_8_3_dl_dw2():
    assert predicted("MODEL_DL_DW2") == pytest.approx(-18.0)


def test_8_4_dl_dc():
    assert predicted("MODEL_DL_DC") == pytest.approx(-8.0)


def test_8_5_six_evaluations():
    assert predicted("EVALUATIONS_FOR_A_3_PARAMETER_GRADIENT") == 6


def test_8_6_two_million_evaluations():
    assert predicted("EVALUATIONS_FOR_A_MILLION_PARAMETER_GRADIENT") == 2_000_000


def test_8_7_reverse_mode_does_not_scale_with_parameters():
    assert predicted("COST_OF_REVERSE_MODE_AUTODIFF") == (
        "stays roughly one forward pass plus one backward pass"
    )


def test_8_8_gradient_checking():
    assert predicted("WHAT_NUMERICAL_GRADIENTS_ARE_STILL_FOR") == (
        "checking that a hand-written backward pass is correct"
    )


def test_8_9_step_against_the_gradient():
    assert predicted("WHICH_WAY_TO_STEP_TO_REDUCE_A_LOSS") == "the negative gradient"
