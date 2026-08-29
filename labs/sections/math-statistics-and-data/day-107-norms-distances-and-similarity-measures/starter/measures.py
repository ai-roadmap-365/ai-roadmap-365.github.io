"""Exercise 1 -- every measure in this lab, built from arithmetic alone.

Seventeen functions to write. Each has a docstring saying exactly what it must
do, a worked example you can check on paper, and a `raise NotImplementedError`
to delete when you write it.

Check yourself as you go, from the LAB DIRECTORY (the one above this file):

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED rather than failed. A skip means
"not attempted"; a failure means "attempted and wrong", and it prints your
answer beside the real one.

**Use only the standard library here.** `math`, `abs`, `sum`, `max`, `sorted`
and set operations are everything you need. NumPy is not forbidden by a lint
rule -- it is forbidden by the point of the exercise. The tests check your work
against `numpy.linalg.norm(v, ord=p)`, `numpy.cov` and `numpy.linalg.inv`, and
that check means nothing if your answer was NumPy's answer all along.

Two conventions, fixed and used everywhere:

1. A vector is a plain sequence of floats. Two vectors of different lengths may
   not be compared, and `_paired` below raises rather than zipping the shorter
   one and quietly answering a different question.

2. A DISTANCE gets smaller as things get more alike; a SIMILARITY gets larger.
   Every function name says which it is. Nothing in this module guesses.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Iterable, Sequence

Vector = Sequence[float]
Matrix = list[list[float]]

# Every float comparison in this lab is made against this tolerance. Written
# for you, and it is not decoration: the Mahalanobis result in exercise 1.16
# comes out as exactly 6.0 through one correct route and 5.999999999999999
# through another. `== 6.0` would pass for one and fail for the other.
TOL = 1e-12


class DimensionMismatch(ValueError):
    """Raised when two vectors of different lengths are compared.

    Written for you. Subclasses ValueError so that an existing
    `except ValueError` catches it, matching how NumPy reports the same
    mistake.
    """


def _paired(u: Vector, v: Vector) -> list[tuple[float, float]]:
    """Pair two vectors elementwise, refusing to compare different lengths.

    Written for you. Use it -- `zip` alone will silently truncate.
    """
    if len(u) != len(v):
        raise DimensionMismatch(
            f"vectors have different lengths: {len(u)} and {len(v)}"
        )
    return list(zip(u, v))


# -- Exercise 1.1 to 1.4: the norms -------------------------------------------


def l1_norm(v: Vector) -> float:
    """The L1 norm of `v`: the sum of the absolute values.

        l1_norm((3.0, -4.0, 12.0))  ->  19.0

    One line with `sum` and a generator expression.
    """
    raise NotImplementedError("exercise 1.1: l1_norm")


def l2_norm(v: Vector) -> float:
    """The L2 norm of `v`: the square root of the sum of squares.

        l2_norm((3.0, -4.0, 12.0))  ->  13.0     exactly, since 169 = 13 * 13

    Use `math.sqrt`. Do not use `** 0.5`; they agree here but `math.sqrt` says
    what you meant.
    """
    raise NotImplementedError("exercise 1.2: l2_norm")


def linf_norm(v: Vector) -> float:
    """The L-infinity norm of `v`: the largest single absolute component.

        linf_norm((3.0, -4.0, 12.0))  ->  12.0
        linf_norm(())                 ->  0.0

    Note the empty case. `max` on an empty sequence raises, so pass
    `default=0.0`.
    """
    raise NotImplementedError("exercise 1.3: linf_norm")


def p_norm(v: Vector, p: float) -> float:
    """The general p-norm: (sum of |x| ** p) ** (1 / p).

        p_norm((3, 4), 1)        ->  7.0
        p_norm((3, 4), 2)        ->  5.0
        p_norm((3, 4), math.inf) ->  4.0

    Two cases the tests check and one trap:

    * `p < 1` is NOT a norm -- the triangle inequality fails below 1 -- so
      raise `ValueError` rather than returning a plausible number.
    * `p = math.inf` must be handled as the LIMIT, returning the largest
      absolute component. Computing it as arithmetic overflows, because
      `x ** math.inf` is `inf` for any x above 1.
    * `math.isinf(p)` is the readable test for the second case.
    """
    raise NotImplementedError("exercise 1.4: p_norm")


# -- Exercise 1.5 to 1.7: the distances ---------------------------------------


def l1_distance(u: Vector, v: Vector) -> float:
    """Manhattan distance: total disagreement, summed across the features.

        l1_distance((4, 3, 2, 1), (4, 3, 2, 6))  ->  5.0

    Every unit of difference costs the same wherever it happens. Use `_paired`.
    """
    raise NotImplementedError("exercise 1.5: l1_distance")


def l2_distance(u: Vector, v: Vector) -> float:
    """Euclidean distance: straight-line separation.

        l2_distance((0, 0), (6, 8))  ->  10.0

    Squaring makes one large disagreement cost far more than several small
    ones that add up to the same total.
    """
    raise NotImplementedError("exercise 1.6: l2_distance")


def linf_distance(u: Vector, v: Vector) -> float:
    """Chebyshev distance: the single worst feature decides, alone.

        linf_distance((0, 0), (6, 8))  ->  8.0

    Every other feature is ignored entirely. Remember `default=0.0`.
    """
    raise NotImplementedError("exercise 1.7: linf_distance")


def minkowski_distance(u: Vector, v: Vector, p: float) -> float:
    """The p-norm of the difference. Written for you, once p_norm exists."""
    return p_norm([a - b for a, b in _paired(u, v)], p)


# -- Exercise 1.8: the angle --------------------------------------------------


def dot(u: Vector, v: Vector) -> float:
    """Day 103's dot product. Written for you."""
    return sum(a * b for a, b in _paired(u, v))


