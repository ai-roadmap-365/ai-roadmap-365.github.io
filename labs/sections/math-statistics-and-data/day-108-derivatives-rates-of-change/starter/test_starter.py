"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Every test that exercises your code runs its whole body inside `written(...)`,
so a test skips if ANY function it needs is still unwritten -- not just the
first one. Python evaluates arguments before the call, so gating on one
function while calling another inside the arguments would let a
NotImplementedError escape and be reported as a failure. That would say
"attempted and wrong" about work you had not attempted, which is precisely the
lie this suite exists to avoid.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import answers
import dataset
from derivatives import (
    average_rate,
    backward_difference,
    best_step,
    central_difference,
    classify_stationary_point,
    error_curve,
    forward_difference,
    is_u_shaped,
    numpy_error_curve,
    second_difference,
    shrinking_slopes,
    tangent_at,
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


def car_distance(t: float) -> float:
    return 4.0 * t * t


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    assert int(np.__version__.split(".")[0]) >= 2, "numpy 2 or later is importable"
    assert dataset.SETTLE_EXPECTED_SLOPES == [7.0, 6.1, 6.01, 6.001], "dataset.py loads"
    assert dataset.square(3.0) == 9.0, "the functions load"


# -- Exercise 1.1: average_rate ----------------------------------------------


def test_1_1_average_rate_over_the_whole_trip():
    assert written(average_rate, car_distance, 0.0, 6.0) == 24.0


def test_1_1_average_rate_over_the_fourth_second():
    assert written(average_rate, car_distance, 3.0, 4.0) == 28.0


def test_1_1_average_rate_of_a_straight_line_is_its_slope():
    def line(x: float) -> float:
        return 3.0 * x + 5.0

    assert written(average_rate, line, -100.0, 100.0) == 3.0


def test_1_1_average_rate_does_not_care_which_end_you_start_at():
    forwards = written(average_rate, dataset.square, 1.0, 4.0)
    backwards = written(average_rate, dataset.square, 4.0, 1.0)
    assert forwards == backwards == 5.0


def test_1_1_average_rate_refuses_a_zero_width_interval():
    def call():
        with pytest.raises(ZeroDivisionError) as caught:
            average_rate(car_distance, 3.0, 3.0)
        return str(caught.value)

    message = written(call)
    assert "interval with width" in message, (
        "raise ZeroDivisionError with a message containing 'interval with width'"
    )


# -- Exercise 1.2: shrinking_slopes ------------------------------------------


def test_1_2_shrinking_slopes_returns_one_value_per_width():
    slopes = written(shrinking_slopes, dataset.square, 3.0, dataset.SETTLE_WIDTHS)
    assert len(slopes) == len(dataset.SETTLE_WIDTHS)


def test_1_2_shrinking_slopes_are_six_plus_h():
    slopes = written(shrinking_slopes, dataset.square, 3.0, dataset.SETTLE_WIDTHS)
    for slope, expected in zip(slopes, dataset.SETTLE_EXPECTED_SLOPES):
        assert abs(slope - expected) < dataset.EXACT_TOL


def test_1_2_shrinking_slopes_settle_on_the_derivative():
    slopes = written(shrinking_slopes, dataset.square, 3.0, dataset.SETTLE_WIDTHS)
    gaps = [abs(s - 6.0) for s in slopes]
    assert gaps == sorted(gaps, reverse=True), "each interval must be closer than the last"
    assert gaps[-1] < 0.002


def test_1_2_shrinking_slopes_keeps_the_order_it_was_given():
    slopes = written(shrinking_slopes, dataset.square, 3.0, [0.001, 1.0])
    assert slopes[0] < slopes[1], "return the results in the order the widths came in"


# -- Exercise 2.1 to 2.3: the three difference quotients ---------------------


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_2_1_forward_difference_of_a_parabola(h):
    assert abs(written(forward_difference, dataset.square, 3.0, h) - (6.0 + h)) < 1e-9


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_2_2_backward_difference_of_a_parabola(h):
    assert abs(written(backward_difference, dataset.square, 3.0, h) - (6.0 - h)) < 1e-9


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_2_3_central_difference_is_exact_on_a_parabola(h):
    assert abs(written(central_difference, dataset.square, 3.0, h) - 6.0) < 1e-11


def test_2_3_central_difference_did_not_forget_the_two():
    """The commonest bug in the topic: dividing by h rather than by 2h."""
    value = written(central_difference, dataset.square, 3.0, 0.1)
    assert abs(value - 12.0) > 1.0, "this is exactly double the right answer: divide by 2 * h"
    assert abs(value - 6.0) < 1e-11


def test_2_3_central_difference_is_the_average_of_the_other_two():
    h = 0.1
    forward = written(forward_difference, dataset.exponential, 1.0, h)
    backward = written(backward_difference, dataset.exponential, 1.0, h)
    central = written(central_difference, dataset.exponential, 1.0, h)
    assert abs((forward + backward) / 2.0 - central) < 1e-14


def test_2_3_central_meets_its_documented_tolerance_on_the_exponential():
    error = abs(written(central_difference, dataset.exponential, 1.0, dataset.COMPARE_WIDTH) - math.e)
    assert error < dataset.CENTRAL_TOL


def test_2_1_forward_meets_its_documented_tolerance_on_the_exponential():
    error = abs(written(forward_difference, dataset.exponential, 1.0, dataset.COMPARE_WIDTH) - math.e)
    assert error < dataset.FORWARD_TOL


def test_2_3_central_beats_forward_by_a_thousandfold_at_the_same_step():
    h = dataset.COMPARE_WIDTH
    forward_error = abs(written(forward_difference, dataset.exponential, 1.0, h) - math.e)
    central_error = abs(written(central_difference, dataset.exponential, 1.0, h) - math.e)
    assert central_error * 1000.0 < forward_error


# -- Exercise 2.4: second_difference -----------------------------------------


def test_2_4_second_difference_of_a_parabola_is_two():
    value = written(second_difference, dataset.parabola, 2.0, dataset.STATIONARY_WIDTH)
    assert abs(value - 2.0) < dataset.SECOND_TOL


def test_2_4_second_difference_at_the_cubic_minimum_is_six():
    value = written(second_difference, dataset.cubic, 1.0, dataset.STATIONARY_WIDTH)
    assert abs(value - 6.0) < dataset.SECOND_TOL


def test_2_4_second_difference_at_the_cubic_maximum_is_minus_six():
    value = written(second_difference, dataset.cubic, -1.0, dataset.STATIONARY_WIDTH)
    assert abs(value + 6.0) < dataset.SECOND_TOL


def test_2_4_second_difference_did_not_forget_to_square_h():
    value = written(second_difference, dataset.parabola, 2.0, 0.01)
    assert abs(value - 0.02) > 1e-3, "dividing by h rather than h**2 gives 0.02 here"
    assert abs(value - 2.0) < dataset.SECOND_TOL


def test_2_4_second_difference_tracks_the_exact_second_derivative():
    for x in [-2.0, -0.5, 0.5, 2.0]:
        value = written(second_difference, dataset.cubic, x, dataset.STATIONARY_WIDTH)
        assert abs(value - dataset.cubic_second_derivative(x)) < dataset.SECOND_TOL


# -- Exercise 3.1: error_curve -----------------------------------------------


def test_3_1_error_curve_returns_one_error_per_width():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference)
    assert len(errors) == len(dataset.U_WIDTHS)


