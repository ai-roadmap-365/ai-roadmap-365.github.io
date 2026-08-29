"""Vectors from scratch, in pure Python.

The reference implementation for the Day 099 lab. Every function here works on
an ordinary Python list of numbers. There is no NumPy in this file on purpose:
the point of the lab is that you write the loop first, so that when NumPy does
the same thing in one character you already know what it is doing.

A vector here is `[3, 4]` or `[9, 0, 1, 0]` — a list of numbers, in a fixed
order, where position means something. Nothing more.

Every function that takes two vectors checks that they have the same length
first. Adding a 2-dimensional vector to a 3-dimensional one is not a slightly
wrong answer, it is a meaningless question, and the code should say so rather
than silently truncating.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

Vector = Sequence[float]


# --------------------------------------------------------------------------
# The guard every two-vector operation shares
# --------------------------------------------------------------------------


def check_same_dimension(u: Vector, v: Vector) -> None:
    """Raise unless `u` and `v` have the same number of components.

    Length is the dimension. Two vectors of different dimension do not live in
    the same space, and no operation below is defined across them.
    """
    if len(u) != len(v):
        raise ValueError(
            f"dimension mismatch: {len(u)} and {len(v)} "
            "— vectors must have the same number of components"
        )


# --------------------------------------------------------------------------
# Addition, subtraction, scaling
# --------------------------------------------------------------------------


def add(u: Vector, v: Vector) -> list[float]:
    """Componentwise sum. Geometrically: walk u, then walk v from where you land."""
    check_same_dimension(u, v)
    return [a + b for a, b in zip(u, v)]


def subtract(u: Vector, v: Vector) -> list[float]:
    """Componentwise difference.

    Geometrically u - v is the arrow that starts at the tip of v and ends at
    the tip of u: "how do I get from v to u". That is why the distance between
    two points is the magnitude of their difference.
    """
    check_same_dimension(u, v)
    return [a - b for a, b in zip(u, v)]


def scale(k: float, v: Vector) -> list[float]:
    """Multiply every component by the number k.

    A positive k changes magnitude and leaves direction alone. A negative k
    reverses the direction as well. k = 0 collapses the vector to the zero
    vector, which is the one vector with no direction at all.
    """
    return [k * a for a in v]


def negate(v: Vector) -> list[float]:
    """The vector of the same magnitude pointing the opposite way: -1 times v."""
    return scale(-1, v)


def zero(dimension: int) -> list[float]:
    """The zero vector of a given dimension: all components 0.

    It is the additive identity — add it to anything and nothing moves — and
    it is the one vector whose magnitude is 0 and whose direction is undefined.
    """
    if dimension < 0:
        raise ValueError(f"dimension must not be negative, got {dimension}")
    return [0.0] * dimension


# --------------------------------------------------------------------------
# Dot product
# --------------------------------------------------------------------------


def dot(u: Vector, v: Vector) -> float:
    """Multiply matching components, then add up the results.

    Returns one number, not a vector. That collapse from two lists to a single
    number is the whole reason the dot product is everywhere: it is how a
    similarity score, a projection and a weighted sum are all computed.
    """
    check_same_dimension(u, v)
    total = 0.0
    for a, b in zip(u, v):
        total += a * b
    return total


# --------------------------------------------------------------------------
# Norms — two ways of answering "how big is this vector"
# --------------------------------------------------------------------------


def l2_norm(v: Vector) -> float:
    """The Euclidean length: square every component, add, take the square root.

    This is Pythagoras, applied one dimension at a time. In 2D it is literally
    the hypotenuse. In 300 dimensions the picture is gone but the arithmetic is
    unchanged, which is the single most useful fact in this lesson.
    """
    return math.sqrt(sum(a * a for a in v))


# The name used everywhere else in the lab, because "magnitude" is the word the
# lesson uses and `norm` unqualified always means L2 in practice.
norm = l2_norm
magnitude = l2_norm


def l1_norm(v: Vector) -> float:
    """The taxicab length: add up the absolute values of the components.

    No squaring, so no square root. L1 counts every component at face value;
    L2 punishes one large component more than several small ones. That
    difference is not cosmetic — the two norms can rank the same pair of
    candidates in opposite orders, which `norms.py` demonstrates.
    """
    return sum(abs(a) for a in v)


# --------------------------------------------------------------------------
# Distance and normalisation
# --------------------------------------------------------------------------


def distance(u: Vector, v: Vector) -> float:
    """Euclidean distance: the magnitude of the difference.

    There is no separate distance formula to memorise. Subtract, then measure.
    """
    return l2_norm(subtract(u, v))


def l1_distance(u: Vector, v: Vector) -> float:
    """Manhattan distance: the L1 norm of the difference."""
    return l1_norm(subtract(u, v))


def normalise(v: Vector) -> list[float]:
    """Scale a vector to magnitude 1, keeping its direction.

    Dividing by the magnitude is the same as multiplying by 1/magnitude, so
    this is scalar multiplication with a particular scalar. The zero vector has
    magnitude 0 and no direction, so it cannot be normalised — this raises
    rather than returning a list of NaNs that would poison every later result.

    The result's magnitude is 1 to within floating-point error, and *not*
    exactly 1. Never test it with `==`; see `normalise.py`.
    """
    length = l2_norm(v)
    if length == 0.0:
        raise ValueError("cannot normalise the zero vector: it has no direction")
    return scale(1.0 / length, v)


def is_unit(v: Vector, *, rel_tol: float = 1e-9, abs_tol: float = 1e-12) -> bool:
    """True if the magnitude is 1 to the stated tolerance.

    The default tolerance is the one used throughout this lab. It is stated as
    a keyword argument rather than hidden in the body so that a caller who
    needs a looser one has to say so out loud.
    """
    return math.isclose(l2_norm(v), 1.0, rel_tol=rel_tol, abs_tol=abs_tol)


# --------------------------------------------------------------------------
# Working with a labelled collection of vectors
# --------------------------------------------------------------------------


def nearest(
    query: Vector,
    labelled: dict[str, Vector],
    *,
    metric=distance,
    exclude: str | None = None,
) -> tuple[str, float]:
    """Return the (label, score) of the closest entry under `metric`.

    `exclude` skips one label, which is what you want when the query is itself
    a member of the collection — otherwise every item's nearest neighbour is
    itself at distance 0, which is true and useless.

    Ties are broken by label so the answer is deterministic and testable.
    """
    candidates = [
        (label, metric(query, vec))
        for label, vec in labelled.items()
        if label != exclude
    ]
    if not candidates:
        raise ValueError("no candidates to compare against")
    return min(candidates, key=lambda pair: (pair[1], pair[0]))


def pairwise_distances(labelled: dict[str, Vector], *, metric=distance) -> dict:
    """Every unordered pair mapped to its distance, keyed by (label_a, label_b)."""
    labels = list(labelled)
    out = {}
    for i, a in enumerate(labels):
        for b in labels[i + 1 :]:
            out[(a, b)] = metric(labelled[a], labelled[b])
    return out


if __name__ == "__main__":
    a = [3, 4]
    b = [6, 8]
    print("a            =", a)
    print("b            =", b)
    print("a + b        =", add(a, b))
    print("b - a        =", subtract(b, a))
    print("2 * a        =", scale(2, a))
    print("a . b        =", dot(a, b))
    print("|a|          =", l2_norm(a))
    print("L1 of a      =", l1_norm(a))
    print("dist(a, b)   =", distance(a, b))
    print("normalise(a) =", normalise(a))
