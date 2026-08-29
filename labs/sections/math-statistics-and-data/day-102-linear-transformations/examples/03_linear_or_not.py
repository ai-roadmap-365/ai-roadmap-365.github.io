"""What makes a transformation linear -- tested on one that is, and one that is not.

Run from inside examples/:

    ../.venv/bin/python3 03_linear_or_not.py

Linear means exactly two things, and nothing else:

    1. it preserves addition:  T(u + v) = T(u) + T(v)
    2. it preserves scaling:   T(s * u) = s * T(u)

Both must hold, for every u, v and s. This script checks both on a matrix,
where they hold, and on "multiply by a matrix and then add a constant", where
they do not -- and measures exactly how much they miss by, because the size of
the gap turns out to be the whole explanation.
"""

import numpy as np

import shapes
from transforms import apply, is_linear, preserves_addition, preserves_scaling

TOL = shapes.TOL

U = (1.0, 2.0)
V = (3.0, -1.0)
S = 5.0
OFFSET = (1.0, 1.0)


def main() -> None:
    print("03_linear_or_not.py")
    print("=" * 70)

    M = shapes.SCALE_MATRIX

    def linear(p):
        """v -> M @ v. Nothing else."""
        return apply(M, p)

    def affine(p):
        """v -> M @ v + b. One addition more, and no longer linear."""
        x, y = apply(M, p)
        return (x + OFFSET[0], y + OFFSET[1])

    print()
    print(f"  M = [{M[0]}, {M[1]}]   (scale by 2 across, 3 up)")
    print(f"  b = {OFFSET}")
    print(f"  u = {U}   v = {V}   s = {S}")

    # -- 1. The matrix passes both halves -------------------------------------
    print()
    print("1. T(v) = M @ v  --  preserves addition")
    print("-" * 70)
    ok, together, separately = preserves_addition(linear, U, V, TOL)
    print(f"  u + v          = {(U[0] + V[0], U[1] + V[1])}")
    print(f"  T(u + v)       = {together}")
    print(f"  T(u)           = {linear(U)}")
    print(f"  T(v)           = {linear(V)}")
    print(f"  T(u) + T(v)    = {separately}")
    print(f"  equal within {TOL!r}: {ok}")
    assert ok

    print()
    print("2. T(v) = M @ v  --  preserves scaling")
    print("-" * 70)
    ok, scaled_first, scaled_after = preserves_scaling(linear, U, S, TOL)
    print(f"  s * u          = {(S * U[0], S * U[1])}")
    print(f"  T(s * u)       = {scaled_first}")
    print(f"  s * T(u)       = {scaled_after}")
    print(f"  equal within {TOL!r}: {ok}")
    assert ok
    assert is_linear(linear, U, V, S, TOL)

    # -- 3. Adding a constant breaks it ---------------------------------------
    print()
    print("3. f(v) = M @ v + b  --  fails to preserve addition")
    print("-" * 70)
    ok_add, together, separately = preserves_addition(affine, U, V, TOL)
    print(f"  f(u + v)       = {together}")
    print(f"  f(u)           = {affine(U)}")
    print(f"  f(v)           = {affine(V)}")
    print(f"  f(u) + f(v)    = {separately}")
    gap_add = (separately[0] - together[0], separately[1] - together[1])
    print(f"  equal within {TOL!r}: {ok_add}")
    print(f"  the gap        = {gap_add}")
    print()
    print("  Look at the gap. It is exactly b. Adding the offset once on the")
    print("  left and twice on the right is the entire failure -- b sneaks in")
    print("  once per term, and adding two terms adds it twice.")
    assert not ok_add
    assert abs(gap_add[0] - OFFSET[0]) <= TOL
    assert abs(gap_add[1] - OFFSET[1]) <= TOL

    print()
    print("4. f(v) = M @ v + b  --  fails to preserve scaling too")
    print("-" * 70)
    ok_scale, scaled_first, scaled_after = preserves_scaling(affine, U, S, TOL)
    print(f"  f(s * u)       = {scaled_first}")
    print(f"  s * f(u)       = {scaled_after}")
    gap_scale = (scaled_after[0] - scaled_first[0], scaled_after[1] - scaled_first[1])
    print(f"  equal within {TOL!r}: {ok_scale}")
    print(f"  the gap        = {gap_scale}")
    print(f"  and (s - 1) * b = {((S - 1) * OFFSET[0], (S - 1) * OFFSET[1])}")
    print()
    print("  Same story: b is added once before the multiply and s times after.")
    assert not ok_scale
    assert abs(gap_scale[0] - (S - 1) * OFFSET[0]) <= TOL
    assert abs(gap_scale[1] - (S - 1) * OFFSET[1]) <= TOL
    assert not is_linear(affine, U, V, S, TOL)

    # -- 5. The one-second version of the same test ---------------------------
    print()
    print("5. The quick check: what happens to the origin?")
    print("-" * 70)
    print(f"  T((0, 0)) = {linear((0.0, 0.0))}     linear: the origin is fixed")
    print(f"  f((0, 0)) = {affine((0.0, 0.0))}     not linear: the origin moved")
    print()
    print("  Every linear transformation sends the origin to the origin, because")
    print("  M @ (0, 0) is a sum of zero lots of each column. So if a function")
    print("  moves the origin it cannot be linear, and you knew that before")
    print("  testing a single pair of vectors.")
    assert linear((0.0, 0.0)) == (0.0, 0.0)
    assert affine((0.0, 0.0)) == OFFSET

    # -- 6. Why a network keeps the bias separate -----------------------------
    print()
    print("6. Which is why a network layer is written X @ W + b")
    print("-" * 70)
    print("  The layer is deliberately NOT one operation. X @ W is the linear")
    print("  part -- it has a matrix, it has columns, it has a determinant, and")
    print("  everything in this lab applies to it. The + b is bolted on")
    print("  afterwards precisely because it cannot be folded into the matrix:")
    print("  a matrix cannot move the origin, and b exists to move the origin.")
    print("  Together they are called an AFFINE transformation: linear, plus a")
    print("  shift. Neither word is decoration.")

    # -- 7. NumPy, saying the same thing --------------------------------------
    print()
    print("7. The same four checks in NumPy")
    print("-" * 70)
    npM = np.array(M)
    npb = np.array(OFFSET)
    npu, npv = np.array(U), np.array(V)
    print(f"  M @ (u + v)             = {(npM @ (npu + npv)).tolist()}")
    print(f"  M @ u + M @ v           = {(npM @ npu + npM @ npv).tolist()}")
    print(f"  (M @ (u + v) + b)       = {(npM @ (npu + npv) + npb).tolist()}")
    print(f"  (M @ u + b) + (M @ v + b) = {(npM @ npu + npb + npM @ npv + npb).tolist()}")
    assert np.allclose(npM @ (npu + npv), npM @ npu + npM @ npv, atol=TOL)
    assert not np.allclose(
        npM @ (npu + npv) + npb, npM @ npu + npb + npM @ npv + npb, atol=TOL
    )

    print()
    print("03_linear_or_not.py: every assertion held.")


if __name__ == "__main__":
    main()
