"""Exercise 1 — matrix multiplication from first principles. Your work.

Seven functions to write, each marked EXERCISE. Everything else is written for
you, including `shape`, `transpose` and the `ShapeMismatch` exception, so that
you spend your time on the operation itself rather than on plumbing.

Check yourself from the LAB DIRECTORY at any point:

    .venv/bin/pytest starter -q

A function you have not written raises NotImplementedError, and its tests SKIP
rather than fail. A skip means "not attempted". A failure means "attempted and
wrong", and it prints both your answer and the real one.

Do not import numpy in this file. The whole point of exercise 1 is that you can
read every line and see where each number came from.
"""

from __future__ import annotations


class ShapeMismatch(ValueError):
    """Raised when two matrices cannot be multiplied. Written for you.

    It subclasses ValueError on purpose, so that code which only knows to catch
    ValueError still catches this. NumPy raises a plain ValueError for the same
    situation.
    """


def shape(M: list[list[float]]) -> tuple[int, int]:
    """Return (rows, columns), checking the grid is rectangular. Written for you."""
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


def transpose(M: list[list[float]]) -> list[list[float]]:
    """Swap rows and columns. Written for you; you built this on Day 100."""
    rows, cols = shape(M)
    return [[M[i][j] for i in range(rows)] for j in range(cols)]


# ---------------------------------------------------------------------------
# EXERCISE 1.1 — the dot product
# ---------------------------------------------------------------------------


def dot(u: list[float], v: list[float]) -> float:
    """Multiply the two vectors pairwise, then add up the products.

    EXERCISE 1.1

        dot([3, 4], [4, 3])  ->  3*4 + 4*3  ->  24
        dot([3, 4], [3, 4])  ->  3*3 + 4*4  ->  25   (the squared length)
        dot([3, 4], [-4, 3]) ->  -12 + 12   ->  0    (perpendicular)

    Raise ShapeMismatch if the two lengths differ — there is no sensible
    partner for the leftover entries, and returning something anyway would be
    worse than stopping.

    Hint: `zip(u, v)` walks both lists together.
    """
    raise NotImplementedError("exercise 1.1: dot")


# ---------------------------------------------------------------------------
# EXERCISE 1.2 — the shape rule
# ---------------------------------------------------------------------------


def check_multipliable(A: list[list[float]], B: list[list[float]]) -> tuple[int, int, int]:
    """Check that A @ B is legal and return (m, n, p) for an (m, n) @ (n, p).

    EXERCISE 1.2

    Use `shape` on each. If A is (m, n) and B is (n2, p), then n and n2 must be
    equal; raise ShapeMismatch if they are not, and put BOTH shapes and both
    inner dimensions in the message. An error message that does not tell you
    the two numbers that disagreed has wasted the exception.

    The test looks for the substrings "(2, 3)" and "inner dimensions 3 and 2"
    when called with two (2, 3) matrices, so include those exact phrasings.

    Return (m, n, p) when it is legal.
    """
    raise NotImplementedError("exercise 1.2: check_multipliable")


# ---------------------------------------------------------------------------
# EXERCISE 1.3 — three nested loops
# ---------------------------------------------------------------------------


