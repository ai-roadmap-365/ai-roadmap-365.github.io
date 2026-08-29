"""The reference suite: every claim this lab makes, checked against a value.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider

Nothing here reads source code or checks that a file exists. Every test calls
something and compares the answer to a number that was worked out by hand or
derived algebraically, with a tolerance stated in `surfaces.py` and justified
there rather than tuned until green.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

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

ALL_SURFACES = sorted(S.SURFACES)


# ==========================================================================
# 1. partial: one input moves, the rest hold still
# ==========================================================================

@pytest.mark.parametrize("name", ALL_SURFACES)
@pytest.mark.parametrize("point", S.PROBE_POINTS)
@pytest.mark.parametrize("index", (0, 1))
def test_partial_matches_the_hand_derived_value(name, point, index):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    assert partial(f, point, index) == pytest.approx(
        exact_gradient(point)[index], abs=S.GRADIENT_TOL
    )


def test_partial_leaves_the_other_coordinates_untouched():
    """The defining property. If the y coordinate moved, this is not a partial."""
    seen = []

    def spy(p):
        seen.append(tuple(float(v) for v in p))
        return S.product(p)

    partial(spy, (2.0, 5.0), 0)
    assert len(seen) == 2
    assert {p[1] for p in seen} == {5.0}, "y must be identical in both evaluations"
    assert sorted(p[0] for p in seen) == [2.0 - S.H_DEFAULT, 2.0 + S.H_DEFAULT]


def test_partial_does_not_mutate_the_point_it_was_given():
    point = np.array([1.0, 2.0])
    partial(S.bowl, point, 0)
    assert point.tolist() == [1.0, 2.0]


def test_partial_accepts_a_tuple_a_list_and_an_array_alike():
    answers = [
        partial(S.bowl, (1.0, 1.0), 0),
        partial(S.bowl, [1.0, 1.0], 0),
        partial(S.bowl, np.array([1.0, 1.0]), 0),
    ]
    assert answers[0] == answers[1] == answers[2]


def test_central_difference_is_exact_on_a_quadratic_for_any_step():
    """((x+h)^2 - (x-h)^2) / 2h = 2x algebraically, so h barely matters."""
    for h in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        assert partial(S.bowl, (2.0, 1.0), 0, h) == pytest.approx(4.0, abs=1e-7)


def test_a_zero_partial_does_not_mean_a_flat_point():
    """At (1, 0) on f = xy the x-slope is zero and the y-slope is 1."""
    assert partial(S.product, (1.0, 0.0), 0) == pytest.approx(0.0, abs=S.GRADIENT_TOL)
    assert partial(S.product, (1.0, 0.0), 1) == pytest.approx(1.0, abs=S.GRADIENT_TOL)


# ==========================================================================
# 2. gradient: the vector of partials
# ==========================================================================

@pytest.mark.parametrize("name", ALL_SURFACES)
@pytest.mark.parametrize("point", S.PROBE_POINTS)
def test_gradient_matches_the_hand_derived_vector(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    assert gradient(f, point) == pytest.approx(
        exact_gradient(point), abs=S.GRADIENT_TOL
    )


@pytest.mark.parametrize("name", ALL_SURFACES)
@pytest.mark.parametrize("point", S.PROBE_POINTS)
def test_gradient_is_exactly_the_partials_side_by_side(name, point):
    f = S.SURFACES[name][0]
    built = np.array([partial(f, point, 0), partial(f, point, 1)])
    assert gradient(f, point) == pytest.approx(built, abs=0.0)


def test_gradient_has_one_entry_per_input_not_one_per_dimension_of_the_surface():
    assert gradient(S.bowl, (1.0, 1.0)).size == 2
    assert gradient(S.model_loss, (1.0, 1.0, 1.0)).size == 3


def test_gradient_works_on_three_inputs():
    assert gradient(S.model_loss, S.START_PARAMS) == pytest.approx(
        S.model_loss_gradient(S.START_PARAMS), abs=S.GRADIENT_TOL
    )


def test_the_model_gradient_is_the_three_whole_numbers_worked_out_by_hand():
    assert S.model_loss(S.START_PARAMS) == 22.5
    assert S.model_loss_gradient(S.START_PARAMS).tolist() == [-17.0, -18.0, -8.0]


def test_gradient_returns_a_numpy_array_of_floats():
    g = gradient(S.bowl, (1.0, 1.0))
    assert isinstance(g, np.ndarray)
    assert g.dtype == np.float64


# ==========================================================================
# 3. magnitude and unit
# ==========================================================================

def test_magnitude_is_the_euclidean_norm_from_day_99():
    assert magnitude([3.0, 4.0]) == 5.0
    assert magnitude([1.0, 1.0]) == pytest.approx(math.sqrt(2.0))
    assert magnitude([0.0, 0.0]) == 0.0


def test_magnitude_of_the_bowl_gradient_at_one_one():
    """grad = (2, 6), so the length is sqrt(4 + 36) = sqrt(40)."""
    assert magnitude(gradient(S.bowl, (1.0, 1.0))) == pytest.approx(
        math.sqrt(40.0), abs=1e-9
    )


@pytest.mark.parametrize("point", S.PROBE_POINTS[:3])
def test_unit_has_length_one_and_keeps_the_bearing(point):
    g = gradient(S.cubic, point)
    u = unit(g)
    assert magnitude(u) == pytest.approx(1.0, abs=1e-12)
    assert angle_degrees(u) == pytest.approx(angle_degrees(g), abs=1e-9)


def test_unit_refuses_the_zero_vector_rather_than_dividing_by_zero():
    with pytest.raises(ValueError, match="no direction"):
        unit([0.0, 0.0])


def test_unit_of_a_long_arrow_and_a_short_one_in_the_same_direction_agree():
    assert unit([1.0, 2.0]) == pytest.approx(unit([50.0, 100.0]), abs=1e-15)


# ==========================================================================
# 4. directional derivatives -- Day 103's dot product doing real work
# ==========================================================================

DIRECTIONS = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (-1.0, 2.0),
              (3.0, -1.0), (-2.0, -5.0), (7.0, 0.5))


@pytest.mark.parametrize("direction", DIRECTIONS)
@pytest.mark.parametrize("name", ("bowl", "product", "cubic", "saddle"))
def test_dot_with_the_gradient_agrees_with_a_direct_measurement(name, direction):
    """The claim that grad . u IS the rate of change, checked without assuming it."""
    f = S.SURFACES[name][0]
    point = (1.0, 1.0)
    assert directional_derivative(f, point, direction) == pytest.approx(
        directional_derivative_direct(f, point, direction), abs=S.GRADIENT_TOL
    )


def test_a_partial_derivative_is_the_directional_derivative_along_an_axis():
    point = (1.0, 1.0)
    assert directional_derivative(S.bowl, point, (1.0, 0.0)) == pytest.approx(
        2.0, abs=S.GRADIENT_TOL
    )
    assert directional_derivative(S.bowl, point, (0.0, 1.0)) == pytest.approx(
        6.0, abs=S.GRADIENT_TOL
    )


def test_the_length_of_the_direction_arrow_does_not_change_the_answer():
    point = (1.0, 1.0)
    short = directional_derivative(S.bowl, point, (1.0, 2.0))
    long = directional_derivative(S.bowl, point, (1000.0, 2000.0))
    assert short == pytest.approx(long, abs=1e-9)


def test_walking_backwards_negates_the_rate():
    point = (2.0, -1.0)
    forward = directional_derivative(S.cubic, point, (1.0, 3.0))
    backward = directional_derivative(S.cubic, point, (-1.0, -3.0))
    assert forward == pytest.approx(-backward, abs=1e-9)


def test_a_direction_perpendicular_to_the_gradient_gives_zero():
    """grad of the bowl at (1, 1) is (2, 6); (3, -1) dots to 3*2 - 1*6 = 0."""
    assert directional_derivative(S.bowl, (1.0, 1.0), (3.0, -1.0)) == pytest.approx(
        0.0, abs=S.GRADIENT_TOL
    )


# ==========================================================================
# 5. steepest ascent -- the first fact that must be demonstrated
# ==========================================================================

SWEEP_TRIALS = (
    ("bowl", (1.0, 1.0)),
    ("bowl", (0.25, 0.75)),
    ("bowl", (3.0, -2.0)),
    ("bowl", (1.0, 0.4)),
    ("product", (2.0, -1.0)),
    ("saddle", (1.5, 0.5)),
    ("cubic", (1.0, 1.0)),
    ("plane", (-2.0, 4.0)),
)


@pytest.mark.parametrize("name,point", SWEEP_TRIALS)
def test_the_best_of_360_directions_is_the_gradient_direction(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    angles, rates = sweep_directions(f, point)
    best = int(np.argmax(rates))
    gap = angular_gap_degrees(
        float(np.degrees(angles[best])), angle_degrees(exact_gradient(point))
    )
    assert gap <= S.ANGLE_TOL_DEGREES


@pytest.mark.parametrize("name,point", SWEEP_TRIALS)
def test_no_direction_at_all_beats_the_gradients_own_magnitude(name, point):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    _angles, rates = sweep_directions(f, point)
    steepest = magnitude(exact_gradient(point))
    assert float(np.max(rates)) <= steepest + S.GRADIENT_TOL


@pytest.mark.parametrize("name,point", SWEEP_TRIALS)
def test_the_winning_rate_is_the_magnitude_times_cosine_of_the_sampling_gap(name, point):
    """Day 103's geometric dot product, to nine decimal places."""
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    angles, rates = sweep_directions(f, point)
    best = int(np.argmax(rates))
    gap = angular_gap_degrees(
        float(np.degrees(angles[best])), angle_degrees(exact_gradient(point))
    )
    ratio = float(np.max(rates)) / magnitude(exact_gradient(point))
    assert ratio == pytest.approx(math.cos(math.radians(gap)), abs=1e-9)


