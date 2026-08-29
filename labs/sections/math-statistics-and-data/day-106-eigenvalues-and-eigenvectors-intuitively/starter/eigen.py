"""Exercise 1 — six functions to write. Your work goes here.

Every function currently `return NotImplemented`, which is what makes the
matching test SKIP rather than fail. Replace each one and the skip turns into
a pass. Check yourself at any point with, from the lab directory:

    .venv/bin/pytest starter -q

Read `00_brief.md` first. It gives the exercises in order with the exact
commands.

The docstrings below tell you what each function must do and, where it
matters, WHY the obvious implementation is wrong. Read them before writing.
"""

from __future__ import annotations

import numpy as np


def abs_cosine(u, v):
    """EXERCISE 1a — return the absolute cosine of the angle between u and v.

    1.0 when the two lie on the same LINE, 0.0 when they are at right angles.

    Steps:
      1. Convert both to float arrays with numpy.asarray(..., dtype=float)
         and flatten them with .ravel().
      2. Compute each one's length with numpy.linalg.norm.
      3. If either length is 0.0, raise ValueError with a message containing
         the words "no direction" — the zero vector has no direction, so no
         angle exists. Returning 0.0 or nan instead would be a lie.
      4. Otherwise return abs(numpy.dot(u, v)) divided by the product of the
         two lengths, as a plain Python float.

    Take the ABSOLUTE value. That is the whole point of this function and the
    single most important habit in this lab: an eigenvector is defined only up
    to sign and scale, so (1, -2) and (-1, 2) are the same answer. Without the
    abs, half of your correct answers will look wrong.
    """
    return NotImplemented


def characteristic_coefficients(matrix):
    """EXERCISE 1b — return (trace, determinant) of a 2x2 matrix, as floats.

    These two numbers ARE the characteristic equation, because for any 2x2

        det(A - lambda*I) = lambda^2 - (trace)*lambda + (determinant)

    Steps:
      1. numpy.asarray(matrix, dtype=float).
      2. If its shape is not (2, 2), raise ValueError with a message
         containing "2x2".
      3. trace       = m[0,0] + m[1,1]
         determinant = m[0,0]*m[1,1] - m[0,1]*m[1,0]
      4. Return them as a tuple of two plain floats.
    """
    return NotImplemented


def eigenvalues_2x2(matrix):
    """EXERCISE 1c — solve the characteristic equation. Return two complex numbers.

        lambda = (trace +/- sqrt(trace^2 - 4*determinant)) / 2

    Steps:
      1. Get trace and determinant from characteristic_coefficients.
      2. discriminant = trace*trace - 4*determinant
      3. Take its square root with numpy.emath.sqrt, NOT numpy.sqrt.
         numpy.sqrt of a negative float returns nan and warns; numpy.emath.sqrt
         returns a complex number, which is the correct answer and is what
         makes the rotation case in exercise 3 work without special-casing.
      4. Return (complex((trace + root) / 2), complex((trace - root) / 2)).

    Always complex, even when the imaginary part is zero, so the caller has one
    code path instead of two.
    """
    return NotImplemented


def eigenvector_2x2(matrix, eigenvalue):
    """EXERCISE 1d — return a unit-length eigenvector for a real eigenvalue.

    Solve (A - lambda*I) v = 0 for a non-zero v.

    Why a solution exists: lambda is a root of the characteristic equation, so
    det(A - lambda*I) is 0, so that matrix squashes the plane onto a line
    (Day 102). A whole line of vectors gets sent to the origin, and any one of
    them is an eigenvector.

    Steps:
      1. shifted = matrix - eigenvalue * numpy.eye(2)
      2. For each ROW [p, q] of `shifted`, the candidate (-q, p) satisfies
         p*x + q*y = 0 automatically. Check it: p*(-q) + q*(p) = 0.
      3. Take the first row whose candidate is not the zero vector — compare
         its norm against a small tolerance, not against 0.0 exactly, because
         the entries are floats.
      4. Return that candidate divided by its own norm.
      5. If BOTH rows give the zero vector, the matrix was lambda*I and EVERY
         direction is an eigenvector; return numpy.array([1.0, 0.0]).

    Do not try to fix the sign. Whichever sign falls out is correct, and the
    test compares directions with abs_cosine for exactly that reason.
    """
    return NotImplemented


def power_method(matrix, start, tol=1e-10, max_iter=1000):
    """EXERCISE 1e — find the dominant eigenvector by repeated multiplication.

    Return a dict with keys "vector", "eigenvalue", "iterations", "converged".

    The algorithm:
      1. v = start as a float array, divided by its own norm.
         If start has norm 0.0, raise ValueError mentioning "zero vector".
      2. Loop `iteration` from 1 to max_iter:
           w = matrix @ v
           divide w by its norm
           IF numpy.dot(w, v) < 0, negate w
               — this aligns the signs. Without it, a matrix with a negative
                 dominant eigenvalue flips direction every single step and
                 your convergence test never fires, even though the ANSWER
                 converged on iteration three.
           change = numpy.linalg.norm(w - v)
           v = w
           if change < tol: return the dict with converged=True
      3. If the loop finishes, return the dict with converged=False and
         iterations=max_iter. Report the failure; do not raise and do not
         pretend it converged.

    For "eigenvalue" use the Rayleigh quotient: (v . matrix @ v) / (v . v).

    Normalising each round is not optional. Without it the vector's length
    multiplies by the eigenvalue every step and overflows to inf after a few
    hundred rounds, destroying a direction that was already correct.
    """
    return NotImplemented


def covariance_matrix(data):
    """EXERCISE 1f — the covariance matrix of an (n_points, n_features) array.

    Steps:
      1. numpy.asarray(data, dtype=float).
      2. If it is not 2-D, raise ValueError with a message containing "2-D".
      3. CENTRE IT: subtract data.mean(axis=0). Do not skip this. Without it
         you measure where the cloud sits rather than how it is shaped, and
         exercise 5 shows the answer coming out 136 degrees wrong with no
         error raised.
      4. Return (centred.T @ centred) / (n_points - 1).

    The result is always symmetric, and that symmetry is what guarantees PCA
    gets real eigenvalues and perpendicular eigenvectors.
    """
    return NotImplemented
