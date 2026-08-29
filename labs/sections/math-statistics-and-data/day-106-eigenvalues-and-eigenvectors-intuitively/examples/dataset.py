"""The matrices this lab works with, and the answers worked out by hand.

Everything here is invented and every number is small enough to check on
paper. Nothing is read from disk and nothing is downloaded.

The star of the lab is `A`. It was chosen so that the characteristic equation
factorises over the integers, which means the whole eigenvalue calculation can
be done by hand in about a minute and then checked against NumPy:

    A = [[4, 1],
         [2, 3]]

    trace  = 4 + 3 = 7
    det    = 4*3 - 1*2 = 10
    characteristic equation:  lambda^2 - 7*lambda + 10 = 0
                              (lambda - 5)(lambda - 2) = 0
    eigenvalues:              5 and 2

    for lambda = 5:  A - 5I = [[-1, 1], [2, -2]]  ->  -x + y = 0  ->  (1, 1)
    for lambda = 2:  A - 2I = [[ 2, 1], [2,  1]]  ->  2x + y = 0  ->  (1, -2)

Check both by hand:

    A @ (1,  1) = (4 + 1, 2 + 3) = ( 5,  5) = 5 * (1,  1)
    A @ (1, -2) = (4 - 2, 2 - 6) = ( 2, -4) = 2 * (1, -2)
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# The worked 2x2
# --------------------------------------------------------------------------

A = np.array([[4.0, 1.0], [2.0, 3.0]])

#: The eigenvalues of `A`, worked out by hand above, largest first.
A_EIGENVALUES = (5.0, 2.0)

#: One eigenvector per eigenvalue, in the same order. NOT normalised, and
#: deliberately so: any non-zero multiple of these is equally correct, which
#: is the point exercise 4 is built around.
A_EIGENVECTORS = ((1.0, 1.0), (1.0, -2.0))

#: The direction of each eigenvector as an angle in degrees, measured from the
#: positive x-axis and folded into [0, 180) because a direction and its
#: reverse lie on the same line.
#:   atan2( 1,  1) =  45 degrees
#:   atan2(-2,  1) = -63.4349... degrees, which is 116.5650... modulo 180
A_EIGEN_ANGLES_DEG = (45.0, 116.56505117707799)

# --------------------------------------------------------------------------
# The standard transformations from Day 102, and what each one does to a line
# --------------------------------------------------------------------------

IDENTITY = np.eye(2)
UNIFORM_SCALE = 2.0 * np.eye(2)
NON_UNIFORM_SCALE = np.diag([3.0, 0.5])
REFLECTION_IN_X = np.array([[1.0, 0.0], [0.0, -1.0]])
SHEAR = np.array([[1.0, 1.0], [0.0, 1.0]])
ROTATION_90 = np.array([[0.0, -1.0], [1.0, 0.0]])
ROTATION_60 = np.array(
    [
        [0.5, -np.sqrt(3.0) / 2.0],
        [np.sqrt(3.0) / 2.0, 0.5],
    ]
)
PROJECTION_ONTO_X = np.array([[1.0, 0.0], [0.0, 0.0]])

#: A symmetric matrix, for the two guarantees symmetry buys: real eigenvalues
#: and orthogonal eigenvectors. trace 4, det 3, so lambda^2 - 4L + 3 = 0 and
#: the eigenvalues are 3 and 1.
SYMMETRIC = np.array([[2.0, 1.0], [1.0, 2.0]])

#: A larger symmetric matrix, so the orthogonality claim is checked on
#: something that is not a 2x2 special case.
SYMMETRIC_3X3 = np.array(
    [
        [4.0, 1.0, 2.0],
        [1.0, 3.0, 0.0],
        [2.0, 0.0, 5.0],
    ]
)

#: name -> (matrix, one-line description of what it does to directions)
STANDARD_TRANSFORMATIONS = {
    "identity": (IDENTITY, "leaves everything alone; every direction is an eigenvector"),
    "uniform scale 2x": (UNIFORM_SCALE, "stretches everything equally; every direction survives"),
    "non-uniform scale": (NON_UNIFORM_SCALE, "stretches x by 3 and squashes y by half"),
    "reflection in x-axis": (REFLECTION_IN_X, "flips the sign of y; one eigenvalue is negative"),
    "shear": (SHEAR, "slides the top of the square sideways; only ONE eigendirection"),
    "rotation 90 degrees": (ROTATION_90, "turns every vector; NO real eigenvector at all"),
    "rotation 60 degrees": (ROTATION_60, "the same story at a different angle"),
    "projection onto x-axis": (PROJECTION_ONTO_X, "flattens the plane onto a line; det 0, eigenvalue 0"),
}

# --------------------------------------------------------------------------
# The tiny 2-D dataset for the PCA demonstration
# --------------------------------------------------------------------------

#: The seed for every random draw in this lab. Fixed so that every number in
#: expected-output/ is reproducible on any machine.
SEED = 2106

#: The direction the invented cloud is deliberately stretched along, in
#: degrees from the positive x-axis. PCA has to rediscover this number from
#: the data alone.
ELONGATION_DEG = 30.0

#: Standard deviation of the cloud along the elongation direction, and across
#: it. The ratio 3.0 : 0.4 is what makes the cloud visibly cigar-shaped.
SPREAD_ALONG = 3.0
SPREAD_ACROSS = 0.4

#: How many points, and where the cloud is centred. The centre is deliberately
#: away from the origin so that forgetting to subtract the mean is a mistake
#: with visible consequences.
N_POINTS = 400
CENTRE = np.array([5.0, -2.0])


def elongation_direction() -> np.ndarray:
    """The unit vector the cloud is stretched along. The answer PCA must find."""
    radians = np.radians(ELONGATION_DEG)
    return np.array([np.cos(radians), np.sin(radians)])


def make_cloud() -> np.ndarray:
    """Build the invented 2-D dataset: shape (N_POINTS, 2), one point per row.

    The construction is the whole trick, and it is worth reading rather than
    running: take a unit vector `along` pointing at ELONGATION_DEG, and the
    unit vector `across` at right angles to it. Draw a wide spread of numbers
    to travel `along` and a narrow spread to travel `across`, add them, and
    shift the whole cloud to CENTRE. The result is a cigar-shaped cloud whose
    long axis is known exactly, because it was put there on purpose.

    Nothing about the direction is stored in the array that comes back. The
    covariance matrix has to recover it from 400 pairs of coordinates.
    """
    rng = np.random.default_rng(SEED)
    along = elongation_direction()
    across = np.array([-along[1], along[0]])

    travel_along = rng.normal(0.0, SPREAD_ALONG, size=N_POINTS)
    travel_across = rng.normal(0.0, SPREAD_ACROSS, size=N_POINTS)

    return travel_along[:, None] * along + travel_across[:, None] * across + CENTRE


#: The starting vector for the power method. Drawn from the same seeded
#: generator so the iteration count in expected-output/ is reproducible.
def power_method_start() -> np.ndarray:
    """A random unit vector to start the power method from.

    Random on purpose: the whole claim is that ALMOST ANY starting vector
    converges to the dominant eigenvector, so starting from something chosen
    to work would prove nothing.
    """
    rng = np.random.default_rng(106)
    v = rng.normal(size=2)
    return v / np.linalg.norm(v)
