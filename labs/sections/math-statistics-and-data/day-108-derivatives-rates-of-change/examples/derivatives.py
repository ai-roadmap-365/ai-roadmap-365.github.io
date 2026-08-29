"""The reference implementation: rates of change, computed from first principles.

Ten functions, all built on one idea -- a rate is a difference divided by the
interval it happened over -- and one NumPy-based helper at the end so the
from-scratch version can be checked against the library.

Read `starter/derivatives.py` and write your own before you read this one.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

Function = Callable[[float], float]


# ---------------------------------------------------------------------------
# 1. Average rate of change: rise over run, with real numbers
# ---------------------------------------------------------------------------


def average_rate(f: Function, a: float, b: float) -> float:
    """The average rate of change of f between a and b.

    Rise over run, and nothing more: how much the output changed, divided by
    how much the input changed. If f is distance in metres and the inputs are
    seconds, this is metres per second -- an average speed over the interval,
    exactly what a stopwatch and a tape measure would give you.

    Raises ZeroDivisionError when a == b, which is the honest thing to do: the
    question "how fast, over an interval of no width" has no answer, and the
    whole of today is about approaching that question rather than asking it.
    """
    if a == b:
        raise ZeroDivisionError(
            "average_rate needs an interval with width; a and b are both "
            f"{a!r}. The rate 'right here' is what the derivative is for."
        )
    return (f(b) - f(a)) / (b - a)


def shrinking_slopes(f: Function, a: float, widths: Sequence[float]) -> list[float]:
    """The average rate over [a, a + h] for each h, in the order given.

    Feed it widths that get smaller and watch the returned numbers settle. That
    settling is the limit, met as an observation rather than as a definition.
    """
    return [average_rate(f, a, a + h) for h in widths]


# ---------------------------------------------------------------------------
# 2. The two difference quotients
# ---------------------------------------------------------------------------


def forward_difference(f: Function, x: float, h: float) -> float:
    """Slope of the secant from x to x + h. The definition, stopped early.

    Error shrinks like h: halve the step and you roughly halve the error.
    """
    return (f(x + h) - f(x)) / h


def backward_difference(f: Function, x: float, h: float) -> float:
    """Slope of the secant from x - h to x. The forward rule facing the other way."""
    return (f(x) - f(x - h)) / h


def central_difference(f: Function, x: float, h: float) -> float:
    """Slope of the secant from x - h to x + h, straddling the point.

    This is the average of the forward and backward differences, and the
    averaging is why it is so much better: the two rules lean off the tangent in
    opposite directions by almost exactly the same amount, so their leading
    errors cancel. Error shrinks like h**2 -- halve the step and the error
    quarters -- for one extra function call over the forward rule, and none at
    all over computing forward and backward separately.
    """
    return (f(x + h) - f(x - h)) / (2.0 * h)


def second_difference(f: Function, x: float, h: float) -> float:
    """The rate of change of the rate of change: an approximate f''(x).

    Built by taking a central difference of central differences and letting the
    algebra collapse. Its sign is curvature: positive is a bowl, negative is a
    dome, and that is what tells a minimum from a maximum when the first
    derivative has said only 'flat'.

    Note the h**2 in the divisor. It magnifies rounding error far harder than
    the first-difference rules do, so the useful range of h is both narrower and
    larger here.
    """
    return (f(x + h) - 2.0 * f(x) + f(x - h)) / (h * h)


# ---------------------------------------------------------------------------
# 3. Measuring how wrong the approximation is
# ---------------------------------------------------------------------------


def error_curve(
    f: Function,
    x: float,
    exact_slope: float,
    widths: Sequence[float],
    rule: Callable[[Function, float, float], float],
) -> list[float]:
    """Absolute error of `rule` against a known exact slope, one entry per width.

    Only usable when you already know the right answer, which is exactly why the
    lab measures it on e**x rather than on something interesting: the point is
    to see the shape of the error, and you cannot see the shape of an error you
    cannot compute.
    """
    return [abs(rule(f, x, h) - exact_slope) for h in widths]


def best_step(widths: Sequence[float], errors: Sequence[float]) -> tuple[float, float]:
    """The (width, error) pair with the smallest error. The bottom of the U.

    Ties go to the first, which for a descending list of widths means the
    largest h that achieves the minimum -- the conservative choice, since a
    larger step sits further from the cancellation cliff.
    """
    if len(widths) != len(errors):
        raise ValueError(
            f"widths and errors must be the same length; got {len(widths)} and {len(errors)}"
        )
    if not widths:
        raise ValueError("best_step needs at least one width")
    index = min(range(len(errors)), key=lambda i: errors[i])
    return (widths[index], errors[index])


def is_u_shaped(errors: Sequence[float]) -> bool:
    """True when the errors fall to a single minimum and then rise again.

    Deliberately tolerant of the wobble at the bottom: rounding error is a
    random walk, not a smooth curve, so this asks only that the error at the
    large-h end and the error at the small-h end are both meaningfully worse
    than the best one in the middle, and that the minimum is not at either end.
    """
    if len(errors) < 3:
        return False
    index = min(range(len(errors)), key=lambda i: errors[i])
    if index == 0 or index == len(errors) - 1:
        return False
    best = errors[index]
    return errors[0] > 10.0 * best and errors[-1] > 10.0 * best


# ---------------------------------------------------------------------------
# 4. What a zero derivative does and does not tell you
# ---------------------------------------------------------------------------


def tangent_at(f: Function, x: float, h: float) -> tuple[float, float]:
    """(slope, intercept) of the tangent line to f at x, estimated centrally.

    The tangent is the line through (x, f(x)) with the derivative as its slope,
    so the intercept follows from y = mx + c rearranged: c = f(x) - m*x.
    """
    slope = central_difference(f, x, h)
    return (slope, f(x) - slope * x)


def classify_stationary_point(f: Function, x: float, h: float, tol: float) -> str:
    """Name what kind of point x is, from the first and second derivatives.

    Returns one of:
      'not stationary' -- the first derivative is not zero within tol
      'minimum'        -- flat, and curving upward
      'maximum'        -- flat, and curving downward
      'undecided'      -- flat, and the second derivative is zero too

    That last case is the honest one and the reason this function exists. A zero
    first derivative says the ground is level; it does not say whether you are
    at the bottom of a valley, the top of a hill, or on a flat step partway down
    a slope. The second derivative resolves two of those three, and when it is
    also zero it resolves nothing -- x**3 at 0 and x**4 at 0 are both flat with
    zero curvature and are a step and a minimum respectively.
    """
    first = central_difference(f, x, h)
    if abs(first) > tol:
        return "not stationary"
    second = second_difference(f, x, h)
    if second > tol:
        return "minimum"
    if second < -tol:
        return "maximum"
    return "undecided"


# ---------------------------------------------------------------------------
# 5. The same job, handed to NumPy
# ---------------------------------------------------------------------------


def numpy_gradient_slope(f: Function, x: float, h: float) -> float:
    """The derivative at x via numpy.gradient over a three-point sample.

    `np.gradient` differentiates SAMPLES rather than a function: you hand it
    values you already have and it returns a derivative estimate at every one of
    them. On the interior points it uses the central difference, which is why
    the middle of a three-point sample straddling x agrees with
    `central_difference` to the last bit. On the two ends it has nothing on one
    side, so it falls back to a one-sided rule -- which is exactly the forward
    or backward difference, and exactly as much worse.

    The spacing is passed as the scalar `h`. Handing `np.gradient` an array of
    coordinates instead is algebraically the same request and takes a different
    route through the arithmetic, so it lands a few units in the last place away;
    `numpy_gradient_slope_from_coordinates` below is that version, kept so the
    difference can be measured rather than argued about.
    """
    ys = np.array([f(x - h), f(x), f(x + h)], dtype=np.float64)
    return float(np.gradient(ys, h)[1])


def numpy_gradient_slope_from_coordinates(f: Function, x: float, h: float) -> float:
    """The same three-point estimate, with coordinates passed instead of spacing.

    Kept only to show that "the same formula" is a claim about the mathematics.
    With unevenly spaced coordinates NumPy must use a general weighted rule, and
    it uses that rule even when the coordinates happen to be evenly spaced -- so
    this returns a number a few units in the last place from the one above.
    """
    xs = np.array([x - h, x, x + h], dtype=np.float64)
    ys = np.array([f(v) for v in xs], dtype=np.float64)
    return float(np.gradient(ys, xs)[1])


def numpy_error_curve(
    f: Function,
    x: float,
    exact_slope: float,
    widths: Sequence[float],
    rule: Callable[[Function, float, float], float],
) -> np.ndarray:
    """`error_curve` as a float64 array, for plotting and for argmin.

    Same numbers, different container. The array form is what makes
    `errors.argmin()` and the log-log plot in the lesson one line each.
    """
    return np.array(error_curve(f, x, exact_slope, widths, rule), dtype=np.float64)
