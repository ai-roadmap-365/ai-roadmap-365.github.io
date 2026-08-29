"""Exercises 2 to 5 — predict first, then let NumPy tell you.

Every value below is a prediction you make BEFORE running anything. Replace
each `None` with your answer, then check them from the lab directory:

    .venv/bin/pytest starter -q

Each prediction still set to None is skipped rather than failed, so the test
run is a running score. A wrong prediction fails with both numbers printed.

Predicting first matters more than it sounds. Broadcasting and axis arguments
are where NumPy stops doing the obvious thing, and the only way to find out
whether your mental model is right is to commit to an answer while it can
still be wrong.

The matrix everything below refers to — three invented potting mixes described
by four ingredients, in litres per bag:

                base   bark   grit   compost
    Seedling       2      4      1         3
    Container      0      5      2         7
    Alpine         6      1      4         2

and the ingredient prices, in pence per litre: base 10, bark 2, grit 5,
compost 1.
"""

# ---------------------------------------------------------------------------
# Exercise 2 — shape and the three meanings
# ---------------------------------------------------------------------------

# 2.1 The shape of the matrix above, as a (rows, columns) tuple.
SHAPE_OF_M = None

# 2.2 The shape of its transpose.
SHAPE_OF_M_T = None

# 2.3 Read as a TABLE: the Alpine row, as a plain list of four integers.
ALPINE_ROW = None

# 2.4 Read as a TABLE: the grit column, as a plain list of three integers.
GRIT_COLUMN = None

# 2.5 Read as a TRANSFORMATION: apply the matrix to the price vector and you
#     get the cost of one bag of each mix, in pence. Work all three out on
#     paper — each is four multiplications and three additions — and write
#     them here as a list of three integers, in the mix order above.
COST_PER_BAG_PENCE = None

# 2.6 A (3, 4) matrix applied to a vector returns a vector of what length?
LENGTH_OF_TRANSFORMED_VECTOR = None

# ---------------------------------------------------------------------------
# Exercise 3 — views and copies
# ---------------------------------------------------------------------------

# 3.1 M is the (3, 4) array. You write:
#         flat = M.reshape(12)
#         flat[0] = 99
#     What is M[0, 0] afterwards? An integer.
M_00_AFTER_WRITING_THROUGH_RESHAPE = None

# 3.2 Same again, but:
#         independent = M.copy().reshape(12)
#         independent[0] = 99
#     What is M[0, 0] afterwards? An integer.
M_00_AFTER_WRITING_THROUGH_A_COPY = None

# 3.3 Does a basic slice — M[:, 2] — share memory with M? True or False.
SLICE_SHARES_MEMORY = None

# 3.4 Does fancy indexing — M[[0, 2]] — share memory with M? True or False.
FANCY_INDEX_SHARES_MEMORY = None

# 3.5 Does M.T share memory with M? True or False.
TRANSPOSE_SHARES_MEMORY = None

# ---------------------------------------------------------------------------
# Exercise 4 — broadcasting
# ---------------------------------------------------------------------------

# 4.1 Apply the rule by hand: shape (3, 4) combined with shape (4,).
#     Write the resulting shape as a tuple, or the string "error" if the rule
#     rejects it.
BROADCAST_3x4_WITH_4 = None

# 4.2 Shape (3, 4) combined with shape (3,). Tuple, or "error".
BROADCAST_3x4_WITH_3 = None

# 4.3 Shape (3, 4) combined with shape (3, 1). Tuple, or "error".
BROADCAST_3x4_WITH_3x1 = None

# 4.4 Shape (3, 1) combined with shape (1, 4). Tuple, or "error".
BROADCAST_3x1_WITH_1x4 = None

# 4.5 When broadcasting is rejected, which exception class does NumPy raise?
#     Write the class itself, not its name as a string — for example
#     BROADCAST_FAILURE_EXCEPTION = KeyError
BROADCAST_FAILURE_EXCEPTION = None

# ---------------------------------------------------------------------------
# Exercise 5 — axis=0 against axis=1
# ---------------------------------------------------------------------------

# 5.1 M.sum(axis=0) — write the resulting shape as a tuple.
SHAPE_OF_SUM_AXIS_0 = None

# 5.2 M.sum(axis=1) — write the resulting shape as a tuple.
SHAPE_OF_SUM_AXIS_1 = None

# 5.3 "How many litres are in each bag?" is one number per mix. Which axis
#     argument answers it — 0 or 1?
AXIS_FOR_LITRES_PER_BAG = None

# 5.4 "How many litres of each ingredient does one bag of every mix need?" is
#     one number per ingredient. Which axis argument answers it — 0 or 1?
AXIS_FOR_LITRES_PER_INGREDIENT = None

# 5.5 Work out both totals on paper and write them as lists of integers.
LITRES_PER_BAG = None
LITRES_PER_INGREDIENT = None

# 5.6 M.sum(axis=1, keepdims=True) — the resulting shape, as a tuple.
SHAPE_OF_SUM_AXIS_1_KEEPDIMS = None
