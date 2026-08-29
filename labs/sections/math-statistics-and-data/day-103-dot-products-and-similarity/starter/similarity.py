"""Exercise 1 — write the similarity toolkit yourself, in pure Python.

Seven functions, none longer than four lines. Together they are the entire
arithmetic of semantic search, and after writing them you will never again be
unsure what a vector database is doing when it says "cosine".

Check your work as you go, from the LAB DIRECTORY (one level up from here):

    .venv/bin/pytest starter -q

Every test for a function you have not written yet is SKIPPED, not failed, so
the output is a running score rather than a wall of red. When all of them pass,
compare your file with examples/similarity.py — they should agree on behaviour,
not necessarily on wording.

Rules for all seven:

  * pure Python only — `import math` is allowed and nothing else. The point of
    the exercise is that nothing here is done for you;
  * never modify the arguments;
  * raise ValueError, not a bare assert, when the input makes no sense. NumPy
    raises ValueError for the same situations, so one `except ValueError` will
    catch your code and the library alike.
"""

from __future__ import annotations

import math


def _check_same_length(a, b) -> None:
    """Written for you: refuse two vectors of different lengths, loudly.

    Every function below that takes two vectors should call this first.
    """
    if len(a) != len(b):
        raise ValueError(
            f"vectors must have the same number of components: "
            f"got {len(a)} and {len(b)}"
        )


# ------------------------------------------------------------------ 1.1 --
def dot(a, b):
    """EXERCISE 1.1 — the dot product: multiply component by component, then add.

        dot([1, 2, 3], [4, 5, 6]) = 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32.0

    Return a float, not a list — the dot product of two vectors is a single
    number. Call _check_same_length first.

    Hint: sum(x * y for x, y in zip(a, b)), wrapped in float().
    """
    raise NotImplementedError("write dot")


# ------------------------------------------------------------------ 1.2 --
def l2_norm(a):
    """EXERCISE 1.2 — the length of a vector: sqrt of the sum of its squares.

        l2_norm([3, 4]) = sqrt(9 + 16) = sqrt(25) = 5.0

    Day 99 built this with Pythagoras. Today there is a shorter route worth
    noticing and using: a vector's length is the square root of the vector
    dotted with ITSELF.

    Hint: math.sqrt(dot(a, a)). One line, and it reuses 1.1.
    """
    raise NotImplementedError("write l2_norm")


# ------------------------------------------------------------------ 1.3 --
def normalise(a):
    """EXERCISE 1.3 — the unit vector: same direction, length exactly 1.

        normalise([3, 4]) = [0.6, 0.8]

    Divide every component by the vector's own length, and return a NEW list.

    The zero vector has no direction, so there is no unit vector pointing the
    same way. Raise ValueError with a message saying so, rather than letting
    Python raise ZeroDivisionError from somewhere deeper.
    """
    raise NotImplementedError("write normalise")


# ------------------------------------------------------------------ 1.4 --
def euclidean_distance(a, b):
    """EXERCISE 1.4 — straight-line distance: the length of the difference.

        euclidean_distance([9, 0, 1, 0], [8, 0, 2, 0])
            = sqrt(1 + 0 + 1 + 0) = sqrt(2) = 1.41421...

    This is Day 99's measure, and today's job is to know when it is the wrong
    one. Call _check_same_length first.
    """
    raise NotImplementedError("write euclidean_distance")


# ------------------------------------------------------------------ 1.5 --
def cosine_similarity(a, b):
    """EXERCISE 1.5 — the cosine of the angle between them, from -1 to 1.

        a dot b = |a| |b| cos(theta)      so      cos(theta) = (a dot b) / (|a| |b|)

    Three things this function must get right, and each of them is asserted by
    a separate test:

      1. Divide by BOTH lengths. That is what makes the result magnitude-free:
         doubling either vector must not change the answer at all.
      2. Raise ValueError if either vector is the zero vector. Returning NaN
         is the tempting shortcut and it is a bad one — a NaN sorts
         unpredictably and quietly ruins every average it touches.
      3. Clamp the result into the range -1 to 1 before returning it. Floating
         point can hand you 1.0000000000000002 for a vector compared with
         itself — three of this lab's six articles miss exact 1.0 — and
         math.acos of anything above 1.0 raises ValueError.

    Hint for the clamp: max(-1.0, min(1.0, value)).
    """
    raise NotImplementedError("write cosine_similarity")


# ------------------------------------------------------------------ 1.6 --
def cosine_distance(a, b):
    """EXERCISE 1.6 — one minus the cosine similarity.

        cosine_distance(a, b) = 1 - cosine_similarity(a, b)

    Zero when the two point the same way, 1 when they are perpendicular, 2
    when they point in opposite directions. One line, reusing 1.5.

    Remember what exercise 3 will make you prove about it: despite the name,
    this is not a metric.
    """
    raise NotImplementedError("write cosine_distance")


# ------------------------------------------------------------------ 1.7 --
def rank_by_cosine(query, catalogue):
    """EXERCISE 1.7 — the search itself. Score everything, best first.

    `catalogue` is a dict of {label: vector}. Return a list of
    (label, similarity) pairs sorted so the highest similarity comes first.

    Break ties by label, alphabetically. That matters more than it looks: two
    articles in this lab score exactly 0.0 against the cooking query, and a
    ranking that puts them in a different order on different runs makes a test
    suite that fails at random.

    Hint: build the list of pairs, then
        sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
    The minus sign sorts the score downwards while the label still sorts
    upwards, which is the whole trick.
    """
    raise NotImplementedError("write rank_by_cosine")
