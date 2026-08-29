"""Eigenvalues and eigenvectors, written out by hand.

The reference implementation. Every function here does something NumPy will
do for you in one call; the point of writing them is that afterwards you know
what that one call is doing, and you know which of its answers are forced by
mathematics and which are arbitrary choices the library made for you.

Nothing in this file imports anything beyond NumPy, and no function here
touches the file system, the clock or the network.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Measuring whether a vector kept its direction
# --------------------------------------------------------------------------


def abs_cosine(u, v) -> float:
    """The absolute cosine of the angle between two vectors: 1.0 when they lie
    on the same LINE, 0.0 when they are at right angles.

    The absolute value is the whole point, and it is the single most important
    habit in this lab. An eigenvector is defined only up to sign and scale: if
    v satisfies A v = lambda v, then so does -v, and so does 3.7 v. NumPy
    returns *a* unit-length eigenvector, and which of the two possible signs
    it hands back is a detail of the LAPACK routine underneath, not a fact
    about the matrix. So a test that compares components will fail on a
    correct answer roughly half the time. Compare DIRECTIONS instead, and
    "direction" means "line", which is what taking the absolute value does.
    """
    u = np.asarray(u, dtype=float).ravel()
    v = np.asarray(v, dtype=float).ravel()
    nu = float(np.linalg.norm(u))
    nv = float(np.linalg.norm(v))
    if nu == 0.0 or nv == 0.0:
        raise ValueError("the zero vector has no direction, so no angle is defined")
    return abs(float(np.dot(u, v)) / (nu * nv))


def deviation_degrees(u, v) -> float:
    """How far apart two directions are, in degrees, ignoring sign.

    Returns a number in [0, 90]. Zero means "these lie on the same line",
    which is exactly the test for "this vector kept its direction".
    """
    c = min(1.0, abs_cosine(u, v))
    return float(np.degrees(np.arccos(c)))


def direction_degrees(v) -> float:
    """The direction of a 2-D vector as an angle in [0, 180) degrees.

    Folded modulo 180 because a vector and its reverse describe the same line,
    and a line is what an eigenvector really names.
    """
    v = np.asarray(v, dtype=float).ravel()
    return float(np.degrees(np.arctan2(v[1], v[0])) % 180.0)


def fan_of_directions(n: int) -> np.ndarray:
    """`n` unit vectors spread evenly around the circle, as rows of an (n, 2) array."""
    angles = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    return np.column_stack([np.cos(angles), np.sin(angles)])


def sweep_deviations(matrix, angles_deg) -> tuple[np.ndarray, np.ndarray]:
    """For each angle, how far the matrix knocks that direction off its line.

    Returns (deviations, collapsed) where `deviations` is in degrees and
    `collapsed` is a boolean mask marking directions the matrix sends to the
    origin. Those get `numpy.nan` for their deviation, and that is the honest
    answer rather than a defect: the zero vector has no direction, so "did it
    keep its direction?" has nothing to compare against. A collapsed direction
    is an eigenvector with eigenvalue 0 — it is squashed rather than turned —
    and the caller has to decide what to do about it, because this measurement
    cannot.

    Vectorised on purpose: this is called with 180,000 angles in exercise 1,
    and a Python loop over that is the difference between instant and tedious.
    """
    radians = np.radians(np.asarray(angles_deg, dtype=float))
    vectors = np.column_stack([np.cos(radians), np.sin(radians)])
    outputs = vectors @ np.asarray(matrix, dtype=float).T

    input_norms = np.linalg.norm(vectors, axis=1)
    output_norms = np.linalg.norm(outputs, axis=1)
    collapsed = output_norms <= 1e-12 * max(1.0, float(np.abs(matrix).max()))

    dots = np.einsum("ij,ij->i", vectors, outputs)
    deviations = np.full(len(radians), np.nan)
    live = ~collapsed
    cosines = np.clip(
        np.abs(dots[live] / (input_norms[live] * output_norms[live])), 0.0, 1.0
    )
    deviations[live] = np.degrees(np.arccos(cosines))
    return deviations, collapsed


def eigen_lines_by_sweep(
    matrix,
    step: float = 0.001,
    keep_below: float = 0.01,
    gap: float = 1.0,
) -> dict:
    """Find the eigendirections of a 2x2 by brute-force measurement.

    Sweep every direction from 0 to 180 degrees, keep the ones the matrix
    barely moves, group the survivors into clusters, and report the very best
    angle in each cluster.

    Returns a dict with:
        verdict   one of "none", "every direction", "some"
        lines     one representative angle in degrees per distinct eigen-line
        collapsed angles the matrix sends to the origin (eigenvalue 0)
        fraction  what proportion of the swept directions kept their line

    `len(result["lines"])` is the number of distinct eigen-lines, which the
    algebra calls the geometric multiplicity count. That COUNT is the reliable
    output. The angles are approximate — good to roughly the width of the
    surviving band, which is a few hundredths of a degree here — because they
    come from sampling a smooth curve rather than from solving anything. The
    shear's single line comes back as 0.005 rather than 0.000 for exactly that
    reason: its deviation curve is not symmetric about the eigendirection, so
    the surviving band is not centred on it. Use this to find out HOW MANY
    directions survive and roughly where; use the algebra to get them exactly.

    Four details that are not obvious and that a first attempt gets wrong:

      * Only 0 to 180 is swept, because a direction and its reverse are the
        same line and sweeping the full circle would double-count every answer.
      * The clustering wraps around, because 179.999 degrees and 0.001 degrees
        are neighbours on a line-through-the-origin, not opposite ends of a
        range. A shear's single eigen-line sits exactly on that seam, so a
        version without the wrap reports two lines where there is one.
      * `keep_below` cannot be made arbitrarily small. Near an eigendirection
        the deviation curve is smooth, so the sampled grid usually straddles
        the true minimum rather than landing on it — the second eigen-line of
        this lab's matrix sits at 116.56505 degrees and the nearest sample at
        0.001-degree spacing still deviates by 7.7e-05. A threshold of 1e-06
        would find nothing there and report one eigen-line instead of two.
        0.01 degrees is far below the several-degree deviations of every
        non-eigendirection and far above the sampling error.
      * A matrix that keeps EVERY direction — the identity, or any uniform
        scaling — makes every sample a survivor, and they all merge into one
        giant cluster. Reporting "1 eigen-line" there would be exactly wrong,
        so that case is detected by the survivor fraction and named.
    """
    angles = np.arange(0.0, 180.0, step)
    deviations, collapsed = sweep_deviations(matrix, angles)
    keep = deviations < keep_below  # nan compares False, so collapsed is excluded
    fraction = float(np.count_nonzero(keep)) / len(angles)
    collapsed_angles = [float(a) for a in angles[collapsed]]

    if fraction > 0.99:
        return {
            "verdict": "every direction",
            "lines": [],
            "collapsed": collapsed_angles,
            "fraction": fraction,
        }
    if not np.any(keep):
        return {
            "verdict": "none",
            "lines": [],
            "collapsed": collapsed_angles,
            "fraction": fraction,
        }

    surviving_angles = angles[keep]
    surviving_deviations = deviations[keep]

    clusters: list[list[int]] = [[0]]
    for index in range(1, len(surviving_angles)):
        if surviving_angles[index] - surviving_angles[index - 1] <= gap:
            clusters[-1].append(index)
        else:
            clusters.append([index])

    # The seam: the last cluster may be the same line as the first one.
    if len(clusters) > 1:
        wrapped = 180.0 - surviving_angles[clusters[-1][0]] + surviving_angles[clusters[0][0]]
        if wrapped <= gap:
            clusters[0] = clusters[-1] + clusters[0]
            clusters.pop()

    # Report each cluster by its CENTRE, not by its lowest sample. Near an
    # eigendirection the deviation is so small that arccos rounds a whole run
    # of samples to exactly 0.0 — fifteen of them for the shear — so "the
    # sample with the smallest deviation" is decided by a floating-point tie
    # and lands wherever the tie happens to break. The centre of the surviving
    # band is stable, and the band is symmetric about the true eigendirection.
    #
    # Angles are folded RELATIVE TO THE CLUSTER'S OWN FIRST MEMBER, so that a
    # cluster straddling the 0/180 seam becomes contiguous. Folding at a fixed
    # boundary instead — say, everything above 90 minus 180 — splits the
    # perfectly ordinary cluster sitting at 90 degrees and reports it as two.
    best = []
    for cluster in clusters:
        raw = surviving_angles[np.array(cluster)]
        anchor = float(raw[0])
        relative = raw - anchor
        relative = np.where(relative > 90.0, relative - 180.0, relative)
        relative = np.where(relative < -90.0, relative + 180.0, relative)
        centre = anchor + (float(relative.min()) + float(relative.max())) / 2.0
        best.append(round(centre % 180.0, 6))
    return {
        "verdict": "some",
        "lines": sorted(best),
        "collapsed": collapsed_angles,
        "fraction": fraction,
    }


# --------------------------------------------------------------------------
# Solving a 2x2 by hand
# --------------------------------------------------------------------------


def characteristic_coefficients(matrix) -> tuple[float, float]:
    """The two numbers that define the characteristic equation of a 2x2.

    Returns (trace, determinant), which is everything you need, because for a
    2x2 the determinant of (A - lambda*I) always works out to

        lambda^2 - (trace)*lambda + (determinant)

    Derive it once and you never have to again. Writing A as [[a, b], [c, d]]:

        A - lambda*I = [[a - lambda, b], [c, d - lambda]]
        det          = (a - lambda)(d - lambda) - b*c
                     = lambda^2 - (a + d)*lambda + (a*d - b*c)

    and (a + d) is the trace while (a*d - b*c) is the determinant of A.
    """
    m = np.asarray(matrix, dtype=float)
    if m.shape != (2, 2):
        raise ValueError(f"this hand method is for 2x2 matrices only, got {m.shape}")
    trace = float(m[0, 0] + m[1, 1])
    determinant = float(m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0])
    return trace, determinant


def eigenvalues_2x2(matrix) -> tuple[complex, complex]:
    """Solve the characteristic equation with the school quadratic formula.

    lambda = (trace +/- sqrt(trace^2 - 4*det)) / 2

    The discriminant decides the whole character of the matrix:

      * positive  -> two different real eigenvalues, two separate eigendirections
      * zero      -> one repeated real eigenvalue; there may be one
                     eigendirection or every direction, and the eigenvalue
                     alone cannot tell you which
      * negative  -> no real eigenvalues at all, which geometrically means the
                     matrix knocks EVERY direction off its line. A rotation in
                     the plane is the example to remember.

    Returns complex numbers always, so that the negative-discriminant case
    needs no special handling by the caller. Take `.real` when you have
    already checked that the imaginary part is zero.
    """
    trace, determinant = characteristic_coefficients(matrix)
    discriminant = trace * trace - 4.0 * determinant
    root = np.emath.sqrt(discriminant)  # returns a complex root when negative
    first = (trace + root) / 2.0
    second = (trace - root) / 2.0
    return complex(first), complex(second)


def eigenvector_2x2(matrix, eigenvalue: float) -> np.ndarray:
    """A non-zero solution v of (A - lambda*I) v = 0, for a real eigenvalue.

    The reasoning, which is the part worth carrying away. Once lambda is a
    root of the characteristic equation, det(A - lambda*I) is zero, and Day
    102 taught what a zero determinant means: the matrix squashes the plane
    onto a line (or onto a point). Every vector on the line that gets squashed
    to the origin is an eigenvector, so a whole line of solutions exists and
    we only have to name one point on it.

    Concretely: writing B = A - lambda*I as [[p, q], [r, s]], the row [p, q]
    says p*x + q*y = 0. The vector (-q, p) satisfies that for free. If that
    row happens to be all zeros it tells us nothing, so we try the other row.
    If BOTH rows are zero then B is the zero matrix, every direction works,
    and we return (1, 0) with a note in the docstring rather than pretending
    the answer is unique.

    Returned as a unit vector, matching what NumPy does, and with the sign
    left exactly as the arithmetic produced it — because the sign is not
    determined by anything, and pretending otherwise is the trap this lab is
    built to teach.
    """
    m = np.asarray(matrix, dtype=float)
    if m.shape != (2, 2):
        raise ValueError(f"this hand method is for 2x2 matrices only, got {m.shape}")
    shifted = m - eigenvalue * np.eye(2)

    scale = max(1.0, float(np.abs(m).max()))
    tiny = 1e-12 * scale

    for row in (shifted[0], shifted[1]):
        candidate = np.array([-row[1], row[0]])
        if float(np.linalg.norm(candidate)) > tiny:
            return candidate / float(np.linalg.norm(candidate))

    # Both rows vanished: A was lambda*I, so EVERY direction is an
    # eigenvector. One representative is as good as another.
    return np.array([1.0, 0.0])


def solve_2x2(matrix) -> tuple[tuple[complex, complex], list[np.ndarray] | None]:
    """The whole hand method in one call: eigenvalues, and eigenvectors if real.

    Returns (eigenvalues, eigenvectors) where eigenvectors is None when the
    eigenvalues are not real — because in that case there is no real vector
    that keeps its direction, and returning something anyway would be a lie
    dressed as an answer.
    """
    values = eigenvalues_2x2(matrix)
    if any(abs(value.imag) > 1e-12 for value in values):
        return values, None
    vectors = [eigenvector_2x2(matrix, value.real) for value in values]
    return values, vectors


# --------------------------------------------------------------------------
# The power method
# --------------------------------------------------------------------------


def power_method(
    matrix,
    start=None,
    tol: float = 1e-10,
    max_iter: int = 1000,
) -> dict:
    """Find the dominant eigenvector by multiplying, over and over.

    The whole algorithm is three lines, and the reason it works is one
    sentence: write the starting vector as a mixture of the eigenvectors, and
    every application of A multiplies each ingredient by its own eigenvalue,
    so the ingredient with the largest-magnitude eigenvalue outgrows all the
    others and eventually the mixture is nothing but that one direction.

    Normalising after each step is not part of the mathematics — it is there
    to stop the numbers running away. On this lab's matrix the vector would
    grow by a factor of 5 per step, so after 500 steps it would overflow to
    infinity and the direction, which is the thing we actually want, would be
    lost inside a NaN.

    Convergence is measured as the distance between successive UNIT vectors,
    after aligning their signs — because the iteration can flip the sign at
    every step when the dominant eigenvalue is negative, and a sign flip is
    not a failure to converge.

    Returns a dict with the vector, the eigenvalue estimate (the Rayleigh
    quotient), the iteration count, the final change, and the change at every
    step, so that the RATE of convergence can be inspected as well as the
    result.
    """
    m = np.asarray(matrix, dtype=float)
    if start is None:
        v = np.ones(m.shape[0], dtype=float)
    else:
        v = np.asarray(start, dtype=float).ravel().copy()
    norm = float(np.linalg.norm(v))
    if norm == 0.0:
        raise ValueError(
            "the power method cannot start from the zero vector: "
            "A @ 0 is 0 forever, which is why the zero vector is excluded "
            "from the definition of an eigenvector in the first place"
        )
    v = v / norm

    history: list[float] = []
    for iteration in range(1, max_iter + 1):
        w = m @ v
        length = float(np.linalg.norm(w))
        if length == 0.0:
            raise ValueError(
                "the iteration collapsed to the zero vector: the starting "
                "vector lay entirely in the part of space this matrix sends "
                "to the origin"
            )
        w = w / length
        if float(np.dot(w, v)) < 0.0:
            w = -w  # align signs so a flip is not mistaken for wandering
        change = float(np.linalg.norm(w - v))
        history.append(change)
        v = w
        if change < tol:
            return {
                "vector": v,
                "eigenvalue": rayleigh_quotient(m, v),
                "iterations": iteration,
                "change": change,
                "history": history,
                "converged": True,
            }

    return {
        "vector": v,
        "eigenvalue": rayleigh_quotient(m, v),
        "iterations": max_iter,
        "change": history[-1],
        "history": history,
        "converged": False,
    }


def rayleigh_quotient(matrix, v) -> float:
    """The best scalar estimate of the eigenvalue for a given vector.

    If v really is an eigenvector then A v = lambda v exactly, so

        (v . A v) / (v . v) = (v . lambda v) / (v . v) = lambda

    and if v is merely close to an eigenvector this is the closest thing to an
    eigenvalue that v admits.

    It is usually introduced with the claim that its error is the SQUARE of
    the vector's, so it converges twice as fast. That claim has a condition
    attached which is easy to lose: it needs the eigenvectors to be at right
    angles, which symmetry guarantees. Measured in exercise 4, the ratio of
    quotient error to squared angle locks onto 2.0 for the symmetric matrix
    in this lab and runs away for the non-symmetric one, where the quotient
    converges merely linearly and buys nothing over the vector.

    So: on a symmetric matrix — a covariance matrix, a Gram matrix, a graph
    Laplacian — take the Rayleigh quotient. On a general matrix, take it
    because it is one line and is never worse, but do not expect the speed-up.
    """
    m = np.asarray(matrix, dtype=float)
    v = np.asarray(v, dtype=float).ravel()
    return float(np.dot(v, m @ v) / np.dot(v, v))


# --------------------------------------------------------------------------
# Covariance, which is where PCA starts
# --------------------------------------------------------------------------


def covariance_matrix(data) -> np.ndarray:
    """The covariance matrix of an (n_points, n_features) array, from scratch.

    Two steps, and the first is the one people forget:

      1. Subtract the mean of each column, so the cloud is centred on the
         origin. Skip this and you measure how far the cloud is from the
         origin instead of how it is shaped, and the top eigenvector points
         at the cloud rather than along it.
      2. Take Xc.T @ Xc and divide by (n - 1).

    The (n - 1) rather than n is Bessel's correction, and it is what NumPy's
    numpy.cov uses by default. It does not change the eigenVECTORS at all —
    scaling a matrix by a constant scales its eigenvalues and leaves its
    eigenvectors exactly where they were — so for PCA's directions the choice
    is irrelevant. It matters only if you quote the eigenvalues as variances.

    The result is always symmetric, because entry (i, j) and entry (j, i) are
    the same sum of products written in the other order. That symmetry is not
    decoration: it is the guarantee that the eigenvalues are real and the
    eigenvectors are at right angles, which is what makes PCA well behaved.
    """
    x = np.asarray(data, dtype=float)
    if x.ndim != 2:
        raise ValueError(f"expected a 2-D (n_points, n_features) array, got shape {x.shape}")
    n_points = x.shape[0]
    if n_points < 2:
        raise ValueError("covariance needs at least two points")
    centred = x - x.mean(axis=0)
    return (centred.T @ centred) / (n_points - 1)


def principal_components(data) -> tuple[np.ndarray, np.ndarray]:
    """PCA in five lines: centre, covariance, eigh, sort, return.

    Returns (variances, directions) with the largest variance first, and
    directions given as COLUMNS so that directions[:, 0] is the top principal
    component — matching NumPy's own convention, which is worth matching
    exactly rather than improving on.

    numpy.linalg.eigh rather than numpy.linalg.eig, because a covariance
    matrix is symmetric and eigh is the routine written for that case: it
    returns real values in ascending order rather than unsorted complex ones,
    and on the authoring machine it was an order of magnitude faster on a
    400 by 400 matrix.
    """
    covariance = covariance_matrix(data)
    variances, directions = np.linalg.eigh(covariance)
    order = np.argsort(variances)[::-1]
    return variances[order], directions[:, order]
