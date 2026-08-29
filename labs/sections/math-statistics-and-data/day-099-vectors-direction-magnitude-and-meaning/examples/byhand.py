"""Norms and distances whose answers are exact whole numbers.

Every line this prints can be re-derived with a pen. That is the point: before
you trust a library to measure a vector, measure four of them yourself and
confirm the library agrees.

The vectors are chosen so the square root comes out whole. (3, 4) is the 3-4-5
right triangle; (2, 3, 6) and (1, 2, 2) are the same trick in three dimensions,
where 4 + 9 + 36 = 49 and 1 + 4 + 4 = 9.

Run from the examples directory:

    python3 byhand.py
"""

from __future__ import annotations

import math

from vectors import distance, l1_norm, l2_norm, subtract

# (vector, the exact magnitude a human gets on paper)
EXACT_NORMS = [
    ([3, 4], 5),
    ([6, 8], 10),
    ([2, 3, 6], 7),
    ([1, 2, 2], 3),
    ([0, 0, 0], 0),
]

# (u, v, the exact distance between them)
EXACT_DISTANCES = [
    ([1, 2], [4, 6], 5),
    ([0, 0, 0], [2, 3, 6], 7),
    ([10, 10], [10, 10], 0),
    ([1, 1, 1], [2, 3, 3], 3),
]

TOLERANCE = "rel_tol=1e-9, abs_tol=1e-12"


def show_norm(v: list[int], expected: int) -> bool:
    squares = [a * a for a in v]
    total = sum(squares)
    got = l2_norm(v)
    agrees = math.isclose(got, expected, rel_tol=1e-9, abs_tol=1e-12)
    working = " + ".join(f"{a}^2" for a in v)
    numbers = " + ".join(str(s) for s in squares)
    print(f"  |{v}|")
    print(f"      = sqrt({working})")
    print(f"      = sqrt({numbers})")
    print(f"      = sqrt({total})")
    print(f"      = {expected}          computed: {got!r}   agrees: {agrees}")
    return agrees


def show_distance(u: list[int], v: list[int], expected: int) -> bool:
    diff = subtract(u, v)
    squares = [a * a for a in diff]
    total = sum(squares)
    got = distance(u, v)
    agrees = math.isclose(got, expected, rel_tol=1e-9, abs_tol=1e-12)
    numbers = " + ".join(str(s) for s in squares)
    print(f"  dist({u}, {v})")
    print(f"      = |{u} - {v}|")
    print(f"      = |{[int(x) for x in diff]}|")
    print(f"      = sqrt({numbers}) = sqrt({total})")
    print(f"      = {expected}          computed: {got!r}   agrees: {agrees}")
    return agrees


def main() -> int:
    print("Magnitudes you can check with a pen")
    print(f"(agreement is math.isclose with {TOLERANCE}, never ==)")
    print()
    ok = True
    for v, expected in EXACT_NORMS:
        ok = show_norm(v, expected) and ok
        print()

    print("Distances you can check with a pen")
    print("(distance is not a separate formula: subtract, then measure)")
    print()
    for u, v, expected in EXACT_DISTANCES:
        ok = show_distance(u, v, expected) and ok
        print()

    print("The two norms of the same vector are different numbers")
    print()
    for v in ([3, 4], [1, 2, 2], [4, 0, 0], [2, 2, 2]):
        print(
            f"  {str(v):<12} L1 = {l1_norm(v):<6.4f} "
            f"L2 = {l2_norm(v):.4f}"
        )
    print()
    print("all exact cases agree:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
