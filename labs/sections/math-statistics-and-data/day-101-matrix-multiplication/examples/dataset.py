"""The numbers every script in this lab shares, and the answers worked by hand.

Everything here is invented and everything here is small. That is deliberate:
each answer below was worked out with a pen before it was ever run, and you can
do the same. A lab about an operation you cannot check by hand is a lab that
teaches you to trust output, which is the opposite of the point.

The hand-worked answers are stored beside the inputs so that the reference
tests can assert against a number a human derived, not against whatever NumPy
happened to return. If NumPy and the pen disagree, that is a finding, and the
tests are arranged so you would see it rather than absorb it.
"""

# ---------------------------------------------------------------------------
# One layer of a neural network: X @ W + b
# ---------------------------------------------------------------------------

# A batch of two examples, three features each. Shape (2, 3).
# Row 0 is the first example, row 1 is the second. Rows are examples and
# columns are features — the table reading from Day 100.
X = [
    [1, 2, 0],
    [0, 1, 3],
]

# The weights of one layer: three inputs in, two outputs out. Shape (3, 2).
# Column j holds the weights that produce output j. Read it that way and the
# shape rule stops needing to be memorised.
W = [
    [2, 0],
    [-1, 1],
    [0, 4],
]

# One bias per output unit. Shape (2,). It is added to every row of X @ W,
# which is broadcasting from Day 100 doing exactly the job it was built for.
BIAS = [5, -2]

# X @ W, worked by hand:
#   row 0 = [1, 2, 0]
#     column 0 of W is [2, -1, 0]:  1*2 + 2*(-1) + 0*0  =  2 - 2 + 0  =  0
#     column 1 of W is [0,  1, 4]:  1*0 + 2*1    + 0*4  =  0 + 2 + 0  =  2
#   row 1 = [0, 1, 3]
#     column 0 of W is [2, -1, 0]:  0*2 + 1*(-1) + 3*0  =  0 - 1 + 0  = -1
#     column 1 of W is [0,  1, 4]:  0*0 + 1*1    + 3*4  =  0 + 1 + 12 = 13
XW = [
    [0, 2],
    [-1, 13],
]

# Then the bias is added to every row: [5, -2] on top of each.
#   row 0: [0 + 5,  2 - 2] = [5,  0]
#   row 1: [-1 + 5, 13 - 2] = [4, 11]
LAYER_OUT = [
    [5, 0],
    [4, 11],
]

# The single output cell the architecture diagram highlights: row 1, column 1
# of X @ W. Row 1 of X is [0, 1, 3]; column 1 of W is [0, 1, 4].
HIGHLIGHT_CELL = (1, 1)
HIGHLIGHT_ROW = [0, 1, 3]
HIGHLIGHT_COLUMN = [0, 1, 4]
HIGHLIGHT_TERMS = [0, 1, 12]  # 0*0, 1*1, 3*4
HIGHLIGHT_VALUE = 13

# ---------------------------------------------------------------------------
# Composition: two transformations of the plane, in both orders
# ---------------------------------------------------------------------------

# A quarter turn anticlockwise. It sends (1, 0) to (0, 1) and (0, 1) to (-1, 0),
# and those two images ARE its columns — which is the whole trick for reading a
# transformation matrix off a picture.
ROT90 = [
    [0, -1],
    [1, 0],
]

# A reflection in the horizontal axis: x stays, y flips sign.
FLIP_X = [
    [1, 0],
    [0, -1],
]

# ROT90 @ FLIP_X means "flip first, then rotate" — the rightmost matrix meets
# the vector first, because that is the one standing next to it in A @ (B @ v).
# The product turns out to be the reflection in the line y = x.
ROT_AFTER_FLIP = [
    [0, 1],
    [1, 0],
]

# FLIP_X @ ROT90 means "rotate first, then flip". Same two operations, opposite
# order, and the result is the reflection in the line y = -x. A different
# transformation entirely, which is what "not commutative" means in practice.
FLIP_AFTER_ROT = [
    [0, -1],
    [-1, 0],
]

# The test vector the flow diagram follows, and every waypoint on its journey.
V = [3, 1]
FLIP_V = [3, -1]  # FLIP_X @ V
ROT_AFTER_FLIP_V = [1, 3]  # ROT90 @ (FLIP_X @ V), and also ROT_AFTER_FLIP @ V
ROT_V = [-1, 3]  # ROT90 @ V
FLIP_AFTER_ROT_V = [-1, -3]  # FLIP_X @ (ROT90 @ V), and also FLIP_AFTER_ROT @ V

# The elementwise product of those same two matrices is all zeros, because
# every entry of one lines up with a zero of the other. Same operands, same
# shape out, and not a single number in common with the matrix product.
ROT_TIMES_FLIP_ELEMENTWISE = [
    [0, 0],
    [0, 0],
]

# ---------------------------------------------------------------------------
# A second, less tidy pair: three different answers from two matrices
# ---------------------------------------------------------------------------

P = [
    [1, 2],
    [3, 4],
]
Q = [
    [5, 6],
    [7, 8],
]

# P @ Q, worked by hand:
#   [0][0] = 1*5 + 2*7 = 5 + 14 = 19      [0][1] = 1*6 + 2*8 = 6 + 16 = 22
#   [1][0] = 3*5 + 4*7 = 15 + 28 = 43     [1][1] = 3*6 + 4*8 = 18 + 32 = 50
P_AT_Q = [
    [19, 22],
    [43, 50],
]

