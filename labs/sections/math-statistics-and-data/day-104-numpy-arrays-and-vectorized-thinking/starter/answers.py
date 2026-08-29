"""Exercises 2 to 7 -- your predictions. Work them out BEFORE running anything.

Nearly all of these can be done on paper or in your head. That is deliberate:
a lab about NumPy whose answers you cannot check by hand is a lab that teaches
you to trust output.

Replace each `None` with your answer. Anything still `None` is SKIPPED by the
test suite rather than failed, so your score only ever counts work you actually
attempted.

Check yourself from the LAB DIRECTORY:

    .venv/bin/pytest starter -q
"""

# Imported for you: exercise 5.1 asks for an exception CLASS, and several
# answers are dtypes or NumPy values.
import numpy


# =============================================================================
# Exercise 2 -- what an array actually is
# =============================================================================

# 2.1 A list of one million Python integers and an int64 array of the same
#     million numbers. Roughly how many times more memory does the LIST use,
#     counting the integer objects it points at as well as its own pointers?
#     Answer with a float. The lab measures 4.5 on this machine; you are being
#     asked whether you expect roughly 1, roughly 4.5, or roughly 100.
LIST_TO_ARRAY_MEMORY_RATIO = None

# 2.2 How many bytes is one Python int on CPython 3.14, as sys.getsizeof
#     reports it? An integer.
BYTES_PER_PYTHON_INT = None

# 2.3 How many bytes is one element of an int64 array? An integer.
BYTES_PER_INT64_ELEMENT = None

# 2.4 sys.getsizeof(list(range(1_000_000))) comes out at 8,000,056 -- almost
#     exactly the same as the array's 8,000,000. Why does that number NOT show
#     that a list is as compact as an array?
#     Answer with one of these strings:
#       "the list is genuinely as compact"
#       "getsizeof measures only the pointers, not the integers"
#       "getsizeof is inaccurate for large objects"
WHY_GETSIZEOF_MISLEADS = None

# 2.5 np.arange(12).reshape(3, 4) has int64 elements. What are its strides, as
#     a tuple of two integers? Think: how many BYTES do you skip to move one
#     row down, and how many to move one column across?
STRIDES_OF_A_THREE_BY_FOUR = None

# 2.6 Does transposing that array copy any data? True or False.
TRANSPOSE_COPIES_DATA = None


# =============================================================================
# Exercise 3 -- dtypes
# =============================================================================

# 3.1 np.array([127], dtype=np.int8) + np.array([1], dtype=np.int8)
#     What is the single value that comes out? An integer.
INT8_127_PLUS_1 = None

# 3.2 Does that raise an exception? True or False.
INT8_OVERFLOW_RAISES = None

# 3.3 Does it emit a warning on numpy 2.5.2? True or False.
INT8_OVERFLOW_WARNS = None

# 3.4 np.array([120, 125, 127], dtype=np.int8) * np.int8(2)
#     Give all three values, as a list of three integers.
INT8_DOUBLED = None

# 3.5 np.array([127], dtype=np.int8) + 1  -- note the plain Python 1 this time.
#     What DTYPE does the result have? Give the numpy dtype itself, for
#     example numpy.int16, not the string "int16".
DTYPE_OF_INT8_PLUS_PYTHON_INT = None

# 3.6 A float32 has 24 bits of significand, so above 2 ** 24 the gap between
#     representable values is at least 1. Is np.float32(16777216.0) + 1 equal
#     to np.float32(16777216.0)? True or False.
FLOAT32_CANNOT_ADD_ONE = None

# 3.7 np.full(3, 7) -- what dtype? np.full(3, 7.0) -- what dtype?
#     A tuple of two numpy dtypes, for example (numpy.int8, numpy.float32).
DTYPES_OF_FULL = None


# =============================================================================
# Exercise 4 -- masking
# =============================================================================
#
# The twenty readings are in dataset.py, both as a seeded generator and
# written out as SMALL_READINGS_EXPECTED so you can count by eye:
#
#   [70, 83, 34, 69, 26, 21, 18, 12, 65, 37,
#    17, 75, 30, 73, 37, 41, 97, 64, 21, 82]

# 4.1 How many are strictly greater than 50? An integer.
COUNT_ABOVE_50 = None

# 4.2 Which ones? A list of integers, in the order they appear in the data.
VALUES_ABOVE_50 = None

# 4.3 (readings > 30) & (readings < 70) -- how many? An integer.
COUNT_BETWEEN_30_AND_70 = None

# 4.4 What is the SHAPE of `readings > 50`? A tuple.
SHAPE_OF_A_MASK = None

# 4.5 What is the DTYPE of `readings > 50`? A numpy dtype, e.g. numpy.int64.
DTYPE_OF_A_MASK = None