def test_3_1_error_curve_values_are_non_negative():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference)
    assert all(e >= 0.0 for e in errors), "an absolute error is never negative"


def test_3_1_error_curve_uses_the_rule_it_was_handed():
    forward_errors = written(error_curve, dataset.exponential, 1.0, math.e, [1e-3], forward_difference)
    central_errors = written(error_curve, dataset.exponential, 1.0, math.e, [1e-3], central_difference)
    assert forward_errors[0] > central_errors[0] * 100.0


def test_3_1_error_curve_on_a_parabola_is_exactly_h_for_the_forward_rule():
    errors = written(error_curve, dataset.square, 3.0, 6.0, [1.0, 0.1, 0.01], forward_difference)
    for error, h in zip(errors, [1.0, 0.1, 0.01]):
        assert abs(error - h) < 1e-9


# -- Exercise 3.2: best_step -------------------------------------------------


def test_3_2_best_step_finds_the_smallest_error():
    assert written(best_step, [1.0, 0.1, 0.01], [5.0, 0.5, 2.0]) == (0.1, 0.5)


def test_3_2_best_step_prefers_the_first_of_a_tie():
    assert written(best_step, [1.0, 0.1, 0.01], [2.0, 0.5, 0.5]) == (0.1, 0.5)


def test_3_2_best_step_rejects_mismatched_lengths():
    def call():
        with pytest.raises(ValueError):
            best_step([1.0, 2.0], [1.0])
        return True

    assert written(call)


