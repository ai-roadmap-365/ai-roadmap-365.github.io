"""Numerical partial derivatives and gradients, built from nothing.

Eleven functions. The first two are the whole day: `partial` asks what happens
when you nudge ONE input and hold the rest still, and `gradient` collects one
of those per input into a vector. Everything else in this file is built out of
those two.

Nothing here knows anything about the functions it is handed. It cannot see
inside them, cannot differentiate them symbolically, and does not try. It
evaluates them at points and subtracts. That is both the strength (it works on
anything you can call) and the weakness (it costs two evaluations per input,
which is why nobody trains a neural network this way -- see the lesson's
alternatives section, and Day 110).
"""

from __future__ import annotations

import numpy as np

from surfaces import H_DEFAULT


def partial(f, point, index, h=H_DEFAULT):
    """The partial derivative of `f` with respect to input number `index`.

    Nudge coordinate `index` up by h and down by h, leave every other
    coordinate exactly where it was, and divide the change in f by the total
    distance moved, 2h. That is Day 108's central difference with one word
    added: "and hold everything else still".

        df/dx_i  ~  ( f(... x_i + h ...) - f(... x_i - h ...) ) / (2h)

    The forward difference ( f(x+h) - f(x) ) / h would also work and costs one
    fewer evaluation when you already have f(x). It is also markedly worse:
    its error shrinks like h where the central difference's shrinks like h
    squared. Script 06 measures both.
    """
    base = np.asarray(point, dtype=float)
    up = base.copy()
    down = base.copy()
    up[index] += h
    down[index] -= h
    return float((f(up) - f(down)) / (2.0 * h))


def forward_partial(f, point, index, h=H_DEFAULT):
    """The same thing with a one-sided step, kept only for the comparison."""
    base = np.asarray(point, dtype=float)
    up = base.copy()
    up[index] += h
    return float((f(up) - f(base)) / h)


def gradient(f, point, h=H_DEFAULT):
    """The gradient: one partial derivative per input, collected into a vector.

    This is the definition and there is nothing hidden in it. If the point has
    two coordinates you get a vector of two numbers; if it has three you get
    three; if it has a million you get a million, and the loop below is why
    nobody does it that way.

    Written with the nabla symbol as grad f, and it is a VECTOR living in the
    same space as the input, not a number and not a point on the surface.
    """
    base = np.asarray(point, dtype=float)
    return np.array([partial(f, base, i, h) for i in range(base.size)])


def magnitude(vector):
    """The length of a vector -- Day 99's Euclidean norm, unchanged.

    Applied to a gradient it answers "how steep is the steepest way up",
    in units of f per unit of distance travelled in the input space.
    """
    return float(np.sqrt(np.dot(np.asarray(vector, dtype=float),
                                np.asarray(vector, dtype=float))))


def unit(vector):
    """The same direction, scaled to length 1.

    A direction has to be a unit vector before a directional derivative means
    anything: without that, doubling the vector would double the answer and
    the "rate of change in this direction" would depend on how long an arrow
    you happened to draw.
    """
    v = np.asarray(vector, dtype=float)
    length = magnitude(v)
    if length == 0.0:
        raise ValueError("the zero vector has no direction")
    return v / length


def directional_derivative(f, point, direction, h=H_DEFAULT):
    """How fast f changes if you walk from `point` along `direction`.

    Two lines, and the second is Day 103 doing real work: normalise the
    direction, then dot it with the gradient. That the dot product is the
    right answer is not obvious and is not asserted here -- script 03 checks
    it against a direct measurement, which is a straight central difference
    taken ALONG the direction rather than along an axis.
    """
    u = unit(direction)
    return float(np.dot(gradient(f, point, h), u))


def directional_derivative_direct(f, point, direction, h=H_DEFAULT):
    """The same quantity measured without ever forming a gradient.

    Step h forward along the direction and h back along it, and divide by 2h.
    No partials, no dot product, no assumption that the two agree. This
    function exists to check the one above.
    """
    base = np.asarray(point, dtype=float)
    u = unit(direction)
    return float((f(base + h * u) - f(base - h * u)) / (2.0 * h))


def sweep_directions(f, point, n=None, h=H_DEFAULT):
    """Try n directions evenly spaced around the circle; report each rate.

    Returns (angles_in_radians, rates). Only meaningful for a function of two
    inputs, which is the case the reader can draw.
    """
    from surfaces import N_DIRECTIONS

    if n is None:
        n = N_DIRECTIONS
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    rates = np.array([
        directional_derivative_direct(f, point, np.array([np.cos(a), np.sin(a)]), h)
        for a in angles
    ])
    return angles, rates


def angle_degrees(vector):
    """The compass bearing of a 2-D vector, measured from the positive x-axis,
    reported in [0, 360) degrees so two angles can be compared directly."""
    v = np.asarray(vector, dtype=float)
    return float(np.degrees(np.arctan2(v[1], v[0])) % 360.0)


def angular_gap_degrees(a, b):
    """The smaller of the two ways round between two bearings, in degrees.

    Without the wrap-around, 359.6 and 0.1 would look 359.5 degrees apart
    instead of 0.5, and the steepest-ascent check would fail for a reason
    that has nothing to do with calculus.
    """
    raw = abs(a - b) % 360.0
    return float(min(raw, 360.0 - raw))


def contour_chord(f, contour, level, t, delta):
    """A unit vector along the contour of f, built without using the gradient.

    Takes two points on the exact algebraic contour, at parameters t and
    t + delta, and returns the unit vector from the first to the second, plus
    the two points. As delta shrinks the chord approaches the tangent, and the
    tangent is the thing the gradient is claimed to be perpendicular to.

    The value of f at both points is returned as well, so the caller can check
    that the parametrisation really does stay on one level rather than trust
    the algebra.
    """
    p = contour(level, t)
    q = contour(level, t + delta)
    return unit(q - p), p, q, f(p), f(q)
