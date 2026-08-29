"""The determinant as an area factor, the inverse, and what a collapse costs.

Run from inside examples/:

    ../.venv/bin/python3 05_determinant_inverse_rank.py

The determinant is introduced here the way it is actually useful: send the unit
square through the transformation and measure the area of what comes out. That
number, with its sign, IS the determinant. Everything else -- when an inverse
exists, what rank means, why a collapse is permanent -- reads off it.
"""

import numpy as np

import shapes
from transforms import (
    apply,
    compose,
    determinant,
    identity,
    inverse,
    rank,
    reflection_in_x_axis,
    scaling,
    shear_x,
    signed_area,
    transform_polygon,
    SingularMatrix,
)

TOL = shapes.TOL


def main() -> None:
    print("05_determinant_inverse_rank.py")
    print("=" * 70)

    print()
    print("1. The unit square, before anything happens to it")
    print("-" * 70)
    print(f"  corners (anticlockwise): {shapes.UNIT_SQUARE}")
    print(f"  signed area: {signed_area(shapes.UNIT_SQUARE)}")
    assert abs(signed_area(shapes.UNIT_SQUARE) - 1.0) <= TOL
    print("  Anticlockwise gives a POSITIVE area. List the same four corners")
    print("  the other way round and the shoelace formula returns -1. That sign")
    print("  is the thing to watch.")

    # -- 2. Measure, then compare against the determinant ---------------------
    print()
    print("2. Send it through four transformations and measure what comes out")
    print("-" * 70)
    cases = [
        ("scaling(2, 3)", scaling(2.0, 3.0), 6.0),
        ("shear_x(2)", shear_x(2.0), 1.0),
        ("reflection in x", reflection_in_x_axis(), -1.0),
        ("collapse", shapes.COLLAPSE_MATRIX, 0.0),
    ]
    print(f"  {'transformation':<18}{'measured area':>15}{'determinant':>14}"
          f"{'by hand':>10}")
    for name, M, by_hand in cases:
        moved = transform_polygon(M, shapes.UNIT_SQUARE)
        area = signed_area(moved)
        det = determinant(M)
        print(f"  {name:<18}{area:>15}{det:>14}{by_hand:>10}")
        assert abs(area - det) <= TOL, (name, area, det)
        assert abs(det - by_hand) <= TOL, (name, det, by_hand)

    print()
    print("  The measured area and the determinant are the same number every")
    print("  time, sign included. The determinant is not a formula that happens")
    print("  to be useful; it is the area factor, computed without drawing.")

    # -- 3. What the sign means -----------------------------------------------
    print()
    print("3. What a NEGATIVE determinant means")
    print("-" * 70)
    F = reflection_in_x_axis()
    flipped = transform_polygon(F, shapes.UNIT_SQUARE)
    print(f"  before: {shapes.UNIT_SQUARE}")
    print(f"  after : {flipped}")
    print(f"  signed area went from {signed_area(shapes.UNIT_SQUARE)} to "
          f"{signed_area(flipped)}")
    print("  The size did not change -- the square is still area 1. What")
    print("  changed is that the corners now run clockwise. The plane was")
    print("  turned over, and no amount of rotating will turn it back, the same")
    print("  way no amount of turning a left glove makes it a right one.")
    assert signed_area(flipped) < 0
    assert abs(abs(signed_area(flipped)) - 1.0) <= TOL

    # -- 4. What zero means ----------------------------------------------------
    print()
    print("4. What a ZERO determinant means")
    print("-" * 70)
    G = shapes.COLLAPSE_MATRIX
    print(f"  G = [{G[0]}, {G[1]}]")
    print("  column 0 = (1, 2)   column 1 = (2, 4)")
    print("  The second column is exactly twice the first. Both basis vectors")
    print("  land on the SAME LINE through the origin, so everything else does")
    print("  too -- there is nowhere else left to land.")
    landed = [apply(G, p) for p in [(1.0, 0.0), (0.0, 1.0), (3.0, -1.0), (7.0, 7.0)]]
    for start, end in zip([(1.0, 0.0), (0.0, 1.0), (3.0, -1.0), (7.0, 7.0)], landed):
        on_line = abs(end[1] - 2.0 * end[0]) <= TOL
        print(f"    {str(start):<12} -> {str(end):<14} on the line y = 2x: {on_line}")
        assert on_line
    squashed = transform_polygon(G, shapes.UNIT_SQUARE)
    print(f"  the unit square becomes {squashed}")
    print(f"  its area is {signed_area(squashed)}")
    assert abs(signed_area(squashed)) <= TOL
    print()
    print("  Two different starting points now share a landing place:")
    print(f"    (2, 0) -> {apply(G, (2.0, 0.0))}")
    print(f"    (0, 1) -> {apply(G, (0.0, 1.0))}")
    assert apply(G, (2.0, 0.0)) == apply(G, (0.0, 1.0))
    print("  No rule can send that shared place back to both of them. The")
    print("  information is not hidden, it is gone, and that is exactly what")
    print("  'no inverse' means.")

    # -- 5. Rank ---------------------------------------------------------------
    print()
    print("5. Rank: how many dimensions survive")
    print("-" * 70)
    for name, M in [
        ("identity", identity()),
        ("scaling(2, 3)", scaling(2.0, 3.0)),
        ("shear_x(2)", shear_x(2.0)),
        ("collapse", G),
        ("everything to the origin", [[0.0, 0.0], [0.0, 0.0]]),
    ]:
        mine = rank(M)
        theirs = int(np.linalg.matrix_rank(np.array(M)))
        print(f"  {name:<26} rank {mine}   numpy.linalg.matrix_rank: {theirs}")
        assert mine == theirs
    print()
    print("  Rank 2: the output still fills the plane. Rank 1: it is squashed")
    print("  onto a line. Rank 0: everything lands on the origin. For a square")
    print("  matrix, full rank and a non-zero determinant are the same sentence.")
    assert rank(G) == shapes.COLLAPSE_RANK

    # -- 6. The inverse --------------------------------------------------------
    print()
    print("6. The inverse, where one exists")
    print("-" * 70)
    H = shear_x(2.0)
    Hinv = inverse(H)
    print(f"  shear_x(2)          [{H[0]}, {H[1]}]")
    print(f"  its inverse         [{Hinv[0]}, {Hinv[1]}]")
    print("  which is shear_x(-2) -- push the deck of cards back the other way.")
    back = compose(Hinv, H)
    print(f"  inverse @ original = [{back[0]}, {back[1]}]   the identity")
    for row, want in zip(back, identity()):
        for got, expect in zip(row, want):
            assert abs(got - expect) <= TOL
    probe = (1.0, 1.0)
    there = apply(H, probe)
    home = apply(Hinv, there)
    print(f"  {probe} -> {there} -> {home}")
    assert abs(home[0] - probe[0]) <= TOL and abs(home[1] - probe[1]) <= TOL

    S = scaling(2.0, 3.0)
    Sinv = inverse(S)
    print(f"  scaling(2, 3) inverse: [{Sinv[0]}, {Sinv[1]}]")
    print("  which is scaling by 1/2 and 1/3, as it must be.")
    assert abs(Sinv[0][0] - 0.5) <= TOL
    assert abs(Sinv[1][1] - 1.0 / 3.0) <= TOL

    # -- 7. Asking for the impossible ------------------------------------------
    print()
    print("7. Asking for the inverse of a collapse")
    print("-" * 70)
    try:
        inverse(G)
    except SingularMatrix as exc:
        print(f"  from-scratch inverse raises SingularMatrix: {exc}")
    else:  # pragma: no cover - the assert below turns this into a failure
        raise AssertionError("the from-scratch inverse should have refused")

    try:
        np.linalg.inv(np.array(G))
    except np.linalg.LinAlgError as exc:
        print(f"  numpy.linalg.inv raises {type(exc).__name__}: {exc}")
    else:  # pragma: no cover
        raise AssertionError("numpy should have refused too")

    print()
    print("  Both refuse, and both refusals are catchable as ValueError:")
    print(f"    SingularMatrix is a ValueError:      "
          f"{issubclass(SingularMatrix, ValueError)}")
    print(f"    numpy.linalg.LinAlgError is one too: "
          f"{issubclass(np.linalg.LinAlgError, ValueError)}")
    assert issubclass(SingularMatrix, ValueError)
    assert issubclass(np.linalg.LinAlgError, ValueError)

    # -- 8. Where the two determinants disagree, and why ----------------------
    print()
    print("8. An honest difference between the two determinants")
    print("-" * 70)
    P = shapes.PICTURE_MATRIX
    mine = determinant(P)
    theirs = float(np.linalg.det(np.array(P)))
    print(f"  P = [{P[0]}, {P[1]}]")
    print(f"  by hand:            3 * 2 - (-1) * 1 = {shapes.PICTURE_DETERMINANT}")
    print(f"  from-scratch:       {mine!r}")
    print(f"  numpy.linalg.det:   {theirs!r}")
    print(f"  they differ by      {abs(mine - theirs)!r}")
    print()
    print("  This is not a bug in either one. The from-scratch version computes")
    print("  a*d - b*c directly, which for these four whole numbers is exact.")
    print("  numpy.linalg.det factorises the matrix first -- the same routine")
    print("  it uses for a 500 by 500 matrix, where the direct formula is not")
    print("  an option -- and that factorisation rounds. The general method")
    print("  pays a little accuracy on tiny inputs to stay usable on large")
    print("  ones. It is a good trade and it is worth knowing about, because")
    print("  it is why you compare determinants with a tolerance rather than")
    print("  with ==.")
    assert abs(mine - shapes.PICTURE_DETERMINANT) <= TOL
    assert abs(theirs - shapes.PICTURE_DETERMINANT) <= 1e-9
    assert mine == shapes.PICTURE_DETERMINANT

    print()
    print("05_determinant_inverse_rank.py: every assertion held.")


if __name__ == "__main__":
    main()
