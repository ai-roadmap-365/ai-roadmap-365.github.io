"""The data this lab works on. Read it; you do not need to change it.

Everything here is invented. A 2 by 2 matrix has four numbers in it, and the
whole point of the day is that you can check every one of them on paper.

Points are `(x, y)` pairs. Polygons are lists of corners in counter-clockwise
order, because the SIGN of a polygon's area depends on which way round its
corners are listed, and that sign is what tells you whether a transformation
turned the plane over.
"""

# -- The standard basis -------------------------------------------------------

E1 = (1.0, 0.0)
E2 = (0.0, 1.0)

# -- The unit square, listed counter-clockwise from the origin ----------------

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

# -- The flag ------------------------------------------------------------------
#
# A deliberately lopsided shape, so you can tell at a glance whether it has
# been turned, stretched, sheared or mirrored: an L lying on its back.

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
# Exercise 2 describes a drawing in words rather than showing it, because the
# skill is going from "where did the basis vectors land" to "what is the
# matrix", and a picture would let you skip the step. The drawing shows:
#
#     the arrow (1, 0) redrawn ending at (3, 1)
#     the arrow (0, 1) redrawn ending at (-1, 2)

PICTURE_E1_LANDS_AT = (3.0, 1.0)
PICTURE_E2_LANDS_AT = (-1.0, 2.0)

# -- The transformations the exercises use ------------------------------------

SCALE_X, SCALE_Y = 2.0, 3.0
SHEAR_K = 2.0

# -- The collapse --------------------------------------------------------------
#
# Look at the two columns before you predict anything about this one.

COLLAPSE_MATRIX = [[1.0, 2.0], [2.0, 4.0]]

# -- Tolerance -----------------------------------------------------------------
#
# Why 1e-12 and not equality: cos(pi / 2) is 6.123233995736766e-17 in binary
# floating point, not 0.0, and sin(pi / 6) is 0.49999999999999994, not 0.5.
# Both are about 1e-17 from the exact answer. 1e-12 sits five orders of
# magnitude above that error and about four below the smallest quantity this
# lab cares about, so it accepts the rounding and would still catch a genuinely
# wrong answer.
TOL = 1e-12
