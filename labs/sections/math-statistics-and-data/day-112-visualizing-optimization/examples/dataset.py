"""Shared numbers for the Day 112 lab -- the reference implementation.

Every script and every test in this lab imports its constants from here so
that the lesson's claims, the reference scripts, and the test suite are all
computed from the same numbers rather than three copies that could drift.

Two bowls, both centred on the origin with minimum value 0:

    WELL(x, y) = x^2 +  y^2          -- a perfectly round bowl
    ILL(x, y)  = x^2 + 25 y^2        -- a valley squeezed 25x narrower in y

The two runs compared throughout the lab and the lesson start at the same
point and take the same number of steps at the SAME learning rate. The only
difference is which bowl they descend. That is deliberate: it isolates
conditioning as the one variable that explains why one run's path is short
and geometric while the other's is long and zig-zagging, even though both
land within a few percent of the same final loss.
"""

import numpy as np

# -- the two bowls -----------------------------------------------------------

WELL_A, WELL_B = 1.0, 1.0
ILL_A, ILL_B = 1.0, 25.0

START = np.array([4.0, 4.0])
LEARNING_RATE = 0.038
STEPS = 60


def bowl(a: float, b: float):
    """Return (f, grad) for f(x, y) = a x^2 + b y^2.

    The minimum is always at the origin with value 0, regardless of a and b --
    only the SHAPE of the bowl changes, never where the bottom is.
    """

    def f(x, y):
        return a * x**2 + b * y**2

    def grad(x, y):
        return np.array([2.0 * a * x, 2.0 * b * y])

    return f, grad


WELL_F, WELL_GRAD = bowl(WELL_A, WELL_B)
ILL_F, ILL_GRAD = bowl(ILL_A, ILL_B)

# -- the one-dimensional bowl used for the learning-rate sweep ---------------
#
# f(x) = x^2, grad = 2x. The update is x <- x - eta * 2x = (1 - 2 eta) x, an
# exact geometric recursion with ratio rho = 1 - 2 eta. It converges only for
# 0 < eta < 1: the sweep therefore has a genuine cliff at eta = 1, not merely
# "large enough to eventually diverge".

SWEEP_X0 = 4.0
SWEEP_STEPS = 300


def sweep_f(x):
    return x**2


def sweep_grad(x):
    return 2.0 * x


# -- tolerances, each tied to the comparison it governs ----------------------

# Two analytic quantities computed by different routes: machine precision.
EXACT_TOL = 1e-9

# "Two runs land within a few percent of the same final loss." Chosen once
# from the pair of runs this file specifies (see WELL_RUN / ILL_RUN below,
# and examples/06_two_runs_same_loss.py, which prints the measured gap).
LOSS_MATCH_TOL = 0.05

# "The paths differ by a large factor." The measured ratio is over 13x; 5x is
# a conservative floor that would still be true on a different machine or
# numpy build, since the recursion above is closed-form and exact.
PATH_LENGTH_RATIO_MIN = 5.0

# How close the LAST drawn pixel marker must land to the pixel of the true
# minimum (0, 0), in pixels, for the world-to-pixel round trip to count as
# correct. One pixel of slack absorbs rounding in both directions.
PIXEL_TOL = 2.0
