"""Exercises 2 to 6 — predict first, then let the arithmetic tell you.

Every value below is a prediction you make BEFORE running anything. Replace
each `None` with your answer, then check from the lab directory:

    .venv/bin/pytest starter -q

Each prediction still set to None is SKIPPED rather than failed, so the run is
a running score. A wrong prediction fails with both numbers printed.

Predicting first matters here more than usual, because the whole day is about
two measures that feel like they should agree and do not. The only way to find
out whether your intuition is right is to commit to an answer while it can
still be wrong.

The data everything below refers to — the same six invented articles as Day 99,
described by how often each one talks about four things:

                        cooking  running  money  weather
    roast-chicken             9        0      1        0
    slow-cooker-stew          8        0      2        0
    marathon-plan             0        9      1        2
    race-day-nutrition        4        6      3        0
    household-budget          1        0      9        0
    storm-bulletin            0        1      0        9

and one more: roast-chicken written at twice the length, every count doubled,

    roast-chicken (2x)       18        0      2        0

Float answers are compared with a tolerance of 1e-6, so four decimal places is
plenty. Where a whole number is exact, give the whole number.
"""

# ---------------------------------------------------------------------------
# Exercise 2 — the length confound
# ---------------------------------------------------------------------------

# 2.1 The Euclidean distance between roast-chicken and its doubled copy.
#     Work it out on paper: subtract, square, add, square-root.
#     [9, 0, 1, 0] - [18, 0, 2, 0] = ?
DISTANCE_TO_DOUBLED_COPY = None

# 2.2 The Euclidean distance between roast-chicken and race-day-nutrition.
DISTANCE_TO_RACE_DAY = None

# 2.3 Given those two numbers: does Euclidean distance place the doubled copy
#     of roast-chicken FURTHER from roast-chicken than race-day-nutrition is?
#     True or False.
DOUBLED_COPY_IS_FURTHER = None

# 2.4 The cosine similarity between roast-chicken and its doubled copy.
#     You should be able to answer this one without any arithmetic at all.
COSINE_TO_DOUBLED_COPY = None

# 2.5 There is a tidy general fact behind 2.1. For any vector v, the distance
#     between v and 2v equals one of the following. Which? Answer with the
#     string exactly as written: "0", "|v|", "2|v|", or "|v| squared".
DISTANCE_BETWEEN_V_AND_2V = None


# ---------------------------------------------------------------------------
# Exercise 3 — the sign of the dot product
# ---------------------------------------------------------------------------

# 3.1 [3, 0] dot [6, 0] — a single number.
DOT_SAME_DIRECTION = None

# 3.2 [3, 0] dot [0, 5].
DOT_PERPENDICULAR = None

# 3.3 [3, 0] dot [-6, 0].
DOT_OPPOSITE = None

# 3.4 The angle in degrees between [3, 0] and [1, 1]. A whole number.
ANGLE_45_CASE = None

# 3.5 Which articles in the table above have a dot product of exactly 0 with
#     storm-bulletin? A dot product of 0 means the two share no vocabulary at
#     all — wherever one has a count, the other has none. Answer with a list
#     of the article names, sorted alphabetically. (There is more than one.)
ORTHOGONAL_TO_STORM_BULLETIN = None


# ---------------------------------------------------------------------------
# Exercise 4 — cosine distance is not a metric
# ---------------------------------------------------------------------------
#
# Three vectors in two dimensions:
#
#     a = [1, 0]      b = [1, 1]      c = [0, 1]
#

# 4.1 The cosine distance from a to b, to four decimal places.
D_A_TO_B = None

# 4.2 The cosine distance from a to c.
D_A_TO_C = None

# 4.3 The triangle inequality says d(a, c) <= d(a, b) + d(b, c). Does it hold
#     for these three under COSINE distance? True or False.
TRIANGLE_HOLDS_FOR_COSINE = None

# 4.4 Does it hold for the same three under EUCLIDEAN distance? True or False.
TRIANGLE_HOLDS_FOR_EUCLIDEAN = None


# ---------------------------------------------------------------------------
# Exercise 5 — the same ranking on the unit sphere
# ---------------------------------------------------------------------------
#
# For two UNIT vectors u and v:
#
#     |u - v|^2 = (u - v) dot (u - v)
#               = (u dot u) - 2 (u dot v) + (v dot v)
#               = 1 - 2 cos(theta) + 1
#

# 5.1 Complete the identity. The Euclidean distance between two unit vectors
#     equals sqrt of what expression in cos? Answer with the string exactly as
#     written: "2 - 2cos", "1 - cos", "2 + 2cos", or "1 - 2cos".
UNIT_DISTANCE_FORMULA = None

# 5.2 Two unit vectors at 90 degrees. How far apart are they, to four decimal
#     places?
DISTANCE_BETWEEN_PERPENDICULAR_UNIT_VECTORS = None

# 5.3 Two unit vectors pointing in opposite directions. How far apart?
DISTANCE_BETWEEN_OPPOSITE_UNIT_VECTORS = None

# 5.4 Rank the catalogue against a normalised roast-chicken, once by cosine
#     similarity descending and once by Euclidean distance ascending. Are the
#     two orderings identical? True or False.
NORMALISED_RANKINGS_MATCH = None

# 5.5 Do the same on the RAW vectors, with the doubled copy included in the
#     catalogue. Are those two orderings identical? True or False.
RAW_RANKINGS_MATCH = None


# ---------------------------------------------------------------------------
# Exercise 6 — the search, and the curse
# ---------------------------------------------------------------------------

# 6.1 The query "roast it" becomes [1, 0, 0, 0]. Which article does cosine
#     similarity rank first? A string, exactly as spelled in the table.
TOP_HIT_FOR_ROAST_IT = None

# 6.2 The same query, ranked by RAW Euclidean distance instead. Which article
#     comes first? (Day 99 answered this one; it is not the same answer.)
NEAREST_BY_RAW_EUCLIDEAN_FOR_ROAST_IT = None

# 6.3 The query "training for a race and what to eat" becomes [2, 5, 0, 0].
#     Which article does cosine rank first?
TOP_HIT_FOR_TRAINING = None

# 6.4 Multiply that query by 100, giving [200, 500, 0, 0]. Does the cosine
#     ranking change? True or False.
SCALING_THE_QUERY_CHANGES_THE_RANKING = None

# 6.5 Two random vectors in a high-dimensional space. As the number of
#     dimensions grows, the average absolute cosine similarity between them
#     tends towards which value? Answer with a number: 0, 0.5, or 1.
MEAN_ABS_COSINE_TENDS_TOWARDS = None