def cosine_similarity(u: Vector, v: Vector) -> float:
    """The cosine of the angle between two vectors: 1 identical, 0 orthogonal.

        cosine_similarity((4, 3, 2, 1), (12, 9, 6, 3))  ->  1.0

    Day 103 derived this: the dot product divided by both lengths. Length is
    divided out, which is the whole point -- the second vector above is the
    first at three times the size and scores exactly 1.

    The zero vector has no direction, so cosine is undefined for it. RAISE
    `ValueError` rather than returning 0.0; a silent wrong answer here
    propagates into a ranking and is very hard to find later. Use `TOL` to
    test for a zero length rather than `== 0`.
    """
    raise NotImplementedError("exercise 1.8: cosine_similarity")


def cosine_distance(u: Vector, v: Vector) -> float:
    """1 minus the cosine similarity. Written for you.

    Widely used, useful, and NOT a metric: exercise 2 asks you to say which
    axiom it breaks.
    """
    return 1.0 - cosine_similarity(u, v)


# -- Exercise 1.9 to 1.11: categorical and set data ---------------------------


def hamming_distance(a: Sequence, b: Sequence) -> int:
    """How many positions differ. The right answer for categorical features.

        hamming_distance(("steel", "zinc", "M8"),
                         ("brass", "zinc", "M8"))   ->  1

    Nothing is subtracted, so the values need not be numbers. Return an `int`,
    not a float, and use `_paired` so that a length mismatch raises.
    """
    raise NotImplementedError("exercise 1.9: hamming_distance")


def normalised_hamming(a: Sequence, b: Sequence) -> float:
    """Hamming as a fraction of the fields. Written for you."""
    if not a:
        raise ValueError("normalised Hamming needs at least one field")
    return hamming_distance(a, b) / len(a)


