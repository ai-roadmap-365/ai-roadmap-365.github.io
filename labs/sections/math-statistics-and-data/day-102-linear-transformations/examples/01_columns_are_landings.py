"""Where do the basis vectors land? Read a matrix off a picture, and back.

Run from inside examples/:

    ../.venv/bin/python3 01_columns_are_landings.py

The claim under test: if you know where (1, 0) and (0, 1) land, you know where
every vector lands, and you did not need the picture for anything else.
"""

import numpy as np

import shapes
from transforms import apply, columns_of, from_landings

TOL = shapes.TOL


def main() -> None:
    print("01_columns_are_landings.py")
    print("=" * 70)

    # -- 1. The picture, in words ---------------------------------------------
    print()
    print("1. The picture says two things, and only two things")
    print("-" * 70)
    print(f"  the arrow (1, 0) has been redrawn ending at {shapes.PICTURE_E1_LANDS_AT}")
    print(f"  the arrow (0, 1) has been redrawn ending at {shapes.PICTURE_E2_LANDS_AT}")
    print()
    print("  Write those two landing places down as COLUMNS. That is the matrix.")

    M = from_landings(shapes.PICTURE_E1_LANDS_AT, shapes.PICTURE_E2_LANDS_AT)
    print(f"  row 0: {M[0]}")
    print(f"  row 1: {M[1]}")
    assert M == shapes.PICTURE_MATRIX

    # -- 2. And back again ----------------------------------------------------
    print()
    print("2. Reading the picture back off the matrix")
    print("-" * 70)
    e1_lands, e2_lands = columns_of(M)
    print(f"  column 0 = {e1_lands}   <- where (1, 0) went")
    print(f"  column 1 = {e2_lands}   <- where (0, 1) went")
    print()
    print("  Careful: the matrix is WRITTEN as rows. Row 0 is", M[0], "and that")
    print("  is not a landing place. (3, 1) is, and it is read downwards.")
    assert e1_lands == shapes.PICTURE_E1_LANDS_AT
    assert e2_lands == shapes.PICTURE_E2_LANDS_AT

    # -- 3. Everything else follows -------------------------------------------
    print()
    print("3. Now every other vector, without looking at the picture again")
    print("-" * 70)
    v = (2.0, 1.0)
    print(f"  {v} = 2 * (1, 0) + 1 * (0, 1)")
    print("  A linear transformation keeps that combination intact, so it must")
    print("  land at 2 * (3, 1) + 1 * (-1, 2):")
    print("      2 * (3, 1) = (6, 2)")
    print("      1 * (-1, 2) = (-1, 2)")
    print("      (6, 2) + (-1, 2) = (5, 4)")
    landed = apply(M, v)
    print(f"  from-scratch apply:  {landed}")
    assert landed == shapes.PICTURE_SENDS_2_1_TO

    # -- 4. NumPy agrees ------------------------------------------------------
    print()
    print("4. NumPy, doing the same thing with the @ operator")
    print("-" * 70)
    npM = np.array(shapes.PICTURE_MATRIX)
    npv = np.array(v)
    print(f"  M @ v = {(npM @ npv).tolist()}")
    print(f"  M @ e1 = {(npM @ np.array(shapes.E1)).tolist()}   (column 0)")
    print(f"  M @ e2 = {(npM @ np.array(shapes.E2)).tolist()}   (column 1)")
    assert np.allclose(npM @ npv, np.array(landed), atol=TOL)
    assert np.allclose(npM @ np.array(shapes.E1), np.array(e1_lands), atol=TOL)
    assert np.allclose(npM @ np.array(shapes.E2), np.array(e2_lands), atol=TOL)

    # -- 5. The identity, which is the do-nothing case ------------------------
    print()
    print("5. The matrix that leaves the basis vectors exactly where they are")
    print("-" * 70)
    I = from_landings(shapes.E1, shapes.E2)
    print(f"  from_landings((1, 0), (0, 1)) = {I}")
    print("  That is the identity matrix, and it is the identity for one reason:")
    print("  nothing moved, so nothing moves.")
    for point in [(0.0, 0.0), (2.0, 1.0), (-3.5, 7.25)]:
        assert apply(I, point) == point
    print("  checked on (0, 0), (2, 1) and (-3.5, 7.25): each came back unchanged")
    assert np.allclose(np.array(I), np.eye(2), atol=TOL)

    print()
    print("01_columns_are_landings.py: every assertion held.")


if __name__ == "__main__":
    main()