def matmul_loops(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Multiply two matrices with three nested loops. The definition, verbatim.

    EXERCISE 1.3

    Call `check_multipliable` first, then build an m by p grid of zeros and
    fill it. Entry (i, j) is the sum over k of A[i][k] * B[k][j].

        C = [[0] * p for _ in range(m)]

    Write that line exactly. `[[0] * p] * m` looks equivalent and is a bug: it
    makes m references to ONE row, so writing to C[0][0] changes every row at
    once. That is the Day 100 view-versus-copy lesson turning up in plain
    Python, and it catches people every year.

    Count as you write: the innermost line runs m*n*p times. That number is why
    exercise 6 exists.
    """
    raise NotImplementedError("exercise 1.3: matmul_loops")


# ---------------------------------------------------------------------------
# EXERCISE 1.4 — a matrix applied to a vector, as a sum of COLUMNS
# ---------------------------------------------------------------------------


def matvec(A: list[list[float]], v: list[float]) -> list[float]:
    """Apply A to v as a weighted sum of A's columns.

    EXERCISE 1.4

    You could write this as "dot v with each row", and you would get the right
    numbers. Write it the other way instead, because the other way is the
    picture that makes everything later obvious:

        take v[0] copies of A's first column,
        plus v[1] copies of A's second column,
        plus ... and add them all up.

    So: start with a list of m zeros, loop over the columns j, and add
    v[j] * A[i][j] into out[i] for every row i.

    Raise ShapeMismatch if len(v) is not the number of COLUMNS of A. There is
    one weight per column and no spares.

    When you have it, try `matvec(A, [1, 0])` and see which column comes back.
    That is not a trick; it is the reason the columns of a transformation
    matrix are where the basis vectors land.
    """
    raise NotImplementedError("exercise 1.4: matvec")


# ---------------------------------------------------------------------------
# EXERCISE 1.5 — the same product, as a list of dot products
# ---------------------------------------------------------------------------


def matmul_dots(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Entry (i, j) is row i of A dotted with column j of B. Nothing else.

    EXERCISE 1.5

    Call `check_multipliable`, get B's columns with `transpose(B)`, then build
    the answer with your own `dot`. This can be a single comprehension, and it
    should produce exactly the same numbers as `matmul_loops` on every input —
    the tests check that on six different shapes.
    """
    raise NotImplementedError("exercise 1.5: matmul_dots")


# ---------------------------------------------------------------------------
# EXERCISE 1.6 — the identity matrix, and adding a bias
# ---------------------------------------------------------------------------


def identity(n: int) -> list[list[float]]:
    """The n by n matrix with 1 on the main diagonal and 0 everywhere else.

    EXERCISE 1.6

    Raise ValueError for n < 1. Then check the property that actually defines
    it: multiplying by it changes nothing. The tests check both sides, and note
    that X being (2, 3) means the identity that fits on its left is 2 by 2 and
    the one that fits on its right is 3 by 3.
    """
    raise NotImplementedError("exercise 1.6: identity")


def add_bias(M: list[list[float]], bias: list[float]) -> list[list[float]]:
    """Add one bias vector to EVERY row of M.

    EXERCISE 1.7

    NumPy does this with `M + b` and calls it broadcasting. Write it out as a
    loop once, so that the two-character version is visibly shorthand rather
    than magic.

    Raise ShapeMismatch if len(bias) is not the number of COLUMNS of M: there
    is one bias per output, not one per example.
    """
    raise NotImplementedError("exercise 1.7: add_bias")


# ---------------------------------------------------------------------------
# EXERCISE 1.8 — counting the work
# ---------------------------------------------------------------------------


def multiplication_count(m: int, n: int, p: int) -> int:
    """How many multiplications does an (m, n) @ (n, p) cost?

    EXERCISE 1.8

    Look at your own `matmul_loops` and count how many times the innermost
    line runs. One expression, no loops needed.
    """
    raise NotImplementedError("exercise 1.8: multiplication_count")


def chain_costs(m: int, n: int, p: int, q: int) -> tuple[int, int]:
    """Cost of ((A B) C) against (A (B C)) for (m,n) @ (n,p) @ (p,q).

    EXERCISE 1.9

    Return the two totals as a tuple, left-first then right-first.

        (A B) C : the (m, n) @ (n, p) costs one lot, and multiplying that
                  (m, p) result by C costs another.
        A (B C) : the (n, p) @ (p, q) costs one lot, and multiplying A by
                  that (n, q) result costs another.

    Both give the identical answer. They do not cost the identical amount, and
    on the shapes in exercise 6 the gap is not a rounding difference.
    """
    raise NotImplementedError("exercise 1.9: chain_costs")