def test_the_steepest_descent_is_the_exact_opposite_bearing():
    angles, rates = sweep_directions(S.bowl, (1.0, 1.0))
    up = float(np.degrees(angles[int(np.argmax(rates))]))
    down = float(np.degrees(angles[int(np.argmin(rates))]))
    assert angular_gap_degrees(up, down) == pytest.approx(180.0, abs=1e-9)
    assert float(np.max(rates)) == pytest.approx(-float(np.min(rates)), abs=1e-6)


def test_the_two_flattest_bearings_are_ninety_degrees_from_the_gradient():
    point = (1.0, 1.0)
    angles, rates = sweep_directions(S.bowl, point)
    bearing = angle_degrees(S.bowl_gradient(point))
    for i in np.argsort(np.abs(rates))[:2]:
        off = angular_gap_degrees(float(np.degrees(angles[i])), bearing)
        assert off == pytest.approx(90.0, abs=S.ANGLE_TOL_DEGREES)


def test_the_residual_gap_is_bounded_by_the_sampling_not_by_the_calculus():
    """The gap can never exceed half the spacing between sampled bearings.

    Note what this test does NOT assert. The obvious version -- that a finer
    sweep always gives a strictly smaller gap -- is false, and was found to be
    false here: the bowl's gradient at (1, 1) has bearing 71.5651 degrees, and
    both a 60-direction sweep (every 6 degrees) and a 360-direction sweep
    (every 1 degree) land on 72, so both leave exactly the same 0.4349-degree
    gap. Sampling more finely guarantees a smaller BOUND, not a smaller gap on
    any particular bearing.
    """
    point = (1.0, 1.0)
    bearing = angle_degrees(S.bowl_gradient(point))
    gaps = {}
    for n in (60, 360, 3600):
        angles, rates = sweep_directions(S.bowl, point, n=n)
        best = int(np.argmax(rates))
        gap = angular_gap_degrees(float(np.degrees(angles[best])), bearing)
        gaps[n] = gap
        assert gap <= 180.0 / n, (n, gap)
    assert gaps[60] == pytest.approx(gaps[360], abs=1e-12)
    assert gaps[3600] < gaps[360]
    assert gaps[3600] < 0.05


