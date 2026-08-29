"""Shared data for the Day 111 lab -- read this file, do not change it.

Every constant here is invented and stated to be invented. Nothing is fitted
to a real dataset; every number is chosen so a reader can re-derive it by
hand, and every tolerance below is derived from the arithmetic that actually
governs the comparison it guards, not tuned until a test happened to pass.

The core object of the day is the one-dimensional quadratic
    f(x) = 0.5 * a * x**2          f'(x) = a * x
because its gradient-descent update has a closed form:
    x_{n+1} = x_n - lr * a * x_n = x_n * (1 - lr * a)
so after n steps
    x_n = x_0 * (1 - lr * a) ** n
and the whole regime structure of the lesson -- monotone, exact, oscillating,
divergent -- falls out of the single number (1 - lr * a).
"""

from __future__ import annotations

import numpy as np

EPSILON = float(np.finfo(np.float64).eps)

# ---------------------------------------------------------------------------
# The 1-D quadratic that the first half of the lab is built on.
# ---------------------------------------------------------------------------

A = 5.0                       # curvature of f(x) = 0.5 * A * x**2
CRITICAL_LR = 1.0 / A          # 0.2 -- exact one-step landing
DIVERGENCE_LR = 2.0 / A        # 0.4 -- boundary of the oscillating-but-converging regime

X0_1D = 1.0

# The four learning rates exercise 3 classifies, chosen to sit one in each
# regime relative to CRITICAL_LR = 0.2 and DIVERGENCE_LR = 0.4:
LR_MONOTONE = 0.10             # 0 < lr < 1/A            -> monotone decrease
LR_EXACT = 0.20                # lr == 1/A                -> exact in one step
LR_OSCILLATING = 0.35          # 1/A < lr < 2/A          -> alternates sign, |x| shrinks
LR_DIVERGENT = 0.45            # lr > 2/A                -> |x| grows without bound

REGIME_ITERS = 30

# The opening hook: the simplest convex function there is, and a learning
# rate only slightly above its own divergence boundary.
HOOK_A = 1.0
HOOK_DIVERGENCE_LR = 2.0 / HOOK_A      # 2.0
HOOK_LR = 2.2                          # "only slightly too large"
HOOK_X0 = 1.0
HOOK_ITERS = 4000                      # long enough to reach inf, then nan

# ---------------------------------------------------------------------------
# Tolerances, derived rather than chosen.
# ---------------------------------------------------------------------------
# The quadratic's update is EXACT algebra in floating point: one
# multiplication per step, x_{n+1} = x_n * (1 - lr * A). float64 carries
# about 15-17 significant decimal digits, and after a modest number of
# multiplications the accumulated rounding is still many orders of magnitude
# below 1e-9, so two routes to the same exact quantity (a direct formula and
# a step-by-step loop) are compared at:
EXACT_TOL = 1e-9

# The central difference used to check an analytic gradient against a
# numerical one carries truncation error of order h**2 and rounding error of
# order EPSILON / h. At h = 1e-6 (h**2 = 1e-12, EPSILON / h ~ 2.2e-10) the
# total is comfortably under 1e-6 for the smooth functions this lab uses, so:
NUMERIC_H = 1e-6
NUMERIC_TOL = 1e-6

# ---------------------------------------------------------------------------
# Ill-conditioning: f(x, y) = 0.5 * (x**2 + kappa * y**2)
# ---------------------------------------------------------------------------
# The Hessian of this bowl is diag(1, kappa), so its condition number is
# exactly kappa (Day 106: the ratio of the eigenvalues -- min eigenvalue 1,
# max eigenvalue kappa). This lab uses the standard optimal FIXED step size
# for a quadratic with eigenvalues mu (smallest) and L (largest),
#     lr* = 2 / (mu + L) = 2 / (1 + kappa)
# which is the single learning rate that minimises the worst-case per-step
# contraction over every eigen-direction at once. For kappa = 1 (an
# isotropic bowl) that contraction is exactly zero -- gradient descent with
# the optimal step solves an isotropic quadratic in ONE step, the same
# "exact" regime exercise 3 meets on the 1-D bowl. As kappa grows, the
# optimal step shrinks and the worst-case per-step contraction, which is
# exactly (kappa - 1) / (kappa + 1), climbs towards 1 -- so the number of
# steps needed to reach a fixed gradient tolerance grows with kappa, with no
# free parameter left to compensate.
KAPPA_VALUES = (1, 5, 20, 100)
KAPPA_START = (1.0, 1.0)
KAPPA_GRAD_TOL = 1e-4
KAPPA_MAX_ITERS = 5000


