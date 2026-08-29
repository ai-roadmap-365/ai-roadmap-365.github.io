"""The data, the functions and every tolerance this lab compares against.

Read this file. Nothing here is tuned: every tolerance below is derived from
the error terms that actually govern the comparison being made, and the
arithmetic is written out beside it. A tolerance reached by running a test and
enlarging the number until it went green is a tolerance chosen by whatever bug
happened to exist at the time.

Almost every number in this lab is exact in float64. The chains, the two-path
example and the whole two-layer network were chosen so that the reader can
re-derive each one with a pen. Where a value is not exact -- a sine, a
logarithm, an exponential -- it is computed here from `math` rather than
written down as a literal, so nothing in this lab is a remembered constant.
"""

import math
from typing import Callable, NamedTuple

import numpy as np

# --------------------------------------------------------------------------
# Machine constants
# --------------------------------------------------------------------------

#: float64 machine epsilon, read from NumPy rather than trusted as a literal.
EPSILON: float = float(np.finfo(np.float64).eps)

# --------------------------------------------------------------------------
# The numerical step, and the three tolerances
# --------------------------------------------------------------------------

#: The central-difference step. Day 108 measured the bottom of the error U for
#: the central rule on e**x and found it in the 1e-7 to 1e-4 band; 1e-5 sits
#: inside it with room on both sides.
H: float = 1e-5

# The central difference (f(x+h) - f(x-h)) / (2h) carries two errors:
#
#   truncation  ~ (h**2 / 6) * |f'''(x)|   = 1.667e-11 * |f'''(x)|  at h = 1e-5
#   rounding    ~ EPSILON * |f(x)| / h     = 2.220e-11 * |f(x)|     at h = 1e-5
#
# No function differentiated in this lab has |f| or |f'''| above about 250 at
# the points used, so the bound is about 250 * (1.667e-11 + 2.220e-11), which
# is roughly 9.7e-9. The tolerance below is 1e-6, so there is about a
# hundredfold margin -- enough that ordinary float64 noise cannot trip it, and
# far too tight to hide a chain rule that dropped a factor or summed the wrong
# paths. The smallest true gradient this tolerance guards is 0.25, so a
# mistake would have to be smaller than four parts in a million to slip past.
#: Analytic gradient against a central difference. See the derivation above.
NUMERIC_TOL: float = 1e-6

#: The same comparison, stated relatively, for the handful of quantities whose
#: magnitude runs into the hundreds -- where an absolute 1e-6 would be
#: stricter than the arithmetic can honestly support.
NUMERIC_REL_TOL: float = 1e-6

# Two analytic computations of the same quantity -- for example the product of
# five local rates against the closed-form derivative of the whole chain --
# differ only in the order the multiplications happen, so they differ by a few
# units in the last place. At a magnitude of 1e2 one ulp is about 1.4e-14, and
# a chain of five products can accumulate a handful of them, so the honest
# bound is a few times 1e-13.
#: Analytic against analytic: rounding only, no truncation.
ANALYTIC_TOL: float = 1e-12

# --------------------------------------------------------------------------
# Gears: the whole idea, before any calculus
# --------------------------------------------------------------------------

#: Gear A turns twice for every turn of B; B turns three times for every turn
#: of C. So A turns six times per turn of C. The rates multiplied.
GEAR_RATIOS: tuple[float, ...] = (2.0, 3.0)
GEAR_RATIO_PRODUCT: float = 6.0

#: A longer train, to show the product keeping on multiplying.
GEAR_TRAIN: tuple[float, ...] = (2.0, 3.0, 1.5, 4.0)
GEAR_TRAIN_PRODUCT: float = 36.0

#: The same arithmetic with money instead of teeth. 1 unit of the first
#: currency buys 1.25 of the second, which buys 0.8 of the third, which buys
#: 150 of the fourth. These rates are invented for the arithmetic and are not
#: quoted from any market.
CURRENCY_RATES: tuple[float, ...] = (1.25, 0.8, 150.0)
CURRENCY_PRODUCT: float = 150.0

# --------------------------------------------------------------------------
# Functions used as the outer and inner halves of a composition
# --------------------------------------------------------------------------


def square(x: float) -> float:
    """x squared."""
    return x * x


