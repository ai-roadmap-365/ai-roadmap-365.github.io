"""The reference implementation: every measure in this lab, in pure Python.

Read this AFTER you have attempted `starter/measures.py`. Nothing here uses
NumPy. That is deliberate and it is the whole basis of the day's evidence: if
these functions were built out of NumPy calls, then checking them against
NumPy would be checking NumPy against itself and would prove nothing at all.

NumPy appears in the tests and in the demonstration scripts, where it is the
independent answer. `numpy.linalg.norm(v, ord=p)` is exactly the p-norm family
implemented below, and agreeing with it to 1e-12 on values this code computed
from `abs`, `**` and `sum` is a real check.

Two conventions, fixed and used everywhere:

1. A vector is a plain sequence of floats. Two vectors compared must have the
   same length, and every function here says so by raising rather than by
   zipping the shorter one and quietly answering the wrong question.

2. A DISTANCE gets smaller as things get more alike; a SIMILARITY gets larger.
   Every function name says which it is. Mixing them up is the single most
   common way to build a retrieval system that returns the worst match with
   great confidence, so this module never guesses: `rank` takes an explicit
   `higher_is_better` flag.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Iterable, Sequence

Vector = Sequence[float]
Matrix = list[list[float]]

# Every float comparison in this lab is made against this tolerance. It is not
# decoration. `math.sqrt(2) ** 2` is 2.0000000000000004, and the Mahalanobis
# result this lab is built around comes out as exactly 6.0 through the
# Gauss-Jordan inverse below and as 5.999999999999999 through
# `numpy.linalg.inv` -- two correct routes to the same number, disagreeing in
# the last bit. `== 6.0` would pass for one and fail for the other.
TOL = 1e-12


class DimensionMismatch(ValueError):
    """Raised when two vectors of different lengths are compared.

    Subclasses ValueError so that an existing `except ValueError` catches it,
    matching how NumPy reports the same mistake.
    """


def _paired(u: Vector, v: Vector) -> list[tuple[float, float]]:
    """Pair two vectors elementwise, refusing to compare different lengths."""
    if len(u) != len(v):
        raise DimensionMismatch(
            f"vectors have different lengths: {len(u)} and {len(v)}"
        )
    return list(zip(u, v))


# -- Norms: the size of one vector --------------------------------------------


def p_norm(v: Vector, p: float) -> float:
    """The general p-norm of `v`: (sum of |x| ** p) ** (1 / p).

    `p` must be at least 1. Below 1 the shape stops obeying the triangle
    inequality and the result is no longer a norm at all, which is why this
    refuses rather than returning a plausible number.

    `p = math.inf` is the limit as p grows: the largest single absolute
    component, and it is computed as that limit rather than by arithmetic,
    because `x ** math.inf` overflows.

        p_norm((3, 4), 1)        -> 7.0
        p_norm((3, 4), 2)        -> 5.0
        p_norm((3, 4), math.inf) -> 4.0
    """
    if p < 1:
        raise ValueError(f"p must be at least 1 to be a norm; got {p}")
    if math.isinf(p):
        return max((abs(x) for x in v), default=0.0)
    return sum(abs(x) ** p for x in v) ** (1.0 / p)


def l1_norm(v: Vector) -> float:
    """The L1 norm: the sum of absolute values. Also called the taxicab norm."""
    return sum(abs(x) for x in v)


def l2_norm(v: Vector) -> float:
    """The L2 norm: the square root of the sum of squares.

    This is the one ordinary geometry gives you, and the only p for which the
    unit ball is round.
    """
    return math.sqrt(sum(x * x for x in v))


def linf_norm(v: Vector) -> float:
    """The L-infinity norm: the largest single absolute component."""
    return max((abs(x) for x in v), default=0.0)


# -- Distances: how far apart two vectors are ---------------------------------


def minkowski_distance(u: Vector, v: Vector, p: float) -> float:
    """The p-norm of the difference. Every distance below is a special case."""
    return p_norm([a - b for a, b in _paired(u, v)], p)


def l1_distance(u: Vector, v: Vector) -> float:
    """Manhattan distance: total disagreement, summed across the features.

    Every unit of difference costs the same wherever it happens, so ten
    features each one out costs exactly what one feature ten out costs.
    """
    return sum(abs(a - b) for a, b in _paired(u, v))


def l2_distance(u: Vector, v: Vector) -> float:
    """Euclidean distance: straight-line separation.

    Squaring makes one large disagreement cost far more than several small
    ones adding to the same total.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in _paired(u, v)))


