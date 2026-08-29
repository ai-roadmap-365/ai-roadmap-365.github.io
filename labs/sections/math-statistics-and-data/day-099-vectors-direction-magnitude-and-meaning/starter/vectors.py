"""YOUR WORK GOES HERE — nine numbered exercises.

Every function below is a working skeleton: it runs, it returns `None`, and it
tells you honestly that it is not finished yet. Replace each `return None` with
real code, in order. Nothing here needs NumPy — that is the point. You write
the loop, and only then do you compare it with the library.

Run this file at any time to see how far you have got:

    python3 starter/vectors.py

Run the exercise suite to check your work:

    .venv/bin/pytest starter -q

Nine tests are skipped until you finish the matching exercise. Remove the
`@pytest.mark.skip` line above a test in `starter/test_starter.py` once you
have implemented its function.

A vector here is an ordinary Python list of numbers: `[3, 4]`, `[9, 0, 1, 0]`.
Position means something — the first component of every article vector in this
lab counts mentions of cooking — so the order never changes and two vectors are
only comparable if they have the same length.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------
# Provided for you: the guard every two-vector operation needs.
# Call this at the top of any function that takes two vectors.
# --------------------------------------------------------------------------


def check_same_dimension(u, v) -> None:
    """Raise ValueError unless u and v have the same number of components."""
    if len(u) != len(v):
        raise ValueError(
            f"dimension mismatch: {len(u)} and {len(v)} "
            "— vectors must have the same number of components"
        )


# --------------------------------------------------------------------------
# EXERCISE 1 — add
#
# Return a new list whose i-th entry is u[i] + v[i].
#   add([1, 2, 3], [10, 20, 30])  ->  [11, 22, 33]
#
# Call check_same_dimension(u, v) first. A list comprehension over
# zip(u, v) is the shortest way, but a plain for-loop is just as good.
# --------------------------------------------------------------------------


def add(u, v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 2 — subtract
#
# Return a new list whose i-th entry is u[i] - v[i].
#   subtract([4, 6], [1, 2])  ->  [3, 4]
#
# Geometrically u - v is the arrow from the tip of v to the tip of u. Hold on
# to that: exercise 7 depends on it.
# --------------------------------------------------------------------------


def subtract(u, v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 3 — scale
#
# Multiply every component by the number k and return the new list.
#   scale(3, [1, 2])   ->  [3, 6]
#   scale(-1, [1, 2])  ->  [-1, -2]
#
# Note what this does and does not change: a positive k changes the magnitude
# and leaves the direction alone; a negative k reverses the direction too.
# --------------------------------------------------------------------------


def scale(k, v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 4 — dot
#
# Multiply matching components, then add up the results. Return ONE NUMBER,
# not a list.
#   dot([1, 2, 3], [4, 5, 6])  ->  1*4 + 2*5 + 3*6 = 32
#
# Check your work on a case you can see: dot([1, 0], [0, 1]) must be 0,
# because those two arrows are at right angles.
# --------------------------------------------------------------------------


def dot(u, v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 5 — l2_norm  (the magnitude)
#
# Square every component, add the squares, take the square root.
#   l2_norm([3, 4])     ->  sqrt(9 + 16)      = sqrt(25) = 5
#   l2_norm([2, 3, 6])  ->  sqrt(4 + 9 + 36)  = sqrt(49) = 7
#
# Use math.sqrt, imported at the top of this file. This is Pythagoras, applied
# one dimension at a time, and it works in any number of dimensions.
# --------------------------------------------------------------------------


def l2_norm(v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 6 — l1_norm  (the taxicab length)
#
# Add up the absolute values of the components. No squaring, no square root.
#   l1_norm([3, 4])   ->  3 + 4 = 7
#   l1_norm([-3, 4])  ->  3 + 4 = 7
#
# The same vector has an L1 of 7 and an L2 of 5. Both are correct answers to
# "how big is this", and exercise 9 shows they can disagree about which of two
# candidates is nearer.
# --------------------------------------------------------------------------


def l1_norm(v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 7 — distance
#
# The distance between two vectors is the MAGNITUDE OF THEIR DIFFERENCE.
# There is no new formula. Subtract, then measure.
#   distance([1, 2], [4, 6])  ->  |[-3, -4]| = 5
#
# Write this in terms of the two functions you have already written.
# --------------------------------------------------------------------------


def distance(u, v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 8 — normalise
#
# Scale a vector so its magnitude becomes 1, keeping its direction.
# Dividing by the magnitude is the same as scaling by 1 / magnitude.
#   normalise([3, 4])  ->  [0.6, 0.8]
#
# The zero vector has magnitude 0 and no direction. Raise ValueError with a
# message containing the words "zero vector" rather than dividing by zero.
#
# WARNING, and it is the point of the exercise: the magnitude of your result
# will be 1 to within floating-point error and sometimes NOT exactly 1.0.
# Never test it with ==. The suite uses math.isclose, and so should you.
# --------------------------------------------------------------------------


def normalise(v):
    return None


# --------------------------------------------------------------------------
# EXERCISE 9 — nearest
#
# `labelled` is a dict of name -> vector. Return the (name, score) pair with
# the smallest `metric(query, vector)`.
#
#   nearest([9, 0, 1, 0], CATALOGUE, exclude="roast-chicken")
#       ->  ("slow-cooker-stew", 1.4142135623730951)
#
# `exclude` skips one label, which is what you want when the query is itself a
# member of the collection — otherwise everything's nearest neighbour is
# itself at distance 0, which is true and useless.
#
# `metric` defaults to `distance`, so calling nearest(..., metric=l1_distance)
# answers the same question under the other norm. Break ties by label so the
# answer is deterministic: min(candidates, key=lambda pair: (pair[1], pair[0])).
#
# Raise ValueError if there are no candidates left to compare against.
# --------------------------------------------------------------------------


def l1_distance(u, v):
    """Provided: the L1 version of exercise 7, once exercises 2 and 6 are done."""
    return l1_norm(subtract(u, v))


def nearest(query, labelled, *, metric=None, exclude=None):
    if metric is None:
        metric = distance
    return None


# --------------------------------------------------------------------------
# The catalogue the exercises are checked against. Six short articles, four
# hand-counted features: cooking, running, money, weather.
# --------------------------------------------------------------------------

FEATURES = ("cooking", "running", "money", "weather")

CATALOGUE = {
    "roast-chicken":      [9, 0, 1, 0],
    "slow-cooker-stew":   [8, 0, 2, 0],
    "marathon-plan":      [0, 9, 1, 2],
    "race-day-nutrition": [4, 6, 3, 0],
    "household-budget":   [1, 0, 9, 0],
    "storm-bulletin":     [0, 1, 0, 9],
}


# --------------------------------------------------------------------------
# Progress report — run this file directly to see it.
# --------------------------------------------------------------------------

EXERCISES = [
    (1, "add", lambda: add([1, 2, 3], [10, 20, 30])),
    (2, "subtract", lambda: subtract([4, 6], [1, 2])),
    (3, "scale", lambda: scale(3, [1, 2])),
    (4, "dot", lambda: dot([1, 2, 3], [4, 5, 6])),
    (5, "l2_norm", lambda: l2_norm([3, 4])),
    (6, "l1_norm", lambda: l1_norm([3, 4])),
    (7, "distance", lambda: distance([1, 2], [4, 6])),
    (8, "normalise", lambda: normalise([3, 4])),
    (9, "nearest", lambda: nearest([9, 0, 1, 0], CATALOGUE, exclude="roast-chicken")),
]


def main() -> int:
    print("Day 099 starter — Vectors You Can Hold")
    print()
    done = 0
    for number, name, probe in EXERCISES:
        try:
            result = probe()
        except Exception as exc:  # noqa: BLE001 - a partial answer is expected
            print(f"  {number}. {name:<12} raised {type(exc).__name__}: {exc}")
            continue
        if result is None:
            print(f"  {number}. {name:<12} not started")
        else:
            done += 1
            print(f"  {number}. {name:<12} returns {result!r}")
    print()
    print(f"{done} of {len(EXERCISES)} exercises return something.")
    if done < len(EXERCISES):
        print("Keep going, then run:  .venv/bin/pytest starter -q")
    else:
        print("All nine return a value. Now check them:  .venv/bin/pytest starter -q")
    print()
    print(f"(math.sqrt is already imported for you: math.sqrt(25) = {math.sqrt(25)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