# ==========================================================================
# 6. perpendicular to the contour -- the second fact
# ==========================================================================

@pytest.mark.parametrize("name", sorted(S.CONTOURS))
@pytest.mark.parametrize("t", (0.4, 0.9, 1.4, 1.9))
def test_the_parametrised_contour_really_does_hold_f_constant(name, t):
    """Checked BEFORE the contour is used, so the algebra is not taken on trust."""
    f, contour, level, _t0 = S.CONTOURS[name]
    assert f(contour(level, t)) == pytest.approx(level, abs=1e-12)


@pytest.mark.parametrize("name", sorted(S.CONTOURS))
@pytest.mark.parametrize("t", (0.4, 0.9, 1.4, 1.9))
def test_the_gradient_is_perpendicular_to_a_step_along_the_contour(name, t):
    f, contour, level, _t0 = S.CONTOURS[name]
    chord, p, _q, _fp, _fq = contour_chord(f, contour, level, t, S.CONTOUR_DELTA)
    assert abs(float(np.dot(unit(gradient(f, p)), chord))) < S.CONTOUR_DOT_TOL


@pytest.mark.parametrize("name", sorted(S.CONTOURS))
def test_the_dot_product_shrinks_in_step_with_the_contour_step(name):
    """The honest form of 'it goes to zero': first-order, ten for ten."""
    f, contour, level, t0 = S.CONTOURS[name]
    previous = None
    for k in (2, 3, 4, 5, 6):
        delta = 10.0 ** (-k)
        chord, p, _q, _fp, _fq = contour_chord(f, contour, level, t0, delta)
        dot = abs(float(np.dot(unit(gradient(f, p)), chord)))
        if previous is not None:
            assert 9.0 < previous / dot < 11.0
        previous = dot


