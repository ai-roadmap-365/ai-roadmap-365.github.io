"""Matrix multiplication from first principles, written three different ways.

The three functions below compute exactly the same thing and are asserted equal
to each other and to NumPy's `@` in `01_matmul_from_scratch.py`. They exist
separately because each one makes a different fact obvious:

* `matmul_loops`   — three nested loops. The definition, transcribed. It makes
                     the COST obvious: the body runs m * n * p times.
* `matmul_dots`    — a list of dot products. It makes the DEFINITION obvious:
                     entry (i, j) is row i of A dotted with column j of B, and
                     nothing else.
* `matmul_columns` — column j of the answer is A applied to column j of B, and
                     A applied to a vector is a weighted sum of A's columns. It
                     makes the MEANING obvious, and it is the reading that
                     makes every later idea in linear algebra easy.

Nothing here imports NumPy. That is the point of a from-scratch build: you
should be able to read every line and see where each number came from.

Matrices are plain nested lists of numbers, rows outermost, exactly as they are
written on paper. Vectors are flat lists.
"""

from __future__ import annotations


class ShapeMismatch(ValueError):
    """Raised when two matrices cannot be multiplied.

    Subclasses ValueError deliberately, so that code which only knows to catch
    ValueError still catches this, while code that wants to be specific can be.
    NumPy raises its own ValueError for the same situation.
    """


def shape(M: list[list[float]]) -> tuple[int, int]:
    """Return (rows, columns), checking that the grid is rectangular."""
    if not M or not isinstance(M, list) or not isinstance(M[0], list):
        raise ValueError("a matrix is a non-empty list of rows, each a list")
    n_cols = len(M[0])
    for i, row in enumerate(M):
        if len(row) != n_cols:
            raise ValueError(
                f"row {i} has {len(row)} entries but row 0 has {n_cols}; "
                "a matrix is rectangular"
            )
    return (len(M), n_cols)


def check_multipliable(A: list[list[float]], B: list[list[float]]) -> tuple[int, int, int]:
    """Check the shape rule and return (m, n, p) for an (m, n) @ (n, p).

    The rule is not a convention to memorise. A @ B means "do B, then do A".
    B has shape (n, p), so it turns a vector of length p into one of length n.
    A has shape (m, n), so it accepts a vector of length n and returns one of
    length m. A's column count is the length of what it ACCEPTS; B's row count
    is the length of what it PRODUCES. The inner dimensions must match because
    the second thing has to accept what the first one hands it. The outer
    dimensions survive because they are the two ends of the pipeline: what goes
    in at one end, and what comes out at the other.
    """
    m, n = shape(A)
    n2, p = shape(B)
    if n != n2:
        raise ShapeMismatch(
            f"cannot multiply ({m}, {n}) by ({n2}, {p}): "
            f"the inner dimensions {n} and {n2} disagree. "
            f"In A @ B the right-hand matrix runs first and returns vectors of "
            f"length {n2}, and the left-hand matrix only accepts vectors of "
            f"length {n}."
        )
    return m, n, p


def dot(u: list[float], v: list[float]) -> float:
    """Multiply pairwise, then add. The whole of the dot product."""
    if len(u) != len(v):
        raise ShapeMismatch(
            f"cannot dot a vector of length {len(u)} with one of length {len(v)}; "
            "there is no sensible partner for the leftover entries"
        )
    total = 0
    for a, b in zip(u, v):
        total += a * b
    return total


def matmul_loops(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Version 1: three nested loops. The definition with nothing hidden.

    Count the work: the innermost line runs once for every (i, k, j), which is
    m * n * p times. For two 200 by 200 matrices that is eight million
    multiply-and-adds, and Python will do every one of them as an interpreted
    step. That number is the reason the timing script exists.
    """
    m, n, p = check_multipliable(A, B)
    C = [[0] * p for _ in range(m)]
    for i in range(m):  # each row of the answer
        for j in range(p):  # each column of the answer
            total = 0
            for k in range(n):  # walk A's row and B's column together
                total += A[i][k] * B[k][j]
            C[i][j] = total
    return C


def matmul_dots(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Version 2: entry (i, j) is row i of A dotted with column j of B."""
    check_multipliable(A, B)
    B_columns = transpose(B)  # so a column is a list we can hand to dot()
    return [[dot(row, column) for column in B_columns] for row in A]


def matvec(A: list[list[float]], v: list[float]) -> list[float]:
    """A applied to one vector, computed as a weighted sum of A's COLUMNS.

    This is the picture worth keeping. A @ v does not really "dot v with the
    rows". It takes v[0] copies of A's first column, v[1] copies of the second,
    and so on, and adds them up. The answer is therefore always a combination
    of A's columns and can never leave the space they span — which is why the
    output has as many entries as A has rows, and why the length of v must
    equal the number of columns: one weight per column, no spares.
    """
    m, n = shape(A)
    if len(v) != n:
        raise ShapeMismatch(
            f"cannot apply an ({m}, {n}) matrix to a vector of length {len(v)}: "
            f"there is one weight per column and the matrix has {n} columns"
        )
    out = [0] * m
    for j in range(n):  # for each column of A
        weight = v[j]
        for i in range(m):  # add that many copies of it into the running total
            out[i] += weight * A[i][j]
    return out


def matmul_columns(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Version 3: column j of the answer is A applied to column j of B.

    Matrix-matrix multiplication is matrix-vector multiplication done once per
    column, and nothing more. Once you believe `matvec`, this needs no separate
    justification — which is the reason to write it this way.
    """
    check_multipliable(A, B)
    columns = [matvec(A, column) for column in transpose(B)]
    return transpose(columns)


def transpose(M: list[list[float]]) -> list[list[float]]:
    """Swap rows and columns: an (r, c) matrix becomes (c, r). From Day 100."""
    rows, cols = shape(M)
    return [[M[i][j] for i in range(rows)] for j in range(cols)]


def identity(n: int) -> list[list[float]]:
    """The n by n matrix that does nothing: 1 on the diagonal, 0 elsewhere.

    "Does nothing" is the definition worth carrying, not the picture. Applied
    to a vector it returns that same vector, because the weighted sum of its
    columns picks out exactly one column per coordinate.
    """
    if n < 1:
        raise ValueError("the identity matrix needs at least one row")
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def add_bias(M: list[list[float]], bias: list[float]) -> list[list[float]]:
    """Add one bias vector to EVERY row. NumPy would do this by broadcasting.

    Written out, so that the two-character version in the NumPy script is
    visibly shorthand for a loop rather than magic.
    """
    rows, cols = shape(M)
    if len(bias) != cols:
        raise ShapeMismatch(
            f"the bias has {len(bias)} entries but each row has {cols}; "
            "there must be one bias per output column"
        )
    return [[M[i][j] + bias[j] for j in range(cols)] for i in range(rows)]


def multiplication_count(m: int, n: int, p: int) -> int:
    """How many multiplications an (m, n) @ (n, p) costs: one per (i, k, j)."""
    return m * n * p


def chain_costs(m: int, n: int, p: int, q: int) -> tuple[int, int]:
    """Cost of ((A B) C) against (A (B C)) for (m,n) @ (n,p) @ (p,q).

    Both associations give the identical answer — that is associativity, and it
    is a theorem, not a coincidence. They do not give the identical amount of
    work, and on realistic shapes the gap is not a rounding difference.
    """
    left_first = multiplication_count(m, n, p) + multiplication_count(m, p, q)
    right_first = multiplication_count(n, p, q) + multiplication_count(m, n, q)
    return left_first, right_first
