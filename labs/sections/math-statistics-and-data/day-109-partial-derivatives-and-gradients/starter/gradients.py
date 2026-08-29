"""Exercise 1 -- eight functions to write. Your work goes here.

Each one raises NotImplementedError until you write it, and the test suite
SKIPS anything still unwritten rather than failing it. Your score only ever
counts work you actually attempted.

Check yourself from the LAB DIRECTORY (the one above this file):

    .venv/bin/pytest starter -q

Read each docstring before writing the body. Every one gives the formula and a
worked example small enough to check on paper.

The order matters. `partial` is the only one that touches f directly; every
other function here is built out of it, so if `partial` is wrong, everything
below inherits the error. Get it passing first.

The three helpers at the bottom are written for you.
"""

from __future__ import annotations

import numpy as np

from surfaces import H_DEFAULT, N_DIRECTIONS


# ===========================================================================
# The two that matter
# ===========================================================================


def partial(f, point, index, h=H_DEFAULT):
    """1.1 -- the partial derivative of f with respect to input `index`.

    Move coordinate `index` up by h and down by h, leave EVERY other
    coordinate exactly where it was, and divide the change in f by 2h:

        ( f(... x_i + h ...) - f(... x_i - h ...) ) / (2h)

    Three things to get right, in order of how often they are got wrong:

      * Copy the point before you modify it. `np.asarray(point, dtype=float)`
        then `.copy()` twice. If you mutate the caller's array, the tests will
        catch you, but your own code will be haunted.
      * Only ONE coordinate moves. That is the entire definition. A test
        watches which points f is actually called with.
      * Divide by 2h, not by h. Dividing by h gives an answer exactly twice
        too big, which is a satisfying bug because everything still looks
        plausible.

    Return a plain float, not a NumPy scalar: wrap the result in `float(...)`.

    >>> partial(lambda p: p[0] ** 2 + 3 * p[1] ** 2, (2.0, 1.0), 0)
    4.000000000026205
    """
    raise NotImplementedError("partial")


def gradient(f, point, h=H_DEFAULT):
    """1.2 -- the gradient: one partial derivative per input, as a vector.

    Call `partial` once for each coordinate of the point and put the results
    into a NumPy array, in order. Two or three lines.

    Return an array whose length matches the INPUT, not the number of
    dimensions the surface lives in: a function of two inputs has a
    two-component gradient, even though its graph is a surface in three
    dimensions.

    Use `np.asarray(point, dtype=float).size` to find out how many inputs
    there are rather than assuming two -- exercise 1.2 is tested on a function
    of three.

    >>> gradient(lambda p: p[0] ** 2 + 3 * p[1] ** 2, (1.0, 1.0)).round(6).tolist()
    [2.0, 6.0]
    """
    raise NotImplementedError("gradient")


# ===========================================================================
# Vector arithmetic -- Day 99, unchanged
# ===========================================================================


def magnitude(vector):
    """1.3 -- the length of a vector. Return a plain float.

    Day 99's Euclidean norm: the square root of the sum of the squares.
    `np.dot(v, v)` gives you that sum in one call.

    Applied to a gradient, this answers "how steep is the steepest way up".

    >>> magnitude([3.0, 4.0])
    5.0
    """
    raise NotImplementedError("magnitude")


def unit(vector):
    """1.4 -- the same direction, scaled to length exactly 1.

    Divide the vector by its magnitude. RAISE `ValueError` if the magnitude is
    zero, with a message containing the words "no direction" -- a zero vector
    has no direction to preserve, and returning NaNs instead of saying so
    would push the failure somewhere harder to find.

    >>> unit([3.0, 4.0]).tolist()
    [0.6, 0.8]
    """
    raise NotImplementedError("unit")


# ===========================================================================
# Directional derivatives -- Day 103's dot product, doing real work
# ===========================================================================


