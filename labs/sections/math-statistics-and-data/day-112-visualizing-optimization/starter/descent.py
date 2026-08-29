"""Exercises 7 and 8 -- path_length and the learning-rate sweep.

`return None` where your code goes; `pytest starter -q` skips what you have
not attempted and fails only what you have attempted incorrectly.
"""

from __future__ import annotations

import numpy as np


def path_length(path: np.ndarray) -> float:
    """Exercise 8a -- total Euclidean distance travelled along a path: the
    sum of the step sizes between consecutive points.

    Approach: `steps = np.diff(path, axis=0)`, then sum the row-wise norm:
    `np.sum(np.linalg.norm(steps, axis=1))`.
    """
    return None


def sweep_final_loss(grad_fn, f, x0: float, eta: float, steps: int) -> float:
    """Exercise 7a -- run gradient descent on a 1D function at learning rate
    eta for `steps` steps, and return the final loss.

    A learning rate above the stability threshold makes the iterate grow
    without bound. That growth eventually overflows float64 to `inf` --
    which is expected behaviour to CATCH, not an exception to let escape.
    Use `numpy.errstate(over="ignore", invalid="ignore")` around the update
    and around the final `f(x)`, and check `np.isfinite(x)` after every step;
    return `float('inf')` the moment it stops being finite.

    Approach:

        x = np.float64(x0)
        for _ in range(steps):
            with np.errstate(over="ignore", invalid="ignore"):
                x = x - eta * grad_fn(x)
            if not np.isfinite(x):
                return float("inf")
        with np.errstate(over="ignore", invalid="ignore"):
            value = f(x)
        return float(value) if np.isfinite(value) else float("inf")
    """
    return None


def learning_rate_sweep(grad_fn, f, x0: float, etas, steps: int):
    """Exercise 7b -- run sweep_final_loss at every learning rate in etas.

    Return a list of (eta, final_loss) pairs, in the order etas was given.

    Approach: one line, a list comprehension calling sweep_final_loss.
    """
    return None
