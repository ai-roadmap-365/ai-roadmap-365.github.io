"""The data this lab argues over. Written by hand, on purpose.

Nothing here is downloaded and nothing here is random. Every number is small
enough to check on paper, and each dataset was chosen because it makes exactly
one measure look right and the others look wrong -- which is the point of the
day.

There IS a seeded random generator in this lab, in
`06_scaling_changes_the_answer.py`, used to show that the scaling effect is not
a property of these six hand-picked parts. It is seeded with
`numpy.random.default_rng(107)` and every claim made about it is structural (a
count, a direction, a percentage floor) rather than a specific digit, because
NumPy does not promise that a generator's exact stream survives a version
change. Everything asserted to the last decimal place in this lab comes from the
literal tables below.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. The opening disagreement: three articles, one query, three winners.
# ---------------------------------------------------------------------------
#
# A tiny help-centre search. Each article is counted over four terms, and the
# query is the reader's own short note. Raw counts, not frequencies -- which is
# exactly what makes the three measures disagree.

TERMS = ("norm", "distance", "vector", "cluster")

QUERY = (4, 3, 2, 1)

# "Aisle" mentions cluster six times where the query mentions it once, and
# matches the other three terms exactly. One big disagreement, nothing else.
#
# "Beacon" is a little off on three of the four terms and exact on the fourth.
# Three small disagreements adding to more in total than Aisle's single one.
#
# "Cartogram" is the query's profile at exactly three times the length: a long
# article on precisely this topic. Its direction is identical, so its cosine
# similarity is exactly 1.0, and its raw counts are further away than anything
# else here.
ARTICLES: dict[str, tuple[int, ...]] = {
    "Aisle": (4, 3, 2, 6),
    "Beacon": (6, 1, 4, 1),
    "Cartogram": (12, 9, 6, 3),
}

# ---------------------------------------------------------------------------
# 2. Chebyshev, and where a single worst component decides.
# ---------------------------------------------------------------------------
#
# One displacement, in metres, across a warehouse floor laid out on aisles.
# The same two points, three operationally different answers:
#
#   L1  = 14  a picker who must walk the aisles, one axis at a time
#   L2  = 10  a drone that can fly the diagonal
#   Linf = 8  a two-axis gantry whose motors run at once, so the slower axis
#             alone sets the finishing time
#
# None of the three is the "real" distance. Each is the real distance for a
# different machine.

FLOOR_FROM = (0.0, 0.0)
FLOOR_TO = (6.0, 8.0)

# A machined part and its nominal dimensions, in millimetres. The part is
# rejected if ANY dimension is out by more than the tolerance -- which is a
# Chebyshev ball, and nothing else.
NOMINAL_PART = (40.00, 25.00, 12.00, 6.00)
PART_TOLERANCE_MM = 0.05
MEASURED_PARTS: dict[str, tuple[float, ...]] = {
    # Four dimensions each a little out. Total error is large, worst is small.
    "batch-A": (40.04, 24.96, 12.04, 5.96),
    # Three dimensions perfect, one badly out. Total error is smaller.
    "batch-B": (40.00, 25.00, 12.00, 6.09),
}

# ---------------------------------------------------------------------------
# 3. Hamming, for data with no arithmetic in it.
# ---------------------------------------------------------------------------
#
# Six categorical fields from a parts register. Subtracting "steel" from
# "brass" is not a smaller number than subtracting "steel" from "nylon"; it is
# not a number at all. Hamming counts the fields that differ and refuses to
# invent an ordering.

FIELDS = ("material", "finish", "thread", "grade", "colour", "origin")

REFERENCE_RECORD = ("steel", "zinc", "M8", "8.8", "silver", "IN")
CANDIDATE_RECORDS: dict[str, tuple[str, ...]] = {
    "part-71": ("steel", "zinc", "M8", "8.8", "black", "IN"),
    "part-72": ("brass", "zinc", "M8", "10.9", "silver", "DE"),
    "part-73": ("nylon", "plain", "M6", "4.6", "white", "CN"),
}

# The same measure on bits, which is where Hamming was defined: two 8-bit
# feature flags from the same register.
FLAGS_A = (1, 0, 1, 1, 0, 0, 1, 0)
FLAGS_B = (1, 0, 0, 1, 0, 1, 1, 0)

# ---------------------------------------------------------------------------
# 4. Jaccard against cosine on the same set-like data.
# ---------------------------------------------------------------------------
#
# Ingredient lists. The query has four ingredients.
#
#   "Sachertorte" contains ALL FOUR of them, plus seven more.
#   "Shortbread"  shares two of the four and has one ingredient of its own.
#
# Cosine, which divides by the square root of the two sizes, prefers
# Sachertorte: everything asked for is present. Jaccard, which counts the union
# in the denominator, prefers Shortbread: Sachertorte's seven extra ingredients
# are seven things the two recipes do not share, and Jaccard charges for them.
#
# Neither is wrong. They answer different questions -- "is what I asked for
# there?" against "how much of everything involved is shared?" -- and the day's
# job is to notice that you have to pick one.

RECIPE_QUERY = frozenset({"flour", "butter", "sugar", "egg"})
RECIPES: dict[str, frozenset[str]] = {
    "Sachertorte": frozenset({
        "flour", "butter", "sugar", "egg",
        "cocoa", "apricot jam", "chocolate", "vanilla",
        "salt", "milk", "almond",
    }),
    "Shortbread": frozenset({"flour", "butter", "cornflour"}),
}

# ---------------------------------------------------------------------------
# 5. Mahalanobis: Euclidean after accounting for how the data actually varies.
# ---------------------------------------------------------------------------
#
# Eight readings of two sensors that move together almost perfectly. The mean
# is exactly (0, 0) and the population covariance comes out exactly
#
#     [[7.5, 7.0],
#      [7.0, 7.5]]
#
# whose determinant is exactly 7.25. The data lies along the line y = x: that
# is the grain of it, and Day 106's eigenvectors of this matrix are what name
# that direction.
#
# The two probe points are the same Euclidean distance from the mean -- both
# sqrt(18) = 4.2426... -- and nothing about ordinary distance can tell them
# apart. Mahalanobis can: ALONG the grain is cheap, ACROSS it is expensive.

SENSOR_READINGS: tuple[tuple[float, float], ...] = (
    (-4.0, -3.0),
    (-3.0, -4.0),
    (-2.0, -1.0),
    (-1.0, -2.0),
    (1.0, 2.0),
    (2.0, 1.0),
    (3.0, 4.0),
    (4.0, 3.0),
)

# Along the grain of the data: both sensors high together, which is what this
# pair of sensors does all day.
PROBE_ALONG = (3.0, 3.0)
# Across the grain: one sensor high while the other is low, which never happens
# in the eight readings above. Same Euclidean distance. Not the same event.
PROBE_ACROSS = (3.0, -3.0)

# ---------------------------------------------------------------------------
# 6. The scaling demonstration: the thing that silently decides your answer.
# ---------------------------------------------------------------------------
#
# A bearing catalogue with two features recorded in the units the supplier
# happened to use: bore diameter in METRES and mass in GRAMS. The numbers in
# one column are around 0.02 and in the other around 350, so squared
# differences in the second column are roughly ten million times larger. The
# bore column does not lose the argument. It never enters it.

BEARING_FEATURES = ("bore diameter (m)", "mass (g)")

BEARING_QUERY = (0.020, 300.0)

BEARINGS: dict[str, tuple[float, float]] = {
    # Bore matches the query EXACTLY. 40 g heavier.
    "P": (0.020, 340.0),
    # Bore is 12 mm too big -- 60 per cent out, and unusable. Mass is 2 g off.
    "R": (0.032, 302.0),
    "S": (0.008, 250.0),
    "T": (0.026, 410.0),
    "U": (0.014, 275.0),
    "V": (0.038, 500.0),
}

# ---------------------------------------------------------------------------
# 7. The counter-example that shows cosine distance is not a metric.
# ---------------------------------------------------------------------------
#
# Day 103 proved this. It is restated here rather than re-derived, because a
# concrete triple is worth more than the proof once you have seen the proof.
#
#   cosine_distance(EAST, DIAGONAL) + cosine_distance(DIAGONAL, NORTH)
#     = 0.2929 + 0.2929 = 0.5858
#   cosine_distance(EAST, NORTH)
#     = 1.0
#
# The direct route is longer than going via a third point, which no metric may
# ever allow.

EAST = (1.0, 0.0)
DIAGONAL = (1.0, 1.0)
NORTH = (0.0, 1.0)

# The triple used for the POSITIVE side of the same check: L1, L2 and
# L-infinity must all satisfy the triangle inequality on every triple, and
# these three vectors are checked exhaustively in all six orderings.
TRIANGLE_TRIPLE = ((1.0, 7.0, 2.0), (4.0, 1.0, 9.0), (-2.0, 3.0, 3.0))

# The single vector every norm axiom is checked on, and the scalar it is
# multiplied by for absolute homogeneity.
AXIOM_VECTOR = (3.0, -4.0, 12.0)
AXIOM_SCALAR = -2.5
