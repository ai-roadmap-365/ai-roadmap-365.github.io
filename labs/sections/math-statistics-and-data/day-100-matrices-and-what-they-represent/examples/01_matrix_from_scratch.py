"""Exercise 1 — the from-scratch matrix, and the same thing in NumPy.

Run from the lab directory:

    .venv/bin/python3 examples/01_matrix_from_scratch.py

Every claim printed here is asserted immediately after it is printed, so the
script exits non-zero the moment a number stops being true.
"""

import numpy as np

from matrix import Matrix, ShapeMismatch

TOL = 1e-12  # every float comparison below uses numpy.allclose with this


def rule(title):
    print()
    print(title)
    print("-" * len(title))


A = Matrix([[2, 4, 1, 3], [0, 5, 2, 7], [6, 1, 4, 2]])
B = Matrix([[1, 0, 0, 1], [2, 2, 2, 2], [0, 3, 0, 3]])

npA = np.array(A.to_lists())
npB = np.array(B.to_lists())

rule("1a. Shape is (rows, columns) — rows first")
print(f"  from scratch : {A.shape}")
print(f"  numpy        : {npA.shape}")
print(f"  numpy ndim   : {npA.ndim}   (a matrix is a 2-dimensional array)")
print(f"  numpy size   : {npA.size}   (rows x columns, the entry count)")
assert A.shape == npA.shape == (3, 4)
assert npA.ndim == 2
assert npA.size == 12

rule("1b. Indexing counts from zero in both")
print("  the matrix:")
print(A.format())
print(f"  A[0, 0] = {A[0, 0]}   (row 0, column 0 — the top-left entry)")
print(f"  A[2, 3] = {A[2, 3]}   (row 2, column 3 — the bottom-right entry)")
print(f"  npA[2, 3] = {npA[2, 3]}")
print("  written in a paper, the bottom-right entry of this matrix is a_34,")
print("  because mathematics counts rows and columns from 1. Same entry.")
assert A[0, 0] == npA[0, 0] == 2
assert A[2, 3] == npA[2, 3] == 2
assert A.row(1) == list(npA[1]) == [0, 5, 2, 7]
assert A.col(1) == list(npA[:, 1]) == [4, 5, 1]

out_of_range = None
try:
    A[3, 0]
except IndexError as exc:
    out_of_range = str(exc)
print(f"  A[3, 0] raises IndexError: {out_of_range}")
assert out_of_range is not None and "shape (3, 4)" in out_of_range

rule("1c. Transpose swaps the axes")
print("  A.T:")
print(A.T.format())
print(f"  shape {A.shape} becomes {A.T.shape}")
assert A.T.shape == (4, 3)
assert np.array_equal(np.array(A.T.to_lists()), npA.T)
assert A.T.T == A, "transposing twice returns the original"

rule("1d. Addition is elementwise, and demands identical shapes")
print((A + B).format())
assert np.array_equal(np.array((A + B).to_lists()), npA + npB)

mismatch = None
try:
    A.add(Matrix([[1, 2], [3, 4]]))
except ShapeMismatch as exc:
    mismatch = str(exc)
print(f"  adding a (2, 2) raises ShapeMismatch: {mismatch}")
assert mismatch is not None
assert issubclass(ShapeMismatch, ValueError), "so `except ValueError` catches both"

rule("1e. Scalar multiplication multiplies every entry")
print((A * 3).format())
assert np.array_equal(np.array((A * 3).to_lists()), npA * 3)
assert np.array_equal(np.array((3 * A).to_lists()), 3 * npA)

rule("1f. The matrices worth recognising on sight")
print("  zeros(2, 3) — the additive nothing:")
print(Matrix.zeros(2, 3).format())
print("  identity(3) — leaves every vector exactly as it found it:")
print(Matrix.identity(3).format())
print("  diagonal([2, 5, 1]) — scales each coordinate by its own factor:")
print(Matrix.diagonal([2, 5, 1]).format())
S = Matrix([[1, 7, 3], [7, 4, 0], [3, 0, 9]])
print("  a symmetric matrix — equal to its own transpose:")
print(S.format())
print(f"  S.is_symmetric() = {S.is_symmetric()}   A.is_symmetric() = {A.is_symmetric()}")
assert np.array_equal(np.array(Matrix.identity(3).to_lists()), np.eye(3, dtype=int))
assert np.array_equal(np.array(Matrix.diagonal([2, 5, 1]).to_lists()), np.diag([2, 5, 1]))
assert S.is_symmetric() is True
assert A.is_symmetric() is False, "A is not even square, so it cannot be symmetric"

v = [1.0, 2.0, 3.0]
print(f"  identity(3) applied to {v} gives {Matrix.identity(3).apply_to(v)}")
assert np.allclose(Matrix.identity(3).apply_to(v), v, atol=TOL)

rule("1g. The one thing the from-scratch class cannot do")
print("  NumPy adds a (4,) row to every row of a (3, 4) array without asking:")
print(f"  npA + np.array([100, 200, 300, 400]) =\n{npA + np.array([100, 200, 300, 400])}")
refused = None
try:
    A.add([100, 200, 300, 400])
except TypeError as exc:
    refused = str(exc)
print(f"  the from-scratch class refuses: TypeError: {refused}")
assert refused is not None and "broadcasting" in refused
print("  That refusal is honest, and it is also the gap. Exercise 3 is about")
print("  what filling it costs you.")

print()
print("01_matrix_from_scratch.py: every assertion held.")
