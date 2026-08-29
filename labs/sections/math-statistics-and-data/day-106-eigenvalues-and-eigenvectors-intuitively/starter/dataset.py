"""The data for the exercises. Read this file; you do not need to change it.

The star of the lab is `A`, chosen so the whole eigenvalue calculation can be
done with a pencil in about a minute:

    A = [[4, 1],
         [2, 3]]

Work it out before you write any code. You will need the answer in exercise 2.
"""

from __future__ import annotations

import numpy as np

A = np.array([[4.0, 1.0], [2.0, 3.0]])

SHEAR = np.array([[1.0, 1.0], [0.0, 1.0]])
ROTATION_90 = np.array([[0.0, -1.0], [1.0, 0.0]])
ROTATION_60 = np.array(
    [
        [0.5, -np.sqrt(3.0) / 2.0],
        [np.sqrt(3.0) / 2.0, 0.5],
    ]
)
SYMMETRIC = np.array([[2.0, 1.0], [1.0, 2.0]])
PROJECTION_ONTO_X = np.array([[1.0, 0.0], [0.0, 0.0]])
REFLECTION_IN_X = np.array([[1.0, 0.0], [0.0, -1.0]])

# --------------------------------------------------------------------------
# The invented 2-D dataset for exercise 5
# --------------------------------------------------------------------------

SEED = 2106
ELONGATION_DEG = 30.0
SPREAD_ALONG = 3.0
SPREAD_ACROSS = 0.4
N_POINTS = 400
CENTRE = np.array([5.0, -2.0])


def elongation_direction() -> np.ndarray:
    """The unit vector the cloud is stretched along — the answer PCA must find."""
    radians = np.radians(ELONGATION_DEG)
    return np.array([np.cos(radians), np.sin(radians)])


def make_cloud() -> np.ndarray:
    """400 points, shape (400, 2), stretched along ELONGATION_DEG degrees.

    Seeded, so your numbers will match the captured output exactly.
    """
    rng = np.random.default_rng(SEED)
    along = elongation_direction()
    across = np.array([-along[1], along[0]])
    travel_along = rng.normal(0.0, SPREAD_ALONG, size=N_POINTS)
    travel_across = rng.normal(0.0, SPREAD_ACROSS, size=N_POINTS)
    return travel_along[:, None] * along + travel_across[:, None] * across + CENTRE


def power_method_start() -> np.ndarray:
    """A seeded random unit vector, for exercise 4."""
    rng = np.random.default_rng(106)
    v = rng.normal(size=2)
    return v / np.linalg.norm(v)
