"""The Day 99 article set, unchanged, plus the queries this lab asks of it.

Six short invented articles, each described by four hand-counted features: how
many times the article talks about cooking, about running, about money, and
about weather. Day 99 used exactly these numbers to introduce vectors, norms
and Euclidean distance. Today they answer a better question, and the fact that
the data has not changed is the point — the measure changed, and that was
enough to change every answer.

Nothing here is real. The articles do not exist and the counts were chosen by
hand so that every number in this lab can be re-derived with a pen.
"""

from __future__ import annotations

FEATURES = ("cooking", "running", "money", "weather")

CATALOGUE = {
    "roast-chicken":      [9, 0, 1, 0],
    "slow-cooker-stew":   [8, 0, 2, 0],
    "marathon-plan":      [0, 9, 1, 2],
    "race-day-nutrition": [4, 6, 3, 0],
    "household-budget":   [1, 0, 9, 0],
    "storm-bulletin":     [0, 1, 0, 9],
}

# The same article, written at twice the length: every count doubled. Same
# subject, same emphasis, twice as many words. This is the vector that breaks
# Euclidean distance in section 1.
LONG_ROAST_CHICKEN = [18, 0, 2, 0]

# Two queries, written as feature counts the same way the articles were.
QUERIES = {
    # A one-line cooking note: "roast it".
    "roast it": [1, 0, 0, 0],
    # "training for a race and what to eat" — two counts for cooking, five for
    # running. Deliberately a close call between two articles; the lab reports
    # the margin rather than pretending the winner was obvious.
    "training for a race and what to eat": [2, 5, 0, 0],
}

# Three vectors whose cosine distances break the triangle inequality. Chosen so
# every number is exact on paper: two axis vectors and the bisector between
# them.
TRIANGLE_A = [1, 0]
TRIANGLE_B = [1, 1]
TRIANGLE_C = [0, 1]

# The sign cases. Each pair is (label, a, b, expected sign of a dot b), with
# `a` fixed so only the second vector's direction changes.
SIGN_CASES = (
    ("same direction",     [3, 0], [6, 0],   "positive"),
    ("45 degrees apart",   [3, 0], [1, 1],   "positive"),
    ("perpendicular",      [3, 0], [0, 5],   "zero"),
    ("135 degrees apart",  [3, 0], [-2, 2],  "negative"),
    ("opposite direction", [3, 0], [-6, 0],  "negative"),
)

# The projection picture: a 3-4-5 triangle, so the arithmetic is exact.
PROJECTION_A = [3, 4]   # length 5
PROJECTION_B = [10, 0]  # length 10
