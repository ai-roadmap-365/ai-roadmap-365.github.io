"""Exercises 2 to 6 -- your predictions. Work them out BEFORE running anything.

Every one of these can be reasoned out on paper. That is the point: a lab about
image transformations whose answers you cannot check by hand is a lab that
teaches you to trust output.

Replace each `None` with your answer. Anything still `None` is SKIPPED by the
test suite rather than failed, so your score only ever counts work you actually
attempted.

Check yourself from the LAB DIRECTORY:

    .venv/bin/pytest starter -q
"""

# =============================================================================
# Exercise 2 -- an image is a matrix, and the ordering trap
# =============================================================================
#
# The test pattern is a capital F drawn on a 9 by 9 greyscale grid:
#
#     .######..
#     .##......
#     .##......
#     .##......
#     .####....
#     .##......
#     .##......
#     .##......
#     .##.....o
#
# where `.` is 0, `#` is 255 and `o` is 96. Rows are numbered 0 to 8 from the
# TOP; columns 0 to 8 from the LEFT.

# 2.1 What does `img.shape` report? A tuple of two ints.
#     Careful: NumPy reports (height, width), not (width, height).
SHAPE = None

# 2.2 The colour version stacks three of those planes. What is ITS shape?
COLOUR_SHAPE = None

# 2.3 The `o` pixel sits at row 8, column 8. Written as a POINT in the
#     language of Week 15 -- (x, y) -- what is it? A tuple of two ints.
MARK_AS_POINT = None

# 2.4 One ink pixel of the F sits at row 4, column 3 (in the middle bar).
#     What is the VALUE of img[3, 4] -- the same two numbers, swapped?
#     An int. This is the trap: swapping them does not raise, it returns a
#     wrong answer silently.
VALUE_AT_SWAPPED_INDEX = None

# 2.5 How many pixels of the image are ink (value 255)? An int.
#     Count them off the picture above: the top bar, the two-wide stem down
#     all nine rows, and the middle bar. Mind the overlaps.
INK_PIXEL_COUNT = None


# =============================================================================
# Exercise 3 -- forward mapping leaves holes
# =============================================================================
#
# Forward mapping walks the INPUT and writes each pixel where it lands.

# 3.1 Scale the 9 by 9 image up by 2 into an 18 by 18 output, by forward
#     mapping. AT LEAST how many output pixels must be holes? An int.
#     This is a counting argument, not a rounding one: how many output pixels
#     are there, and how many input pixels are available to fill them?
MINIMUM_HOLES_WHEN_DOUBLING = None

# 3.2 Now shrink instead: forward-map into a 5 by 5 output. How many holes?
#     An int. Think about whether there are enough input pixels this time.
HOLES_WHEN_SHRINKING = None

# 3.3 Shrinking leaves no holes but loses information a different way. In one
#     word, what happens when two input pixels land on the same output pixel?
#     Answer with the string "overwriting" or "blending" -- only one of them
#     is what the algorithm in warp_forward actually does.
WHAT_SHRINKING_DOES = None

# 3.4 Inverse mapping leaves SOME output pixels at the fill value after a 30
#     degree rotation. Is that the same failure as a hole?
#     Answer True if those pixels are holes, or False if they are something
#     else. If False, exercise 3.5 asks you to name it.
FILL_PIXELS_ARE_HOLES = None

# 3.5 One word for what those fill-valued pixels actually are: the source
#     position fell outside the input image. The string is one of
#     "clipping", "aliasing", "quantisation".
NAME_FOR_FILL_PIXELS = None


# =============================================================================
# Exercise 4 -- inverse mapping, with exact answers
# =============================================================================

# 4.1 Rotate the F a quarter turn using rotation_quarter_turns(1) about the
#     image centre. The corner mark starts at (row 8, column 8). Where does it
#     end up? A tuple (row, column) of two ints.
#     Remember: y grows downward, so the counter-clockwise matrix turns the
#     PICTURE clockwise.
MARK_AFTER_QUARTER_TURN = None