def d_square(x: float) -> float:
    """The derivative of x squared."""
    return 2.0 * x


def line(x: float) -> float:
    """3x + 1."""
    return 3.0 * x + 1.0


def d_line(x: float) -> float:
    """The derivative of 3x + 1: a constant 3."""
    return 3.0


def half_negative_square(x: float) -> float:
    """-x squared over 2 -- the inside of a Gaussian bump."""
    return -0.5 * x * x


def d_half_negative_square(x: float) -> float:
    """The derivative of -x squared over 2."""
    return -x


def shifted_square(x: float) -> float:
    """x squared plus 1, which is never zero, so its logarithm is safe."""
    return x * x + 1.0


def reciprocal(x: float) -> float:
    """1 / x."""
    return 1.0 / x


def d_reciprocal(x: float) -> float:
    """The derivative of 1 / x."""
    return -1.0 / (x * x)


def one_plus_exp_negative(x: float) -> float:
    """1 + e to the minus x -- the denominator of the sigmoid."""
    return 1.0 + math.exp(-x)


def d_one_plus_exp_negative(x: float) -> float:
    """The derivative of 1 + e to the minus x."""
    return -math.exp(-x)


def double_plus_one(x: float) -> float:
    """2x + 1."""
    return 2.0 * x + 1.0


def d_double_plus_one(x: float) -> float:
    """The derivative of 2x + 1: a constant 2."""
    return 2.0


def d_tanh(x: float) -> float:
    """The derivative of tanh, written in terms of x rather than of tanh(x)."""
    t = math.tanh(x)
    return 1.0 - t * t


def d_ln(x: float) -> float:
    """The derivative of the natural logarithm."""
    return 1.0 / x


# --------------------------------------------------------------------------
# The one-variable chain rule: six compositions, each checked numerically
# --------------------------------------------------------------------------


class Composition(NamedTuple):
    """One composed function f(g(x)), with both halves and both derivatives.

    `exact` is the closed-form derivative at `x`, computed from `math` rather
    than written down as a literal, so nothing here is a remembered constant.
    """

    name: str
    outer: Callable[[float], float]
    d_outer: Callable[[float], float]
    inner: Callable[[float], float]
    d_inner: Callable[[float], float]
    x: float
    exact: float


COMPOSITIONS: tuple[Composition, ...] = (
    # (3x + 1) squared at x = 2. Inner is 7, outer rate is 2*7 = 14, inner
    # rate is 3, so the answer is 42 -- exact, and checkable in one line.
    Composition("square of a line", square, d_square, line, d_line, 2.0, 42.0),
    # sin(x squared) at x = 1.5. Rate is cos(2.25) * 3.
    Composition(
        "sine of a square",
        math.sin,
        math.cos,
        square,
        d_square,
        1.5,
        math.cos(2.25) * 3.0,
    ),
    # A Gaussian bump, e to the minus x squared over 2, at x = 0.8.
    Composition(
        "gaussian bump",
        math.exp,
        math.exp,
        half_negative_square,
        d_half_negative_square,
        0.8,
        math.exp(-0.32) * -0.8,
    ),
    # ln(x squared + 1) at x = 2. Inner is 5, outer rate is 1/5, inner rate
    # is 4, so the answer is 0.8 -- exact.
    Composition(
        "log of a shifted square",
        math.log,
        d_ln,
        shifted_square,
        d_square,
        2.0,
        0.8,
    ),
    # The sigmoid, written as 1 / (1 + e to the minus x), at x = 0. Inner is
    # 2, outer rate is -1/4, inner rate is -1, so the answer is 0.25 -- which
    # is the largest value the sigmoid's slope ever takes.
    Composition(
        "the sigmoid",
        reciprocal,
        d_reciprocal,
        one_plus_exp_negative,
        d_one_plus_exp_negative,
        0.0,
        0.25,
    ),
    # tanh(2x + 1) at x = -0.5, where the inner function is exactly 0 and
    # tanh's slope is exactly 1, so the answer is exactly 2.
    Composition(
        "tanh of a line",
        math.tanh,
        d_tanh,
        double_plus_one,
        d_double_plus_one,
        -0.5,
        2.0,
    ),
)

