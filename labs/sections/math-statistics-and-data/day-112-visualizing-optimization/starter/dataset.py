"""Shared numbers for the Day 112 lab -- given to you, not an exercise.

Identical to examples/dataset.py. This day's own subject is turning arrays
into pictures; the loss surfaces and the learning-rate schedule below are
infrastructure carried over from Day 111 so you can spend your effort on
visualization, not on re-deriving a bowl function.
"""

import numpy as np

# -- the two bowls -----------------------------------------------------------

WELL_A, WELL_B = 1.0, 1.0
ILL_A, ILL_B = 1.0, 25.0

START = np.array([4.0, 4.0])
LEARNING_RATE = 0.038
STEPS = 60


def bowl(a: float, b: float):
    """Return (f, grad) for f(x, y) = a x^2 + b y^2."""

    def f(x, y):
        return a * x**2 + b * y**2

    def grad(x, y):
        return np.array([2.0 * a * x, 2.0 * b * y])

    return f, grad


WELL_F, WELL_GRAD = bowl(WELL_A, WELL_B)
ILL_F, ILL_GRAD = bowl(ILL_A, ILL_B)

# -- the one-dimensional bowl used for the learning-rate sweep ---------------

SWEEP_X0 = 4.0
SWEEP_STEPS = 300


def sweep_f(x):
    return x**2


def sweep_grad(x):
    return 2.0 * x


# -- tolerances ----------------------------------------------------------

EXACT_TOL = 1e-9
LOSS_MATCH_TOL = 0.05
PATH_LENGTH_RATIO_MIN = 5.0
PIXEL_TOL = 2.0


def gradient_descent(grad_fn, x0, lr: float, steps: int) -> np.ndarray:
    """Given: run steps of x <- x - lr * grad_fn(x), returning every visited
    point as an array of shape (steps + 1, len(x0)).

    This is Day 111's subject -- the update rule itself -- not this day's.
    """
    x = np.array(x0, dtype=float)
    path = [x.copy()]
    for _ in range(steps):
        x = x - lr * np.asarray(grad_fn(*x))
        path.append(x.copy())
    return np.array(path)


def losses_along(f, path: np.ndarray) -> np.ndarray:
    """Given: evaluate f at every point on a path."""
    return np.array([f(*p) for p in path])