def test_the_exact_tangent_and_the_exact_gradient_dot_to_exactly_zero():
    """No tolerance needed: the algebra cancels term for term."""
    level = 4.0
    a = math.sqrt(level)
    b = math.sqrt(level / 3.0)
    for t in (0.0, 0.4, 0.9, 1.4, 1.9, 2.7):
        p = S.bowl_contour(level, t)
        tangent = np.array([-a * math.sin(t), b * math.cos(t)])
        assert abs(float(np.dot(tangent, S.bowl_gradient(p)))) < 1e-14


def test_a_step_along_the_contour_changes_f_far_less_than_a_step_across_it():
    point = np.array([1.0, 1.0])
    g = gradient(S.bowl, point)
    along = unit(np.array([-g[1], g[0]]))
    across = unit(g)
    step = 0.001
    gain_along = abs(S.bowl(point + step * along) - S.bowl(point))
    gain_across = abs(S.bowl(point + step * across) - S.bowl(point))
    assert gain_across > 100 * gain_along


def test_the_gradients_length_predicts_the_gain_of_a_small_step_up_it():
    point = np.array([1.0, 1.0])
    g = gradient(S.bowl, point)
    step = 0.001
    measured = S.bowl(point + step * unit(g)) - S.bowl(point)
    assert measured == pytest.approx(magnitude(g) * step, abs=1e-4)


# ==========================================================================
# 7. linear and quadratic
# ==========================================================================

@pytest.mark.parametrize("point", ((0.0, 0.0), (1.0, 1.0), (-40.0, 17.5),
                                   (0.001, 0.002), (7.5, -3.25)))
def test_the_gradient_of_a_plane_is_the_same_vector_everywhere(point):
    assert gradient(S.plane, point) == pytest.approx([3.0, -2.0], abs=S.GRADIENT_TOL)


def test_the_planes_gradient_never_varies_between_points():
    seen = [gradient(S.plane, p) for p in ((0.0, 0.0), (1.0, 1.0), (-40.0, 17.5))]
    assert float(np.max(np.abs(np.array(seen) - seen[0]))) < S.GRADIENT_TOL


@pytest.mark.parametrize("point", ((0.5, 0.5), (1.0, 1.0), (2.0, 2.0),
                                   (4.0, 4.0), (-3.0, 1.0)))
