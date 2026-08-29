"""Three from-scratch implementations and NumPy's @, asserted equal.

Run from inside this directory:

    ../.venv/bin/python3 01_matmul_from_scratch.py

Every claim printed below is also asserted. If an assertion fails the script
stops with a traceback instead of printing a reassuring final line.
"""

import numpy as np

from dataset import HIGHLIGHT_COLUMN, HIGHLIGHT_ROW, HIGHLIGHT_TERMS, HIGHLIGHT_VALUE, W, X, XW
from matmul import (
    ShapeMismatch,
    dot,
    identity,
    matmul_columns,
    matmul_dots,
    matmul_loops,
    matvec,
    multiplication_count,
    shape,
    transpose,
)


def show(M):
    return "[" + ", ".join("[" + ", ".join(f"{v:g}" for v in row) + "]" for row in M) + "]"


print("=" * 74)
print("1. The dot product: multiply pairwise, then add")
print("=" * 74)

u = [3, 4]
v = [4, 3]
w = [-4, 3]

print(f"  u = {u}, v = {v}, w = {w}")
print(f"  u . v = 3*4 + 4*3 = 12 + 12 = {dot(u, v)}")
print(f"  u . u = 3*3 + 4*4 =  9 + 16 = {dot(u, u)}   <- the length of u, squared")
print(f"  u . w = 3*-4 + 4*3 = -12 + 12 = {dot(u, w)}   <- zero means perpendicular")
assert dot(u, v) == 24
assert dot(u, u) == 25
assert dot(u, w) == 0
assert dot(u, u) == round(float(np.linalg.norm(u)) ** 2)
print("  A vector dotted with itself is its squared length, every time.")
print(f"  NumPy agrees: np.dot(u, v) = {np.dot(u, v)}, u @ v = {np.array(u) @ np.array(v)}")

print()
print("=" * 74)
print("2. Matrix times vector, as a weighted sum of the matrix's COLUMNS")
print("=" * 74)

A = [[2, 0], [-1, 1], [0, 4]]  # shape (3, 2)
c = [3, 5]

print(f"  A = {show(A)}, shape {shape(A)}")
print(f"  c = {c}")
print("  A @ c takes 3 copies of A's first column plus 5 copies of its second:")
print("      3 * [2, -1, 0]  =  [6, -3, 0]")
print("      5 * [0,  1, 4]  =  [0,  5, 20]")
print("      sum             =  [6,  2, 20]")
result = matvec(A, c)
print(f"  matvec(A, c) = {result}")
assert result == [6, 2, 20]
assert result == (np.array(A) @ np.array(c)).tolist()
print("  NumPy returns the same three numbers.")
print("  Note what this guarantees: the answer is ALWAYS a combination of A's")
print("  columns, so it can never land anywhere those columns cannot reach.")

print()
print("=" * 74)
print("3. Matrix times matrix: the same thing, once per column")
print("=" * 74)

print(f"  X = {show(X)}   shape {shape(X)}")
print(f"  W = {show(W)}   shape {shape(W)}")
print()
print("  The highlighted cell, entry (1, 1) of X @ W, in full:")
print(f"      row 1 of X    = {HIGHLIGHT_ROW}")
print(f"      column 1 of W = {HIGHLIGHT_COLUMN}")
print(
    f"      0*0 + 1*1 + 3*4 = {HIGHLIGHT_TERMS[0]} + {HIGHLIGHT_TERMS[1]}"
    f" + {HIGHLIGHT_TERMS[2]} = {HIGHLIGHT_VALUE}"
)
assert sum(HIGHLIGHT_TERMS) == HIGHLIGHT_VALUE

by_loops = matmul_loops(X, W)
by_dots = matmul_dots(X, W)
by_columns = matmul_columns(X, W)
by_numpy = (np.array(X) @ np.array(W)).tolist()

print()
print(f"  three nested loops   {show(by_loops)}")
print(f"  list of dot products {show(by_dots)}")
print(f"  A applied per column {show(by_columns)}")
print(f"  NumPy's @            {show(by_numpy)}")
print(f"  worked out by hand   {show(XW)}")
assert by_loops == by_dots == by_columns == by_numpy == XW
assert by_loops[1][1] == HIGHLIGHT_VALUE
print("  All five agree, including the one a human derived with a pen.")

print()
print("  And the cost, counted rather than guessed:")
m, n = shape(X)
_, p = shape(W)
print(f"      ({m}, {n}) @ ({n}, {p}) costs m*n*p = {m}*{n}*{p} = {multiplication_count(m, n, p)}")
print("      multiplications, one per (row, column, inner step).")
assert multiplication_count(m, n, p) == 12

print()
print("=" * 74)
print("4. Several shapes, all four implementations, all equal")
print("=" * 74)

rng = np.random.default_rng(101)  # seeded, so this script is reproducible
for m, n, p in [(1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 4), (5, 1, 3), (1, 6, 2)]:
    L = rng.integers(-9, 10, size=(m, n)).tolist()
    R = rng.integers(-9, 10, size=(n, p)).tolist()
    expected = (np.array(L) @ np.array(R)).tolist()
    got_loops = matmul_loops(L, R)
    got_dots = matmul_dots(L, R)
    got_cols = matmul_columns(L, R)
    assert got_loops == expected, (m, n, p)
    assert got_dots == expected, (m, n, p)
    assert got_cols == expected, (m, n, p)
    count = multiplication_count(m, n, p)
    print(
        f"  ({m}, {n}) @ ({n}, {p}) -> ({m}, {p})   "
        f"loops = dots = columns = NumPy   "
        f"({count} multiplication{'' if count == 1 else 's'})"
    )

print()
print("=" * 74)
print("5. The identity matrix: the transformation that does nothing")
print("=" * 74)

I3 = identity(3)
I2 = identity(2)
print(f"  identity(3) = {show(I3)}")
print(f"  I2 @ X      = {show(matmul_loops(I2, X))}    (X unchanged)")
print(f"  X  @ I3     = {show(matmul_loops(X, I3))}    (X unchanged)")
assert matmul_loops(I2, X) == X
assert matmul_loops(X, I3) == X
assert I3 == np.eye(3, dtype=int).tolist()
print("  Note the two different sizes. X is (2, 3), so the identity that fits")
print("  on the left is 2 by 2 and the one that fits on the right is 3 by 3.")
print("  'The' identity matrix is really one per size.")

print()
print("=" * 74)
print("6. The shape rule, and what happens when it is broken")
print("=" * 74)

try:
    matmul_loops(X, X)
except ShapeMismatch as exc:
    print("  matmul_loops(X, X) raises ShapeMismatch:")
    print(f"    {exc}")
else:  # pragma: no cover - only reached if the guard is broken
    raise AssertionError("(2, 3) @ (2, 3) should not have been allowed")

try:
    np.array(X) @ np.array(X)
except ValueError as exc:
    print("  NumPy raises ValueError for the same thing:")
    print(f"    {type(exc).__name__}: {str(exc).splitlines()[0]}")
else:  # pragma: no cover
    raise AssertionError("NumPy should have refused (2, 3) @ (2, 3)")

fixed = matmul_loops(X, transpose(X))
print(f"  X @ X.T is (2, 3) @ (3, 2) -> {shape(fixed)}: {show(fixed)}")
assert shape(fixed) == (2, 2)
assert fixed == (np.array(X) @ np.array(X).T).tolist()

print()
print("01_matmul_from_scratch.py: every assertion held.")
