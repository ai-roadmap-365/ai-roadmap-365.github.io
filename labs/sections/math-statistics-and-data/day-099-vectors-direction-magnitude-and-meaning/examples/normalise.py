"""Normalisation, and the float comparison that will bite you.

Normalising a vector scales it to magnitude 1 while leaving its direction
alone. The arithmetic is simple. The trap is what you do next: if you write

    assert l2_norm(unit) == 1.0

you have written a test that passes for some vectors and fails for others, for
reasons that have nothing to do with your code being right. Day 46 covered why:
a float is a binary approximation, and dividing by a square root and then
squaring the results back up does not have to land on exactly 1.0.

This script normalises seven vectors and shows, for each one, the exact
repr of the resulting magnitude, whether `== 1.0` holds, and whether
`math.isclose` holds. Run it from the examples directory:

    python3 normalise.py
"""

from __future__ import annotations

import math

from vectors import l2_norm, normalise, scale

REL_TOL = 1e-9
ABS_TOL = 1e-12

CASES = [
    [3, 4],
    [1, 2, 2],
    [1, 1],
    [1, 1, 1],
    [0.1, 0.2, 0.3],
    [2, 3, 6],
    [7, 1, 5, 3, 9, 2],
]


def main() -> int:
    print("Normalising: v_hat = (1 / |v|) * v")
    print(f"tolerance in use: math.isclose(rel_tol={REL_TOL}, abs_tol={ABS_TOL})")
    print()
    header = f"{'vector':<26}{'|v|':<22}{'|v_hat| (exact repr)':<26}{'== 1.0':<9}isclose"
    print(header)
    print("-" * len(header))

    exact_equal = 0
    close_count = 0
    for v in CASES:
        unit = normalise(v)
        length = l2_norm(unit)
        equal = length == 1.0
        close = math.isclose(length, 1.0, rel_tol=REL_TOL, abs_tol=ABS_TOL)
        exact_equal += equal
        close_count += close
        print(
            f"{str(v):<26}{l2_norm(v)!r:<22}{length!r:<26}"
            f"{str(equal):<9}{close}"
        )

    print()
    print(f"exactly 1.0 : {exact_equal} of {len(CASES)}")
    print(f"isclose 1.0 : {close_count} of {len(CASES)}")
    print()
    print("This is the whole argument for never comparing floats with ==.")
    print("The maths is right in every row. Only the equality test disagrees.")
    print()

    print("Direction is preserved: v_hat scaled back up by |v| returns v")
    print()
    for v in ([3, 4], [1, 2, 2]):
        unit = normalise(v)
        back = scale(l2_norm(v), unit)
        agrees = all(
            math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)
            for a, b in zip(back, v)
        )
        print(f"  v      = {v}")
        print(f"  v_hat  = {[round(x, 6) for x in unit]}")
        print(f"  |v| * v_hat = {[round(x, 6) for x in back]}   recovers v: {agrees}")
        print()

    print("The zero vector cannot be normalised, and says so")
    try:
        normalise([0, 0, 0])
    except ValueError as exc:
        print(f"  normalise([0, 0, 0]) -> ValueError: {exc}")
    else:  # pragma: no cover - would be a bug in vectors.py
        print("  normalise([0, 0, 0]) returned without raising, which is a bug")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