# 4.6 (readings > 30) and (readings < 70) -- with the keyword rather than the
#     operator. Name the exception CLASS this raises. Give the class itself,
#     not a string. It is a builtin.
EXCEPTION_FROM_KEYWORD_AND = None

# 4.7 Why does `and` fail where `&` works? One of these strings:
#       "NumPy forgot to implement it"
#       "and is a keyword, so it asks the array for a single True or False"
#       "and only works on lists"
WHY_AND_FAILS = None

# 4.8 mask.mean() on `readings > 50`, where mask has 9 Trues out of 20.
#     A float.
MEAN_OF_THE_MASK = None

# 4.9 readings[[0, 5, 19, 5]] -- fancy indexing, and note the repeat.
#     A list of four integers.
FANCY_INDEX_RESULT = None


# =============================================================================
# Exercise 5 -- axes, views and copies
# =============================================================================

# 5.1 np.arange(12).reshape(3, 4).sum(axis=0) -- what SHAPE comes out?
#     A tuple. The rule: the axis you name is the one that disappears.
SHAPE_AFTER_SUM_AXIS_0 = None

# 5.2 And .sum(axis=1)? A tuple.
SHAPE_AFTER_SUM_AXIS_1 = None

# 5.3 .sum(axis=1) on that array -- the three values, as a list of integers.
VALUES_OF_SUM_AXIS_1 = None

# 5.4 v = np.array([1.0, 2.0, 3.0]). What shape is v[:, np.newaxis]? A tuple.
SHAPE_OF_A_COLUMN = None

# 5.5 grid = np.arange(12).reshape(3, 4); row = grid[1]; row[0] = 999
#     What is grid[1, 0] afterwards? An integer.
GRID_AFTER_WRITING_THROUGH_A_SLICE = None

# 5.6 Same again, but with `row = grid[1].copy()`. An integer.
GRID_AFTER_WRITING_THROUGH_A_COPY = None

# 5.7 Which of these share memory with the array they came from? Answer with a
#     list of the labels that DO, in this order, as strings:
#       "row slice", "column slice", "transpose", "reshape",
#       "boolean mask", "fancy index"
#     For example: ["row slice", "reshape"]
WHICH_ARE_VIEWS = None

# 5.8 grid.ravel() and grid.flatten() both give you a flat array. One is a
#     view when it can be and one is always a copy. Which is always a copy?
#     The string "ravel" or the string "flatten".
ALWAYS_A_COPY = None


# =============================================================================
# Exercise 6 -- sorting, ranking and speed
# =============================================================================

# 6.1 scores = np.array([5.0, 1.0, 9.0, 3.0]). What is np.argsort(scores)?
#     A list of four integers.
ARGSORT_OF_THE_SCORES = None

# 6.2 Does `np.sort(scores)` change `scores` itself? True or False.
NP_SORT_MUTATES = None

# 6.3 Does the METHOD `scores.sort()` change `scores` itself? True or False.
SORT_METHOD_MUTATES = None

# 6.4 The lab computes the square root of a million values three ways:
#     math.sqrt in a loop, x ** 0.5 in a loop, and np.sqrt on the array.
#     Two of the three agree bit for bit. Which one is the odd one out?
#     One of these strings: "math.sqrt", "x ** 0.5", "np.sqrt"
THE_ODD_ONE_OUT = None

# 6.5 Roughly how much faster is the vectorised version than the loop, on a
#     million elements? Not the exact figure -- the ORDER OF MAGNITUDE.
#     One of these strings: "about the same", "about 2x", "about 100x"
ROUGH_SPEEDUP = None

# 6.6 On an array of FOUR elements, which is faster: the list comprehension or
#     the NumPy call? One of these strings: "comprehension", "numpy"
FASTER_ON_FOUR_ELEMENTS = None


# =============================================================================
# Exercise 7 -- nan
# =============================================================================

# 7.1 np.nan == np.nan -- True or False.
NAN_EQUALS_ITSELF = None

# 7.2 a = np.array([1.0, 2.0, np.nan, 4.0]). How many elements does the mask
#     `a == np.nan` mark as True? An integer.
COUNT_FROM_COMPARING_TO_NAN = None

# 7.3 And np.isnan(a).sum()? An integer.
COUNT_FROM_ISNAN = None

# 7.4 What does a.mean() return for that array? Answer with the string "nan"
#     if it returns nan, or with the float if it returns a number.
MEAN_OF_THE_HOLED_ARRAY = None

# 7.5 And np.nanmean(a)? A float. Work out the arithmetic first: it is the
#     mean of the values that are actually there.
NANMEAN_OF_THE_HOLED_ARRAY = None

# 7.6 Is a.mean() returning nan a bug in NumPy? True or False, and think about
#     what the alternative would mean for a reading that was never taken.
NAN_PROPAGATION_IS_A_BUG = None
