"""The invented data, the functions, the step sizes and the tolerances.

Everything in this lab is computed from the definitions below. Nothing is read
from disk, nothing is downloaded, and no number here was chosen to make a test
pass -- every tolerance is derived in `TOLERANCES` from the two error terms that
actually govern a difference quotient, and the derivation is written out beside
it so you can check the arithmetic yourself.

Read this file. Do not change it: the reference tests compare captured values
against the constants here, so editing one moves the goalposts rather than
fixing anything.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# The car, which is where the day starts
# ---------------------------------------------------------------------------

# Invented. A car's distance from a marker post, in metres, sampled once a
# second for six seconds. The numbers were chosen so the arithmetic is doable in
# your head: they are 4 * t**2, so the car is accelerating steadily.
CAR_TIMES_S = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
CAR_DISTANCE_M = [0.0, 4.0, 16.0, 36.0, 64.0, 100.0, 144.0]

# Average speed over the whole six seconds: (144 - 0) / (6 - 0).
CAR_AVERAGE_SPEED_WHOLE_TRIP = 24.0
# Average speed over the fourth second only: (64 - 36) / (4 - 3).
CAR_AVERAGE_SPEED_SECOND_FOUR = 28.0
# The speedometer reading at t = 3 exactly, which is d/dt of 4t**2 = 8t.
CAR_INSTANT_SPEED_AT_3 = 24.0


# ---------------------------------------------------------------------------
# The functions the lab differentiates
# ---------------------------------------------------------------------------


def square(x: float) -> float:
    """f(x) = x**2. Exact derivative 2x. The whole lab's first example."""
    return x * x


def square_derivative(x: float) -> float:
    return 2.0 * x


def cubic(x: float) -> float:
    """f(x) = x**3 - 3x. Stationary at x = -1 (a maximum) and x = +1 (a minimum)."""
    return x * x * x - 3.0 * x


def cubic_derivative(x: float) -> float:
    return 3.0 * x * x - 3.0


def cubic_second_derivative(x: float) -> float:
    return 6.0 * x


def parabola(x: float) -> float:
    """f(x) = (x - 2)**2 + 1. Vertex at x = 2, where the slope is exactly zero."""
    return (x - 2.0) ** 2 + 1.0


def parabola_derivative(x: float) -> float:
    return 2.0 * (x - 2.0)


def plain_cube(x: float) -> float:
    """f(x) = x**3. Flat at x = 0 and yet neither a maximum nor a minimum."""
    return x * x * x


def plain_cube_derivative(x: float) -> float:
    return 3.0 * x * x


def exponential(x: float) -> float:
    """f(x) = e**x. Its own derivative, which is what makes e special."""
    return math.exp(x)


def natural_log(x: float) -> float:
    """f(x) = ln(x). Derivative 1/x."""
    return math.log(x)


def absolute(x: float) -> float:
    """f(x) = |x|. No derivative at 0 -- and the corner ReLU is built from."""
    return abs(x)


def relu(x: float) -> float:
    """max(x, 0). Day 102 met this as a transformation; here it is the corner."""
    return x if x > 0.0 else 0.0


# ---------------------------------------------------------------------------
# The points, the widths and the exact answers
# ---------------------------------------------------------------------------

# Where the shrinking-interval demonstration happens.
SETTLE_POINT = 3.0
SETTLE_EXACT_SLOPE = 6.0  # d/dx of x**2 at x = 3
SETTLE_WIDTHS = [1.0, 0.1, 0.01, 0.001]
# For f(x) = x**2 the average rate over [a, a + h] is exactly 2a + h, so at
# a = 3 the sequence below is 6 + h and can be written down without a computer.
SETTLE_EXPECTED_SLOPES = [7.0, 6.1, 6.01, 6.001]

# Where the U-shaped error curve is measured. e**x at x = 1 is chosen because
# every one of its derivatives is e, which makes both error terms easy to state.
U_POINT = 1.0
U_EXACT_SLOPE = math.e  # 2.718281828459045

# 27 step sizes, one per decade and two thirds, spanning 1e-1 down to 1e-14.
U_WIDTHS = [10.0 ** (-1.0 - 0.5 * k) for k in range(27)]

# The point at which forward and central are compared head to head.
COMPARE_WIDTH = 1e-5

# The step used for the stationary-point work. Small enough that the truncation
# term is invisible, large enough that the second difference's h**2 divisor has
# not started amplifying rounding error.
STATIONARY_WIDTH = 1e-4

# Machine epsilon for float64: the gap between 1.0 and the next float up.
EPSILON = 2.220446049250313e-16


# ---------------------------------------------------------------------------
# The tolerances, and where each one comes from
# ---------------------------------------------------------------------------