def test_3_2_best_step_rejects_an_empty_grid():
    def call():
        with pytest.raises(ValueError):
            best_step([], [])
        return True

    assert written(call)


def test_3_2_best_step_on_the_real_central_curve():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference)
    h, error = written(best_step, dataset.U_WIDTHS, errors)
    assert error == min(errors)
    assert 1e-7 <= h <= 1e-4, "the bottom of the U for a central difference in float64"


def test_3_2_best_step_on_the_real_forward_curve():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, forward_difference)
    h, _ = written(best_step, dataset.U_WIDTHS, errors)
    assert 1e-9 <= h <= 1e-6, "the bottom of the U for a forward difference in float64"


# -- Exercise 3.3: is_u_shaped -----------------------------------------------


def test_3_3_is_u_shaped_accepts_a_clear_u():
    assert written(is_u_shaped, [100.0, 1.0, 0.01, 1.0, 100.0]) is True


def test_3_3_is_u_shaped_rejects_a_monotone_fall():
    assert written(is_u_shaped, [100.0, 10.0, 1.0, 0.1]) is False


def test_3_3_is_u_shaped_rejects_a_monotone_rise():
    assert written(is_u_shaped, [0.1, 1.0, 10.0, 100.0]) is False


def test_3_3_is_u_shaped_rejects_a_sequence_that_is_too_short():
    assert written(is_u_shaped, [1.0, 0.5]) is False


def test_3_3_the_real_central_curve_is_u_shaped():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference)
    assert written(is_u_shaped, errors) is True


def test_3_3_the_real_forward_curve_is_u_shaped():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, forward_difference)
    assert written(is_u_shaped, errors) is True


def test_3_3_both_ends_of_the_real_curve_are_far_worse_than_the_middle():
    errors = written(error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference)
    best = min(errors)
    assert errors[0] > 100.0 * best
    assert errors[-1] > 100.0 * best


# -- Exercise 4.1: classify_stationary_point ---------------------------------


@pytest.mark.parametrize(
    ("f", "x", "expected"),
    [
        (dataset.parabola, 2.0, "minimum"),
        (dataset.cubic, 1.0, "minimum"),
        (dataset.cubic, -1.0, "maximum"),
        (dataset.plain_cube, 0.0, "undecided"),
        (dataset.cubic, 0.0, "not stationary"),
        (dataset.exponential, 0.0, "not stationary"),
    ],
    ids=["parabola vertex", "cubic minimum", "cubic maximum", "flat step", "sloping cubic", "exponential"],
)
def test_4_1_classification(f, x, expected):
    verdict = written(classify_stationary_point, f, x, dataset.STATIONARY_WIDTH, dataset.STATIONARY_TOL)
    assert verdict == expected