# 4.2 That same quarter turn equals one of NumPy's own rotations exactly.
#     Which value of k makes numpy.rot90(img, k) identical to your result?
#     An int in the range -3 to 3.
NUMPY_ROT90_K = None

# 4.3 How many pixels take the fill value after a quarter turn of a SQUARE
#     image? An int.
FILL_COUNT_AFTER_QUARTER_TURN = None

# 4.4 Scale up by exactly 2 with nearest-neighbour into an 18 by 18 output.
#     How many DISTINCT pixel values does the result contain? An int.
#     The input contains three. Does enlarging invent any new ones?
DISTINCT_VALUES_AFTER_DOUBLING = None

# 4.5 Scale DOWN by exactly a half into a 4 by 4 output. The result turns out
#     to be a plain NumPy strided slice of the input. Which one?
#     Answer with the string "img[0::2, 0::2]" or "img[1::2, 1::2]".
#     Hint: output pixel 0 is sampled at its centre, 0.5, which doubles to 1.0.
DOWNSCALE_IS_THE_SLICE = None


# =============================================================================
# Exercise 5 -- homogeneous coordinates and composition
# =============================================================================

# 5.1 Why can no 2 by 2 matrix perform a translation? Answer with the string
#     "it cannot move the origin", "it cannot change area", or
#     "it cannot rotate".
WHY_2X2_CANNOT_TRANSLATE = None

# 5.2 What is the determinant of translation(7, -3)? A float.
DETERMINANT_OF_A_TRANSLATION = None

# 5.3 `compose(B, A)` applies which one first? Answer with the string "A"
#     or "B".
COMPOSE_APPLIES_FIRST = None

# 5.4 Rotate the image 30 degrees twelve times in a row, resampling each time,
#     then compare with the original. Will it come back exactly?
#     True or False.
TWELVE_SEPARATE_ROTATIONS_ARE_EXACT = None

# 5.5 Compose those same twelve rotations into ONE matrix and apply it once.
#     Will THAT come back exactly? True or False.
#     If your two answers differ, you have understood the day's main practical
#     lesson.
TWELVE_COMPOSED_ROTATIONS_ARE_EXACT = None


# =============================================================================
# Exercise 6 -- against Pillow, and the half-pixel question
# =============================================================================

# 6.1 Pillow's affine coefficients (a, b, c, d, e, f) express the map in which
#     direction? Answer with the string "input to output" or
#     "output to input".
PILLOW_COEFFICIENT_DIRECTION = None

# 6.2 So if you pass c = +1 with everything else at identity, which way does
#     the picture appear to move? The string "left" or "right".
PICTURE_MOVES_WHEN_C_IS_POSITIVE = None

# 6.3 Pillow evaluates the transformation at which point of each output pixel?
#     The string "its top-left corner" or "its centre".
#     Exercise 6 in the reference scripts settles this by measurement; predict
#     it first.
PILLOW_SAMPLES_AT = None

# 6.4 A shear whose coefficient b is 2.0. The mathematics says row 0 has y = 0
#     and therefore does not move. By how many whole pixels does row 0
#     ACTUALLY move? An int.
#     Work it out from your answer to 6.3.
ROW_ZERO_SHIFT_WITH_B_EQUALS_2 = None

# 6.5 Rotate by 2*pi -- a full turn -- as a single matrix, with
#     nearest-neighbour. How many pixels of the 81 differ from the original?
#     An int.
#     math.sin(2*math.pi) is about -2.4e-16, not 0. Does an error that size
#     survive rounding to a whole pixel?
PIXELS_CHANGED_BY_A_FULL_TURN = None

# 6.6 Ours and Pillow disagree on 8 of the 360 whole-degree rotations. Those
#     eight are 30, 60, 120, 150, 210, 240, 300 and 330 degrees. What do those
#     angles have in common? Answer with the string
#     "their sines and cosines land samples exactly on pixel boundaries",
#     "they are all multiples of 30", or
#     "they are randomly distributed".
#     The second is a true statement about the list and explains nothing --
#     90, 180 and 270 are multiples of 30 too, and they agreed. Pick the one
#     that says WHY.
WHY_THOSE_ANGLES_DISAGREE = None
