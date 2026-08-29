"""Doing two transformations is one matrix -- and the order is not what it reads like.

Run from inside examples/:

    ../.venv/bin/python3 04_composition_and_order.py

Two claims, both checked against real numbers:

    1. shearing and then rotating a shape gives exactly the same answer as
       transforming it once by the product of the two matrices;
    2. that product is written ROTATE @ SHEAR, with the FIRST step on the
       RIGHT -- and writing it the other way round gives a different
       transformation, not a differently-spelled one.
"""

import math

import numpy as np

import shapes
from transforms import (
    apply,
    compose,
    determinant,
    rotation,
    shear_x,
    transform_polygon,
)

TOL = shapes.TOL


def rounded(points):
    return [(round(x, 6) + 0.0, round(y, 6) + 0.0) for x, y in points]


def main() -> None:
    print("04_composition_and_order.py")
    print("=" * 70)

    A = shear_x(shapes.SHEAR_K)          # step one
    B = rotation(math.pi / 2)            # step two

    print()
    print("  A = shear_x(2)        first")
    print(f"      [{A[0]}, {A[1]}]")
    print("  B = rotation(pi / 2)  second")
    print(f"      [[{B[0][0]:.1f}, {B[0][1]:.1f}], [{B[1][0]:.1f}, {B[1][1]:.1f}]]"
          "   (printed to one decimal; see script 02 for the raw values)")

    # -- 1. One step at a time -------------------------------------------------
    print()
    print("1. The two steps, one after the other, on the flag")
    print("-" * 70)
    step1 = transform_polygon(A, shapes.FLAG)
    step2 = transform_polygon(B, step1)
    print(f"  start        {rounded(shapes.FLAG)}")
    print(f"  after shear  {rounded(step1)}")
    print(f"  after turn   {rounded(step2)}")

    # -- 2. The single matrix that does both ----------------------------------
    print()
    print("2. Building the one matrix that does both, column by column")
    print("-" * 70)
    print("  Where does (1, 0) end up after BOTH steps?")
    after_e1 = apply(B, apply(A, shapes.E1))
    print(f"    shear sends (1, 0) to {apply(A, shapes.E1)}")
    print(f"    then the turn sends that to {rounded([after_e1])[0]}")
    print("  Where does (0, 1) end up?")
    after_e2 = apply(B, apply(A, shapes.E2))
    print(f"    shear sends (0, 1) to {apply(A, shapes.E2)}")
    print(f"    then the turn sends that to {rounded([after_e2])[0]}")
    print("  Write the two landings as columns and you have the composite.")

    C = compose(B, A)
    print(f"  compose(B, A) = [{rounded([tuple(C[0])])[0]}, {rounded([tuple(C[1])])[0]}]")
    print(f"  by hand:        [{shapes.SHEAR_THEN_ROTATE[0]}, {shapes.SHEAR_THEN_ROTATE[1]}]")
    for row_mine, row_hand in zip(C, shapes.SHEAR_THEN_ROTATE):
        for got, want in zip(row_mine, row_hand):
            assert abs(got - want) <= TOL, (got, want)

    # -- 3. One step gives the same answer as two -----------------------------
    print()
    print("3. One transformation, same landing places")
    print("-" * 70)
    at_once = transform_polygon(C, shapes.FLAG)
    print(f"  two steps    {rounded(step2)}")
    print(f"  one matrix   {rounded(at_once)}")
    for (x1, y1), (x2, y2) in zip(step2, at_once):
        assert abs(x1 - x2) <= TOL and abs(y1 - y2) <= TOL
    print(f"  every corner agrees within {TOL!r}")
    print()
    print("  This is why composition matters in practice. A stack of twenty")
    print("  transformations applied to a million points is twenty million")
    print("  operations; multiplying the twenty small matrices together first")
    print("  and applying one is a million. The answer is identical.")

    # -- 4. The order gotcha ---------------------------------------------------
    print()
    print("4. The order that trips everyone up")
    print("-" * 70)
    other = compose(A, B)   # rotate FIRST, then shear
    print(f"  compose(B, A)  shear then turn  = "
          f"[{rounded([tuple(C[0])])[0]}, {rounded([tuple(C[1])])[0]}]")
    print(f"  compose(A, B)  turn then shear  = "
          f"[{rounded([tuple(other[0])])[0]}, {rounded([tuple(other[1])])[0]}]")
    print(f"  by hand, turn then shear:         "
          f"[{shapes.ROTATE_THEN_SHEAR[0]}, {shapes.ROTATE_THEN_SHEAR[1]}]")
    for row_mine, row_hand in zip(other, shapes.ROTATE_THEN_SHEAR):
        for got, want in zip(row_mine, row_hand):
            assert abs(got - want) <= TOL, (got, want)

    differs = any(
        abs(a - b) > TOL for r1, r2 in zip(C, other) for a, b in zip(r1, r2)
    )
    print(f"  the two products differ: {differs}")
    assert differs
    probe = (1.0, 1.0)
    print(f"  and they send {probe} to different places:")
    print(f"    shear then turn -> {rounded([apply(C, probe)])[0]}")
    print(f"    turn then shear -> {rounded([apply(other, probe)])[0]}")
    assert rounded([apply(C, probe)])[0] != rounded([apply(other, probe)])[0]
    print()
    print("  Read a product RIGHT TO LEFT. B @ A means A first. It looks")
    print("  backwards until you write out B @ (A @ v): A is the one standing")
    print("  next to the vector, so A is the one that touches it first.")

    # -- 5. Determinants multiply ---------------------------------------------
    print()
    print("5. A free consequence: the area factors multiply")
    print("-" * 70)
    dA, dB, dC = determinant(A), determinant(B), determinant(C)
    print(f"  det(A) = {dA}    (a shear preserves area)")
    print(f"  det(B) = {dB}    (a turn preserves area)")
    print(f"  det(C) = {dC}")
    print(f"  det(A) * det(B) = {dA * dB}")
    assert abs(dC - dA * dB) <= TOL
    print("  Here both factors are 1, so the product is 1 and the composite")
    print("  preserves area as well. The rule is general and it is obvious once")
    print("  said out loud: if one step doubles area and the next triples it,")
    print("  area comes out six times bigger, whatever the matrices look like.")
    print("  A useful corollary: if either factor is 0, so is the product, so")
    print("  once a collapse has happened nothing downstream can undo it.")

    # -- 6. NumPy ---------------------------------------------------------------
    print()
    print("6. NumPy, with the @ operator")
    print("-" * 70)
    npA = np.array(A)
    npB = np.array(B)
    print(f"  B @ A = {np.round(npB @ npA, 6).tolist()}")
    print(f"  A @ B = {np.round(npA @ npB, 6).tolist()}")
    assert np.allclose(npB @ npA, np.array(C), atol=TOL)
    assert np.allclose(npA @ npB, np.array(other), atol=TOL)
    assert not np.allclose(npB @ npA, npA @ npB, atol=TOL)
    v = np.array([1.0, 1.0])
    assert np.allclose(npB @ (npA @ v), (npB @ npA) @ v, atol=TOL)
    print("  B @ (A @ v) equals (B @ A) @ v, which is the whole justification")
    print("  for composing matrices at all.")

    print()
    print("04_composition_and_order.py: every assertion held.")


if __name__ == "__main__":
    main()
