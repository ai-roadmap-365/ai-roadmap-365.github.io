"""Exercises 2 to 6 — predictions. Replace each None with your answer.

The rule that makes this worth doing: WRITE THE ANSWER DOWN BEFORE YOU RUN
ANYTHING. A prediction you check is worth ten outputs you read. If you run the
code first and then fill these in, every one will be right and you will have
learned nothing.

Anything still `None` is reported as SKIPPED, not failed. A failure means you
committed to an answer and it was wrong, and the failure prints both numbers.

All the matrices referred to here are defined at the top of test_starter.py and
repeated in 00_brief.md, so you never have to guess what X or W is.
"""

# ===========================================================================
# EXERCISE 2 — the shape rule
#
#   X is (2, 3)      W is (3, 2)      P and Q are both (2, 2)
#
# For each expression, give the SHAPE of the result as a tuple, or the string
# "error" if it raises. Work them out from the rule, not from memory:
# an (m, n) @ (n, p) is legal only when the inner dimensions agree, and the
# result is (m, p).
# ===========================================================================

SHAPE_OF_X_AT_W = None  # e.g. (2, 2) or "error"
SHAPE_OF_W_AT_X = None
SHAPE_OF_X_AT_X = None
SHAPE_OF_X_AT_X_T = None  # X @ X.T
SHAPE_OF_X_T_AT_X = None  # X.T @ X
SHAPE_OF_P_AT_Q = None

# X is (2, 3) and u is the length-3 vector [10, 2, 5]. What shape is X @ u?
# Careful: u is one-dimensional, so the answer is not a pair.
SHAPE_OF_X_AT_U = None

# Which exception class does NumPy raise for X @ X? Give the CLASS itself,
# not its name as a string — e.g. TypeError, not "TypeError".
SHAPE_ERROR_EXCEPTION = None


# ===========================================================================
# EXERCISE 3 — composition and order
#
#   A = ROT90  = [[0, -1], [1, 0]]    a quarter turn anticlockwise
#   B = FLIP_X = [[1,  0], [0, -1]]   a reflection in the horizontal axis
#   v = [3, 1]
#
# Do these with a pen. Each one is four multiplications and two additions.
# ===========================================================================

# Apply B to v. (Reflection in the horizontal axis flips the sign of y.)
B_TIMES_V = None  # a list of two numbers

# Now apply A to THAT result — so this is A @ (B @ v).
A_TIMES_B_TIMES_V = None

# The single matrix A @ B, worked out entry by entry.
A_AT_B = None  # a list of two lists

# And B @ A, the other order.
B_AT_A = None

# Does (A @ B) @ v land in the same place as A @ (B @ v)? True or False.
COMPOSITION_MATCHES = None

# Does A @ B equal B @ A? True or False.
ORDER_DOES_NOT_MATTER = None

# In the expression A @ B @ v, which matrix meets the vector first?
# Answer with the string "A" or the string "B".
WHICH_ACTS_FIRST = None


# ===========================================================================
# EXERCISE 4 — `*` against `@`
#
#   P = [[1, 2], [3, 4]]     Q = [[5, 6], [7, 8]]
#   X = [[1, 2, 0], [0, 1, 3]]      u = [10, 2, 5]
# ===========================================================================

# P * Q — entry by entry, nothing summed.
P_STAR_Q = None  # a list of two lists

# P @ Q — rows dotted with columns.
P_AT_Q = None

# Are those two the same SHAPE? True or False. (Think before you answer: this
# is the reason the `*` versus `@` mistake survives so long in real code.)
P_STAR_AND_AT_SAME_SHAPE = None

# X * u — u is broadcast across both rows, then multiplied entry by entry.
X_STAR_U_SHAPE = None  # a tuple

# X @ u — each row is multiplied by u and then SUMMED.
X_AT_U_SHAPE = None  # a tuple
X_AT_U_VALUES = None  # a list of numbers

# One sentence, expressed as code: `@` is `*` followed by a sum along which
# axis? Give the integer axis number that turns (X * u) into (X @ u).
AXIS_THAT_TURNS_STAR_INTO_AT = None


# ===========================================================================
# EXERCISE 5 — one layer of a neural network
#
#   X    = [[1, 2, 0],      the batch: two examples, three features each
#            [0, 1, 3]]
#   W    = [[ 2, 0],        the weights: three inputs, two outputs
#           [-1, 1],
#           [ 0, 4]]
#   bias = [5, -2]
#
# Compute X @ W + bias entirely by hand. This is the operation that consumes
# essentially all the compute in training any model, and it is worth having
# done once with a pen.
# ===========================================================================

X_AT_W = None  # a list of two lists
LAYER_OUTPUT = None  # X @ W + bias, a list of two lists

# The bias has 2 entries. Is that one per EXAMPLE or one per OUTPUT?
# Answer with the string "example" or the string "output".
BIAS_IS_ONE_PER = None

# If the batch grew from 2 examples to 64, which of the three shapes changes?
# Answer with a list of the names that change, drawn from "X", "W" and "bias".
# For example ["X", "W"] — but that is not the answer.
SHAPES_THAT_CHANGE_WITH_THE_BATCH = None

# Two layers with no activation function between them collapse into a single
# layer. True or False?
TWO_LINEAR_LAYERS_COLLAPSE = None


# ===========================================================================
# EXERCISE 6 — cost
# ===========================================================================

# How many multiplications does a (2, 3) @ (3, 2) cost?
COST_OF_THE_SMALL_LAYER = None

# How many does a (200, 200) @ (200, 200) cost?
COST_OF_200_SQUARED = None

# For the chain (10, 100) @ (100, 5) @ (5, 50), count both associations.
#   (AB)C  = 10*100*5 + 10*5*50
#   A(BC)  = 100*5*50 + 10*100*50
CHAIN_LEFT_FIRST = None
CHAIN_RIGHT_FIRST = None

# Which association is cheaper here? Answer "(AB)C" or "A(BC)".
CHEAPER_ASSOCIATION = None

# Do the two associations give the same ANSWER, ignoring cost? True or False.
ASSOCIATIONS_AGREE = None

# NumPy's `@` on a float64 array is far faster than on an int64 array of the
# same shape and values. What is the reason? Answer with one of these strings:
#   "floats are smaller"
#   "BLAS only implements floating point"
#   "integers overflow so numpy checks every entry"
#   "numpy converts integers to Python objects"
WHY_FLOAT_BEATS_INT = None
