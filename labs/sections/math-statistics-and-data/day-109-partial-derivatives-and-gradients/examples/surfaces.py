"""The surfaces this lab measures, and the exact gradients to check against.

Every function here is a function of several inputs. Every one has a gradient
you can work out with a pencil in under a minute, which is the entire point:
the numerical machinery in `gradients.py` is only trustworthy if there is
something exact to hold it against.

All the data is invented. None of it is a measurement of anything real. What
IS real is every number the lab prints about these functions, because those are
computed from these definitions at run time.

Read this file. Do not change it -- the tests compare against the values
written down here.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# The step size, and why this one
# --------------------------------------------------------------------------
#
# Day 108 established the shape: a central difference has a truncation error
# that shrinks like h squared and a roundoff error that GROWS like 1/h, so the
# total error is U-shaped in h and the best step is somewhere in the middle.
# For a central difference on float64 the trough sits near the cube root of
# the machine epsilon, which is about 6e-6. This lab uses 1e-5, which is close
# enough to the bottom of that trough to be within a factor of two of the best
# achievable error on every surface here, and is a round number a reader can
# remember. Script 06 sweeps h over twelve orders of magnitude and prints the
# curve rather than asking you to take this on trust.
H_DEFAULT = 1.0e-5

# The tolerance every gradient assertion in this lab uses.
#
# It is set from what the arithmetic can achieve, not from what makes the
# tests pass. Four of the six surfaces below are at most quadratic in each
# variable, and a central difference is ALGEBRAICALLY EXACT for those -- the
# h-squared term is multiplied by a third derivative that is zero, so the only
# error left is floating-point roundoff, which lands around 1e-11 at h = 1e-5
# for points of this size. The one genuinely cubic surface has a truncation
# error of exactly h squared, which is 1e-10 here. GRADIENT_TOL is three
# orders of magnitude above the worst of those, which leaves room for a
# different processor's rounding without leaving room for a wrong answer.
GRADIENT_TOL = 1.0e-8

# Directions sampled around the full circle when the lab checks that the
# gradient really is the steepest way up. With 360 evenly spaced directions
# the closest sample sits within 0.5 degrees of any given angle, so the
# tolerance below is that bound with a little slack for the wrap-around at
# 360 degrees.
N_DIRECTIONS = 360
ANGLE_TOL_DEGREES = 1.0

# The step taken along a contour when the lab checks perpendicularity. The
# chord between two points on a curve is not the tangent; it differs from it
# by an angle of order delta, so the dot product of a unit gradient with a
# unit chord is of order delta rather than exactly zero. Script 04 halves
# delta four times and prints the dot product each time, so the reader watches
# it shrink instead of being handed a tolerance.
CONTOUR_DELTA = 1.0e-5
CONTOUR_DOT_TOL = 1.0e-4

# Used where a random point or a random direction is wanted. Seeded, so every
# number in `expected-output/` is reproducible.
SEED = 109


# --------------------------------------------------------------------------
# 1. A quadratic bowl -- the shape every optimisation picture is drawn on
# --------------------------------------------------------------------------

def bowl(point):
    """f(x, y) = x^2 + 3y^2. A bowl with its lowest point at the origin.

    The 3 makes it an elliptical bowl rather than a circular one: it is three
    times steeper in y than in x at the same distance out, which is exactly
    the situation that makes gradient descent zig-zag on Day 111.
    """
    x, y = point
    return x * x + 3.0 * y * y


def bowl_gradient(point):
    """grad f = (2x, 6y). Differentiate x^2 + 3y^2 one variable at a time."""
    x, y = point
    return np.array([2.0 * x, 6.0 * y])


# --------------------------------------------------------------------------
# 2. A plane -- the function whose gradient is the same everywhere
# --------------------------------------------------------------------------

def plane(point):
    """f(x, y) = 3x - 2y + 5. A flat tilted sheet."""
    x, y = point
    return 3.0 * x - 2.0 * y + 5.0


def plane_gradient(point):
    """grad f = (3, -2), at every point in the plane. The point is ignored."""
    del point
    return np.array([3.0, -2.0])


# --------------------------------------------------------------------------
# 3. A product -- the smallest function whose partials involve each other
# --------------------------------------------------------------------------

def product(point):
    """f(x, y) = xy. Flat along both axes through the origin, curved between.

    This is the function that makes the phrase "hold the other one still" do
    real work. Along the x-axis (y = 0) the function is identically zero, so
    the slope in x is zero. Move off that line and the slope in x is y.
    """
    x, y = point
    return x * y


def product_gradient(point):
    """grad f = (y, x). Each partial is the OTHER variable, held fixed."""
    x, y = point
    return np.array([y, x])


# --------------------------------------------------------------------------
# 4. A saddle -- a stationary point that is neither a peak nor a floor
# --------------------------------------------------------------------------

def saddle(point):
    """f(x, y) = x^2 - y^2. Up along x, down along y, flat at the origin."""
    x, y = point
    return x * x - y * y


def saddle_gradient(point):
    """grad f = (2x, -2y). Zero at the origin, and the origin is a saddle."""
    x, y = point
    return np.array([2.0 * x, -2.0 * y])


# --------------------------------------------------------------------------
# 5. A dome -- a stationary point that IS a maximum
# --------------------------------------------------------------------------

def dome(point):
    """f(x, y) = -(x^2 + y^2). The bowl turned upside down."""
    x, y = point
    return -(x * x + y * y)


def dome_gradient(point):
    """grad f = (-2x, -2y). Also zero at the origin. Also a stationary point."""
    x, y = point
    return np.array([-2.0 * x, -2.0 * y])


# --------------------------------------------------------------------------
# 6. A genuine cubic -- the one surface where truncation error is visible
# --------------------------------------------------------------------------

def cubic(point):
    """f(x, y) = x^3 + x*y^2.

    Every other surface here is at most quadratic in each variable, which
    makes the central difference exact for them. This one is not, and its
    error is not merely small but PREDICTABLE: expanding
    ((x+h)^3 - (x-h)^3) / (2h) gives 3x^2 + h^2 exactly, so the numerical
    partial in x overshoots the true one by exactly h squared, with no other
    terms at all. Script 06 measures that and checks it to twelve decimal
    places.
    """
    x, y = point
    return x ** 3 + x * y * y


def cubic_gradient(point):
    """grad f = (3x^2 + y^2, 2xy)."""
    x, y = point
    return np.array([3.0 * x * x + y * y, 2.0 * x * y])


# --------------------------------------------------------------------------
# The registry the scripts and tests iterate over
# --------------------------------------------------------------------------

SURFACES = {
    "bowl": (bowl, bowl_gradient, "x^2 + 3y^2", "grad = (2x, 6y)"),
    "plane": (plane, plane_gradient, "3x - 2y + 5", "grad = (3, -2)"),
    "product": (product, product_gradient, "xy", "grad = (y, x)"),
    "saddle": (saddle, saddle_gradient, "x^2 - y^2", "grad = (2x, -2y)"),
    "dome": (dome, dome_gradient, "-(x^2 + y^2)", "grad = (-2x, -2y)"),
    "cubic": (cubic, cubic_gradient, "x^3 + x*y^2", "grad = (3x^2 + y^2, 2xy)"),
}

# The points every surface is probed at. Chosen by hand: one in the first
# quadrant, one with a negative coordinate, one off-axis with a fraction, one
# ON an axis where a partial vanishes, and one far out.
PROBE_POINTS = (
    (1.0, 1.0),
    (2.0, -1.0),
    (-0.5, 3.0),
    (4.0, 0.0),
    (0.25, 0.75),
)

# The three surfaces that all have a zero gradient at the origin, and what the
# origin actually IS for each. The gradient cannot tell them apart; this table
# is the answer the gradient does not carry.
STATIONARY_AT_ORIGIN = (
    ("bowl", "minimum", "every direction goes up"),
    ("dome", "maximum", "every direction goes down"),
    ("saddle", "saddle", "up along x, down along y"),
)


# --------------------------------------------------------------------------
# Exact contours, parametrised WITHOUT reference to the gradient
# --------------------------------------------------------------------------
#
# The claim being tested is that the gradient is perpendicular to the contour.
# Walking along the contour by stepping perpendicular to the gradient would
# make that claim true by construction and prove nothing. So each contour
# below is an exact algebraic parametrisation, derived on paper from the
# function alone, and the lab checks it lands back on the same value of f
# before it uses it for anything.

def bowl_contour(level, t):
    """A point on the ellipse x^2 + 3y^2 = level, for the angle parameter t.

    Substitute x = sqrt(level) cos t and y = sqrt(level/3) sin t into
    x^2 + 3y^2 and you get level (cos^2 t + sin^2 t) = level, for every t.
    """
    a = np.sqrt(level)
    b = np.sqrt(level / 3.0)
    return np.array([a * np.cos(t), b * np.sin(t)])


def product_contour(level, t):
    """A point on the hyperbola xy = level, for the parameter t (x = t)."""
    return np.array([t, level / t])


def dome_contour(level, t):
    """A point on the circle -(x^2 + y^2) = level, for the angle t.

    level must be negative; the radius is sqrt(-level).
    """
    r = np.sqrt(-level)
    return np.array([r * np.cos(t), r * np.sin(t)])


CONTOURS = {
    "bowl": (bowl, bowl_contour, 4.0, 0.7),
    "product": (product, product_contour, 6.0, 2.0),
    "dome": (dome, dome_contour, -9.0, 1.1),
}


# --------------------------------------------------------------------------
# A three-parameter model, so "one partial per parameter" is not just a claim
# --------------------------------------------------------------------------
#
# Four invented samples. Each row is (a, b, target). Nothing was measured to
# produce these; they were chosen so the arithmetic stays checkable by hand.

SAMPLES = (
    (1.0, 2.0, 8.0),
    (2.0, 1.0, 7.0),
    (3.0, 3.0, 15.0),
    (0.0, 1.0, 3.0),
)

# The parameter vector the lab evaluates the loss and its gradient at.
START_PARAMS = (1.0, 1.0, 1.0)


def model_loss(params):
    """Mean squared error of `pred = w1*a + w2*b + c` over SAMPLES.

    Three parameters, so the gradient is a vector of three numbers -- one per
    parameter. A real network has millions of parameters and the gradient has
    millions of entries. The idea does not change; only the count does.
    """
    w1, w2, c = params
    total = 0.0
    for a, b, target in SAMPLES:
        residual = w1 * a + w2 * b + c - target
        total += residual * residual
    return total / len(SAMPLES)


def model_loss_gradient(params):
    """The exact gradient, differentiated by hand.

    L = (1/n) sum r_i^2 with r_i = w1*a_i + w2*b_i + c - y_i, so
    dL/dw1 = (2/n) sum r_i * a_i, dL/dw2 = (2/n) sum r_i * b_i,
    dL/dc  = (2/n) sum r_i.
    """
    w1, w2, c = params
    n = len(SAMPLES)
    g_w1 = g_w2 = g_c = 0.0
    for a, b, target in SAMPLES:
        residual = w1 * a + w2 * b + c - target
        g_w1 += 2.0 * residual * a
        g_w2 += 2.0 * residual * b
        g_c += 2.0 * residual
    return np.array([g_w1 / n, g_w2 / n, g_c / n])
