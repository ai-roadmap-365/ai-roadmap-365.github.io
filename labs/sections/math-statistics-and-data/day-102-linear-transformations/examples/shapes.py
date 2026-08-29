"""The invented data this lab works on, and the answers worked out by hand.

Everything here is made up. There is no dataset, no download and no file to
read: a 2 by 2 matrix has four numbers in it, and the whole point of the day is
that you can check every one of them on paper.

Points are `(x, y)` pairs of plain Python numbers. Polygons are lists of points
in counter-clockwise order, because the SIGN of a polygon's area depends on
which way round you list its corners, and that sign is what tells you whether a
transformation flipped the plane over.
"""

# -- The standard basis -------------------------------------------------------

E1 = (1.0, 0.0)
E2 = (0.0, 1.0)

# -- The unit square, listed counter-clockwise from the origin ----------------
#
# Corners: origin, one step right, the far corner, one step up. Its area is 1
# and its signed area is +1. After a transformation, the signed area of the
# image is exactly the determinant of the matrix -- sign included.

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

# -- The flag ------------------------------------------------------------------
#
# A deliberately lopsided shape, so you can see at a glance whether it has been
# turned, stretched, sheared or mirrored. It is an L lying on its back: a long
# foot along the x axis and a short mast going up at the left.

FLAG = [
    (0.0, 0.0),
    (2.0, 0.0),
    (2.0, 0.5),
    (0.5, 0.5),
    (0.5, 2.0),
    (0.0, 2.0),
]

# -- The picture you read a matrix off of --------------------------------------
#
# Exercise 1 describes a drawing in words rather than showing it, because the
# skill being trained is going from "where did the basis vectors land" to "what
# is the matrix", and a picture would let you skip the step. The drawing shows:
#
#     the arrow (1, 0) has been redrawn ending at (3, 1)
#     the arrow (0, 1) has been redrawn ending at (-1, 2)
#
# Those two landing places, written as COLUMNS, are the matrix.

PICTURE_E1_LANDS_AT = (3.0, 1.0)
PICTURE_E2_LANDS_AT = (-1.0, 2.0)

PICTURE_MATRIX = [
    [3.0, -1.0],
    [1.0, 2.0],
]

# Worked by hand, so the test has something honest to compare against.
#
#   (2, 1) = 2 * (1, 0) + 1 * (0, 1)
#   so it must land at 2 * (3, 1) + 1 * (-1, 2)
#                    = (6, 2) + (-1, 2)
#                    = (5, 4)
#
# and the determinant is 3 * 2 - (-1) * 1 = 6 + 1 = 7.
PICTURE_SENDS_2_1_TO = (5.0, 4.0)
PICTURE_DETERMINANT = 7.0

# -- The four standard transformations, with their hand-worked matrices --------

SCALE_X, SCALE_Y = 2.0, 3.0
SCALE_MATRIX = [[2.0, 0.0], [0.0, 3.0]]      # e1 -> (2, 0), e2 -> (0, 3)

FLIP_MATRIX = [[1.0, 0.0], [0.0, -1.0]]      # reflection in the x axis

SHEAR_K = 2.0
SHEAR_MATRIX = [[1.0, 2.0], [0.0, 1.0]]      # e1 stays, e2 -> (2, 1)

# Rotation by a quarter turn. Written exactly here; computed from cosine and
# sine in transforms.py, where it comes out as 6.123233995736766e-17 rather
# than 0. That difference is the reason every float check in this lab states a
# tolerance.
QUARTER_TURN_MATRIX = [[0.0, -1.0], [1.0, 0.0]]

# -- Composition ---------------------------------------------------------------
#
# Shear first, then rotate a quarter turn. In matrix form that is ROT @ SHEAR,
# with the FIRST transformation written on the RIGHT, because it is the one
# standing next to the vector.
#
#   ROT @ SHEAR = [[0, -1], [1, 0]] @ [[1, 2], [0, 1]]
#               = [[0*1 + -1*0, 0*2 + -1*1],
#                  [1*1 +  0*0, 1*2 +  0*1]]
#               = [[0, -1], [1, 2]]
SHEAR_THEN_ROTATE = [[0.0, -1.0], [1.0, 2.0]]

# The other order, to show that it is a different transformation entirely.
#
#   SHEAR @ ROT = [[1, 2], [0, 1]] @ [[0, -1], [1, 0]]
#               = [[1*0 + 2*1, 1*-1 + 2*0],
#                  [0*0 + 1*1, 0*-1 + 1*0]]
#               = [[2, -1], [1, 0]]
ROTATE_THEN_SHEAR = [[2.0, -1.0], [1.0, 0.0]]

# -- The collapse --------------------------------------------------------------
#
# Both columns point along the same line: (2, 4) is exactly twice (1, 2). So
# every vector in the plane lands somewhere on the line through (1, 2), the
# whole plane is squashed onto a line, and the area of anything you send
# through is zero. Nothing can undo it, because everything on that line came
# from a whole line's worth of starting points.
COLLAPSE_MATRIX = [[1.0, 2.0], [2.0, 4.0]]
COLLAPSE_DETERMINANT = 0.0                    # 1 * 4 - 2 * 2
COLLAPSE_RANK = 1

# -- Tolerance -----------------------------------------------------------------
#
# Why 1e-12 and not equality: cos(pi / 2) is 6.123233995736766e-17 in binary
# floating point, not 0.0, and sin(pi / 6) is 0.49999999999999994, not 0.5.
# Both are about 1e-17 away from the exact answer. 1e-12 sits five orders of
# magnitude above that error and about four below the smallest quantity this
# lab cares about (0.5), so it accepts the rounding and would still catch a
# genuinely wrong answer.
TOL = 1e-12