def test_the_bowls_gradient_points_away_from_its_minimum(point):
    outward = float(np.dot(unit(gradient(S.bowl, point)), unit(np.array(point))))
    assert outward > 0.0


def test_the_bowls_gradient_grows_with_distance_from_the_minimum():
    lengths = [magnitude(gradient(S.bowl, (r, r))) for r in (0.5, 1.0, 2.0, 4.0)]
    assert lengths == sorted(lengths)
    assert lengths[1] == pytest.approx(2.0 * lengths[0], rel=1e-6)


def test_the_negative_gradient_does_not_point_straight_at_the_minimum_on_an_ellipse():
    """The mismatch that makes gradient descent zig-zag. Real, and measured."""
    point = (1.0, 1.0)
    back = angle_degrees(-gradient(S.bowl, point))
    straight = angle_degrees(-np.array(point))
    assert angular_gap_degrees(back, straight) > 20.0


# ==========================================================================
# 8. the zero gradient, and what it cannot tell you
# ==========================================================================

@pytest.mark.parametrize("name,kind,_why", S.STATIONARY_AT_ORIGIN)
def test_all_three_surfaces_have_a_zero_gradient_at_the_origin(name, kind, _why):
    del kind, _why
    assert magnitude(gradient(S.SURFACES[name][0], (0.0, 0.0))) < S.GRADIENT_TOL


def test_the_three_zero_gradients_are_indistinguishable_from_each_other():
    vectors = [gradient(S.SURFACES[n][0], (0.0, 0.0))
               for n, _k, _w in S.STATIONARY_AT_ORIGIN]
    for v in vectors[1:]:
        assert v == pytest.approx(vectors[0], abs=S.GRADIENT_TOL)


def test_but_the_points_themselves_are_completely_different():
    radius = 0.1
    verdicts = {}
    for name, _kind, _why in S.STATIONARY_AT_ORIGIN:
        f = S.SURFACES[name][0]
        changes = [f(radius * np.array([math.cos(a), math.sin(a)])) - f(np.zeros(2))
                   for a in np.radians(np.arange(0, 360, 45))]
        up = sum(1 for c in changes if c > 1e-12)
        down = sum(1 for c in changes if c < -1e-12)
        verdicts[name] = (up > 0, down > 0)
    assert verdicts["bowl"] == (True, False)     # a minimum: only up
    assert verdicts["dome"] == (False, True)     # a maximum: only down
    assert verdicts["saddle"] == (True, True)    # a saddle: both


def test_the_saddle_rises_along_x_and_falls_along_y():
    assert S.saddle((0.5, 0.0)) > 0.0
    assert S.saddle((0.0, 0.5)) < 0.0
    assert S.saddle((0.5, 0.5)) == 0.0


def test_near_a_saddle_the_gradient_is_small_without_being_zero():
    lengths = [magnitude(gradient(S.saddle, (r, r))) for r in (1.0, 0.1, 0.01)]
    assert lengths[0] > lengths[1] > lengths[2] > 0.0


# ==========================================================================
# 9. step size, and Day 108's U-curve
# ==========================================================================

@pytest.mark.parametrize("h", (1e-1, 1e-2, 1e-3))
def test_the_cubics_truncation_error_is_exactly_h_squared(h):
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    error = partial(S.cubic, (2.0, 1.0), 0, h) - exact
    assert error == pytest.approx(h * h, rel=1e-5)


def test_the_error_curve_is_u_shaped_rather_than_monotonic():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    errors = {k: abs(partial(S.cubic, (2.0, 1.0), 0, 10.0 ** -k) - exact)
              for k in range(0, 15)}
    best = min(errors, key=errors.get)
    assert 0 < best < 14, "the best step is in the middle, not at either end"
    assert errors[0] > errors[best] < errors[14]


def test_the_default_step_sits_at_the_bottom_of_that_curve():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    errors = {k: abs(partial(S.cubic, (2.0, 1.0), 0, 10.0 ** -k) - exact)
              for k in range(0, 15)}
    assert 10.0 ** -min(errors, key=errors.get) == S.H_DEFAULT


