"""Exercise 3 — the eigenvectors of the transformations you already know.

Run from inside examples/:

    ../.venv/bin/python3 03_standard_transformations.py

Day 102 built a small vocabulary of transformations: scale, reflect, shear,
rotate, project. Each one is a matrix, so each one has eigenvalues, and the
answers are not all of the same kind. One has every direction. One has two.
One has exactly one. One has none at all.

The "none at all" case is the one to spend time on, because it is the moment
the geometry and the algebra agree loudly.
"""

from __future__ import annotations

import numpy as np

from dataset import (
    ROTATION_60,
    ROTATION_90,
    SHEAR,
    STANDARD_TRANSFORMATIONS,
    SYMMETRIC,
    SYMMETRIC_3X3,
)
from eigen import abs_cosine, direction_degrees, eigen_lines_by_sweep, sweep_deviations

SCRIPT = "03_standard_transformations.py"

TOL = 1e-9


def describe(matrix) -> tuple[np.ndarray, np.ndarray, bool]:
    """eigenvalues, eigenvectors, and whether the eigenvalues are all real."""
    values, vectors = np.linalg.eig(np.asarray(matrix, dtype=float))
    is_real = bool(np.all(np.abs(values.imag) < 1e-12))
    return values, vectors, is_real


def main() -> None:
    print(f"{SCRIPT}")
    print("=" * 72)
    print()

    # ---------------------------------------------------------------- 1
    print("1. Every transformation from Day 102, and what it does to directions.")
    print()
    print("   Two independent answers per matrix: what numpy.linalg.eig says,")
    print("   and what a brute-force sweep of 180,000 directions measures. They")
    print("   have to agree, and where they seem not to, the disagreement is")
    print("   itself the lesson.")
    print()
    for name, (matrix, note) in STANDARD_TRANSFORMATIONS.items():
        values, vectors, is_real = describe(matrix)
        determinant = float(np.linalg.det(matrix))
        found = eigen_lines_by_sweep(matrix)
        print(f"   {name}")
        print(f"     matrix       [[{matrix[0, 0]: .4f}, {matrix[0, 1]: .4f}], [{matrix[1, 0]: .4f}, {matrix[1, 1]: .4f}]]")
        print(f"     determinant  {determinant: .6f}")
        if is_real:
            real_values = values.real
            real_vectors = vectors.real
            print(f"     eigenvalues  {np.array2string(real_values, precision=6, suppress_small=True)}   (real)")
            directions = sorted({round(direction_degrees(real_vectors[:, i]), 6) for i in range(2)})
            same_line = abs_cosine(real_vectors[:, 0], real_vectors[:, 1]) > 1.0 - 1e-8
            print(f"     eig columns  {directions} degrees" + ("  <-- BOTH THE SAME LINE" if same_line else ""))
        else:
            print(f"     eigenvalues  {np.array2string(values, precision=6, suppress_small=True)}   (COMPLEX: no real eigenvector)")
        summary = found["verdict"] if found["verdict"] != "some" else f"{len(found['lines'])} line(s) near {found['lines']} degrees"
        print(f"     measured     {summary}")
        if found["collapsed"]:
            print(f"     collapsed    {found['collapsed']} degrees sent to the origin (eigenvalue 0)")
        print(f"     {note}")
        print()

    print("   Three rows in that table are worth arguing with.")
    print()
    print("   The identity and the uniform scaling: eig returned the columns 0")
    print("   and 90 degrees, which reads like two special directions. The sweep")
    print("   says 'every direction', and the sweep is right. When every")
    print("   direction is an eigenvector, eig still has to return exactly two")
    print("   columns, so it returns a basis and the arbitrariness is invisible.")
    print()
    print("   The projection: the sweep found ONE surviving line and separately")
    print("   reported that 90 degrees was collapsed to the origin. The y-axis")
    print("   IS an eigenvector, with eigenvalue 0, but 'did it keep its")
    print("   direction?' cannot be answered about a vector that no longer has")
    print("   one. Measuring angles cannot see eigenvalue 0; the algebra can.")
    print()
    print("   The shear: eig returned two columns, the sweep found one line.")
    print("   Section 2 is about that.")
    print()

    # ---------------------------------------------------------------- 2
    print("2. The shear: one eigenvalue, repeated, and only one eigen-line.")
    print()
    values, vectors, _ = describe(SHEAR)
    print("   S = [[1, 1],")
    print("        [0, 1]]  — slides the top of the unit square to the right.")
    print()
    print(f"   eigenvalues: {np.array2string(values.real, precision=6, suppress_small=True)}  — 1 twice. Its ALGEBRAIC multiplicity is 2.")
    print(f"   NumPy returned two eigenvectors anyway:")
    for i in range(2):
        column = vectors.real[:, i]
        print(f"       column {i}: [{column[0]: .17f}, {column[1]: .17f}]")
    similarity = abs_cosine(vectors.real[:, 0], vectors.real[:, 1])
    print()
    print(f"   abs_cosine between them = {similarity:.15f}")
    print("   They are the same line. NumPy has to return a square array of")
    print("   eigenvectors, so when there are not enough distinct directions to")
    print("   fill it, it fills the space anyway. Counting COLUMNS would tell you")
    print("   there are two eigendirections. There is one. The number of")
    print("   independent directions is the GEOMETRIC multiplicity, and here it")
    print("   is 1 while the algebraic multiplicity is 2 — the gap is exactly")
    print("   what makes this matrix impossible to diagonalise.")
    print()
    print("   Geometrically it is obvious. A shear leaves the x-axis alone and")
    print("   tilts everything else. Only the horizontal line survives.")
    print()
    assert np.allclose(values.real, [1.0, 1.0], atol=TOL)
    assert similarity > 1.0 - 1e-8

    # Confirm it by brute force too: sweep the circle and count the bands.
    found = eigen_lines_by_sweep(SHEAR)
    print(f"   Brute-force check: sweeping 180,000 directions finds")
    print(f"   {len(found['lines'])} surviving line, near {found['lines'][0]} degrees — the x-axis, to")
    print(f"   the accuracy a sampled sweep can offer. One line, found by")
    print(f"   measurement, agreeing with the one line found by algebra.")
    print()
    assert found["verdict"] == "some"
    assert len(found["lines"]) == 1
    assert min(found["lines"][0], 180.0 - found["lines"][0]) < 0.05

    # ---------------------------------------------------------------- 3
    print("3. The rotation: no real eigenvector at all, and you can SEE why.")
    print()
    for name, matrix, degrees in (("90 degrees", ROTATION_90, 90.0), ("60 degrees", ROTATION_60, 60.0)):
        values, _, is_real = describe(matrix)
        print(f"   rotation by {name}:")
        print(f"       eigenvalues  {np.array2string(values, precision=6, suppress_small=True)}")
        print(f"       all real?    {is_real}")
        print(f"       magnitudes   {np.round(np.abs(values), 12).tolist()}  (rotation changes no lengths, so both are 1)")
        print(f"       real parts   {np.round(values.real, 6).tolist()}  = cos({degrees:.0f} degrees) = {np.cos(np.radians(degrees)):.6f}")
        print(f"       imag parts   {np.round(values.imag, 6).tolist()}  = +/- sin({degrees:.0f} degrees) = {np.sin(np.radians(degrees)):.6f}")
        print()
        assert not is_real
        assert np.allclose(np.abs(values), 1.0, atol=TOL)

    print("   The geometry says it first: a rotation turns EVERY vector by the")
    print("   same angle. If a vector kept its line it would have to be turned")
    print("   by 0 or by 180 degrees, and this rotation turns by neither. So no")
    print("   direction survives, and there is nothing for the algebra to find.")
    print()
    print("   The algebra says the same thing in its own words. For the 90-degree")
    print("   rotation, trace = 0 and determinant = 1, so:")
    print("       lambda^2 - 0*lambda + 1 = 0   ->   lambda^2 = -1")
    print("   and no real number squares to -1. The negative discriminant is not")
    print("   an error message; it is the algebra reporting the geometry.")
    print()
    trace = float(ROTATION_90[0, 0] + ROTATION_90[1, 1])
    determinant = float(np.linalg.det(ROTATION_90))
    print(f"       measured: trace = {trace:.0f}, determinant = {determinant:.0f}, discriminant = {trace * trace - 4 * determinant:.0f}")
    print()
    assert trace == 0.0 and abs(determinant - 1.0) < TOL

    grid = np.arange(0.0, 180.0, 0.001)
    deviations, _collapsed = sweep_deviations(ROTATION_90, grid)
    smallest = float(np.nanmin(deviations))
    found = eigen_lines_by_sweep(ROTATION_90)
    print(f"   Brute-force check: over 180,000 directions the SMALLEST swing was")
    print(f"   {smallest:.6f} degrees, and the sweep reports verdict '{found['verdict']}'.")
    print(f"   Nothing came close to keeping its line. A 90-degree rotation turns")
    print(f"   every single direction by 90 degrees, which is the largest swing")
    print(f"   there is once you measure lines rather than arrows.")
    print()
    assert smallest > 89.0
    assert found["verdict"] == "none" and found["lines"] == []

    print("   And here is the trap from exercise 2, sprung. Take .real without")
    print("   checking, and the answer becomes:")
    print()
    values, _, _ = describe(ROTATION_90)
    print(f"       values        = {values}")
    print(f"       values.real   = {values.real}   <-- both zero. The answer is gone.")
    print("   Two eigenvalues of magnitude 1 have been silently reported as 0.")
    print()
    assert np.allclose(values.real, 0.0, atol=TOL)

    # ---------------------------------------------------------------- 4
    print("4. Eigenvalue 0 means the matrix collapsed a direction, and that is")
    print("   the same fact as determinant 0 from Day 102.")
    print()
    projection = STANDARD_TRANSFORMATIONS["projection onto x-axis"][0]
    values, vectors, _ = describe(projection)
    real_values = values.real
    print("   P = [[1, 0],")
    print("        [0, 0]]  — flattens the whole plane onto the x-axis.")
    print()
    print(f"       eigenvalues  {np.array2string(real_values, precision=6, suppress_small=True)}")
    print(f"       determinant  {np.linalg.det(projection):.6f}")
    print(f"       product of the eigenvalues = {float(np.prod(real_values)):.6f}")
    print(f"       sum of the eigenvalues     = {float(np.sum(real_values)):.6f},  trace = {float(np.trace(projection)):.6f}")
    print()
    print("   Two identities worth carrying, both checkable on every matrix in")
    print("   section 1: the eigenvalues multiply to the determinant and add to")
    print("   the trace. So a zero eigenvalue and a zero determinant are the same")
    print("   news arriving twice — some direction was squashed to nothing, and")
    print("   the transformation cannot be undone.")
    print()
    for name, (matrix, _note) in STANDARD_TRANSFORMATIONS.items():
        values, _, _ = describe(matrix)
        product = complex(np.prod(values))
        total = complex(np.sum(values))
        assert abs(product.real - np.linalg.det(matrix)) < 1e-9, name
        assert abs(total.real - np.trace(matrix)) < 1e-9, name
        print(f"       {name:<24} product {product.real: .6f} = det,   sum {total.real: .6f} = trace")
    print()

    # ---------------------------------------------------------------- 5
    print("5. Symmetric matrices: two guarantees, checked rather than proved.")
    print()
    print("   A symmetric matrix — one equal to its own transpose — always has")
    print("   REAL eigenvalues, and eigenvectors at RIGHT ANGLES to each other.")
    print("   The proof is standard and is in any linear algebra text; this lab")
    print("   only checks that the guarantee holds on the matrices it has.")
    print()
    for name, matrix in (("SYMMETRIC (2x2)", SYMMETRIC), ("SYMMETRIC_3X3", SYMMETRIC_3X3)):
        assert np.allclose(matrix, matrix.T)
        values, vectors = np.linalg.eigh(matrix)
        print(f"   {name}: symmetric? {np.array_equal(matrix, matrix.T)}")
        print(f"       numpy.linalg.eigh eigenvalues {np.array2string(values, precision=6)}   dtype {values.dtype}")
        gram = vectors.T @ vectors
        off_diagonal = float(np.abs(gram - np.eye(len(values))).max())
        print(f"       eigenvectors mutually perpendicular: largest deviation from")
        print(f"       the identity in V.T @ V is {off_diagonal:.3e}")
        for i in range(len(values)):
            residual = float(np.linalg.norm(matrix @ vectors[:, i] - values[i] * vectors[:, i]))
            assert residual < 1e-12
        print(f"       every A v = lambda v residual below 1e-12: True")
        print()
        assert values.dtype == np.float64
        assert off_diagonal < 1e-12

    print("   Note the dtype. numpy.linalg.eigh returned float64 — no complex,")
    print("   no .real needed — and its values came back sorted ascending. eig")
    print("   guarantees neither. When your matrix is symmetric, and a covariance")
    print("   matrix always is, eigh is the right call.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