# Q @ P, worked by hand:
#   [0][0] = 5*1 + 6*3 = 5 + 18 = 23      [0][1] = 5*2 + 6*4 = 10 + 24 = 34
#   [1][0] = 7*1 + 8*3 = 7 + 24 = 31      [1][1] = 7*2 + 8*4 = 14 + 32 = 46
Q_AT_P = [
    [23, 34],
    [31, 46],
]

# P * Q, entry by entry, no summing anywhere:
P_TIMES_Q = [
    [5, 12],
    [21, 32],
]

# ---------------------------------------------------------------------------
# The `*` versus `@` trap, where both are legal and neither warns you
# ---------------------------------------------------------------------------

# A vector of length 3 meeting the (2, 3) batch X.
U = [10, 2, 5]

# X * U broadcasts U across both rows and multiplies entry by entry.
# Shape (2, 3) out — the same shape it went in with, nothing summed.
X_TIMES_U = [
    [10, 4, 0],
    [0, 2, 15],
]

# X @ U multiplies and then SUMS along each row. Shape (2,) out.
#   row 0: 1*10 + 2*2 + 0*5 = 10 + 4 + 0  = 14
#   row 1: 0*10 + 1*2 + 3*5 = 0 + 2 + 15  = 17
X_AT_U = [14, 17]

# ---------------------------------------------------------------------------
# The deliberate shape error, and the two different repairs
# ---------------------------------------------------------------------------

# X @ X is (2, 3) @ (2, 3). The inner dimensions are 3 and 2 and they disagree,
# so NumPy raises. Transposing one side fixes it — but WHICH side you transpose
# changes the answer, its shape and its meaning, and nothing will tell you if
# you pick the one you did not want.

# X @ X.T is (2, 3) @ (3, 2) -> (2, 2). Entry (i, j) is row i dotted with row j,
# so this is a table of how alike the two EXAMPLES are.
#   [0][0] = 1*1 + 2*2 + 0*0 = 5      [0][1] = 1*0 + 2*1 + 0*3 = 2
#   [1][0] = 0*1 + 1*2 + 3*0 = 2      [1][1] = 0*0 + 1*1 + 3*3 = 10
X_AT_XT = [
    [5, 2],
    [2, 10],
]

# X.T @ X is (3, 2) @ (2, 3) -> (3, 3). Entry (i, j) is column i dotted with
# column j, so this is a table of how alike the three FEATURES are.
#   columns of X are [1, 0], [2, 1] and [0, 3]
#   [0][0] = 1*1 + 0*0 = 1     [0][1] = 1*2 + 0*1 = 2     [0][2] = 1*0 + 0*3 = 0
#   [1][1] = 2*2 + 1*1 = 5     [1][2] = 2*0 + 1*3 = 3
#   [2][2] = 0*0 + 3*3 = 9
XT_AT_X = [
    [1, 2, 0],
    [2, 5, 3],
    [0, 3, 9],
]

# ---------------------------------------------------------------------------
# The dot product, arithmetically and geometrically
# ---------------------------------------------------------------------------

DOT_U = [3, 4]  # length 5, from Day 99
DOT_V = [4, 3]  # length 5 as well
DOT_W = [-4, 3]  # length 5, and at right angles to DOT_U

DOT_U_U = 25  # 3*3 + 4*4 — a vector dotted with itself is its length squared
DOT_U_V = 24  # 3*4 + 4*3
DOT_U_W = 0  # 3*(-4) + 4*3 = -12 + 12 — perpendicular, and the zero says so

# A pair whose angle has a name you can state exactly.
ANGLE_A = [2, 0]
ANGLE_B = [1, 1]
ANGLE_A_B = 2  # 2*1 + 0*1
# |ANGLE_A| = 2, |ANGLE_B| = sqrt(2), so cos(theta) = 2 / (2 * sqrt(2))
# = 1 / sqrt(2), and that angle is 45 degrees exactly.
ANGLE_DEGREES = 45.0

# ---------------------------------------------------------------------------
# Association order: same answer, wildly different arithmetic
# ---------------------------------------------------------------------------

# A small chain you can count on paper: (10, 100) @ (100, 5) @ (5, 50).
SMALL_CHAIN = (10, 100, 5, 50)
SMALL_LEFT_FIRST = 7_500  # (AB)C  = 10*100*5 + 10*5*50
SMALL_RIGHT_FIRST = 75_000  # A(BC)  = 100*5*50 + 10*100*50

# A chain with the shapes of a real low-rank adapter sitting on a 4096-wide
# layer, applied to a batch of 1024: (1024, 4096) @ (4096, 8) @ (8, 4096).
BIG_CHAIN = (1024, 4096, 8, 4096)
BIG_LEFT_FIRST = 67_108_864  # (XA)B
BIG_RIGHT_FIRST = 17_314_086_912  # X(AB)
BIG_RATIO = 258  # exactly, on these shapes

# ---------------------------------------------------------------------------
# Shapes used to exercise the shape rule
# ---------------------------------------------------------------------------

# (left shape, right shape, expected result shape or the string "error")
SHAPE_CASES = [
    ((2, 3), (3, 2), (2, 2)),
    ((3, 2), (2, 3), (3, 3)),
    ((2, 3), (2, 3), "error"),
    ((1, 4), (4, 1), (1, 1)),
    ((4, 1), (1, 4), (4, 4)),
    ((5, 5), (5, 5), (5, 5)),
    ((2, 3), (4, 2), "error"),
]
