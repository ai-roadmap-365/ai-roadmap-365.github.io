"""Nine functions to write. Every one has a working signature, a docstring
saying exactly what it must do, and a `return None` where your code goes.
Returning None is how the test suite knows an exercise has not been
attempted yet: `pytest starter -q` SKIPS unattempted work rather than
failing it, so your score only ever counts what you have actually done.

Check yourself as you go:

    .venv/bin/pytest starter -q

`dataset.py` sits beside this file with every constant and helper function
you need -- read it, do not change it. `numpy` is used only where a
function genuinely needs a vector (exercises 5, 6 and part of 1); the
scalar exercises need nothing beyond arithmetic.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Exercise 1 -- numeric_gradient
# ---------------------------------------------------------------------------


def numeric_gradient(f, x, h=1e-6):
    """The gradient of `f` at `x`, by central differences (Day 108's
    definition: (f(x+h) - f(x-h)) / (2h), applied to every coordinate).

    `x` may be a plain Python float, in which case call `f` with a float
    on either side of `x` and return a float. Or `x` may be a 1-D
    array-like, in which case `f` expects the whole vector: perturb one
    coordinate at a time, holding the rest fixed, and return a numpy array
    the same shape as `x`.

    Approach: `np.isscalar(x)` tells the two cases apart. For the vector
    case, copy `x` into a numpy array, then for each index i build a
    forward copy with x[i] + h and a backward copy with x[i] - h.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 2 -- gradient_descent
# ---------------------------------------------------------------------------


def gradient_descent(grad_fn, x0, lr, iters):
    """Run `iters` steps of x <- x - lr * grad_fn(x), starting from x0.

    Return the WHOLE path as a list of length iters + 1, with path[0]
    equal to x0 -- every later exercise inspects the path, not just the
    final value.

    Approach: build a list starting with x0, then loop `iters` times,
    each time computing x <- x - lr * grad_fn(x) and appending the new x.
    Wrap the loop body in `with np.errstate(over="ignore", invalid="ignore"):`
    so that a diverging run overflows to inf and then nan instead of
    printing a runtime warning -- that overflow is the point of exercise 3's
    fourth regime, not a bug to prevent.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 3 -- classify the regime a 1-D quadratic run fell into
# ---------------------------------------------------------------------------


def classify_regime(path, a, lr):
    """Look at a path produced by gradient_descent on f(x) = 0.5*a*x**2 and
    return one of the four strings 'monotone', 'exact', 'oscillating',
    'divergent' -- purely from the observed VALUES in `path`, not from a
    and lr directly, so this is a real behavioural check.

    - 'exact': the second value in the path (path[1]) is exactly 0.0.
    - 'oscillating': the sign alternates from one step to the next AND
      |x| is non-increasing (allow a tiny numerical slack, say 1e-12).
    - 'monotone': |x| is non-increasing and the sign never alternates.
    - 'divergent': anything else -- in particular, the final |x| is much
      larger than the first.

    Approach: compute the list of |x| values and the list of signs first,
    then work through the four cases above in order.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 4 -- the measured per-step contraction ratio
# ---------------------------------------------------------------------------


def per_step_ratios(path):
    """Return the list of |x_{n+1} / x_n| for every step where x_n != 0.

    For f(x) = 0.5*a*x**2 this should equal |1 - lr*a| at every step --
    exercise 4 in test_starter.py measures that prediction against what
    this function actually returns, rather than assuming the formula.

    Approach: one line, a list comprehension over consecutive pairs.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 5 -- steps needed to reach a gradient-norm tolerance
# ---------------------------------------------------------------------------


def steps_to_tolerance(grad_fn, x0, lr, tol, max_iters):
    """Run plain gradient descent (no path storage needed) until
    ||grad_fn(x)|| < tol, and return the number of steps TAKEN before that
    happened. If the tolerance is never reached within max_iters, return
    max_iters.

    `x0` here is a numpy array (a point in 2-D, for the ill-conditioning
    exercise), so `grad_fn(x)` returns a numpy array too and its norm is
    `np.linalg.norm(...)`.

    Approach: a for loop over `range(max_iters)`. At the top of each
    iteration, compute the gradient and check its norm BEFORE taking the
    step -- that is what makes step 0 a valid answer when x0 is already
    within tolerance.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 6 -- momentum
# ---------------------------------------------------------------------------


def gradient_descent_momentum(grad_fn, x0, lr, beta, iters):
    """x <- x - lr * v, where v <- beta * v + grad_fn(x), starting from
    v = 0 (a numpy array the same shape as x0) and x = x0. Return the
    whole path, exactly like `gradient_descent`.

    Momentum is not a new rule -- it substitutes an exponentially
    weighted running average of the gradient for the raw gradient in the
    SAME update. Getting the order right matters: update v first using
    the CURRENT gradient, then update x using the NEW v.

    Approach: same shape as gradient_descent, with one extra state
    variable `v` carried between iterations.
    """
    return None


def steps_to_tolerance_momentum(grad_fn, x0, lr, beta, tol, max_iters):
    """The momentum analogue of steps_to_tolerance: same stopping rule,
    same return convention, but each step updates a velocity `v` first
    and then moves `x` by `-lr * v`.

    Approach: combine the loop shape of steps_to_tolerance with the
    velocity update of gradient_descent_momentum.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 7 -- gradient checking
# ---------------------------------------------------------------------------


def gradient_check(f, grad_analytic_fn, x, h=1e-6, tol=1e-4):
    """Compare an analytic gradient function against numeric_gradient at
    `x`. Return a list of booleans, one per coordinate of x: True where
    the analytic and numeric values agree within `tol`, False where they
    do not -- so a caller can see exactly WHICH component is wrong, not
    merely that something is.

    Approach: call numeric_gradient(f, x, h) once, call
    grad_analytic_fn(x) once, then compare element by element.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 8 -- two minima
# ---------------------------------------------------------------------------


def minima_differ(final_a, final_b, margin):
    """Return True if two converged points are more than `margin` apart --
    the check that two gradient-descent runs on a non-convex function
    landed at genuinely different minima.

    Approach: one line.
    """
    return None


# ---------------------------------------------------------------------------
# Exercise 9 -- the stopping-criterion trap
# ---------------------------------------------------------------------------


def stopping_criteria_disagree(x, grad_fn, value_fn, lr, tol_grad, tol_f):
    """Take ONE gradient-descent step from `x` and report whether the
    naive '|delta f| < tol_f, so we must have converged' rule disagrees
    with the more honest '||gradient|| < tol_grad' rule.

    Return a dict with three keys:
      - 'grad_norm': the gradient's magnitude at x (a plain float; use
        abs() for a scalar x, since this exercise only ever uses scalars)
      - 'delta_f': the ABSOLUTE difference between value_fn(x) and
        value_fn(x_after_one_step)
      - 'naive_stops_early': True exactly when delta_f < tol_f AND
        grad_norm >= tol_grad -- the naive rule fires while the honest
        rule says training is not done.

    Approach: compute grad = grad_fn(x), then x_after = x - lr * grad,
    then compare value_fn at both points.
    """
    return None