def jaccard_similarity(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """|intersection| / |union| for two sets: 1 identical, 0 disjoint.

        jaccard_similarity({1, 2, 3, 4}, {1, 2, 3, 4, 5})  ->  0.8
        jaccard_similarity({1, 2}, {3, 4})                 ->  0.0

    Two conventions the tests check:

    * The arguments may be any iterables. Call `set()` on both first.
    * Two EMPTY sets are defined here as identical, similarity 1.0. That is a
      convention rather than a derivation -- 0/0 has no answer -- and stating
      it is better than letting a ZeroDivisionError escape at 3 a.m.
    """
    raise NotImplementedError("exercise 1.10: jaccard_similarity")


def jaccard_distance(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """1 minus Jaccard similarity. Written for you.

    Unlike cosine distance, this one IS a metric -- the reference tests check
    that on all 4096 triples of subsets of a four-element set.
    """
    return 1.0 - jaccard_similarity(a, b)


def vocabulary(*collections: Iterable[Hashable]) -> list[Hashable]:
    """The SORTED union of several collections. Written for you.

    Sorted rather than in encounter order, so the binary vectors below are the
    same on every run. A set has no order, and a vector built from one without
    sorting is a different vector each time the interpreter starts.
    """
    seen: set[Hashable] = set()
    for collection in collections:
        seen |= set(collection)
    return sorted(seen)


def to_binary_vector(items: Iterable[Hashable],
                     axes: Sequence[Hashable]) -> list[float]:
    """Turn a set into a 1/0 vector over a fixed list of axes.

        to_binary_vector({"a", "c"}, ["a", "b", "c"])  ->  [1.0, 0.0, 1.0]

    This is how a set gets handed to a measure that expects numbers, and it is
    what makes the Jaccard-against-cosine comparison possible on identical
    data. Return floats, not booleans.
    """
    raise NotImplementedError("exercise 1.11: to_binary_vector")


# -- Written for you: small matrix arithmetic ---------------------------------
#
# You have built matrix multiplication already, on Day 101, and Gauss-Jordan
# elimination is a day of its own. These are given so that exercise 1.16 is
# about Mahalanobis distance and not about linear solvers.


def transpose(m: Matrix) -> Matrix:
    """Rows become columns."""
    return [list(col) for col in zip(*m)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Day 101's matrix product."""
    if len(a[0]) != len(b):
        raise DimensionMismatch(
            f"cannot multiply {len(a)}x{len(a[0])} by {len(b)}x{len(b[0])}"
        )
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def mat_vec(m: Matrix, v: Vector) -> list[float]:
    """Matrix times column vector."""
    if len(m[0]) != len(v):
        raise DimensionMismatch(
            f"cannot apply {len(m)}x{len(m[0])} matrix to a vector of {len(v)}"
        )
    return [sum(x * y for x, y in zip(row, v)) for row in m]


def inverse(m: Matrix) -> Matrix:
    """Invert a square matrix by Gauss-Jordan elimination with partial pivoting.

    Raises ValueError when the matrix is singular, which is what a covariance
    matrix with two identical features gives you.
    """
    n = len(m)
    if any(len(row) != n for row in m):
        raise DimensionMismatch("only a square matrix can be inverted")
    aug = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)]
           for i, row in enumerate(m)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) <= TOL:
            raise ValueError("matrix is singular: it has no inverse")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == 0.0:
                continue
            aug[row] = [x - factor * y for x, y in zip(aug[row], aug[col])]
    return [row[n:] for row in aug]


# -- Exercise 1.12 to 1.16: statistics, scaling and Mahalanobis --------------


def column_means(rows: Sequence[Vector]) -> list[float]:
    """The mean of each column of a table of equal-length rows.

        column_means([(1.0, 10.0), (3.0, 20.0)])  ->  [2.0, 15.0]

    Raise `ValueError` on an empty table rather than returning `[]`.
    """
    raise NotImplementedError("exercise 1.12: column_means")


def column_stds(rows: Sequence[Vector]) -> list[float]:
    """The POPULATION standard deviation of each column: divided by n.

        column_stds([(1.0,), (3.0,)])  ->  [1.0]

    Which divisor to use is a real decision and this lab makes it explicitly.
    `n` describes the table you have; `n - 1` estimates a wider population you
    are sampling from. Scikit-learn's StandardScaler divides by `n`, and
    `numpy.std` does too unless you pass `ddof=1`, so `n` is what this lab
    uses and what the tests check against.
    """
    raise NotImplementedError("exercise 1.13: column_stds")