# --------------------------------------------------------------------------
# A chain of five functions, built so every local rate is a round number
# --------------------------------------------------------------------------

#: Applied in order, left to right: double, add 3, square, square root,
#: natural logarithm. Starting from x = 1 the values are 1, 2, 5, 25, 5,
#: ln 5, and the local rates are 2, 1, 10, 0.1, 0.2. Their product is 0.4.
#:
#: The whole chain collapses to ln(2x + 3), whose derivative is 2 / (2x + 3),
#: which at x = 1 is 2/5 = 0.4. Two routes, the same number.
FIVE_STAGES: tuple[Callable[[float], float], ...] = (
    lambda u: 2.0 * u,
    lambda u: u + 3.0,
    lambda u: u * u,
    math.sqrt,
    math.log,
)

FIVE_RATES: tuple[Callable[[float], float], ...] = (
    lambda u: 2.0,
    lambda u: 1.0,
    lambda u: 2.0 * u,
    lambda u: 0.5 / math.sqrt(u),
    lambda u: 1.0 / u,
)

FIVE_START: float = 1.0
FIVE_VALUES: tuple[float, ...] = (1.0, 2.0, 5.0, 25.0, 5.0, math.log(5.0))
FIVE_LOCAL_RATES: tuple[float, ...] = (2.0, 1.0, 10.0, 0.1, 0.2)
FIVE_DERIVATIVE: float = 0.4


def five_chain_closed_form(x: float) -> float:
    """The five stages collapsed by hand: ln(2x + 3)."""
    return math.log(2.0 * x + 3.0)


def d_five_chain_closed_form(x: float) -> float:
    """Its derivative: 2 / (2x + 3)."""
    return 2.0 / (2.0 * x + 3.0)


# --------------------------------------------------------------------------
# Two paths into one output: the case where contributions ADD
# --------------------------------------------------------------------------

#: x reaches the output twice: once through u = x squared, once through
#: v = 3x. The output is f = u * v.
#:
#:   df/dx = (df/du)(du/dx) + (df/dv)(dv/dx)
#:         = v * 2x         + u * 3
#:         = 3x * 2x        + x squared * 3
#:         = 6 x squared    + 3 x squared     = 9 x squared
#:
#: At x = 2 that is 36. The two path contributions are 24 and 12. Neither one
#: alone is the answer, and this is exactly the mistake the lab is built to
#: catch: taking the product along one path and stopping there.
TWO_PATH_X: float = 2.0
TWO_PATH_U: float = 4.0
TWO_PATH_V: float = 6.0
TWO_PATH_OUTPUT: float = 24.0
TWO_PATH_CONTRIBUTIONS: tuple[float, float] = (24.0, 12.0)
TWO_PATH_DERIVATIVE: float = 36.0


def two_path_direct(x: float) -> float:
    """The same function with the composition already done: 3 x cubed."""
    return 3.0 * x * x * x


def d_two_path_direct(x: float) -> float:
    """Its derivative: 9 x squared."""
    return 9.0 * x * x


# --------------------------------------------------------------------------
# The full multivariable chain rule: two inputs, two intermediates
# --------------------------------------------------------------------------

#: z = u squared + v squared, with u = s*t and v = s - t, at (s, t) = (2, 3).
#:
#:   u = 6,  v = -1,  z = 37
#:   dz/du = 12,  dz/dv = -2
#:   du/ds = t = 3,   du/dt = s = 2
#:   dv/ds = 1,       dv/dt = -1
#:
#:   dz/ds = 12*3 + (-2)*1  = 34
#:   dz/dt = 12*2 + (-2)*-1 = 26
#:
#: Every one of those is an integer, so the whole thing is exact in float64.
SURFACE_POINT: tuple[float, float] = (2.0, 3.0)
SURFACE_U: float = 6.0
SURFACE_V: float = -1.0
SURFACE_Z: float = 37.0
SURFACE_DZ_DU: float = 12.0
SURFACE_DZ_DV: float = -2.0
SURFACE_GRADIENT: tuple[float, float] = (34.0, 26.0)


def surface(s: float, t: float) -> float:
    """z as a function of s and t, with the intermediates substituted in."""
    u = s * t
    v = s - t
    return u * u + v * v


