"""Exercises 2 to 6 -- your predictions. Work them out BEFORE running anything.

Every one of these can be done on paper in under a minute. That is the point:
a lab about transformations whose answers you cannot check by hand is a lab
that teaches you to trust output.

Replace each `None` with your answer. Anything still `None` is SKIPPED by the
test suite rather than failed, so your score only ever counts work you actually
attempted.

Check yourself from the LAB DIRECTORY:

    .venv/bin/pytest starter -q
"""

# Imported for you: exercise 6.8 asks for an exception CLASS, and the one it is
# looking for lives at numpy.linalg.LinAlgError.
import numpy

# =============================================================================
# Exercise 2 -- reading a matrix off a picture
# =============================================================================
#
# The picture shows the arrow (1, 0) redrawn ending at (3, 1), and the arrow
# (0, 1) redrawn ending at (-1, 2). Nothing else.

# 2.1 Write the matrix, as a list of two ROWS. Careful: the landing places are
#     the COLUMNS, so they are read downwards, not across.
#     Example of the format: [[1.0, 0.0], [0.0, 1.0]]
PICTURE_MATRIX = None

# 2.2 Where does (2, 1) land? Work it out as 2 lots of the first landing place
#     plus 1 lot of the second, and give an (x, y) tuple of floats.
PICTURE_SENDS_2_1_TO = None

# 2.3 Which of the two ROWS of that matrix is a landing place for a basis
#     vector -- 0, 1, or neither? Answer with the integer 0, the integer 1, or
#     the string "neither".
WHICH_ROW_IS_A_LANDING = None


# =============================================================================
# Exercise 3 -- the four standard transformations
# =============================================================================

# 3.1 scaling(2, 3) applied to (1, 1). An (x, y) tuple.
SCALE_SENDS_1_1_TO = None

# 3.2 reflection_in_x_axis() applied to (2, 3). An (x, y) tuple.
FLIP_SENDS_2_3_TO = None

# 3.3 shear_x(2) applied to (1, 1). An (x, y) tuple.
#     Remember: the sideways push is proportional to the HEIGHT.
SHEAR_SENDS_1_1_TO = None

# 3.4 shear_x(2) applied to (5, 0). An (x, y) tuple. Think before you compute.
SHEAR_SENDS_5_0_TO = None

# 3.5 A quarter turn anticlockwise, rotation(pi / 2), applied to (1, 0).
#     Give the answer you would write on paper, as an (x, y) tuple. The test
#     compares with a tolerance of 1e-12 rather than with ==, and exercise 3.6
#     is about why.
QUARTER_TURN_SENDS_1_0_TO = None

# 3.6 In binary floating point, is math.cos(math.pi / 2) exactly 0.0?
#     True or False.
COS_OF_QUARTER_TURN_IS_EXACTLY_ZERO = None

# 3.7 Every matrix in this lab sends one particular point to itself, no matter
#     what the four entries are. Which point? An (x, y) tuple.
THE_POINT_NO_MATRIX_CAN_MOVE = None


# =============================================================================
# Exercise 4 -- linearity, and the function that fails it
# =============================================================================
#
# T(v) = M @ v          with M = [[2, 0], [0, 3]]
# f(v) = M @ v + b      with b = (1, 1)
# u = (1, 2), v = (3, -1), s = 5

# 4.1 T(u + v). An (x, y) tuple.
T_OF_U_PLUS_V = None

# 4.2 T(u) + T(v). An (x, y) tuple.
T_OF_U_PLUS_T_OF_V = None

# 4.3 f(u + v). An (x, y) tuple.
F_OF_U_PLUS_V = None

# 4.4 f(u) + f(v). An (x, y) tuple.
F_OF_U_PLUS_F_OF_V = None

# 4.5 Subtract 4.3 from 4.4. The gap is one recognisable quantity -- which?
#     An (x, y) tuple.
THE_GAP_BETWEEN_THEM = None

# 4.6 Is f linear? True or False.
F_IS_LINEAR = None

# 4.7 f((0, 0)). An (x, y) tuple -- and notice what it tells you about 4.6
#     without needing 4.1 to 4.5 at all.
F_OF_THE_ORIGIN = None


# =============================================================================
# Exercise 5 -- composition and order
# =============================================================================
#
# A = shear_x(2), B = rotation(pi / 2). You shear FIRST and then rotate.

# 5.1 Which expression is the single matrix that does shear-then-rotate?
#     Answer with the string "compose(B, A)" or the string "compose(A, B)".
SHEAR_THEN_ROTATE_IS = None

# 5.2 Write that matrix out, as two rows of floats. Work it out from where the
#     two basis vectors end up after both steps -- it is easier than the
#     row-by-column rule and it is the same answer.
SHEAR_THEN_ROTATE_MATRIX = None

# 5.3 Do the two orders give the same matrix? True or False.
BOTH_ORDERS_AGREE = None

# 5.4 det(A) is 1 and det(B) is 1. What is the determinant of the composite?
#     A float.
DET_OF_THE_COMPOSITE = None


# =============================================================================
# Exercise 6 -- determinant, area, orientation, rank and the inverse
# =============================================================================

# 6.1 The unit square has area 1. What area does scaling(2, 3) give it?
#     A float.
AREA_AFTER_SCALING = None

# 6.2 What is the SIGNED area of the unit square after reflection in the x
#     axis? A float. Mind the sign; that is the whole question.
SIGNED_AREA_AFTER_REFLECTION = None

# 6.3 What does a negative determinant tell you? Answer with one of the
#     strings: "the shape got smaller", "the plane was flipped over",
#     "the transformation cannot be undone".
A_NEGATIVE_DETERMINANT_MEANS = None

# 6.4 What is the determinant of shear_x(2)? A float, and it should surprise
#     you slightly less once you have drawn the sheared square.
DET_OF_SHEAR = None

# 6.5 COLLAPSE_MATRIX is [[1, 2], [2, 4]]. Look at its two columns. What is its
#     determinant? A float.
DET_OF_COLLAPSE = None

# 6.6 What is its rank -- how many dimensions survive? The integer 0, 1 or 2.
RANK_OF_COLLAPSE = None

# 6.7 Every vector it touches lands on one line through the origin. The line is
#     y = m * x. What is m? A float.
COLLAPSE_LANDS_EVERYTHING_ON_THE_LINE_Y_EQUALS = None

# 6.8 numpy.linalg.inv of that matrix raises an exception. Which class?
#     Give the class itself, not a string, for example: ValueError
#     `numpy` is already imported for you below.
COLLAPSE_INVERSE_EXCEPTION = None

# 6.9 The inverse of shear_x(2) is another shear. With what k? A float.
INVERSE_OF_SHEAR_IS_SHEAR_WITH_K = None

# 6.10 The inverse of scaling(2, 4), as two rows of floats.
INVERSE_OF_SCALING_2_4 = None