def kappa_lr(kappa: float) -> float:
    """The optimal fixed learning rate for a bowl of condition number kappa."""
    return 2.0 / (1.0 + kappa)


def bowl_grad(kappa: float):
    """Return the gradient function of f(x, y) = 0.5 * (x**2 + kappa * y**2)."""

    def grad(point):
        x, y = point
        return np.array([x, kappa * y])

    return grad


def bowl_value(kappa: float, point) -> float:
    x, y = point
    return 0.5 * (x * x + kappa * y * y)


# ---------------------------------------------------------------------------
# Momentum comparison, on the kappa = 20 bowl.
# ---------------------------------------------------------------------------
MOMENTUM_KAPPA = 20
MOMENTUM_BETA = 0.5
# Momentum is given exactly the SAME learning rate plain descent uses --
# kappa_lr(MOMENTUM_KAPPA) -- so the comparison isolates what the beta*v
# term buys on its own, with nothing else changed.
MOMENTUM_LR = kappa_lr(MOMENTUM_KAPPA)

# ---------------------------------------------------------------------------
# Gradient checking: a deliberately wrong analytic gradient.
# ---------------------------------------------------------------------------
CHECK_POINT = np.array([0.7, -1.3, 2.1])


def check_function(point) -> float:
    x, y, z = point
    return x * x + 2.0 * y * y + 0.5 * z * z * z


def check_gradient_correct(point):
    x, y, z = point
    return np.array([2.0 * x, 4.0 * y, 1.5 * z * z])


def check_gradient_buggy(point):
    """The correct gradient with the SIGN of component 1 (index 1) flipped."""
    correct = check_gradient_correct(point)
    buggy = correct.copy()
    buggy[1] = -buggy[1]
    return buggy


CHECK_TOL = 1e-4

# ---------------------------------------------------------------------------
# Non-convexity: two minima, initialisation decides the answer.
# ---------------------------------------------------------------------------
# f(x) = (x**2 - 1)**2 has minima at x = -1 and x = +1 (value 0) and a local
# maximum at x = 0 (value 1). f'(x) = 4*x**3 - 4*x, which is negative for
# 0 < x < 1 (pulling towards +1) and positive for -1 < x < 0 (pulling
# towards -1), so any start strictly inside (-1, 1) but on one side of 0
# converges to the minimum on that side.
TWO_MINIMA_LR = 0.05
TWO_MINIMA_ITERS = 400
TWO_MINIMA_LEFT_START = -0.1
TWO_MINIMA_RIGHT_START = 0.1
TWO_MINIMA_MARGIN = 1.5


def two_minima_value(x: float) -> float:
    return (x * x - 1.0) ** 2


def two_minima_grad(x: float) -> float:
    return 4.0 * x ** 3 - 4.0 * x


# ---------------------------------------------------------------------------
# Stopping-criterion trap: a shallow bowl, far from its own minimum.
# ---------------------------------------------------------------------------
# The same quadratic family as the top of this file, but with curvature so
# small that a point far from the minimum still has a small local slope --
# a real, bounded plateau rather than an unbounded linear tail. Locally,
# taking one gradient-descent step changes the value by
#   delta_f = -lr * a * x**2 * (1 - 0.5 * lr * a)   (exact algebra, not an
#   approximation, for this exact quadratic)
# which is tiny whenever `a` is tiny, even while the gradient a*x itself is
# comfortably above a small tolerance.
PLATEAU_A = 1e-4
PLATEAU_X0 = 100.0
PLATEAU_LR = 1e-3
PLATEAU_GRAD_TOL = 1e-3
PLATEAU_DELTA_F_TOL = 1e-6


def plateau_grad(x: float) -> float:
    return PLATEAU_A * x


def plateau_value(x: float) -> float:
    return 0.5 * PLATEAU_A * x * x