# --------------------------------------------------------------------------
# The tiny two-layer network, backpropagated by hand
# --------------------------------------------------------------------------

#: Half the natural logarithm of 3. tanh of this number is exactly 0.5 in
#: float64, and 1 - tanh squared is then exactly 0.75. Both facts are asserted
#: by the test suite rather than assumed.
#:
#: The bias of the second hidden unit is set to this value on purpose, so that
#: every number in the hand-worked backward pass is exact and can be checked
#: with a pen. Nothing about the chain rule depends on the choice; it is a
#: convenience for the reader, and it is declared rather than hidden.
HALF_LN3: float = 0.5 * math.log(3.0)

#: The two inputs.
NET_X1: float = 1.0
NET_X2: float = 2.0

#: Hidden unit A: weights and bias. Pre-activation is 1*1 + (-0.5)*2 + 0 = 0.
NET_WA1: float = 1.0
NET_WA2: float = -0.5
NET_BA: float = 0.0

#: Hidden unit B: pre-activation is -0.5*1 + 0.25*2 + HALF_LN3 = HALF_LN3.
NET_WB1: float = -0.5
NET_WB2: float = 0.25
NET_BB: float = HALF_LN3

#: The output layer: a linear combination of the two hidden activations.
NET_VA: float = 2.0
NET_VB: float = -3.0
NET_C: float = 1.0

#: The target the loss is measured against.
NET_TARGET: float = 1.0

#: The forward pass, every value exact.
NET_A_PRE: float = 0.0
NET_A: float = 0.0
NET_B_PRE: float = HALF_LN3
NET_B: float = 0.5
NET_OUT: float = -0.5
NET_LOSS: float = 2.25

#: The backward pass, every value exact. Worked out in full in
#: `06_backprop_by_hand.py` and asserted against the engine in the tests.
NET_GRADIENTS: dict[str, float] = {
    "out": -3.0,
    "c": -3.0,
    "vA": 0.0,  # zero, because hidden unit A output exactly 0
    "vB": -1.5,
    "a": -6.0,
    "b": 9.0,
    "a_pre": -6.0,
    "b_pre": 6.75,
    "wA1": -6.0,
    "wA2": -12.0,
    "bA": -6.0,
    "wB1": 6.75,
    "wB2": 13.5,
    "bB": 6.75,
    # x1 and x2 each reach the loss through BOTH hidden units, so each of
    # these is a sum over two paths, not a single product.
    "x1": -9.375,
    "x2": 4.6875,
}

#: The two per-path contributions to dL/dx1, which must be added.
NET_X1_CONTRIBUTIONS: tuple[float, float] = (-6.0, -3.375)

#: The names of the twelve parameters, in the order the scripts print them.
NET_PARAMETERS: tuple[str, ...] = (
    "wA1",
    "wA2",
    "bA",
    "wB1",
    "wB2",
    "bB",
    "vA",
    "vB",
    "c",
)

# --------------------------------------------------------------------------
# Products that collapse and products that blow up
# --------------------------------------------------------------------------

#: A gradient that passes through 50 layers, each contributing a local rate
#: slightly below or slightly above 1.
DECAY_FACTOR: float = 0.9
GROWTH_FACTOR: float = 1.1
CHAIN_LENGTH: int = 50
LONG_CHAIN_LENGTH: int = 200

#: Asserted as orders of magnitude rather than as exact values, because the
#: point is the scale and not the digits.
DECAY_ORDER: int = -3  # 0.9**50 is about 5.15e-3
GROWTH_ORDER: int = 2  # 1.1**50 is about 1.17e+2

#: A harsher pair, to show how quickly the arithmetic leaves the useful range.
#: 0.25 is not an arbitrary choice: it is the LARGEST slope the sigmoid ever
#: has, measured in `02_composition_and_the_chain_rule.py`. A stack of sigmoid
#: layers is multiplying numbers no bigger than this one.
SHARP_DECAY: float = 0.25
SHARP_GROWTH: float = 2.0

#: A middling decay, kept because its behaviour is genuinely surprising and
#: contradicts the obvious guess. See `07_vanishing_and_exploding.py`.
MILD_DECAY: float = 0.5