def directional_derivative(f, point, direction, h=H_DEFAULT):
    """1.5 -- how fast f changes if you walk from `point` along `direction`.

    Two lines. Normalise the direction with `unit`, then dot it with the
    gradient. Return a plain float.

    Normalising first is not tidiness. Without it, handing in an arrow twice
    as long would double the answer, and "the rate of change in this
    direction" would depend on how long an arrow you happened to draw.

    >>> f = lambda p: p[0] ** 2 + 3 * p[1] ** 2
    >>> round(directional_derivative(f, (1.0, 1.0), (1.0, 0.0)), 6)
    2.0
    """
    raise NotImplementedError("directional_derivative")


def directional_derivative_direct(f, point, direction, h=H_DEFAULT):
    """1.6 -- the same quantity, measured WITHOUT forming a gradient.

    Step h forward along the unit direction and h back along it, and divide by
    2h -- exactly `partial`, except that the step is along an arbitrary
    bearing instead of along an axis:

        ( f(p + h*u) - f(p - h*u) ) / (2h)

    No partials, no dot product, no assumption that the two routes agree.
    This function exists so that 1.5 can be CHECKED rather than believed, and
    the test that compares them is the most important one in the lab.

    >>> f = lambda p: p[0] ** 2 + 3 * p[1] ** 2
    >>> round(directional_derivative_direct(f, (1.0, 1.0), (0.0, 1.0)), 6)
    6.0
    """
    raise NotImplementedError("directional_derivative_direct")


def sweep_directions(f, point, n=None, h=H_DEFAULT):
    """1.7 -- try n bearings evenly spaced around the circle; report each rate.

    Return `(angles, rates)`, both NumPy arrays of length n:

      * `angles` -- n values from 0 up to but NOT including 2*pi. That is
        exactly `np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)`; including
        the endpoint would sample 0 and 2*pi as two different bearings when
        they are the same one.
      * `rates` -- for each angle a, the rate of change along the direction
        `(cos a, sin a)`, measured with `directional_derivative_direct` so
        that the gradient plays no part in producing the numbers.

    Default n to N_DIRECTIONS, imported at the top of this file.

    Two-input functions only; this is the case you can draw.

    >>> f = lambda p: p[0] ** 2 + 3 * p[1] ** 2
    >>> angles, rates = sweep_directions(f, (1.0, 1.0), n=4)
    >>> rates.round(6).tolist()
    [2.0, 6.0, -2.0, -6.0]
    """
    raise NotImplementedError("sweep_directions")


def forward_partial(f, point, index, h=H_DEFAULT):
    """1.8 -- the one-sided version, for the comparison in exercise 6.

        ( f(x + h) - f(x) ) / h

    Return a plain float.

    One evaluation cheaper than a central difference when you already have
    f(x), and markedly worse: its error shrinks like h where a central
    difference's shrinks like h squared. You will measure exactly how much
    worse.

    >>> round(forward_partial(lambda p: p[0] ** 2, (2.0,), 0, 0.1), 6)
    4.1
    """
    raise NotImplementedError("forward_partial")


# ===========================================================================
# Written for you. Read them -- the tests use them.
# ===========================================================================


def angle_degrees(vector):
    """The bearing of a 2-D vector from the positive x-axis, in [0, 360)."""
    v = np.asarray(vector, dtype=float)
    return float(np.degrees(np.arctan2(v[1], v[0])) % 360.0)


def angular_gap_degrees(a, b):
    """The smaller of the two ways round between two bearings, in degrees.

    Without the wrap-around, 359.6 and 0.1 would look 359.5 degrees apart
    instead of 0.5, and every steepest-ascent check would fail for a reason
    that has nothing to do with calculus.
    """
    raw = abs(a - b) % 360.0
    return float(min(raw, 360.0 - raw))


def contour_chord(f, contour, level, t, delta):
    """A unit vector along a contour of f, built WITHOUT using the gradient.

    Takes two points on the exact algebraic contour, at parameters t and
    t + delta, and returns the unit vector from the first to the second, the
    two points, and f at each of them -- so the caller can check the curve
    really did stay on one level rather than trust the algebra.

    Note what this does not do: it never rotates the gradient. Deriving the
    contour direction from the gradient and then observing that the two are
    perpendicular would prove nothing at all.
    """
    p = contour(level, t)
    q = contour(level, t + delta)
    return unit(q - p), p, q, f(p), f(q)
