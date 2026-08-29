"""Exercise 2 -- twenty-five predictions. Replace each `None` with your answer.

These are not busy-work. Every one of them is a value you can work out on
paper, or a judgement the day turns on, and writing the answer down BEFORE you
run the code is the difference between reading a result and predicting one.

A `None` is SKIPPED by the test suite, not failed. Answer the ones you are
sure of, run the tests, then come back for the rest.

Numeric answers are compared with a tolerance of 1e-9 unless stated otherwise,
so `5` and `5.0` are both fine and you need not type more than four decimals
where four are asked for.

The data is in `catalogue.py`. Read it -- everything here refers to it.
"""

# -- The opening disagreement -------------------------------------------------
#
# QUERY   = (4, 3, 2, 1) over the terms (norm, distance, vector, cluster)
# Aisle     = (4, 3, 2, 6)
# Beacon    = (6, 1, 4, 1)
# Cartogram = (12, 9, 6, 3)

# 2.1  The L1 (Manhattan) distance from QUERY to Aisle.
L1_QUERY_TO_AISLE = None

# 2.2  The L1 distance from QUERY to Beacon.
L1_QUERY_TO_BEACON = None

# 2.3  The L2 (Euclidean) distance from QUERY to Aisle. It is a whole number.
L2_QUERY_TO_AISLE = None

# 2.4  The L-infinity (Chebyshev) distance from QUERY to Beacon.
LINF_QUERY_TO_BEACON = None

# 2.5  The cosine similarity between QUERY and Cartogram, to four decimals.
#      Look at the two vectors before you reach for a calculator.
COSINE_QUERY_TO_CARTOGRAM = None

# 2.6  Which article does L1 rank first? A string: "Aisle", "Beacon" or
#      "Cartogram".
L1_WINNER = None

# 2.7  Which article does L2 rank first?
L2_WINNER = None

# 2.8  Which article does cosine similarity rank first?
COSINE_WINNER = None

# -- The p-norm family --------------------------------------------------------

# 2.9  p_norm((3.0, 4.0), 1)
P_NORM_3_4_AT_1 = None

# 2.10 p_norm((3.0, 4.0), 2)
P_NORM_3_4_AT_2 = None

# 2.11 p_norm((3.0, 4.0), math.inf)
P_NORM_3_4_AT_INF = None

# 2.12 As p rises from 1 towards infinity, does the p-norm of a fixed vector
#      rise, fall, or stay the same? One of the strings "rise", "fall",
#      "stay the same".
P_NORM_AS_P_RISES = None

# 2.13 Which of the four norm axioms does SQUARED Euclidean distance break?
#      One of the strings "non-negativity", "zero only at zero",
#      "absolute homogeneity", "triangle inequality".
AXIOM_SQUARED_EUCLIDEAN_BREAKS = None

# -- Metrics ------------------------------------------------------------------

# 2.14 cosine_distance(EAST, NORTH), where EAST = (1, 0) and NORTH = (0, 1).
COSINE_DISTANCE_EAST_NORTH = None

# 2.15 Does the triangle inequality hold for cosine distance on the triple
#      EAST, DIAGONAL, NORTH? True or False.
COSINE_TRIANGLE_HOLDS = None

# 2.16 Is 1 - Jaccard similarity a metric? True or False.
JACCARD_DISTANCE_IS_A_METRIC = None

# -- Categorical and set data -------------------------------------------------

# 2.17 The Hamming distance from REFERENCE_RECORD to part-73, out of 6 fields.
HAMMING_REFERENCE_TO_PART_73 = None

# 2.18 The Hamming distance between FLAGS_A and FLAGS_B.
HAMMING_FLAGS = None

# 2.19 Which recipe does JACCARD similarity prefer? "Sachertorte" or
#      "Shortbread".
JACCARD_RECIPE_WINNER = None

# 2.20 Which recipe does COSINE similarity prefer, on the same two sets?
COSINE_RECIPE_WINNER = None

# -- Mahalanobis --------------------------------------------------------------

# 2.21 The population covariance matrix of SENSOR_READINGS, as a list of lists.
#      Every entry is a clean number; work it out rather than guessing.
COVARIANCE_OF_READINGS = None

# 2.22 Are PROBE_ALONG and PROBE_ACROSS the same Euclidean distance from the
#      mean of SENSOR_READINGS? True or False.
PROBES_EQUIDISTANT_UNDER_EUCLIDEAN = None

# 2.23 The Mahalanobis distance from the mean to PROBE_ACROSS = (3, -3).
#      It is a whole number.
MAHALANOBIS_TO_PROBE_ACROSS = None

# -- Scaling ------------------------------------------------------------------

# 2.24 Which bearing wins on the RAW numbers, bore in metres and mass in
#      grams? A single letter as a string.
RAW_BEARING_WINNER = None

# 2.25 Which bearing wins after both columns are standardised?
STANDARDISED_BEARING_WINNER = None