def test_too_small_a_step_is_worse_than_a_step_a_trillion_times_bigger():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    tiny = abs(partial(S.cubic, (2.0, 1.0), 0, 1e-14) - exact)
    large = abs(partial(S.cubic, (2.0, 1.0), 0, 1e-1) - exact)
    assert tiny > large


def test_the_central_difference_beats_the_forward_one_at_the_default_step():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    central = abs(partial(S.cubic, (2.0, 1.0), 0, S.H_DEFAULT) - exact)
    forward = abs(forward_partial(S.cubic, (2.0, 1.0), 0, S.H_DEFAULT) - exact)
    assert forward > 1000 * central


def test_the_forward_differences_error_falls_like_h_not_h_squared():
    exact = float(S.cubic_gradient((2.0, 1.0))[0])
    errors = [abs(forward_partial(S.cubic, (2.0, 1.0), 0, h) - exact)
              for h in (1e-1, 1e-2, 1e-3)]
    assert errors[0] / errors[1] == pytest.approx(10.0, rel=0.05)
    assert errors[1] / errors[2] == pytest.approx(10.0, rel=0.05)


def test_roundoff_grows_with_the_size_of_f_and_the_bound_predicts_it():
    """Found by watching an assertion fail at (1000, -1000). Kept, and checked."""
    eps = float(np.finfo(float).eps)
    for point in ((1000.0, -1000.0), (100000.0, -100000.0), (10000000.0, -10000000.0)):
        error = abs(partial(S.plane, point, 0) - 3.0)
        predicted = eps * abs(S.plane(point)) / (2.0 * S.H_DEFAULT)
        assert error < 3.0 * predicted
        assert error > predicted / 100.0


def test_the_numerical_gradient_stops_meeting_the_labs_tolerance_far_from_home():
    """The honest boundary on every other tolerance in this file."""
    assert abs(partial(S.plane, (1000.0, -1000.0), 0) - 3.0) > S.GRADIENT_TOL


# ==========================================================================
# 10. numpy.gradient does a related, different job
# ==========================================================================

def _grid():
    xs = np.linspace(0.0, 4.0, 9)
    ys = np.linspace(0.0, 4.0, 9)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    return xs, ys, gx, gy


def test_numpy_gradient_is_exact_in_the_interior_of_a_sampled_quadratic():
    xs, ys, X, Y = _grid()
    gx, gy = np.gradient(X * X + 3.0 * Y * Y, xs, ys)
    assert gx[2, 2] == pytest.approx(2.0 * xs[2], abs=1e-12)
    assert gy[2, 2] == pytest.approx(6.0 * ys[2], abs=1e-12)


def test_numpy_gradient_defaults_to_first_order_at_the_boundary():
    """A real default worth knowing: the corner of an exact quadratic is wrong."""
    xs, ys, X, Y = _grid()
    gx, gy = np.gradient(X * X + 3.0 * Y * Y, xs, ys)
    assert gx[0, 0] == pytest.approx(0.5, abs=1e-12)
    assert gy[0, 0] == pytest.approx(1.5, abs=1e-12)
    assert gx[0, 0] != pytest.approx(0.0, abs=1e-6)


def test_edge_order_two_fixes_that_corner_exactly():
    xs, ys, X, Y = _grid()
    gx, gy = np.gradient(X * X + 3.0 * Y * Y, xs, ys, edge_order=2)
    assert gx[0, 0] == pytest.approx(0.0, abs=1e-12)
    assert gy[0, 0] == pytest.approx(0.0, abs=1e-12)


def test_numpy_gradients_error_on_a_cubic_is_the_grid_spacing_squared():
    """Same h^2 law -- but h is the sampling, which you cannot choose."""
    xs, ys, X, Y = _grid()
    spacing = float(xs[1] - xs[0])
    gx, _gy = np.gradient(X ** 3 + X * Y * Y, xs, ys, edge_order=2)
    exact = 3.0 * xs[4] ** 2 + ys[4] ** 2
    assert abs(gx[4, 4] - exact) == pytest.approx(spacing ** 2, abs=1e-12)


