"""Exercise 2 — solving a 2x2 with a pencil, then checking against NumPy.

Run from inside examples/:

    ../.venv/bin/python3 02_by_hand_2x2.py

Exercise 1 found the eigendirections by brute-force measurement, which works
and does not scale. This script does the same job with algebra: derive the
characteristic equation, solve the quadratic, and read the eigenvectors out of
the squashed matrix. Then hand the same matrix to numpy.linalg.eig and check.

The check is where the interesting part is, and it is not the part anyone
expects.
"""

from __future__ import annotations

import warnings

import numpy as np

from dataset import A, A_EIGENVALUES, A_EIGENVECTORS
from eigen import abs_cosine, characteristic_coefficients, eigenvalues_2x2, eigenvector_2x2

SCRIPT = "02_by_hand_2x2.py"

TOL = 1e-9


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()

    # ---------------------------------------------------------------- 1
    print("1. The characteristic equation, derived rather than quoted.")
    print()
    print("   Ask: for which numbers lambda does A v = lambda v have a solution")
    print("   other than v = 0? Rearrange it so one side is zero:")
    print()
    print("       A v = lambda v")
    print("       A v - lambda v = 0")
    print("       (A - lambda I) v = 0")
    print()
    print("   The I is there because you cannot subtract a number from a matrix.")
    print("   lambda I is the number lambda spread down the diagonal, which does")
    print("   to v exactly what multiplying by lambda does.")
    print()
    print("   Now (A - lambda I) is one matrix, and it sends some non-zero v to")
    print("   the origin. Day 102 named the matrices that do that: the ones with")
    print("   determinant zero, the ones that squash the plane onto a line. So:")
    print()
    print("       det(A - lambda I) = 0")
    print()

    trace, determinant = characteristic_coefficients(A)
    print(f"   For A = [[4, 1], [2, 3]]:  trace = {trace:.0f}, determinant = {determinant:.0f}")
    print()
    print("       A - lambda I = [[4 - lambda,          1],")
    print("                       [         2, 3 - lambda]]")
    print()
    print("       det = (4 - lambda)(3 - lambda) - 1*2")
    print("           = 12 - 4*lambda - 3*lambda + lambda^2 - 2")
    print("           = lambda^2 - 7*lambda + 10")
    print()
    print("   and the 7 is the trace while the 10 is the determinant, which is")
    print("   not a coincidence and holds for every 2x2.")
    print()
    assert trace == 7.0 and determinant == 10.0

    # ---------------------------------------------------------------- 2
    print("2. Solve the quadratic.")
    print()
    discriminant = trace * trace - 4.0 * determinant
    print(f"       discriminant = trace^2 - 4*det = {trace:.0f}^2 - 4*{determinant:.0f} = {discriminant:.0f}")
    print(f"       sqrt({discriminant:.0f}) = {np.sqrt(discriminant):.0f}")
    print(f"       lambda = (7 +/- 3) / 2  ->  5 and 2")
    print()
    print("   Or factorise it and skip the formula:  (lambda - 5)(lambda - 2) = 0")
    print()

    by_hand = eigenvalues_2x2(A)
    print(f"   eigenvalues_2x2(A) = {tuple(round(value.real, 12) for value in by_hand)}")
    print(f"   imaginary parts    = {tuple(round(value.imag, 12) for value in by_hand)}  (both zero: two real eigenvalues)")
    print()
    assert abs(by_hand[0].real - 5.0) < TOL
    assert abs(by_hand[1].real - 2.0) < TOL
    assert all(abs(value.imag) < TOL for value in by_hand)

    # ---------------------------------------------------------------- 3
    print("3. Read each eigenvector out of the squashed matrix.")
    print()
    for eigenvalue, expected in zip(A_EIGENVALUES, A_EIGENVECTORS):
        shifted = A - eigenvalue * np.eye(2)
        v = eigenvector_2x2(A, eigenvalue)
        print(f"   lambda = {eigenvalue:.0f}:")
        print(f"       A - {eigenvalue:.0f}I = [[{shifted[0, 0]:5.0f}, {shifted[0, 1]:5.0f}],")
        print(f"{'':17}[{shifted[1, 0]:5.0f}, {shifted[1, 1]:5.0f}]]")
        print(f"       determinant of that = {np.linalg.det(shifted):.1e}  (zero, as it must be)")
        print(f"       row 0 says {shifted[0, 0]:.0f}*x + {shifted[0, 1]:.0f}*y = 0")
        print(f"       one solution: ({expected[0]:.0f}, {expected[1]:.0f})")
        print(f"       eigenvector_2x2 returned: [{v[0]: .6f}, {v[1]: .6f}]")
        print(f"       same line? abs_cosine = {abs_cosine(v, expected):.15f}")
        if float(np.dot(v, expected)) < 0.0:
            print("       (it came back pointing the other way along that line.")
            print("        Not a bug. The row [p, q] gives (-q, p) and the sign of")
            print("        that depends on which row happened to be non-zero.)")
        out = A @ np.array(expected)
        print(f"       check: A @ ({expected[0]:.0f}, {expected[1]:.0f}) = ({out[0]:.0f}, {out[1]:.0f}) = {eigenvalue:.0f} * ({expected[0]:.0f}, {expected[1]:.0f})")
        print()
        assert abs(np.linalg.det(shifted)) < 1e-12
        assert abs_cosine(v, expected) > 1.0 - TOL
        assert np.allclose(out, eigenvalue * np.array(expected))

    print("   Notice what is NOT determined here. Row 0 of (A - 5I) says")
    print("   -x + y = 0. That is one equation for two unknowns, so it names a")
    print("   whole LINE of solutions: (1, 1), (2, 2), (-1, -1), (0.3, 0.3).")
    print("   All of them are eigenvectors. There is no such thing as THE")
    print("   eigenvector for an eigenvalue, only the eigen-LINE, and every")
    print("   library that returns one has made an arbitrary choice on your")
    print("   behalf. Section 5 shows NumPy making exactly that choice.")
    print()

    # ---------------------------------------------------------------- 4
    print("4. Now numpy.linalg.eig on the same matrix.")
    print()
    values, vectors = np.linalg.eig(A)
    print(f"   eigenvalues  = {values}")
    print(f"   dtype        = {values.dtype}")
    print(f"   eigenvectors =")
    for row in vectors:
        print(f"                  [{row[0]!s:>26}  {row[1]!s:>26}]")
    print(f"   dtype        = {vectors.dtype}")
    print()
    print("   The eigenvalues are 5 and 2, matching the hand calculation. But")
    print("   they came back as complex128 with zero imaginary parts, on a real")
    print("   matrix with two real eigenvalues.")
    print()
    print("   That is worth pausing on, because the docstring shipped with this")
    print("   very version of NumPy says otherwise. Quoting it exactly:")
    print()
    print('       "The resulting array will be of complex type, unless the')
    print('        imaginary part is zero in which case it will be cast to a')
    print('        real type."')
    print()
    print(f"   Observed on numpy {np.__version__} on the authoring machine: the")
    print("   imaginary part IS zero, and the array was NOT cast to a real type.")
    print("   Every case tried came back complex128 — including numpy.eye(2),")
    print("   whose eigenvalues are both exactly 1.")
    print()
    for name, matrix in (
        ("numpy.eye(2)", np.eye(2)),
        ("numpy.diag([1., 2., 3.])", np.diag([1.0, 2.0, 3.0])),
        ("an integer matrix [[2,0],[0,3]]", np.array([[2, 0], [0, 3]])),
    ):
        dtype = np.linalg.eig(matrix)[0].dtype
        print(f"       {name:<32} -> {dtype}")
        assert dtype == np.complex128
    print()
    assert values.dtype == np.complex128
    assert vectors.dtype == np.complex128
    assert np.all(values.imag == 0.0)

    # ---------------------------------------------------------------- 5
    print("5. Why that costs you something, and what to do about it.")
    print()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        as_float = values.astype(float)
        categories = [item.category.__name__ for item in caught]
    print(f"   values.astype(float) = {as_float}   and it warned: {categories}")
    print()
    print("   The fix is one attribute, and it should be a reflex:")
    print()
    real_values = values.real
    real_vectors = vectors.real
    print(f"       values.real  = {real_values}   dtype {real_values.dtype}")
    print()
    print("   But .real is a claim, so check it before you make it:")
    print()
    print("       if numpy.all(numpy.abs(values.imag) < 1e-12):")
    print("           values = values.real")
    print("       else:")
    print("           ... this matrix has no real eigenvalues, handle that case")
    print()
    print("   Taking .real without the check on a rotation matrix silently")
    print("   throws away the entire answer. Exercise 3 shows that happening.")
    print()
    assert as_float.dtype == np.float64
    assert categories == ["ComplexWarning"]
    assert real_values.dtype == np.float64

    # ---------------------------------------------------------------- 6
    print("6. Do the hand answer and the NumPy answer agree?")
    print()
    order = np.argsort(real_values)[::-1]
    print("   eigenvalues, largest first:")
    for hand, numpy_value in zip(A_EIGENVALUES, real_values[order]):
        print(f"       by hand {hand:.0f}   numpy {numpy_value:.12f}   difference {abs(hand - numpy_value):.3e}")
        assert abs(hand - numpy_value) < TOL
    print()
    print("   eigenvectors — and here the naive comparison FAILS:")
    print()
    for eigenvalue, hand, column in zip(A_EIGENVALUES, A_EIGENVECTORS, order):
        theirs = real_vectors[:, column]
        mine = np.array(hand) / np.linalg.norm(hand)
        print(f"       lambda = {eigenvalue:.0f}")
        print(f"         mine   [{mine[0]: .6f}, {mine[1]: .6f}]")
        print(f"         numpy  [{theirs[0]: .6f}, {theirs[1]: .6f}]")
        print(f"         numpy.allclose(mine, theirs)      -> {np.allclose(mine, theirs)}")
        print(f"         abs_cosine(mine, theirs)          -> {abs_cosine(mine, theirs):.15f}")
        print()
        assert abs_cosine(mine, theirs) > 1.0 - TOL

    print("   For lambda = 2 the two answers are exact negatives of each other,")
    print("   and numpy.allclose says False. Nothing is wrong. (1, -2) and")
    print("   (-1, 2) name the same line, and the equation A v = lambda v holds")
    print("   for both — multiply both sides by -1 and it is the same statement.")
    print()
    print("   So: never compare eigenvectors component by component. Compare")
    print("   the absolute cosine, which asks the only question that has a")
    print("   determinate answer: do these two lie on the same LINE?")
    print()

    # ---------------------------------------------------------------- 7
    print("7. The equation itself, checked numerically for every returned pair.")
    print()
    for index in range(len(real_values)):
        lam = real_values[index]
        v = real_vectors[:, index]
        left = A @ v
        right = lam * v
        residual = float(np.linalg.norm(left - right))
        print(f"       lambda = {lam:.6f}")
        print(f"         A @ v      = [{left[0]: .12f}, {left[1]: .12f}]")
        print(f"         lambda * v = [{right[0]: .12f}, {right[1]: .12f}]")
        print(f"         residual   = {residual:.3e}   (tolerance 1e-12)")
        assert residual < 1e-12
    print()
    print("   That residual check is the one to keep. It does not care about")
    print("   sign, scale, ordering or dtype: it asks whether the matrix really")
    print("   does to v what multiplying by a single number does.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
