"""Making arrays without a loop, and operating on them without a loop.

Run from inside examples/:

    ../.venv/bin/python3 04_creating_and_ufuncs.py

The claim under test: you almost never need to build an array by appending to a
list and converting. There is a constructor for the shape you want, and once
you have it, every mathematical function you want already applies to the whole
thing at once.
"""

import math

import numpy as np

import dataset


def main() -> None:
    print("04_creating_and_ufuncs.py")
    print("=" * 70)

    # -- 1. The eight constructors worth knowing by heart ---------------------
    print()
    print("1. Eight ways to make an array, and when each is the right one")
    print("-" * 70)

    from_list = np.array([1.5, 2.5, 3.5])
    zeros = np.zeros(4)
    ones = np.ones((2, 3))
    full = np.full(3, 7)
    arange = np.arange(0, 10, 2)
    linspace = np.linspace(0.0, 1.0, 5)
    eye = np.eye(3)
    rng = np.random.default_rng(dataset.SEED)
    randoms = rng.random(3)

    rows = [
        ("np.array([1.5, 2.5, 3.5])", from_list, "data you already have"),
        ("np.zeros(4)", zeros, "an accumulator to fill in"),
        ("np.ones((2, 3))", ones, "a 2 by 3 block of ones"),
        ("np.full(3, 7)", full, "any constant, dtype taken from it"),
        ("np.arange(0, 10, 2)", arange, "a COUNT: start, stop, step"),
        ("np.linspace(0, 1, 5)", linspace, "a RANGE: start, stop, how many"),
        ("np.eye(3)", eye, "the identity matrix, from Day 102"),
        ("rng.random(3)", randoms, "reproducible pseudo-random values"),
    ]
    for call, value, why in rows:
        flat = np.array2string(value.ravel(), precision=6, separator=", ")
        print(f"  {call:<26} {str(value.dtype):<8} shape {str(value.shape):<7} {flat}")
        print(f"  {'':<26} {why}")
    print()
    print("  The two that get confused: arange counts in steps and EXCLUDES")
    print("  the stop, exactly like Python's range. linspace takes how many")
    print("  points you want and INCLUDES both ends. Ask for a step, use")
    print("  arange; ask for a count, use linspace.")

    assert from_list.dtype == np.float64
    assert zeros.tolist() == [0.0, 0.0, 0.0, 0.0]
    assert ones.shape == (2, 3)
    assert full.tolist() == [7, 7, 7] and full.dtype == np.int64
    assert arange.tolist() == [0, 2, 4, 6, 8]
    assert linspace.tolist() == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert eye.tolist() == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    # -- 2. Seeded randomness -------------------------------------------------
    print()
    print("2. Random, and reproducible, which are not opposites")
    print("-" * 70)
    again = np.random.default_rng(dataset.SEED).random(3)
    print(f"  default_rng({dataset.SEED}).random(3)   {randoms}")
    print(f"  and a second generator, same seed  {again}")
    print(f"  identical: {bool(np.array_equal(randoms, again))}")
    print()
    print("  numpy.random.default_rng is the modern interface. The older")
    print("  numpy.random.seed sets ONE global generator that every library")
    print("  in the process shares, so a call you did not write can move your")
    print("  sequence. A generator object you pass around cannot be moved by")
    print("  anyone else, which is why every number in this lab is stable.")
    assert bool(np.array_equal(randoms, again))

    # -- 3. Universal functions -----------------------------------------------
    print()
    print("3. A ufunc: one call, every element")
    print("-" * 70)
    a = np.array([0.0, 1.0, 4.0, 9.0, 16.0])
    print(f"  a          = {a}")
    print(f"  np.sqrt(a) = {np.sqrt(a)}")
    print(f"  the comprehension [math.sqrt(x) for x in a] gives the same:")
    print(f"               {np.array([math.sqrt(x) for x in a])}")
    print(f"  identical: {bool(np.array_equal(np.sqrt(a), [math.sqrt(x) for x in a]))}")
    assert bool(np.array_equal(np.sqrt(a), [math.sqrt(x) for x in a]))
    print()
    print("  math.sqrt cannot take an array at all -- it wants one number.")
    try:
        math.sqrt(a)
    except TypeError as exc:
        print(f"  math.sqrt(a) raises TypeError: {exc}")
    else:  # pragma: no cover - documents an outcome that would falsify the claim
        raise AssertionError("math.sqrt accepted an array, which it should not")

    # -- 4. The ufuncs you will use --------------------------------------------
    print()
    print("4. The ones that come up daily")
    print("-" * 70)
    small = np.array([-2.0, -0.5, 0.0, 0.5, 2.0])
    for name, result in (
        ("np.abs", np.abs(small)),
        ("np.sqrt(np.abs(x))", np.sqrt(np.abs(small))),
        ("np.exp", np.exp(small)),
        ("np.sign", np.sign(small)),
        ("np.round(x, 2)", np.round(small, 2)),
        ("x ** 2", small ** 2),
        ("np.maximum(x, 0)", np.maximum(small, 0.0)),
    ):
        print(f"  {name:<20} {np.array2string(result, precision=6, separator=', ')}")
    print()
    print("  np.maximum(x, 0) is the ReLU from Day 102, written as a ufunc.")
    print("  It takes TWO arrays and compares them elementwise. np.max takes")
    print("  ONE array and reduces it to a single number. Confusing the two is")
    print("  a rite of passage; the longer name is the elementwise one.")
    assert np.maximum(small, 0.0).tolist() == [0.0, 0.0, 0.0, 0.5, 2.0]
    assert float(np.max(small)) == 2.0
    assert np.abs(small).tolist() == [2.0, 0.5, 0.0, 0.5, 2.0]

    # -- 5. Two arrays at once, elementwise -----------------------------------
    print()
    print("5. Two arrays, elementwise, no loop")
    print("-" * 70)
    left = np.array([1.0, 2.0, 3.0])
    right = np.array([10.0, 20.0, 30.0])
    print(f"  left  = {left}")
    print(f"  right = {right}")
    print(f"  left + right  = {left + right}")
    print(f"  left * right  = {left * right}   <- elementwise, NOT a dot product")
    print(f"  left @ right  = {left @ right}   <- the dot product, from Day 103")
    assert (left * right).tolist() == [10.0, 40.0, 90.0]
    assert float(left @ right) == 140.0
    print()
    print("  `*` is elementwise and `@` is the matrix product. In a language")
    print("  that gives you one symbol for multiplication, this is the single")
    print("  most common source of a silently wrong shape.")

    # -- 6. Shapes must agree, or broadcast -----------------------------------
    print()
    print("6. When the shapes do not match")
    print("-" * 70)
    try:
        np.array([1.0, 2.0, 3.0]) + np.array([1.0, 2.0])
    except ValueError as exc:
        print(f"  (3,) + (2,) raises ValueError: {exc}")
    else:  # pragma: no cover - documents an outcome that would falsify the claim
        raise AssertionError("mismatched shapes must raise")
    print()
    print(f"  but (3,) + a single number works: {left + 100.0}")
    print("  The scalar was BROADCAST: stretched, conceptually, to match. No")
    print("  copy of 100.0 was ever made. Broadcasting is the next section's")
    print("  subject and the reason `2.5 * a + 1.25` in script 03 was legal.")
    assert (left + 100.0).tolist() == [101.0, 102.0, 103.0]

    print()
    print("=" * 70)
    print("04_creating_and_ufuncs.py: every assertion held.")


if __name__ == "__main__":
    main()