# A difference quotient carries two errors that pull in opposite directions.
#
#   TRUNCATION comes from the mathematics: the formula is only the limit's
#   approximation at a finite h. Taylor gives, for f = e**x at x = 1 where every
#   derivative equals e:
#       forward:  |error| ~ (h / 2)  * e
#       central:  |error| ~ (h**2 / 6) * e
#
#   ROUNDING comes from the arithmetic: f(x + h) and f(x - h) are each stored to
#   about EPSILON relative precision, their difference cancels most of their
#   digits, and dividing by h magnifies what is left:
#       either rule: |error| ~ EPSILON * e / h
#
# Add the two, put the numbers in, and every tolerance below follows. None was
# reached by running a test and enlarging the number until it went green.

# Central difference of e**x at x = 1 with h = 1e-5:
#   truncation ~ (1e-10 / 6) * e   = 4.5e-11
#   rounding   ~ 2.22e-16 * e / 1e-5 = 6.0e-11
#   sum        ~ 1.1e-10            -> allow 1e-9, roughly nine times the bound
CENTRAL_TOL = 1e-9

# Forward difference of e**x at x = 1 with h = 1e-5:
#   truncation ~ (1e-5 / 2) * e = 1.36e-5
#   rounding   ~ 6.0e-11, negligible beside it
#   sum        ~ 1.4e-5         -> allow 1e-4, seven times the bound
FORWARD_TOL = 1e-4

# The average-rate sequence over [3, 3 + h] for f = x**2. Each term is 2a + h
# computed in float64 from numbers of order 10, so only a few units in the last
# place of about 1e-15 are available to go wrong.
EXACT_TOL = 1e-12

# The second difference of a cubic is exact in the mathematics -- the h**2 term
# in its Taylor expansion is the answer and there is no h**4 term to leave
# behind -- so only rounding is in play. With h = 1e-4 and |f| of order 2:
#   rounding ~ 4 * EPSILON * |f| / h**2 = 4 * 2.22e-16 * 2 / 1e-8 = 1.8e-7
#   -> allow 1e-5, about fifty times the bound
SECOND_TOL = 1e-5

# A stationary point found with the central difference at h = 1e-4 on the cubic:
# the truncation term is exactly h**2 * f'''/6 = h**2, which is 1e-8.
#   -> allow 1e-6, a hundred times the bound
STATIONARY_TOL = 1e-6


# ---------------------------------------------------------------------------
# The derivative rules, stated as facts and checked numerically in the lab
# ---------------------------------------------------------------------------

# (name, f, exact f', a point to check it at)
RULE_CASES = [
    ("constant: d/dx of 7 is 0", lambda x: 7.0, lambda x: 0.0, 2.0),
    ("power: d/dx of x**2 is 2x", square, square_derivative, 3.0),
    ("power: d/dx of x**5 is 5x**4", lambda x: x**5, lambda x: 5.0 * x**4, 1.5),
    ("power: d/dx of 1/x is -1/x**2", lambda x: 1.0 / x, lambda x: -1.0 / (x * x), 2.0),
    ("constant multiple: d/dx of 5x**2 is 10x", lambda x: 5.0 * x * x, lambda x: 10.0 * x, 3.0),
    ("sum: d/dx of x**2 + x**3 is 2x + 3x**2", lambda x: x**2 + x**3, lambda x: 2.0 * x + 3.0 * x**2, 2.0),
    ("exponential: d/dx of e**x is e**x", exponential, exponential, 1.0),
    ("logarithm: d/dx of ln(x) is 1/x", natural_log, lambda x: 1.0 / x, 4.0),
]

# The exact slopes those eight cases must produce, written out so a reader can
# check them by hand rather than by rerunning the lab.
RULE_EXPECTED = [0.0, 6.0, 25.3125, -0.25, 30.0, 16.0, math.e, 0.25]

# The eight rule cases are checked with the central difference at h = 1e-5. The
# worst truncation term among them belongs to x**5 at 1.5, where the third
# derivative is 60 * 1.5**2 = 135:
#   truncation ~ (h**2 / 6) * 135 = (1e-10 / 6) * 135 = 2.25e-9
#   -> allow 1e-8, about four times the bound
RULE_TOL = 1e-8

# The corner cases at x = 0, where no derivative exists.
CORNER_WIDTH = 1e-5
# |x|: the one-sided slopes are -1 and +1 and disagree, which is the whole
# reason there is no derivative. The central difference averages them to zero
# and reports that zero with total confidence.
ABS_FORWARD_AT_ZERO = 1.0
ABS_BACKWARD_AT_ZERO = -1.0
ABS_CENTRAL_AT_ZERO = 0.0
# max(x, 0): the one-sided slopes are 0 and 1, so the central difference gives
# their average, 0.5. Deep-learning frameworks do not use 0.5; they pick one of
# the one-sided values and move on, and that choice is a convention rather than
# a theorem.
RELU_FORWARD_AT_ZERO = 1.0
RELU_BACKWARD_AT_ZERO = 0.0
RELU_CENTRAL_AT_ZERO = 0.5
