"""Why "linear" is a limitation, and why activation functions are not optional.

Run from inside examples/:

    ../.venv/bin/python3 06_the_limit_of_linear.py

Three facts, each demonstrated rather than asserted in prose:

    1. a linear transformation always fixes the origin;
    2. it always sends straight lines to straight lines -- the midpoint of two
       points lands on the midpoint of their landing places, every time;
    3. a stack of linear transformations, however deep, collapses to ONE
       matrix, so the stack can do nothing a single layer could not.

Put together, they say something concrete about neural networks: twenty
matrix layers with nothing between them are exactly one matrix layer, and no
matrix can draw a curved boundary. That is the reason a non-linear activation
sits between the layers, and it is the best thing this lab has to offer.
"""

import math
import random

import numpy as np

import shapes
from transforms import apply, compose, rotation, scaling, shear_x, transform_polygon

TOL = shapes.TOL


def main() -> None:
    print("06_the_limit_of_linear.py")
    print("=" * 70)

    M = compose(rotation(math.radians(30)), shear_x(1.5))

    # -- 1. The origin cannot move --------------------------------------------
    print()
    print("1. The origin never moves")
    print("-" * 70)
    print(f"  M @ (0, 0) = {apply(M, (0.0, 0.0))}")
    print("  M @ (0, 0) is 0 lots of column 0 plus 0 lots of column 1, which is")
    print("  (0, 0) whatever the columns hold. There is no matrix anywhere that")
    print("  moves the origin. If your data needs shifting, that shift has to")
    print("  arrive from somewhere else -- and in a network layer it does,")
    print("  under the name b.")
    landed = apply(M, (0.0, 0.0))
    assert abs(landed[0]) <= TOL and abs(landed[1]) <= TOL

    # -- 2. Straight stays straight -------------------------------------------
    print()
    print("2. Straight lines land as straight lines")
    print("-" * 70)
    p = (1.0, 3.0)
    q = (4.0, -2.0)
    midpoint = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    print(f"  p = {p}   q = {q}   midpoint of p and q = {midpoint}")
    landed_mid = apply(M, midpoint)
    mid_of_landed = tuple(
        (a + b) / 2 for a, b in zip(apply(M, p), apply(M, q))
    )
    print(f"  M @ midpoint            = {tuple(round(c, 12) for c in landed_mid)}")
    print(f"  midpoint of M@p and M@q = {tuple(round(c, 12) for c in mid_of_landed)}")
    print(f"  the same within {TOL!r}: "
          f"{all(abs(a - b) <= TOL for a, b in zip(landed_mid, mid_of_landed))}")
    assert all(abs(a - b) <= TOL for a, b in zip(landed_mid, mid_of_landed))

    print()
    print("  And not just the midpoint. Eleven points spaced evenly along the")
    print("  line from p to q stay evenly spaced along a line after the transform:")
    worst = 0.0
    for i in range(11):
        t = i / 10
        on_line = (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
        expected = tuple(
            a + t * (b - a) for a, b in zip(apply(M, p), apply(M, q))
        )
        got = apply(M, on_line)
        worst = max(worst, max(abs(a - b) for a, b in zip(got, expected)))
    print(f"  worst disagreement across all eleven points: {worst!r}")
    assert worst <= TOL
    print("  Evenly spaced in, evenly spaced out. A transformation that cannot")
    print("  bend a line cannot draw a curve, and a boundary that needs a curve")
    print("  is therefore out of reach -- not hard, out of reach.")

    # -- 3. A stack collapses --------------------------------------------------
    print()
    print("3. A stack of linear layers is one linear layer")
    print("-" * 70)
    random.seed(102)
    stack = [
        [[random.uniform(-2, 2) for _ in range(2)] for _ in range(2)]
        for _ in range(20)
    ]
    print("  Twenty 2 by 2 matrices with pseudo-random entries (seed 102),")
    print("  applied one after another to a point.")

    point = (0.7, -0.4)
    one_at_a_time = point
    for layer in stack:
        one_at_a_time = apply(layer, one_at_a_time)

    combined = stack[0]
    for layer in stack[1:]:
        combined = compose(layer, combined)
    all_at_once = apply(combined, point)

    print(f"  twenty applications:      {one_at_a_time}")
    print(f"  one combined matrix:      {all_at_once}")
    print(f"  the combined matrix is    [{combined[0]}, {combined[1]}]")
    relative = max(
        abs(a - b) / max(1.0, abs(a)) for a, b in zip(one_at_a_time, all_at_once)
    )
    print(f"  largest relative difference: {relative!r}")
    print()
    print("  A wider tolerance is used here on purpose, and saying why is more")
    print("  useful than hiding it: these entries are not small whole numbers,")
    print("  the two routes multiply them in a different ORDER, and floating")
    print("  point addition is not associative, so twenty layers of rounding")
    print("  accumulate. On this run the two routes agreed to within a")
    print("  relative 1e-15 -- close, but not to the last bit, and demanding")
    print("  the last bit would be demanding something arithmetic does not")
    print("  promise. The check allows 1e-9, which is loose enough to stay")
    print("  true on another machine and tight enough to catch a real error.")
    assert relative <= 1e-9

    print()
    print("  The point stands regardless of the last few digits: twenty layers")
    print("  did nothing that one 2 by 2 matrix could not do. Depth bought")
    print("  nothing. Stack a thousand and it is still one matrix.")

    # -- 4. The consequence, made concrete -------------------------------------
    print()
    print("4. The data that no stack of these can separate")
    print("-" * 70)
    print("  Four points, the classic exclusive-or arrangement:")
    print("    (0, 0) -> class A      (1, 1) -> class A")
    print("    (1, 0) -> class B      (0, 1) -> class B")
    print()
    print("  Class A sits on one diagonal and class B on the other. No straight")
    print("  line separates them -- try it on paper, it takes about ten seconds")
    print("  to convince yourself. A linear transformation followed by a")
    print("  threshold can only ever cut the plane with a straight line, and a")
    print("  stack of them still cuts with a straight line, because point 3")
    print("  says the stack IS one transformation.")
    print()
    print("  Notice that (0, 0) is one of the four. It cannot be moved at all")
    print("  by any matrix, so it is not even a matter of finding good weights.")
    a_points = [(0.0, 0.0), (1.0, 1.0)]
    b_points = [(1.0, 0.0), (0.0, 1.0)]
    for M_try in [scaling(3.0, -2.0), shear_x(4.0), rotation(1.0), combined]:
        moved_a = [apply(M_try, p) for p in a_points]
        assert abs(moved_a[0][0]) <= TOL and abs(moved_a[0][1]) <= TOL
    print("  Checked against four different matrices: (0, 0) stayed at (0, 0)")
    print("  in every one.")

    print()
    print("5. Which is what the activation function is for")
    print("-" * 70)
    print("  Put a function that is NOT linear between the layers -- ReLU, which")
    print("  replaces every negative number with zero, is the usual one -- and")
    print("  the collapse in point 3 stops working, because you can no longer")
    print("  slide the matrices together past it. Depth starts to buy something.")
    print()
    relu_out = [max(0.0, c) for c in apply(M, (1.0, -1.0))]
    print(f"  M @ (1, -1)            = {tuple(round(c, 6) for c in apply(M, (1.0, -1.0)))}")
    print(f"  ReLU of that           = {tuple(round(c, 6) for c in relu_out)}")
    u, v = (1.0, -1.0), (0.5, 2.0)
    relu = lambda pt: tuple(max(0.0, c) for c in apply(M, pt))
    together = relu((u[0] + v[0], u[1] + v[1]))
    separately = tuple(a + b for a, b in zip(relu(u), relu(v)))
    print(f"  relu(M @ (u + v))      = {tuple(round(c, 6) for c in together)}")
    print(f"  relu(M@u) + relu(M@v)  = {tuple(round(c, 6) for c in separately)}")
    print("  Not equal -- so this composite is not linear, so it is not a")
    print("  matrix, so no amount of algebra folds the layers together. The")
    print("  non-linearity is doing the one job the matrix cannot.")
    assert any(abs(a - b) > TOL for a, b in zip(together, separately))

    # -- 6. NumPy -------------------------------------------------------------
    print()
    print("6. NumPy says the same about the stack")
    print("-" * 70)
    npstack = [np.array(layer) for layer in stack]
    npcombined = npstack[0]
    for layer in npstack[1:]:
        npcombined = layer @ npcombined
    print(f"  the product of all twenty: {np.round(npcombined, 6).tolist()}")
    assert np.allclose(npcombined, np.array(combined), rtol=1e-9, atol=0.0)
    print("  agrees with the from-scratch product to a relative 1e-9")

    square = transform_polygon(combined, shapes.UNIT_SQUARE)
    print(f"  the unit square under the whole stack: "
          f"{[(round(x, 4), round(y, 4)) for x, y in square]}")
    print("  still a parallelogram -- four straight edges, opposite sides")
    print("  parallel, one corner nailed to the origin. Twenty layers deep.")

    print()
    print("06_the_limit_of_linear.py: every assertion held.")


if __name__ == "__main__":
    main()