def linf_distance(u: Vector, v: Vector) -> float:
    """Chebyshev distance: the single worst feature decides, alone.

    Every other feature is ignored entirely. That sounds like a weakness until
    you meet a tolerance check, where a part is out of specification if ANY
    dimension is out, or a two-axis machine, where the slower axis sets the
    time.
    """
    return max((abs(a - b) for a, b in _paired(u, v)), default=0.0)


# -- Angle: a similarity, not a distance --------------------------------------


def dot(u: Vector, v: Vector) -> float:
    """Day 103's dot product, repeated here so this module stands alone."""
    return sum(a * b for a, b in _paired(u, v))


def cosine_similarity(u: Vector, v: Vector) -> float:
    """The cosine of the angle between two vectors: 1 identical, 0 orthogonal.

    Day 103 derived this. It is repeated rather than re-taught. Length is
    divided out, which is the whole point: a document three times as long with
    the same word mix scores exactly 1.0.

    Undefined for the zero vector, which has no direction, so this raises
    rather than returning 0.0 and letting a silent wrong answer propagate.
    """
    nu, nv = l2_norm(u), l2_norm(v)
    if nu <= TOL or nv <= TOL:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return dot(u, v) / (nu * nv)


def cosine_distance(u: Vector, v: Vector) -> float:
    """1 minus the cosine similarity.

    Widely used, useful, and NOT a metric: it fails the triangle inequality,
    which Day 103 proved and `03_metrics_and_non_metrics.py` demonstrates again
    with a concrete counter-example. Call it a dissimilarity if you want to be
    precise.
    """
    return 1.0 - cosine_similarity(u, v)


# -- Categorical and set data -------------------------------------------------


def hamming_distance(a: Sequence, b: Sequence) -> int:
    """How many positions differ. The right answer for categorical features.

    Nothing is subtracted, so the values need not be numbers: 'red' against
    'blue' is a difference of 1, exactly like 'red' against 'green'. There is
    no sense in which red is nearer to blue than to green, and any measure that
    invents one has invented data.
    """
    return sum(1 for x, y in _paired(a, b) if x != y)


def normalised_hamming(a: Sequence, b: Sequence) -> float:
    """Hamming distance as a fraction of the fields, so lengths compare."""
    if not a:
        raise ValueError("normalised Hamming needs at least one field")
    return hamming_distance(a, b) / len(a)


