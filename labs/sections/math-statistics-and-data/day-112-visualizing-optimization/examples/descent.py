"""Exercises 7 and 8: running gradient descent and reading the run, not just
its last number.

Nothing here is imported from Day 111's lab -- the update rule is the same
three-line loop every gradient-descent lesson in this course uses, and it is
written out again here on purpose, because this lab's whole point is that the
FINAL LOSS a run prints is not enough to tell two runs apart.
"""

from __future__ import annotations

import numpy as np


def gradient_descent(grad_fn, x0, lr: float, steps: int) -> np.ndarray:
    """Run steps of x <- x - lr * grad_fn(x), returning every visited point.

    Returns an array of shape (steps + 1, len(x0)): the starting point,
    then one row per step, so path[0] is x0 and path[-1] is where the run
    stopped. Keeping the whole path (not just the endpoint) is what makes
    every other function in this lab possible -- you cannot draw a route on
    a map, or a loss curve, from a single final number.
    """
    x = np.array(x0, dtype=float)
    path = [x.copy()]
    for _ in range(steps):
        x = x - lr * np.asarray(grad_fn(*x))
        path.append(x.copy())
    return np.array(path)


def losses_along(f, path: np.ndarray) -> np.ndarray:
    """Evaluate f at every point on a path, returning one loss per row."""
    return np.array([f(*p) for p in path])


def path_length(path: np.ndarray) -> float:
    """Total Euclidean distance travelled along a path: sum of step sizes.

    A short, nearly straight path and a long, zig-zagging one can arrive at
    almost the same final loss -- path_length is the single number that
    tells them apart without needing a picture, and the picture is what
    explains WHY they differ.
    """
    steps = np.diff(path, axis=0)
    return float(np.sum(np.linalg.norm(steps, axis=1)))


def sweep_final_loss(grad_fn, f, x0: float, eta: float, steps: int) -> float:
    """Run gradient descent on a 1D function at learning rate eta, returning
    the final loss -- or float('inf') if the run diverged.

    Overflow during a diverging run is expected behaviour, not an error: a
    learning rate above the stability threshold makes the iterate grow
    without bound, and IEEE-754 represents "grew past the largest
    representable double" as inf rather than raising an exception. This
    function catches that deliberately with numpy's error-state context
    manager (over='ignore') and reports it as a value, so the reader sees a
    clean cliff in the sweep instead of a stack trace.
    """
    x = np.float64(x0)
    for _ in range(steps):
        with np.errstate(over="ignore", invalid="ignore"):
            x = x - eta * grad_fn(x)
        if not np.isfinite(x):
            return float("inf")
    with np.errstate(over="ignore", invalid="ignore"):
        value = f(x)
    return float(value) if np.isfinite(value) else float("inf")


def learning_rate_sweep(grad_fn, f, x0: float, etas, steps: int):
    """Run sweep_final_loss at every learning rate in etas.

    Returns a list of (eta, final_loss) pairs, in the order etas was given.
    """
    return [(float(eta), sweep_final_loss(grad_fn, f, x0, float(eta), steps)) for eta in etas]