def test_4_1_a_genuine_minimum_with_zero_curvature_is_also_undecided():
    verdict = written(
        classify_stationary_point, lambda x: x**4, 0.0, dataset.STATIONARY_WIDTH, dataset.STATIONARY_TOL
    )
    assert verdict == "undecided", (
        "x**4 at 0 IS a minimum, and no second derivative can show it -- "
        "reporting 'minimum' here would be a lie you got away with"
    )


# -- The written-for-you helpers, which start working when your code does ----


def test_tangent_at_three_is_six_x_minus_nine():
    slope, intercept = written(tangent_at, dataset.square, 3.0, dataset.COMPARE_WIDTH)
    assert abs(slope - 6.0) < dataset.CENTRAL_TOL
    assert abs(intercept + 9.0) < 1e-8


def test_numpy_error_curve_is_a_float64_array_of_your_errors():
    array = written(
        numpy_error_curve, dataset.exponential, 1.0, math.e, dataset.U_WIDTHS, central_difference
    )
    assert array.dtype == np.float64
    assert array.shape == (len(dataset.U_WIDTHS),)
    assert 1e-7 <= dataset.U_WIDTHS[int(array.argmin())] <= 1e-4


# -- Exercise 2: average rates ------------------------------------------------


def test_2_1_prediction_average_speed_whole_trip():
    assert predicted("AVERAGE_SPEED_WHOLE_TRIP") == 24.0


def test_2_2_prediction_average_speed_fourth_second():
    assert predicted("AVERAGE_SPEED_FOURTH_SECOND") == 28.0


def test_2_3_prediction_what_an_average_speed_means():
    assert predicted("AVERAGE_SPEED_MEANING") == (
        "the constant speed that would have covered the same distance in the same time"
    )


def test_2_4_prediction_zero_width_raises():
    assert predicted("ZERO_WIDTH_RAISES") is ZeroDivisionError


def test_2_5_prediction_simplified_secant_slope():
    assert predicted("SIMPLIFIED_SECANT_SLOPE") == "6 + h"


# -- Exercise 3: the shrinking interval ---------------------------------------


def test_3_1_prediction_settling_sequence():
    assert predicted("SETTLING_SEQUENCE") == [7.0, 6.1, 6.01, 6.001]


def test_3_2_prediction_settled_value():
    assert predicted("SETTLED_VALUE") == 6.0


def test_3_3_prediction_approach_direction():
    assert predicted("APPROACH_DIRECTION") == "above"


def test_3_4_prediction_tangent_line():
    assert predicted("TANGENT_LINE") == (6.0, -9.0)


def test_3_5_prediction_tangent_definition():
    assert predicted("TANGENT_DEFINITION") == (
        "a tangent line is the line the secant lines approach as the interval shrinks"
    )


# -- Exercise 4: the rules -----------------------------------------------------


def test_4_1_prediction_derivative_of_seven():
    assert predicted("DERIVATIVE_OF_SEVEN") == 0.0


def test_4_2_prediction_derivative_of_x5():
    assert predicted("DERIVATIVE_OF_X5_AT_1_5") == 25.3125


def test_4_3_prediction_derivative_of_5x2():
    assert predicted("DERIVATIVE_OF_5X2_AT_3") == 30.0


def test_4_4_prediction_derivative_of_sum():
    assert predicted("DERIVATIVE_OF_SUM_AT_2") == 16.0


def test_4_5_prediction_derivative_of_ln():
    assert predicted("DERIVATIVE_OF_LN_AT_4") == 0.25


def test_4_6_prediction_slope_of_2x_at_zero():
    assert predicted("SLOPE_OF_2X_AT_ZERO") == "the natural logarithm of 2, about 0.693"


def test_4_7_prediction_why_e_is_special():
    assert predicted("WHY_E_IS_SPECIAL") == (
        "e is the base for which the slope at x = 0 is exactly 1, so e**x is its own derivative"
    )


# -- Exercise 5: forward against central ---------------------------------------