def jaccard_similarity(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """|intersection| / |union| for two sets: 1 identical, 0 disjoint.

    Two empty sets are defined here as identical, similarity 1.0. That is a
    convention rather than a derivation, and it is stated rather than hidden.
    """
    sa, sb = set(a), set(b)
    union = sa | sb
    if not union:
        return 1.0
    return len(sa & sb) / len(union)


def jaccard_distance(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """1 minus Jaccard similarity. Unlike cosine distance, this IS a metric."""
    return 1.0 - jaccard_similarity(a, b)


def vocabulary(*collections: Iterable[Hashable]) -> list[Hashable]:
    """The sorted union of several collections: a fixed axis order.

    Sorted rather than in encounter order, so that the binary vectors below are
    the same on every run and on every machine. A set has no order, and a
    vector built from one without sorting is a different vector each time the
    interpreter starts.
    """
    seen: set[Hashable] = set()
    for collection in collections:
        seen |= set(collection)
    return sorted(seen)


def to_binary_vector(items: Iterable[Hashable],
                     axes: Sequence[Hashable]) -> list[float]:
    """Turn a set into a 1/0 vector over a fixed list of axes.

    This is how a set gets handed to a measure that expects numbers, and it is
    where the Jaccard-against-cosine comparison becomes possible: the same two
    sets, scored both ways, on exactly the same data.
    """
    present = set(items)
    return [1.0 if axis in present else 0.0 for axis in axes]


# -- Small matrix arithmetic, in pure Python ----------------------------------


def transpose(m: Matrix) -> Matrix:
    """Rows become columns."""
    return [list(col) for col in zip(*m)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Day 101's matrix product: row of `a` dotted with column of `b`."""
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

    Written out rather than imported so the Mahalanobis distance below owes
    nothing to NumPy. `test_reference.py` checks it against `numpy.linalg.inv`.

    Partial pivoting -- always taking the largest available pivot -- is not
    tidiness. Without it, a small pivot divides the rest of the row by
    something near zero and the error in every later step is multiplied by
    however small it was.
    """
    n = len(m)
    if any(len(row) != n for row in m):
        raise DimensionMismatch("only a square matrix can be inverted")
    # Work on [m | I] and reduce the left half to the identity.
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


# -- Statistics of a table of rows --------------------------------------------


def column_means(rows: Sequence[Vector]) -> list[float]:
    """The mean of each column of a table of equal-length rows."""
    if not rows:
        raise ValueError("no rows")
    n = len(rows)
    return [sum(row[j] for row in rows) / n for j in range(len(rows[0]))]


def column_stds(rows: Sequence[Vector]) -> list[float]:
    """The POPULATION standard deviation of each column: divided by n, not n-1.

    Which divisor to use is a real decision and this lab makes it explicitly.
    `n` describes the table you have; `n - 1` estimates a wider population you
    are sampling from. Scikit-learn's StandardScaler divides by `n`, and
    `numpy.std` does too unless you pass `ddof=1`, so `n` is what this lab
    uses and what the tests check against.
    """
    means = column_means(rows)
    n = len(rows)
    return [math.sqrt(sum((row[j] - means[j]) ** 2 for row in rows) / n)
            for j in range(len(rows[0]))]


def standardise(
    rows: Sequence[Vector],
    means: Sequence[float] | None = None,
    stds: Sequence[float] | None = None,
) -> list[list[float]]:
    """Subtract the column mean and divide by the column standard deviation.

    Also called the z-score. After it, every column has mean 0 and standard
    deviation 1, so a metre and a gram contribute on the same terms.

    `means` and `stds` may be supplied so that a query is standardised with the
    SAME numbers as the catalogue it is being compared against. Standardising a
    single query against itself would give a row of zeros, which is a mistake
    with a long history in production retrieval systems.

    A column with zero spread is left at 0.0 rather than dividing by zero: it
    carries no information to scale.
    """
    mu = list(means) if means is not None else column_means(rows)
    sd = list(stds) if stds is not None else column_stds(rows)
    out = []
    for row in rows:
        out.append([0.0 if sd[j] <= TOL else (row[j] - mu[j]) / sd[j]
                    for j in range(len(row))])
    return out


def covariance_matrix(rows: Sequence[Vector]) -> Matrix:
    """The population covariance matrix of a table of rows, divided by n.

    Entry (i, j) is the average product of column i's and column j's deviations
    from their own means. The diagonal is each column's variance; the
    off-diagonal is how the two move together. Day 106's eigenvectors of this
    matrix are the directions the data actually spreads along, and Mahalanobis
    distance below is what you get by measuring in those directions.
    """
    means = column_means(rows)
    n, k = len(rows), len(rows[0])
    return [[sum((row[i] - means[i]) * (row[j] - means[j]) for row in rows) / n
             for j in range(k)] for i in range(k)]


def mahalanobis_distance(u: Vector, v: Vector, cov_inverse: Matrix) -> float:
    """Euclidean distance after accounting for how the data actually varies.

    The arithmetic is one line: take the difference, and instead of dotting it
    with itself, dot it with itself THROUGH the inverse covariance matrix.

        d = sqrt( z . (cov_inverse . z) )   where z = u - v

    Substituting the identity matrix for `cov_inverse` gives back ordinary
    Euclidean distance exactly, which is the cleanest way to see what the
    covariance is doing: it re-weights the axes so that a step of one is a step
    of one standard deviation *of the data*, and it un-tilts correlated
    features so that moving along the grain of the data is cheap and moving
    across it is expensive.

    `cov_inverse` is passed in already inverted because in practice you invert
    the covariance once and then score thousands of points against it.
    """
    z = [a - b for a, b in _paired(u, v)]
    squared = dot(z, mat_vec(cov_inverse, z))
    # A covariance matrix is positive semi-definite, so `squared` is
    # non-negative in exact arithmetic. In floating point a value that should
    # be 0 can come out as -1e-17, and math.sqrt would raise on it.
    if squared < 0.0:
        if squared < -TOL:
            raise ValueError(
                f"negative squared distance ({squared}): "
                "the matrix supplied is not a valid inverse covariance"
            )
        squared = 0.0
    return math.sqrt(squared)


# -- One ranking function, with the measure as a parameter --------------------


def rank(
    query,
    candidates: dict[str, object],
    measure: Callable,
    higher_is_better: bool = False,
) -> list[tuple[str, float]]:
    """Score every candidate against the query and sort best first.

    This is the function the day is really about. Swapping Manhattan for
    cosine is ONE argument here, and the rankings move -- which is the honest
    way to see that the choice of measure is a modelling decision and not a
    detail.

    Ties are broken by the candidate's name, so the output is deterministic and
    two runs never disagree for a reason that has nothing to do with the data.
    """
    scored = [(name, float(measure(query, value)))
              for name, value in candidates.items()]
    scored.sort(key=lambda pair: (-pair[1] if higher_is_better else pair[1],
                                  pair[0]))
    return scored


def winner(query, candidates: dict[str, object], measure: Callable,
           higher_is_better: bool = False) -> str:
    """The name at the top of `rank`."""
    return rank(query, candidates, measure, higher_is_better)[0][0]