def test_our_gradient_gets_the_same_point_right_because_it_chooses_its_own_step():
    xs, ys, _X, _Y = _grid()
    point = (float(xs[4]), float(ys[4]))
    assert gradient(S.cubic, point) == pytest.approx(
        S.cubic_gradient(point), abs=S.GRADIENT_TOL
    )


def test_numpy_gradient_returns_a_field_not_a_vector():
    """The shape difference IS the conceptual difference."""
    xs, ys, X, Y = _grid()
    gx, _gy = np.gradient(X * X + 3.0 * Y * Y, xs, ys)
    assert gx.shape == (9, 9)
    assert gradient(S.bowl, (1.0, 1.0)).shape == (2,)


# ==========================================================================
# 11. one partial per parameter
# ==========================================================================

def test_the_loss_is_the_mean_of_the_four_squared_residuals():
    w1, w2, c = S.START_PARAMS
    by_hand = sum((w1 * a + w2 * b + c - y) ** 2 for a, b, y in S.SAMPLES) / 4
    assert S.model_loss(S.START_PARAMS) == by_hand == 22.5


def test_a_numerical_gradient_costs_exactly_two_evaluations_per_parameter():
    calls = []

    def counted(p):
        calls.append(1)
        return S.model_loss(p)

    gradient(counted, S.START_PARAMS)
    assert len(calls) == 2 * len(S.START_PARAMS)


def test_a_small_step_against_the_gradient_reduces_the_loss():
    before = S.model_loss(S.START_PARAMS)
    moved = np.array(S.START_PARAMS) - 0.01 * S.model_loss_gradient(S.START_PARAMS)
    assert S.model_loss(moved) < before


def test_a_small_step_ALONG_the_gradient_increases_it():
    before = S.model_loss(S.START_PARAMS)
    moved = np.array(S.START_PARAMS) + 0.01 * S.model_loss_gradient(S.START_PARAMS)
    assert S.model_loss(moved) > before


def test_too_large_a_step_overshoots_and_ends_up_worse_than_the_start():
    before = S.model_loss(S.START_PARAMS)
    moved = np.array(S.START_PARAMS) - 0.2 * S.model_loss_gradient(S.START_PARAMS)
    assert S.model_loss(moved) > before


def test_the_three_parameter_gradient_still_obeys_steepest_ascent():
    """No picture, same fact: no direction beats the gradient's own length."""
    rng = np.random.default_rng(S.SEED)
    point = S.START_PARAMS
    g = S.model_loss_gradient(point)
    best = magnitude(g)
    for _ in range(200):
        direction = unit(rng.normal(size=3))
        rate = directional_derivative_direct(S.model_loss, point, direction)
        assert rate <= best + 1e-6


def test_the_seeded_generator_is_stated_and_reproducible():
    first = np.random.default_rng(S.SEED).normal(size=3)
    second = np.random.default_rng(S.SEED).normal(size=3)
    assert first.tolist() == second.tolist()


# ==========================================================================
# 12. housekeeping
# ==========================================================================

def test_every_surface_in_the_registry_has_a_matching_exact_gradient():
    for name, (f, exact_gradient, expression, gradient_expression) in S.SURFACES.items():
        assert callable(f) and callable(exact_gradient), name
        assert expression and gradient_expression, name
        assert gradient(f, (1.0, 1.0)) == pytest.approx(
            exact_gradient((1.0, 1.0)), abs=S.GRADIENT_TOL
        ), name


def test_the_tolerances_are_stated_in_one_place_and_are_not_zero():
    for value in (S.H_DEFAULT, S.GRADIENT_TOL, S.CONTOUR_DELTA,
                  S.CONTOUR_DOT_TOL, S.ANGLE_TOL_DEGREES):
        assert value > 0.0


def test_the_gradient_tolerance_has_real_headroom_over_the_worst_probe():
    worst = 0.0
    for name in ALL_SURFACES:
        f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
        for point in S.PROBE_POINTS:
            worst = max(worst, float(np.max(np.abs(
                gradient(f, point) - exact_gradient(point)))))
    assert worst < S.GRADIENT_TOL
    assert S.GRADIENT_TOL / worst > 10.0, "the tolerance is not merely scraping past"
