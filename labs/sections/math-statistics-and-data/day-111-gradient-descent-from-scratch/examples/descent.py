"""The core of the day: numeric_gradient, gradient_descent, and everything
built on top of them. Every function here is deliberately small -- the whole
point of the lab is that the entire training loop used across the rest of
this course is a handful of lines, plus a great deal of care about the
learning rate.
"""

from __future__ import annotations

import numpy as np


def numeric_gradient(f, x, h=1e-6):
    """The gradient of `f` at `x`, by central differences (Day 108's
    definition, applied to every coordinate of `x`).

    `x` may be a plain Python float, in which case call `f` with a float
    on either side of `x` and return a float. Or `x` may be a 1-D
    array-like, in which case `f` is called with the whole perturbed
    vector and is expected to accept one; returns a numpy array the same
    shape as `x`.
    """
    if np.isscalar(x):
        return (f(x + h) - f(x - h)) / (2.0 * h)
    point = np.asarray(x, dtype=float)
    grad = np.zeros_like(point)
    for i in range(point.size):
        forward = point.copy()
        backward = point.copy()
        forward[i] += h
        backward[i] -= h
        grad[i] = (f(forward) - f(backward)) / (2.0 * h)
    return grad


def gradient_descent(grad_fn, x0, lr, iters):
    """Run `iters` steps of x <- x - lr * grad_fn(x), starting from x0.

    Returns the WHOLE path as a list of length iters + 1, path[0] == x0,
    so later exercises can inspect every intermediate value rather than
    only the final answer.

    Runs under numpy's error state set to 'ignore' for overflow: a
    diverging run is expected to produce inf and then nan, and that is the
    day's own point (a diverging training run looks exactly like this),
    not a crash to be prevented.
    """
    path = [x0]
    x = x0
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(iters):
            x = x - lr * grad_fn(x)
            path.append(x)
    return path


def gradient_descent_momentum(grad_fn, x0, lr, beta, iters):
    """x <- x - lr * v, where v <- beta * v + grad_fn(x).

    Momentum is not a different rule; it is an exponentially weighted
    running average of the gradient, substituted for the raw gradient in
    the same update. Returns the whole path, same shape as
    `gradient_descent`.
    """
    path = [x0]
    x = x0
    v = np.zeros_like(np.asarray(x0, dtype=float)) if not np.isscalar(x0) else 0.0
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(iters):
            g = grad_fn(x)
            v = beta * v + g
            x = x - lr * v
            path.append(x)
    return path


def steps_to_tolerance(grad_fn, x0, lr, tol, max_iters):
    """Run gradient descent until the gradient's norm drops below `tol`,
    and return the number of steps taken (not the path). Returns
    `max_iters` if the tolerance was never reached, so callers can tell a
    slow run from a run that never converges.
    """
    x = x0
    scalar = np.isscalar(x0)
    with np.errstate(over="ignore", invalid="ignore"):
        for step in range(max_iters):
            g = grad_fn(x)
            norm = abs(g) if scalar else float(np.linalg.norm(np.asarray(g, dtype=float)))
            if norm < tol:
                return step
            x = x - lr * g
    return max_iters


def steps_to_tolerance_momentum(grad_fn, x0, lr, beta, tol, max_iters):
    """The momentum analogue of `steps_to_tolerance`."""
    x = x0
    v = np.zeros_like(np.asarray(x0, dtype=float))
    with np.errstate(over="ignore", invalid="ignore"):
        for step in range(max_iters):
            g = np.asarray(grad_fn(x), dtype=float)
            if float(np.linalg.norm(g)) < tol:
                return step
            v = beta * v + g
            x = x - lr * v
    return max_iters


def gradient_check(f, grad_analytic_fn, x, h=1e-6, tol=1e-4):
    """Compare an analytic gradient function against a numerical one at
    `x`. Returns a list of booleans, one per coordinate of x, True where
    the two agree within `tol` and False where they do not -- so a caller
    can identify exactly which components are wrong, not merely that
    something is.
    """
    point = np.atleast_1d(np.asarray(x, dtype=float))
    analytic = np.atleast_1d(np.asarray(grad_analytic_fn(point), dtype=float))
    numeric = np.atleast_1d(numeric_gradient(f, point, h))
    return [bool(abs(a - n) < tol) for a, n in zip(analytic, numeric)]


def per_step_ratios(path):
    """The measured contraction ratio |x_{n+1} / x_n| at every step of a
    1-D path where x_n != 0. For a quadratic f(x) = 0.5 * a * x**2 this
    should equal |1 - lr * a| at every step -- exercise 4 measures that
    prediction rather than assuming it.
    """
    return [abs(path[i + 1] / path[i]) for i in range(len(path) - 1) if path[i] != 0]


def minima_differ(final_a, final_b, margin):
    """True if two converged points are farther apart than `margin` --
    the check that two gradient-descent runs on a non-convex function
    landed at genuinely different minima rather than both near the same
    one.
    """
    return abs(final_a - final_b) > margin


def stopping_criteria_disagree(x, grad_fn, value_fn, lr, tol_grad, tol_f):
    """Take ONE gradient-descent step from `x` and report whether the two
    common stopping rules disagree: the naive '|delta f| < tol_f, so we
    must have converged' rule against the more honest
    '||gradient|| < tol_grad' rule.

    Returns a dict with the measured gradient norm, the measured |delta f|,
    and `naive_stops_early`: True when |delta f| < tol_f while the
    gradient norm is still >= tol_grad -- exactly the trap where "the loss
    stopped changing" is mistaken for "we converged".
    """
    grad = grad_fn(x)
    grad_norm = abs(grad) if np.isscalar(grad) else float(np.linalg.norm(grad))
    f_before = value_fn(x)
    x_after = x - lr * grad
    f_after = value_fn(x_after)
    delta_f = abs(f_after - f_before)
    return {
        "grad_norm": grad_norm,
        "delta_f": delta_f,
        "naive_stops_early": bool(delta_f < tol_f and grad_norm >= tol_grad),
    }


def classify_regime(path, a, lr):
    """Classify a 1-D quadratic gradient-descent run into one of
    'monotone', 'exact', 'oscillating', 'divergent', purely from the
    observed path (never from lr and a directly), so the classification is
    a real behavioural check rather than a restatement of the formula.
    """
    values = [abs(v) for v in path]
    if len(values) >= 2 and values[1] == 0.0:
        return "exact"
    signs = [1 if v > 0 else (-1 if v < 0 else 0) for v in path]
    alternates = all(
        signs[i] != 0 and signs[i + 1] != 0 and signs[i] != signs[i + 1]
        for i in range(len(signs) - 1)
    )
    shrinking = all(
        values[i + 1] <= values[i] + 1e-12 for i in range(len(values) - 1)
    )
    growing = values[-1] > values[0] and not shrinking
    if alternates and shrinking:
        return "oscillating"
    if shrinking and not alternates:
        return "monotone"
    if growing or not shrinking:
        return "divergent"
    return "unknown"
