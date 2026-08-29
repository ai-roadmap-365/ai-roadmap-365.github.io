"""The reference implementation: dot product, cosine similarity, cosine distance.

Pure Python, no imports beyond the standard library's `math`. Every function
here is a few lines, and together they are the arithmetic underneath every
semantic search and every retrieval step in a document-answering system.

This is the answer key for `starter/similarity.py`. Read it after you have
written yours, not before.

Design notes worth carrying into any real implementation:

* Every function that compares two vectors checks that the lengths match
  first, and raises ValueError rather than returning a wrong number quietly.
  NumPy raises ValueError for the same mistake, so one `except ValueError`
  catches both.
* `cosine_similarity` refuses the zero vector instead of returning NaN. A zero
  vector has no direction, so "which way does it point" has no answer, and a
  silent NaN travelling through a ranking is much worse than a loud error.
* Results are clamped to [-1, 1]. Floating point can hand you 1.0000000000000002
  for a vector compared with itself, and `math.acos` of that raises ValueError
  — a real failure this lab hit while it was being written.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence


def _check_same_length(a: Sequence[float], b: Sequence[float]) -> None:
    if len(a) != len(b):
        raise ValueError(
            f"vectors must have the same number of components: "
            f"got {len(a)} and {len(b)}"
        )


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Multiply the two vectors component by component, then add it all up.

    That is the whole definition. a dot b = a1*b1 + a2*b2 + ... + an*bn, and
    the answer is a single number, not a vector.
    """
    _check_same_length(a, b)
    return float(sum(x * y for x, y in zip(a, b)))


def l2_norm(a: Sequence[float]) -> float:
    """The length of the vector: the square root of the sum of its squares.

    Note that l2_norm(a) is exactly sqrt(dot(a, a)) — a vector's length is the
    dot product of the vector with itself, square-rooted. Day 99 defined this
    with Pythagoras; today it turns out to be a special case of the dot
    product, which is the first hint that the dot product is the more
    fundamental operation.
    """
    return math.sqrt(dot(a, a))


def normalise(a: Sequence[float]) -> list[float]:
    """Return the unit vector pointing the same way: same direction, length 1."""
    length = l2_norm(a)
    if length == 0.0:
        raise ValueError("the zero vector has no direction, so it cannot be normalised")
    return [x / length for x in a]


def euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """The straight-line distance between the two points: the length of a - b."""
    _check_same_length(a, b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """The cosine of the angle between the two vectors, in the range -1 to 1.

    a dot b = |a| |b| cos(theta), so cos(theta) = (a dot b) / (|a| |b|). The two
    divisions are what make this magnitude-free: scaling either vector by any
    positive number multiplies the top and the bottom by the same factor, and
    the answer does not move.

    Equivalently, and this is worth knowing because it is how a vector database
    ends up doing it: cosine similarity is the plain dot product of the two
    UNIT vectors. Normalise once, and every later comparison is a dot product.
    """
    _check_same_length(a, b)
    na, nb = l2_norm(a), l2_norm(b)
    if na == 0.0 or nb == 0.0:
        raise ValueError(
            "cosine similarity is undefined when either vector is the zero "
            "vector: it has no direction to compare"
        )
    return _clamp(dot(a, b) / (na * nb))


def cosine_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """1 minus the cosine similarity: 0 for identical direction, 2 for opposite.

    Called a distance because it grows as things get less alike, but it is NOT
    a metric — it fails the triangle inequality, and section 5 of this lab
    shows a concrete triple where it does.
    """
    return 1.0 - cosine_similarity(a, b)


def angle_degrees(a: Sequence[float], b: Sequence[float]) -> float:
    """The angle between the two vectors, in degrees, from 0 to 180."""
    return math.degrees(math.acos(cosine_similarity(a, b)))


def scalar_projection(a: Sequence[float], b: Sequence[float]) -> float:
    """How much of b lies along a: the length of b's shadow on a's direction.

    (a dot b) / |a|. Note the asymmetry — this is b measured against a's
    direction, so swapping the arguments generally changes the answer, even
    though the dot product itself does not care about order.
    """
    na = l2_norm(a)
    if na == 0.0:
        raise ValueError("cannot project onto the zero vector: it has no direction")
    return dot(a, b) / na


def vector_projection(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """The shadow itself: the part of b that points along a, as a vector."""
    unit_a = normalise(a)
    length = dot(unit_a, b)
    return [length * x for x in unit_a]


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    """Keep a cosine inside [-1, 1] despite floating-point rounding."""
    return max(low, min(high, value))


def rank_by_cosine(
    query: Sequence[float], catalogue: dict[str, Sequence[float]]
) -> list[tuple[str, float]]:
    """Every item scored against the query, best first. This is the search.

    Ties are broken by name so the ranking is deterministic and testable; a
    real system would break them by document id or by insertion order, and it
    matters that it breaks them by SOMETHING, because an unstable sort makes a
    ranking that changes between runs.
    """
    scored = [
        (label, cosine_similarity(query, vector)) for label, vector in catalogue.items()
    ]
    return sorted(scored, key=lambda pair: (-pair[1], pair[0]))


def rank_by_euclidean(
    query: Sequence[float], catalogue: dict[str, Sequence[float]]
) -> list[tuple[str, float]]:
    """Every item scored by straight-line distance, nearest first."""
    scored = [
        (label, euclidean_distance(query, vector))
        for label, vector in catalogue.items()
    ]
    return sorted(scored, key=lambda pair: (pair[1], pair[0]))


def normalise_all(catalogue: dict[str, Sequence[float]]) -> dict[str, list[float]]:
    """Put every vector in the catalogue on the unit sphere, once."""
    return {label: normalise(vector) for label, vector in catalogue.items()}


def mean_absolute_cosine(pairs: Iterable[tuple[Sequence[float], Sequence[float]]]) -> float:
    """The average of |cos| over a collection of vector pairs.

    Used in section 6 to measure how nearly orthogonal random vectors become as
    the number of dimensions grows.
    """
    values = [abs(cosine_similarity(a, b)) for a, b in pairs]
    if not values:
        raise ValueError("need at least one pair to average over")
    return sum(values) / len(values)