def standardise(
    rows: Sequence[Vector],
    means: Sequence[float] | None = None,
    stds: Sequence[float] | None = None,
) -> list[list[float]]:
    """Subtract the column mean, divide by the column standard deviation.

        standardise([(1.0,), (3.0,)])  ->  [[-1.0], [1.0]]

    Also called the z-score. Three requirements the tests check:

    * When `means` or `stds` is given, USE IT instead of recomputing. This is
      how a query gets standardised with the same numbers as the catalogue it
      is being compared against. Standardising a single query against itself
      gives a row of zeros, which is a real bug with a long history.
    * A column whose standard deviation is 0 (within `TOL`) must come out as
      0.0 rather than dividing by zero. It carries no information to scale.
    * Return a list of lists of floats, one per input row, same order.
    """
    raise NotImplementedError("exercise 1.14: standardise")


def covariance_matrix(rows: Sequence[Vector]) -> Matrix:
    """The population covariance matrix of a table of rows, divided by n.

    Entry (i, j) is the average product of column i's and column j's
    deviations from their own means:

        cov[i][j] = sum over rows of (row[i] - mean[i]) * (row[j] - mean[j]) / n

    The diagonal is each column's variance. On the eight sensor readings in
    `catalogue.py` the answer is exactly [[7.5, 7.0], [7.0, 7.5]], which you
    can check by hand -- and the tests do.

    Day 106's eigenvectors of this matrix are the directions the data actually
    spreads along, which is exactly what the next function measures in.
    """
    raise NotImplementedError("exercise 1.15: covariance_matrix")


def mahalanobis_distance(u: Vector, v: Vector, cov_inverse: Matrix) -> float:
    """Euclidean distance after accounting for how the data actually varies.

    One line of arithmetic. Take the difference `z = u - v`, and instead of
    dotting it with itself, dot it with itself THROUGH the inverse covariance:

        d = sqrt( z . (cov_inverse . z) )

    You have `dot` and `mat_vec` already.

    Check yourself two ways:

    * Passing the IDENTITY matrix as `cov_inverse` must give back ordinary
      Euclidean distance, exactly. That is the cleanest statement of what the
      covariance is doing.
    * On the sensor readings, (3, 3) and (3, -3) are the same Euclidean
      distance from the mean and 1.114172 against 6.0 in Mahalanobis.

    One floating-point guard the tests check. A covariance matrix is positive
    semi-definite, so the value under the square root is non-negative in exact
    arithmetic -- but a result that should be 0 can come out as -1e-17, and
    `math.sqrt` raises on it. Clamp a tiny negative to 0.0, and raise
    `ValueError` for one that is genuinely negative (worse than -TOL), because
    that means the matrix you were handed is not an inverse covariance.
    """
    raise NotImplementedError("exercise 1.16: mahalanobis_distance")


# -- Exercise 1.17: the function the whole day is about ----------------------


def rank(
    query,
    candidates: dict[str, object],
    measure: Callable,
    higher_is_better: bool = False,
) -> list[tuple[str, float]]:
    """Score every candidate against the query and sort best first.

        rank((4, 3, 2, 1), {"Aisle": (4, 3, 2, 6)}, l1_distance)
            ->  [("Aisle", 5.0)]

    This is the function the day is really about. Swapping Manhattan for
    cosine must be ONE argument here.

    Three requirements the tests check:

    * Return a list of `(name, score)` pairs, score as a `float`.
    * `higher_is_better=False` sorts ascending (a distance); `True` sorts
      descending (a similarity). Getting this backwards returns the WORST
      match with complete confidence and no error message.
    * Ties must break by the candidate's name, so two runs never disagree for
      a reason that has nothing to do with the data. A one-key sort on the
      score alone is not enough; sort on a tuple.
    """
    raise NotImplementedError("exercise 1.17: rank")


def winner(query, candidates: dict[str, object], measure: Callable,
           higher_is_better: bool = False) -> str:
    """The name at the top of `rank`. Written for you."""
    return rank(query, candidates, measure, higher_is_better)[0][0]
