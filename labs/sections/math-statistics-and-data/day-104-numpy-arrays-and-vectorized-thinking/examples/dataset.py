"""The data this lab measures, and the tolerances it compares with.

Three kinds of data live here, and each is here for a different reason.

1. A **big** array of a million numbers, drawn from a seeded generator. It
   exists so the memory and speed measurements have something to bite on. A
   thousand elements would make the loop look fine.

2. A **small** array of twenty integers, drawn from the same seeded generator.
   It exists so every boolean mask in this lab can be checked by eye. You can
   read the twenty numbers, count the ones above fifty, and compare with what
   the code says.

3. The **article catalogue from Day 99 and Day 103**, unchanged. Six invented
   articles described by four hand-counted features. Day 103 ranked them by
   cosine similarity; today the ranking is done with `argsort`, which is the
   part of that day that transfers directly to model code.

Nothing here is real. The articles do not exist, the sensor readings are not
sensor readings, and the counts were chosen so that every number in this lab
can be re-derived with a pen.

The seed is fixed at 104 and every number below follows from it, so two runs of
this lab on two machines produce the same values. That is a deliberate choice
rather than a convenience: a lab that asserts on random numbers is a lab that
fails for the reader and not for the author.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Seeds and sizes
# ---------------------------------------------------------------------------

#: The one seed this lab uses. Passed to numpy.random.default_rng.
SEED = 104

#: How many elements the timing and memory comparisons use. One million is
#: large enough that the loop is unmistakably slower and small enough that the
#: array is 8 MB rather than 8 GB.
N_BIG = 1_000_000

#: How many elements the by-eye mask exercises use.
N_SMALL = 20

#: Float comparison tolerance, used wherever two routes to the same number are
#: allowed to differ in the last bits. Most comparisons in this lab do NOT use
#: it: the whole point of the from-scratch section is that the loop and the
#: vectorised version agree EXACTLY, and asserting that with a tolerance would
#: hide the very fact being demonstrated.
TOL = 1e-12


def big_values() -> np.ndarray:
    """A million float64 values in [0, 1), from the fixed seed.

    Returns a fresh array each call so that a test which mutates it cannot
    quietly change the answer of a later one.
    """
    return np.random.default_rng(SEED).random(N_BIG)


def small_readings() -> np.ndarray:
    """Twenty integers in [0, 100), from the fixed seed.

    Drawn from a generator seeded independently of `big_values`, so the two
    are reproducible on their own.
    """
    return np.random.default_rng(SEED).integers(0, 100, size=N_SMALL)


# The literal values `small_readings()` produces on the fixed seed, written out
# so you can check a mask against them without running anything. The reference
# tests assert that this list and the generator still agree; if a future NumPy
# ever changed the generator's output, the suite would say so rather than
# quietly rewriting the lesson.
SMALL_READINGS_EXPECTED = [
    70, 83, 34, 69, 26, 21, 18, 12, 65, 37,
    17, 75, 30, 73, 37, 41, 97, 64, 21, 82,
]

# ---------------------------------------------------------------------------
# The article catalogue, carried unchanged from Day 99 and Day 103
# ---------------------------------------------------------------------------

FEATURES = ("cooking", "running", "money", "weather")

ARTICLE_NAMES = (
    "roast-chicken",
    "slow-cooker-stew",
    "marathon-plan",
    "race-day-nutrition",
    "household-budget",
    "storm-bulletin",
)

#: One row per article, one column per feature, in the order above. Day 103
#: held these as six separate lists; today they are one 6 by 4 array, and that
#: change is the day's subject rather than a tidy-up.
CATALOGUE = np.array(
    [
        [9, 0, 1, 0],   # roast-chicken
        [8, 0, 2, 0],   # slow-cooker-stew
        [0, 9, 1, 2],   # marathon-plan
        [4, 6, 3, 0],   # race-day-nutrition
        [1, 0, 9, 0],   # household-budget
        [0, 1, 0, 9],   # storm-bulletin
    ],
    dtype=np.float64,
)

#: "training for a race and what to eat", written as feature counts the same
#: way the articles were. Deliberately a close call between two articles.
QUERY = np.array([2, 5, 0, 0], dtype=np.float64)

#: How many results the search returns.
TOP_K = 3

# ---------------------------------------------------------------------------
# The three operations implemented twice
# ---------------------------------------------------------------------------
#
# The multiplier, offset and clip bounds are all exactly representable in
# binary floating point (2.5 is 10.1 in binary, 1.25 is 1.01, 0.25 is 0.01,
# 0.75 is 0.11). That matters: it means the loop and the vectorised version
# perform the identical IEEE-754 operation on the identical bits, so they can
# be compared with `==` rather than with a tolerance.

SCALE_M = 2.5
SCALE_C = 1.25
CLIP_LO = 0.25
CLIP_HI = 0.75

# ---------------------------------------------------------------------------
# The dtype demonstrations
# ---------------------------------------------------------------------------

#: The largest value an int8 can hold. Adding 1 to this wraps to INT8_MIN.
INT8_MAX = 127
INT8_MIN = -128

#: Three int8 values doubled in section 2. Two of the three wrap.
INT8_DOUBLING_INPUT = [120, 125, 127]

#: A value float32 cannot tell apart from its successor: 2 ** 24. A float32
#: has 24 bits of significand, so at this magnitude the gap between
#: representable numbers is exactly 1, and adding 1 changes nothing.
FLOAT32_BLIND_SPOT = 16777216.0

# ---------------------------------------------------------------------------
# The array with a hole in it
# ---------------------------------------------------------------------------

#: Four readings, one of which is missing. `mean` on this returns nan; the
#: whole point of section 7 is that the nan is contagious and that saying so
#: loudly is better than silently dropping it.
WITH_A_HOLE = np.array([1.0, 2.0, np.nan, 4.0])