def test_5_1_prediction_backward_on_a_parabola():
    assert predicted("BACKWARD_ON_A_PARABOLA") == "6 - h"


def test_5_2_prediction_central_on_a_parabola():
    assert predicted("CENTRAL_ON_A_PARABOLA") == 6.0


def test_5_3_prediction_forward_error_scaling():
    assert predicted("FORWARD_ERROR_SCALING") == "divided by 10"


def test_5_4_prediction_central_error_scaling():
    assert predicted("CENTRAL_ERROR_SCALING") == "divided by 100"


def test_5_5_prediction_central_function_calls():
    assert predicted("CENTRAL_FUNCTION_CALLS") == 2


def test_5_6_prediction_central_is_the_average_of():
    assert predicted("CENTRAL_IS_THE_AVERAGE_OF") == "the forward and backward differences"


# -- Exercise 6: the U ---------------------------------------------------------


def test_6_1_prediction_truncation_as_h_shrinks():
    assert predicted("TRUNCATION_AS_H_SHRINKS") == "shrinks"


def test_6_2_prediction_rounding_as_h_shrinks():
    assert predicted("ROUNDING_AS_H_SHRINKS") == "grows"


def test_6_3_prediction_absurdly_small_h_result():
    assert predicted("ABSURDLY_SMALL_H_RESULT") == 0.0


def test_6_4_prediction_absurdly_small_h_reason():
    assert predicted("ABSURDLY_SMALL_H_REASON") == (
        "exp(1 + 1e-300) and exp(1) are the same float64, so their difference is exactly zero"
    )


def test_6_5_prediction_best_central_h_band():
    assert predicted("BEST_CENTRAL_H_BAND") == "around 1e-6"


def test_6_6_prediction_best_forward_h_band():
    assert predicted("BEST_FORWARD_H_BAND") == "around 1e-8"


def test_6_7_prediction_tiny_h_is_not_more_careful():
    assert predicted("TINY_H_IS_MORE_CAREFUL") is False


# -- Exercise 7: flat points and corners ---------------------------------------


def test_7_1_prediction_which_is_the_maximum():
    assert predicted("WHICH_IS_THE_MAXIMUM") == "x = -1"


def test_7_2_prediction_second_derivative_at_plus_one():
    assert predicted("SECOND_DERIVATIVE_AT_PLUS_ONE") == 6.0


def test_7_3_prediction_cube_at_zero():
    assert predicted("CUBE_AT_ZERO") == "neither"


def test_7_4_prediction_cube_at_zero_classification():
    assert predicted("CUBE_AT_ZERO_CLASSIFICATION") == "undecided"


def test_7_5_prediction_what_zero_derivative_means():
    assert predicted("WHAT_ZERO_DERIVATIVE_MEANS") == "that the function is flat there, and nothing more"


def test_7_6_prediction_abs_forward_at_zero():
    assert predicted("ABS_FORWARD_AT_ZERO") == 1.0


def test_7_7_prediction_abs_backward_at_zero():
    assert predicted("ABS_BACKWARD_AT_ZERO") == -1.0


def test_7_8_prediction_abs_central_at_zero():
    assert predicted("ABS_CENTRAL_AT_ZERO") == 0.0


def test_7_9_prediction_abs_is_not_differentiable_at_zero():
    assert predicted("ABS_IS_DIFFERENTIABLE_AT_ZERO") is False


def test_7_10_prediction_relu_central_at_zero():
    assert predicted("RELU_CENTRAL_AT_ZERO") == 0.5


def test_7_11_prediction_how_to_detect_a_corner():
    assert predicted("HOW_TO_DETECT_A_CORNER") == "check whether the forward and backward differences disagree"


def test_7_12_prediction_why_derivatives_matter_for_ai():
    assert predicted("WHY_DERIVATIVES_MATTER_FOR_AI") == (
        "the derivative tells you which way to move to make the loss smaller"
    )
