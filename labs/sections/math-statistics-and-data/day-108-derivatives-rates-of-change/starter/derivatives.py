"""Exercise 1 -- ten functions to write. Your work goes here.

Each function raises NotImplementedError until you write it, and the test suite
SKIPS anything still unwritten rather than failing it. So your score only ever
counts work you actually attempted.

Check yourself from the LAB DIRECTORY (the one above this file):

    .venv/bin/pytest starter -q

Read each docstring before you write the body. Every one gives you the formula
in words, and a worked example small enough to check on paper.

One rule for the whole file: no calculus. Nothing here differentiates a formula
symbolically. Every function is allowed to do exactly one thing -- call `f` at
points you choose and do arithmetic on what comes back -- which is the honest
situation you are in whenever the function is a model rather than an equation.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

Function = Callable[[float], float]


# ===========================================================================
# 1. Average rate of change
# ===========================================================================


def average_rate(f: Function, a: float, b: float) -> float:
    """1.1 -- rise over run between a and b.

    How much the output changed, divided by how much the input changed:

        ( f(b) - f(a) ) / ( b - a )

    If a and b are equal there is no interval and no answer, so RAISE
    ZeroDivisionError with a message containing the words "interval with
    width". Do not return 0.0 and do not return nan: the point of the whole day
    is that this question genuinely has no answer, and a function that invents
    one is teaching the wrong lesson.

    >>> average_rate(lambda x: x * x, 3.0, 4.0)
    7.0
    >>> average_rate(lambda x: 4.0 * x * x, 0.0, 6.0)
    24.0
    """
    raise NotImplementedError("average_rate")


def shrinking_slopes(f: Function, a: float, widths: Sequence[float]) -> list[float]:
    """1.2 -- the average rate over [a, a + h], one entry per h, in order.

    One line if you use a list comprehension over `widths` and call
    `average_rate`. Do not reimplement rise over run here.

    >>> shrinking_slopes(lambda x: x * x, 3.0, [1.0, 0.1])
    [7.0, 6.100000000000007]
    """
    raise NotImplementedError("shrinking_slopes")


# ===========================================================================
# 2. The three difference quotients
# ===========================================================================


def forward_difference(f: Function, x: float, h: float) -> float:
    """2.1 -- the slope of the secant from x to x + h.

        ( f(x + h) - f(x) ) / h

    >>> forward_difference(lambda x: x * x, 3.0, 0.1)
    6.100000000000012
    """
    raise NotImplementedError("forward_difference")


def backward_difference(f: Function, x: float, h: float) -> float:
    """2.2 -- the slope of the secant from x - h to x.

        ( f(x) - f(x - h) ) / h

    >>> backward_difference(lambda x: x * x, 3.0, 0.1)
    5.899999999999999
    """
    raise NotImplementedError("backward_difference")


def central_difference(f: Function, x: float, h: float) -> float:
    """2.3 -- the slope of the secant from x - h to x + h, straddling x.

        ( f(x + h) - f(x - h) ) / (2 * h)

    Watch the 2. Forgetting it halves every answer you get, and halving is not
    obviously wrong when you do not already know the right value -- which is
    the single most common bug in this whole topic.

    >>> central_difference(lambda x: x * x, 3.0, 0.1)
    6.000000000000005
    """
    raise NotImplementedError("central_difference")


def second_difference(f: Function, x: float, h: float) -> float:
    """2.4 -- an estimate of f''(x): the rate of change of the rate of change.

        ( f(x + h) - 2 * f(x) + f(x - h) ) / (h * h)

    Read it as: how far does the middle value sag below the average of its two
    neighbours? Sagging down is positive, a bowl. Bulging up is negative, a
    dome.

    Note the h SQUARED in the divisor, which is why this rule is far more
    sensitive to a badly chosen h than the first-difference rules are.

    >>> round(second_difference(lambda x: x * x, 3.0, 0.001), 6)
    2.0
    """
    raise NotImplementedError("second_difference")


# ===========================================================================
# 3. Measuring the error
# ===========================================================================


def error_curve(
    f: Function,
    x: float,
    exact_slope: float,
    widths: Sequence[float],
    rule: Callable[[Function, float, float], float],
) -> list[float]:
    """3.1 -- the absolute error of `rule` against a known answer, one per width.

    `rule` is one of your own functions above, passed in as a value. Call it as
    `rule(f, x, h)`.

    >>> error_curve(lambda x: x * x, 3.0, 6.0, [1.0, 0.1], forward_difference)
    [1.0, 0.10000000000001208]
    """
    raise NotImplementedError("error_curve")


def best_step(widths: Sequence[float], errors: Sequence[float]) -> tuple[float, float]:
    """3.2 -- the (width, error) pair with the smallest error: the bottom of the U.

    Raise ValueError if the two sequences differ in length, and ValueError if
    they are empty. Ties go to the FIRST minimum found, which for a descending
    list of widths is the largest h that achieves it -- the safer choice,
    because a larger step sits further from the cancellation cliff.

    >>> best_step([1.0, 0.1, 0.01], [5.0, 0.5, 2.0])
    (0.1, 0.5)
    """
    raise NotImplementedError("best_step")


def is_u_shaped(errors: Sequence[float]) -> bool:
    """3.3 -- True when the errors fall to an interior minimum and rise again.

    Be deliberately tolerant. Rounding error is a random walk rather than a
    smooth curve, so do NOT demand a monotone descent -- that would be a test
    demanding something untrue, which is worse than no test.

    Ask three things:
      * there are at least three entries;
      * the smallest error is NOT the first or the last entry;
      * both the first and the last entry are more than ten times the smallest.

    >>> is_u_shaped([100.0, 1.0, 0.01, 1.0, 100.0])
    True
    >>> is_u_shaped([100.0, 10.0, 1.0, 0.1])
    False
    """
    raise NotImplementedError("is_u_shaped")


# ===========================================================================
# 4. What a zero derivative does and does not tell you
# ===========================================================================


def classify_stationary_point(f: Function, x: float, h: float, tol: float) -> str:
    """4.1 -- name the kind of point x is, from the first two derivatives.

    Return exactly one of these strings:

        "not stationary"  the central difference is larger than tol in size
        "minimum"         flat, and the second difference is above  +tol
        "maximum"         flat, and the second difference is below  -tol
        "undecided"       flat, and the second difference is inside +/- tol

    That last one is the important one, and returning it is not a cop-out. A
    zero first derivative says the ground is level. It does not say whether you
    are at the bottom of a valley, the top of a hill, or on a flat step partway
    down a slope, and when the curvature is zero as well, nothing here can
    separate x**3 at 0 (a step) from x**4 at 0 (a genuine minimum). Reporting
    "minimum" there would be a confident lie.

    >>> classify_stationary_point(lambda x: (x - 2.0) ** 2 + 1.0, 2.0, 1e-4, 1e-6)
    'minimum'
    >>> classify_stationary_point(lambda x: x ** 3, 0.0, 1e-4, 1e-6)
    'undecided'
    """
    raise NotImplementedError("classify_stationary_point")


# ===========================================================================
# Written for you -- read these, the tests use them
# ===========================================================================


def tangent_at(f: Function, x: float, h: float) -> tuple[float, float]:
    """(slope, intercept) of the tangent line to f at x.

    The tangent passes through (x, f(x)) with the derivative as its slope, so
    rearranging y = mx + c gives c = f(x) - m*x. This calls YOUR
    central_difference, so it starts working the moment exercise 2.3 does.
    """
    slope = central_difference(f, x, h)
    return (slope, f(x) - slope * x)


def numpy_error_curve(
    f: Function,
    x: float,
    exact_slope: float,
    widths: Sequence[float],
    rule: Callable[[Function, float, float], float],
) -> np.ndarray:
    """Your error_curve as a float64 array, so `.argmin()` and a plot are one line."""
    return np.array(error_curve(f, x, exact_slope, widths, rule), dtype=np.float64)
