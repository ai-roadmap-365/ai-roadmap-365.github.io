"""The reference suite: every claim in this lab, checked against a real value.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider

Nothing here reads source code or checks that a function exists. Every test
calls something and compares the result against a number that was either
derived by hand or derived from the error analysis written out in dataset.py.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import dataset as D
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
    numpy_gradient_slope,
    numpy_gradient_slope_from_coordinates,
    second_difference,
    shrinking_slopes,
    tangent_at,
)


# ---------------------------------------------------------------------------
# Average rate of change
# ---------------------------------------------------------------------------


def car_distance(t: float) -> float:
    return 4.0 * t * t


def test_car_table_matches_the_formula():
    assert [car_distance(t) for t in D.CAR_TIMES_S] == D.CAR_DISTANCE_M


def test_average_speed_over_the_whole_trip():
    assert average_rate(car_distance, 0.0, 6.0) == D.CAR_AVERAGE_SPEED_WHOLE_TRIP


def test_average_speed_over_the_fourth_second():
    assert average_rate(car_distance, 3.0, 4.0) == D.CAR_AVERAGE_SPEED_SECOND_FOUR


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(0.0, 1.0, 4.0), (1.0, 2.0, 12.0), (2.0, 3.0, 20.0), (3.0, 4.0, 28.0), (4.0, 5.0, 36.0), (5.0, 6.0, 44.0)],
)
def test_second_by_second_average_speeds(a, b, expected):
    assert average_rate(car_distance, a, b) == expected


def test_average_rate_is_symmetric_in_its_endpoints():
    assert average_rate(D.square, 1.0, 4.0) == average_rate(D.square, 4.0, 1.0)


def test_average_rate_over_a_zero_width_interval_refuses():
    with pytest.raises(ZeroDivisionError):
        average_rate(car_distance, 3.0, 3.0)


def test_the_refusal_explains_itself():
    with pytest.raises(ZeroDivisionError) as caught:
        average_rate(car_distance, 3.0, 3.0)
    assert "interval with width" in str(caught.value)


def test_average_rate_of_a_straight_line_is_the_same_everywhere():
    line = lambda x: 3.0 * x + 5.0  # noqa: E731 - deliberately inline
    assert average_rate(line, 0.0, 1.0) == 3.0
    assert average_rate(line, -100.0, 100.0) == 3.0


def test_instantaneous_speed_sits_between_its_neighbouring_averages():
    before = average_rate(car_distance, 2.0, 3.0)
    after = average_rate(car_distance, 3.0, 4.0)
    assert before < D.CAR_INSTANT_SPEED_AT_3 < after


# ---------------------------------------------------------------------------
# The shrinking interval
# ---------------------------------------------------------------------------


def test_shrinking_slopes_returns_one_value_per_width():
    slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
    assert len(slopes) == len(D.SETTLE_WIDTHS)


@pytest.mark.parametrize(("index", "expected"), list(enumerate(D.SETTLE_EXPECTED_SLOPES)))
def test_each_shrinking_slope_is_six_plus_h(index, expected):
    slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
    assert abs(slopes[index] - expected) < D.EXACT_TOL


def test_the_shrinking_sequence_converges_on_the_exact_derivative():
    slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
    gaps = [abs(s - D.SETTLE_EXACT_SLOPE) for s in slopes]
    assert gaps == sorted(gaps, reverse=True)
    assert gaps[-1] < 0.002


def test_the_sequence_approaches_from_above_for_a_convex_function():
    slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
    assert all(s > D.SETTLE_EXACT_SLOPE for s in slopes)


def test_shrinking_from_the_left_approaches_the_same_number():
    widths = [-w for w in D.SETTLE_WIDTHS]
    slopes = shrinking_slopes(D.square, D.SETTLE_POINT, widths)
    assert all(s < D.SETTLE_EXACT_SLOPE for s in slopes)
    assert abs(slopes[-1] - D.SETTLE_EXACT_SLOPE) < 0.002


def test_the_car_sequence_settles_on_twenty_four():
    slopes = shrinking_slopes(car_distance, 3.0, [1.0, 0.1, 0.01, 0.001])
    assert abs(slopes[-1] - D.CAR_INSTANT_SPEED_AT_3) < 0.005


def test_tangent_line_at_three_is_six_x_minus_nine():
    slope, intercept = tangent_at(D.square, 3.0, D.COMPARE_WIDTH)
    assert abs(slope - 6.0) < D.CENTRAL_TOL
    assert abs(intercept + 9.0) < 1e-8


def test_the_tangent_line_touches_the_curve_at_the_point():
    slope, intercept = tangent_at(D.square, 3.0, D.COMPARE_WIDTH)
    assert abs((slope * 3.0 + intercept) - D.square(3.0)) < 1e-9


# ---------------------------------------------------------------------------
# The rules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("case", "expected"),
    [(case, expected) for case, expected in zip(D.RULE_CASES, D.RULE_EXPECTED)],
    ids=[case[0] for case in D.RULE_CASES],
)
def test_each_rule_states_the_documented_exact_slope(case, expected):
    _, _, exact_derivative, x = case
    assert abs(exact_derivative(x) - expected) < 1e-15


@pytest.mark.parametrize("case", D.RULE_CASES, ids=[case[0] for case in D.RULE_CASES])
def test_each_rule_agrees_with_the_arithmetic(case):
    _, f, exact_derivative, x = case
    measured = central_difference(f, x, D.COMPARE_WIDTH)
    assert abs(measured - exact_derivative(x)) < D.RULE_TOL


def test_the_constant_rule_gives_exactly_zero():
    assert central_difference(lambda x: 7.0, 2.0, D.COMPARE_WIDTH) == 0.0


def test_the_sum_rule_is_the_sum_of_the_parts():
    at = 2.0
    both = central_difference(lambda x: x**2 + x**3, at, D.COMPARE_WIDTH)
    separately = central_difference(D.square, at, D.COMPARE_WIDTH) + central_difference(
        D.plain_cube, at, D.COMPARE_WIDTH
    )
    assert abs(both - separately) < D.RULE_TOL


def test_the_constant_multiple_rule_scales_the_slope():
    at = 3.0
    plain = central_difference(D.square, at, D.COMPARE_WIDTH)
    scaled = central_difference(lambda x: 5.0 * x * x, at, D.COMPARE_WIDTH)
    assert abs(scaled - 5.0 * plain) < D.RULE_TOL


@pytest.mark.parametrize(("base", "expected"), [(2.0, math.log(2.0)), (3.0, math.log(3.0)), (10.0, math.log(10.0))])
def test_the_slope_of_b_to_the_x_at_zero_is_the_natural_log_of_b(base, expected):
    measured = central_difference(lambda x: base**x, 0.0, D.COMPARE_WIDTH)
    assert abs(measured - expected) < 1e-8


def test_e_is_the_base_whose_slope_at_zero_is_one():
    measured = central_difference(D.exponential, 0.0, D.COMPARE_WIDTH)
    assert abs(measured - 1.0) < D.CENTRAL_TOL


@pytest.mark.parametrize("x", [0.0, 1.0, 2.5])
def test_the_exponential_is_proportional_to_its_own_derivative_with_constant_one(x):
    ratio = central_difference(D.exponential, x, D.COMPARE_WIDTH) / D.exponential(x)
    assert abs(ratio - 1.0) < 1e-9


@pytest.mark.parametrize("x", [0.5, 1.0, 4.0, 10.0])
def test_the_derivative_of_ln_is_one_over_x(x):
    measured = central_difference(D.natural_log, x, D.COMPARE_WIDTH)
    assert abs(measured - 1.0 / x) < 1e-7


# ---------------------------------------------------------------------------
# Forward, backward, central
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_forward_difference_of_x_squared_is_exactly_six_plus_h(h):
    assert abs(forward_difference(D.square, 3.0, h) - (6.0 + h)) < 1e-9


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_backward_difference_of_x_squared_is_exactly_six_minus_h(h):
    assert abs(backward_difference(D.square, 3.0, h) - (6.0 - h)) < 1e-9


@pytest.mark.parametrize("h", [1.0, 0.1, 0.01, 0.001])
def test_central_difference_is_exact_on_a_quadratic(h):
    assert abs(central_difference(D.square, 3.0, h) - 6.0) < 1e-11


def test_central_is_the_average_of_forward_and_backward():
    h = 0.1
    average = (forward_difference(D.exponential, 1.0, h) + backward_difference(D.exponential, 1.0, h)) / 2.0
    assert abs(average - central_difference(D.exponential, 1.0, h)) < 1e-14


def test_forward_difference_meets_its_documented_tolerance():
    error = abs(forward_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
    assert error < D.FORWARD_TOL


def test_central_difference_meets_its_documented_tolerance():
    error = abs(central_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
    assert error < D.CENTRAL_TOL


def test_central_beats_forward_by_at_least_a_thousandfold_at_the_same_step():
    forward_error = abs(forward_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
    central_error = abs(central_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
    assert central_error * 1000.0 < forward_error


@pytest.mark.parametrize("h", [1e-1, 1e-2, 1e-3, 1e-4, 1e-5])
def test_central_beats_forward_at_every_sensible_step(h):
    assert abs(central_difference(D.exponential, 1.0, h) - math.e) < abs(
        forward_difference(D.exponential, 1.0, h) - math.e
    )


@pytest.mark.parametrize("h", [1e-1, 1e-2, 1e-3])
def test_forward_error_falls_like_h(h):
    error = abs(forward_difference(D.exponential, 1.0, h) - math.e)
    predicted = (h / 2.0) * math.e
    assert 0.9 < error / predicted < 1.1


@pytest.mark.parametrize("h", [1e-2, 1e-3, 1e-4])
def test_central_error_falls_like_h_squared(h):
    error = abs(central_difference(D.exponential, 1.0, h) - math.e)
    predicted = (h * h / 6.0) * math.e
    assert 0.99 < error / predicted < 1.01


def test_halving_the_step_quarters_the_central_error():
    coarse = abs(central_difference(D.exponential, 1.0, 1e-2) - math.e)
    fine = abs(central_difference(D.exponential, 1.0, 5e-3) - math.e)
    assert 3.9 < coarse / fine < 4.1


def test_halving_the_step_halves_the_forward_error():
    coarse = abs(forward_difference(D.exponential, 1.0, 1e-2) - math.e)
    fine = abs(forward_difference(D.exponential, 1.0, 5e-3) - math.e)
    assert 1.9 < coarse / fine < 2.1


# ---------------------------------------------------------------------------
# The U-shaped error curve
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def forward_errors():
    return error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, forward_difference)


@pytest.fixture(scope="module")
def central_errors():
    return error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)


def test_the_grid_spans_the_documented_range():
    assert len(D.U_WIDTHS) == 27
    assert D.U_WIDTHS[0] == 1e-1
    assert D.U_WIDTHS[-1] == 1e-14
    assert D.U_WIDTHS == sorted(D.U_WIDTHS, reverse=True)


def test_error_curve_returns_one_error_per_width(forward_errors):
    assert len(forward_errors) == len(D.U_WIDTHS)


def test_the_forward_error_curve_is_u_shaped(forward_errors):
    assert is_u_shaped(forward_errors)


def test_the_central_error_curve_is_u_shaped(central_errors):
    assert is_u_shaped(central_errors)


def test_the_forward_minimum_is_not_at_either_end(forward_errors):
    index = forward_errors.index(min(forward_errors))
    assert 0 < index < len(forward_errors) - 1


def test_the_central_minimum_is_not_at_either_end(central_errors):
    index = central_errors.index(min(central_errors))
    assert 0 < index < len(central_errors) - 1


def test_the_largest_step_is_far_worse_than_the_best(central_errors):
    best = min(central_errors)
    assert central_errors[0] > 100.0 * best


def test_the_smallest_step_is_far_worse_than_the_best(central_errors):
    best = min(central_errors)
    assert central_errors[-1] > 100.0 * best


def test_the_error_falls_monotonically_down_the_truncation_side(central_errors):
    first_six = central_errors[:6]
    assert first_six == sorted(first_six, reverse=True)


def test_the_error_rises_over_the_last_stretch(central_errors):
    assert central_errors[-1] > central_errors[-6]


def test_best_step_finds_the_bottom(central_errors):
    h, error = best_step(D.U_WIDTHS, central_errors)
    assert error == min(central_errors)
    assert h == D.U_WIDTHS[central_errors.index(error)]


def test_the_best_central_step_is_in_the_documented_band(central_errors):
    h, _ = best_step(D.U_WIDTHS, central_errors)
    assert 1e-7 <= h <= 1e-4


def test_the_best_forward_step_is_in_the_documented_band(forward_errors):
    h, _ = best_step(D.U_WIDTHS, forward_errors)
    assert 1e-9 <= h <= 1e-6


def test_the_best_central_step_beats_the_best_forward_step(forward_errors, central_errors):
    _, forward_best = best_step(D.U_WIDTHS, forward_errors)
    _, central_best = best_step(D.U_WIDTHS, central_errors)
    assert central_best < forward_best


def test_the_measured_optimum_matches_the_balance_prediction(forward_errors, central_errors):
    forward_h, _ = best_step(D.U_WIDTHS, forward_errors)
    central_h, _ = best_step(D.U_WIDTHS, central_errors)
    assert 0.1 < forward_h / math.sqrt(2.0 * D.EPSILON) < 10.0
    assert 0.1 < central_h / (3.0 * D.EPSILON) ** (1.0 / 3.0) < 10.0


def test_a_thousandth_beats_a_millionth_of_a_millionth(central_errors):
    coarse = central_errors[D.U_WIDTHS.index(1e-3)]
    absurd = central_errors[D.U_WIDTHS.index(1e-12)]
    assert absurd > 100.0 * coarse


def test_an_absurdly_small_step_returns_exactly_zero():
    assert forward_difference(D.exponential, 1.0, 1e-300) == 0.0
    assert central_difference(D.exponential, 1.0, 1e-300) == 0.0


def test_the_two_sampled_values_become_the_same_float():
    assert math.exp(1.0 + 1e-300) == math.exp(1.0)


def test_is_u_shaped_rejects_a_monotone_sequence():
    assert not is_u_shaped([100.0, 10.0, 1.0, 0.1])


def test_is_u_shaped_rejects_a_sequence_that_is_too_short():
    assert not is_u_shaped([1.0, 0.5])


def test_is_u_shaped_accepts_a_clear_u():
    assert is_u_shaped([100.0, 1.0, 0.01, 1.0, 100.0])


def test_best_step_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        best_step([1.0, 2.0], [1.0])


def test_best_step_rejects_an_empty_grid():
    with pytest.raises(ValueError):
        best_step([], [])


def test_the_array_error_curve_holds_the_same_numbers(central_errors):
    array = numpy_error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)
    assert array.dtype == np.float64
    assert array.shape == (len(D.U_WIDTHS),)
    assert array.tolist() == central_errors


def test_argmin_agrees_with_best_step(central_errors):
    array = numpy_error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)
    h, _ = best_step(D.U_WIDTHS, central_errors)
    assert D.U_WIDTHS[int(array.argmin())] == h


# ---------------------------------------------------------------------------
# Stationary points and curvature
# ---------------------------------------------------------------------------

H = D.STATIONARY_WIDTH
TOL = D.STATIONARY_TOL


@pytest.mark.parametrize(
    ("f", "x"),
    [(D.parabola, 2.0), (D.cubic, 1.0), (D.cubic, -1.0), (D.plain_cube, 0.0)],
    ids=["parabola vertex", "cubic minimum", "cubic maximum", "cubic flat step"],
)
def test_the_first_derivative_is_zero_at_every_stationary_point(f, x):
    assert abs(central_difference(f, x, H)) < TOL


def test_the_parabola_vertex_gives_exactly_zero():
    assert central_difference(D.parabola, 2.0, H) == 0.0


def test_the_cubic_is_not_stationary_at_the_origin():
    assert abs(central_difference(D.cubic, 0.0, H)) > 1.0


def test_the_second_derivative_of_the_parabola_is_two():
    assert abs(second_difference(D.parabola, 2.0, H) - 2.0) < D.SECOND_TOL


def test_the_second_derivative_at_the_cubic_minimum_is_six():
    assert abs(second_difference(D.cubic, 1.0, H) - 6.0) < D.SECOND_TOL


def test_the_second_derivative_at_the_cubic_maximum_is_minus_six():
    assert abs(second_difference(D.cubic, -1.0, H) + 6.0) < D.SECOND_TOL


def test_the_second_derivative_at_the_flat_step_is_zero():
    assert abs(second_difference(D.plain_cube, 0.0, H)) < D.SECOND_TOL


def test_the_second_derivative_separates_the_minimum_from_the_maximum():
    assert second_difference(D.cubic, 1.0, H) > 0.0 > second_difference(D.cubic, -1.0, H)


def test_the_first_derivative_does_not_separate_them():
    at_minimum = central_difference(D.cubic, 1.0, H)
    at_maximum = central_difference(D.cubic, -1.0, H)
    assert abs(at_minimum) < TOL and abs(at_maximum) < TOL
    assert abs(at_minimum - at_maximum) < TOL


def test_the_second_difference_matches_the_exact_second_derivative_along_the_cubic():
    for x in [-2.0, -0.5, 0.5, 2.0]:
        assert abs(second_difference(D.cubic, x, H) - D.cubic_second_derivative(x)) < D.SECOND_TOL


@pytest.mark.parametrize(
    ("f", "x", "expected"),
    [
        (D.parabola, 2.0, "minimum"),
        (D.cubic, 1.0, "minimum"),
        (D.cubic, -1.0, "maximum"),
        (D.plain_cube, 0.0, "undecided"),
        (D.cubic, 0.0, "not stationary"),
        (D.square, 0.0, "minimum"),
        (D.exponential, 0.0, "not stationary"),
    ],
    ids=["parabola", "cubic min", "cubic max", "flat step", "sloping", "x squared", "exponential"],
)
def test_classification(f, x, expected):
    assert classify_stationary_point(f, x, H, TOL) == expected


def test_x_to_the_fourth_at_zero_is_also_undecided():
    assert classify_stationary_point(lambda x: x**4, 0.0, H, TOL) == "undecided"


def test_a_minimum_and_a_step_can_be_indistinguishable():
    step = (central_difference(D.plain_cube, 0.0, H), second_difference(D.plain_cube, 0.0, H))
    minimum = (central_difference(lambda x: x**4, 0.0, H), second_difference(lambda x: x**4, 0.0, H))
    assert abs(step[0] - minimum[0]) < TOL
    assert abs(step[1] - minimum[1]) < D.SECOND_TOL


@pytest.mark.parametrize("x", [-1.0, 0.5, 1.5, 2.5, 4.0])
def test_the_sign_of_the_derivative_points_towards_the_minimum(x):
    slope = central_difference(D.parabola, x, H)
    # A small step against the sign of the slope must land nearer the minimum.
    # The step is 0.1 rather than 1.0 because a step larger than the distance
    # to the minimum overshoots it -- which is Day 111's learning-rate problem,
    # arriving three days early.
    downhill = x - 0.1 * math.copysign(1.0, slope)
    assert abs(downhill - 2.0) < abs(x - 2.0)


@pytest.mark.parametrize("x", [-1.0, 0.5, 1.5, 2.5, 4.0])
def test_the_measured_parabola_slope_matches_the_exact_one(x):
    assert abs(central_difference(D.parabola, x, H) - D.parabola_derivative(x)) < D.SECOND_TOL


# ---------------------------------------------------------------------------
# Where no derivative exists
# ---------------------------------------------------------------------------


def test_the_forward_difference_of_abs_at_zero_is_plus_one():
    assert forward_difference(D.absolute, 0.0, D.CORNER_WIDTH) == D.ABS_FORWARD_AT_ZERO


def test_the_backward_difference_of_abs_at_zero_is_minus_one():
    assert backward_difference(D.absolute, 0.0, D.CORNER_WIDTH) == D.ABS_BACKWARD_AT_ZERO


def test_the_central_difference_of_abs_at_zero_is_zero():
    assert central_difference(D.absolute, 0.0, D.CORNER_WIDTH) == D.ABS_CENTRAL_AT_ZERO


@pytest.mark.parametrize("h", [1e-2, 1e-5, 1e-8, 1e-11, 1e-14])
def test_shrinking_h_never_reveals_a_limit_at_the_corner(h):
    assert central_difference(D.absolute, 0.0, h) == 0.0
    assert forward_difference(D.absolute, 0.0, h) == 1.0
    assert backward_difference(D.absolute, 0.0, h) == -1.0


def test_the_one_sided_rules_disagree_at_the_corner():
    gap = abs(
        forward_difference(D.absolute, 0.0, D.CORNER_WIDTH) - backward_difference(D.absolute, 0.0, D.CORNER_WIDTH)
    )
    assert gap == 2.0


def test_the_one_sided_rules_agree_where_a_derivative_exists():
    gap = abs(forward_difference(D.square, 3.0, D.CORNER_WIDTH) - backward_difference(D.square, 3.0, D.CORNER_WIDTH))
    assert gap < 1e-3


@pytest.mark.parametrize("h", [1e-2, 1e-3, 1e-5])
def test_the_second_difference_at_the_corner_diverges_like_two_over_h(h):
    curve = second_difference(D.absolute, 0.0, h)
    assert abs(curve - 2.0 / h) < 1e-6 * (2.0 / h)


def test_the_corner_curvature_grows_as_the_step_shrinks():
    coarse = second_difference(D.absolute, 0.0, 1e-2)
    fine = second_difference(D.absolute, 0.0, 1e-4)
    assert fine > 50.0 * coarse


def test_abs_is_differentiable_away_from_the_corner():
    assert abs(central_difference(D.absolute, 2.0, D.CORNER_WIDTH) - 1.0) < D.CENTRAL_TOL
    assert abs(central_difference(D.absolute, -2.0, D.CORNER_WIDTH) + 1.0) < D.CENTRAL_TOL


def test_relu_forward_at_zero_is_one():
    assert forward_difference(D.relu, 0.0, D.CORNER_WIDTH) == D.RELU_FORWARD_AT_ZERO


def test_relu_backward_at_zero_is_zero():
    assert backward_difference(D.relu, 0.0, D.CORNER_WIDTH) == D.RELU_BACKWARD_AT_ZERO


def test_relu_central_at_zero_is_one_half():
    assert central_difference(D.relu, 0.0, D.CORNER_WIDTH) == D.RELU_CENTRAL_AT_ZERO


def test_the_relu_central_value_is_neither_defensible_choice():
    value = central_difference(D.relu, 0.0, D.CORNER_WIDTH)
    assert value != 0.0
    assert value != 1.0


@pytest.mark.parametrize(("x", "expected"), [(-1.0, 0.0), (-0.5, 0.0), (0.5, 1.0), (1.0, 1.0)])
def test_relu_is_differentiable_away_from_zero(x, expected):
    assert abs(central_difference(D.relu, x, D.CORNER_WIDTH) - expected) < D.CENTRAL_TOL


def test_relu_on_the_flat_arm_is_exactly_zero():
    assert central_difference(D.relu, -1.0, D.CORNER_WIDTH) == 0.0


# ---------------------------------------------------------------------------
# NumPy
# ---------------------------------------------------------------------------


def test_numpy_gradient_with_scalar_spacing_is_our_central_difference():
    assert numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH) == central_difference(
        D.exponential, 1.0, D.COMPARE_WIDTH
    )


@pytest.mark.parametrize("x", [0.5, 1.0, 2.0])
def test_numpy_gradient_matches_at_several_points(x):
    assert numpy_gradient_slope(D.exponential, x, D.COMPARE_WIDTH) == central_difference(
        D.exponential, x, D.COMPARE_WIDTH
    )


def test_numpy_gradient_with_coordinates_differs_in_the_last_bits():
    scalar = numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH)
    coords = numpy_gradient_slope_from_coordinates(D.exponential, 1.0, D.COMPARE_WIDTH)
    assert scalar != coords
    assert abs(scalar - coords) < 1e-10


def test_both_numpy_routes_are_within_tolerance_of_the_truth():
    for value in (
        numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH),
        numpy_gradient_slope_from_coordinates(D.exponential, 1.0, D.COMPARE_WIDTH),
    ):
        assert abs(value - math.e) < D.CENTRAL_TOL


def test_numpy_gradient_edges_use_a_one_sided_rule():
    h = D.COMPARE_WIDTH
    x = 1.0
    ys = np.array([D.exponential(x - h), D.exponential(x), D.exponential(x + h)])
    edge = float(np.gradient(ys, h)[0])
    assert edge == forward_difference(D.exponential, x - h, h)


def test_numpy_gradient_edges_are_as_bad_as_the_forward_rule():
    h = D.COMPARE_WIDTH
    x = 1.0
    ys = np.array([D.exponential(x - h), D.exponential(x), D.exponential(x + h)])
    grad = np.gradient(ys, h)
    edge_error = abs(float(grad[0]) - math.exp(x - h))
    interior_error = abs(float(grad[1]) - math.e)
    assert edge_error > 1000.0 * interior_error


def test_numpy_is_version_two_or_later():
    assert int(np.__version__.split(".")[0]) >= 2


# ---------------------------------------------------------------------------
# The lab's own honesty
# ---------------------------------------------------------------------------


def test_every_documented_tolerance_is_larger_than_the_error_it_covers():
    assert abs(central_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e) < D.CENTRAL_TOL
    assert abs(forward_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e) < D.FORWARD_TOL
    assert abs(second_difference(D.parabola, 2.0, D.STATIONARY_WIDTH) - 2.0) < D.SECOND_TOL


def test_no_tolerance_is_so_loose_that_it_would_hide_a_real_error():
    # Each tolerance must reject an error one order of magnitude above the
    # bound it was derived from, or it is not testing anything.
    assert D.CENTRAL_TOL < 1e-8
    assert D.FORWARD_TOL < 1e-3
    assert D.SECOND_TOL < 1e-4
    assert D.STATIONARY_TOL < 1e-5


def test_epsilon_is_the_real_float64_epsilon():
    assert D.EPSILON == float(np.finfo(np.float64).eps)


def test_the_settle_widths_shrink_by_a_factor_of_ten_each_time():
    ratios = [D.SETTLE_WIDTHS[i] / D.SETTLE_WIDTHS[i + 1] for i in range(len(D.SETTLE_WIDTHS) - 1)]
    assert all(abs(r - 10.0) < 1e-9 for r in ratios)
