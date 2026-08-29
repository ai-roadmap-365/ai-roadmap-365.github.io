"""Scaling, reflection, shear and rotation -- each matrix derived, not given.

Run from inside examples/:

    ../.venv/bin/python3 02_building_the_transformations.py

Nothing here is memorised. Every matrix is built by asking one question --
where does (1, 0) go, and where does (0, 1) go -- and writing the two answers
down as columns.
"""

import math

import numpy as np

import shapes
from transforms import (
    apply,
    reflection_in_x_axis,
    rotation,
    scaling,
    shear_x,
    transform_polygon,
)

TOL = shapes.TOL


def show(name: str, matrix, derivation: str) -> None:
    e1 = (matrix[0][0], matrix[1][0])
    e2 = (matrix[0][1], matrix[1][1])
    print(f"  {name}")
    print(f"    {derivation}")
    print(f"    (1, 0) lands at {e1}      (0, 1) lands at {e2}")
    print(f"    matrix: [{matrix[0]}, {matrix[1]}]")


def main() -> None:
    print("02_building_the_transformations.py")
    print("=" * 70)

    # -- Scaling ---------------------------------------------------------------
    print()
    print("1. Scaling by 2 across and 3 up")
    print("-" * 70)
    S = scaling(shapes.SCALE_X, shapes.SCALE_Y)
    show(
        "scaling(2, 3)",
        S,
        "one step right becomes two steps right; one step up becomes three up",
    )
    assert S == shapes.SCALE_MATRIX
    print(f"    (1, 1) lands at {apply(S, (1.0, 1.0))}    checked by hand: (2, 3)")
    assert apply(S, (1.0, 1.0)) == (2.0, 3.0)

    # -- Reflection ------------------------------------------------------------
    print()
    print("2. Reflection in the x axis")
    print("-" * 70)
    F = reflection_in_x_axis()
    show(
        "reflection_in_x_axis()",
        F,
        "(1, 0) is ON the mirror line so it cannot move; (0, 1) mirrors to (0, -1)",
    )
    assert F == shapes.FLIP_MATRIX
    print(f"    (2, 3) lands at {apply(F, (2.0, 3.0))}   checked by hand: (2, -3)")
    assert apply(F, (2.0, 3.0)) == (2.0, -3.0)

    # -- Shear ----------------------------------------------------------------
    print()
    print("3. Shear: push sideways in proportion to height, k = 2")
    print("-" * 70)
    H = shear_x(shapes.SHEAR_K)
    show(
        "shear_x(2)",
        H,
        "(1, 0) has height 0 so nothing pushes it; (0, 1) has height 1 so it slides 2",
    )
    assert H == shapes.SHEAR_MATRIX
    print(f"    (1, 1) lands at {apply(H, (1.0, 1.0))}    checked by hand: (3, 1)")
    print(f"    (5, 0) lands at {apply(H, (5.0, 0.0))}    the x axis never moves")
    assert apply(H, (1.0, 1.0)) == (3.0, 1.0)
    assert apply(H, (5.0, 0.0)) == (5.0, 0.0)

    # -- Rotation --------------------------------------------------------------
    print()
    print("4. Rotation, derived from the unit circle")
    print("-" * 70)
    print("  Walk anticlockwise around a circle of radius 1, starting at (1, 0),")
    print("  until you have turned through theta. Where you now stand is, BY")
    print("  DEFINITION, (cos theta, sin theta). That is what those two")
    print("  functions are. So (1, 0) lands at (cos theta, sin theta), and")
    print("  (0, 1) -- already a quarter turn ahead -- lands a quarter turn")
    print("  ahead of that, at (-sin theta, cos theta).")
    print()
    for degrees in (30, 45, 90, 180):
        R = rotation(math.radians(degrees))
        print(f"  rotation({degrees} degrees):")
        print(f"    cos = {R[0][0]!r}")
        print(f"    sin = {R[1][0]!r}")
        print(f"    (1, 0) lands at ({R[0][0]!r}, {R[1][0]!r})")

    print()
    print("5. The quarter turn, and why an exact comparison would fail here")
    print("-" * 70)
    Q = rotation(math.pi / 2)
    e1_lands = apply(Q, shapes.E1)
    e2_lands = apply(Q, shapes.E2)
    print(f"  (1, 0) lands at {e1_lands!r}")
    print(f"  (0, 1) lands at {e2_lands!r}")
    print()
    print("  On paper those are (0, 1) and (-1, 0). In binary floating point")
    print(f"  cos(pi / 2) is {math.cos(math.pi / 2)!r}, which is not 0.0, because")
    print("  pi itself cannot be stored exactly and the cosine of the stored")
    print("  value is not the cosine of pi. The error is about 1e-17.")
    print(f"  So every check below uses a tolerance of {TOL!r}: five orders of")
    print("  magnitude above that rounding, and four below the smallest number")
    print("  this lab cares about. `== 0.0` would fail on a correct answer.")
    assert e1_lands != (0.0, 1.0), "exact equality really does fail here"
    assert abs(e1_lands[0] - 0.0) <= TOL and abs(e1_lands[1] - 1.0) <= TOL
    assert abs(e2_lands[0] - (-1.0)) <= TOL and abs(e2_lands[1] - 0.0) <= TOL

    # -- 6. NumPy agrees on all four ------------------------------------------
    print()
    print("6. NumPy builds the same four matrices")
    print("-" * 70)
    theta = math.pi / 2
    npQ = np.array(
        [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
    )
    for name, mine, theirs in [
        ("scaling(2, 3)", S, np.diag([2.0, 3.0])),
        ("reflection", F, np.array([[1.0, 0.0], [0.0, -1.0]])),
        ("shear_x(2)", H, np.array([[1.0, 2.0], [0.0, 1.0]])),
        ("rotation(pi/2)", Q, npQ),
    ]:
        agree = np.allclose(np.array(mine), theirs, atol=TOL)
        print(f"  {name:<16} matches NumPy within {TOL!r}: {agree}")
        assert agree

    # -- 7. The flag, transformed ---------------------------------------------
    print()
    print("7. The flag shape under each transformation")
    print("-" * 70)
    print(f"  original      {[tuple(p) for p in shapes.FLAG]}")
    for name, M in [("scaled", S), ("reflected", F), ("sheared", H), ("turned", Q)]:
        moved = transform_polygon(M, shapes.FLAG)
        rounded = [(round(x, 6) + 0.0, round(y, 6) + 0.0) for x, y in moved]
        print(f"  {name:<13} {rounded}")
        # The corner at the origin never moves, under any of them. A linear
        # transformation always fixes the origin -- there is no matrix that
        # can move it, because M @ (0, 0) is (0, 0) whatever M holds.
        assert abs(moved[0][0]) <= TOL and abs(moved[0][1]) <= TOL
    print()
    print("  Every one of them left the first corner at the origin. That is not")
    print("  a coincidence and it is not avoidable: M @ (0, 0) is (0, 0) for")
    print("  every matrix M there has ever been. A linear transformation cannot")
    print("  move the origin, which is the first of the two limits this lab is")
    print("  really about.")

    print()
    print("02_building_the_transformations.py: every assertion held.")


if __name__ == "__main__":
    main()
