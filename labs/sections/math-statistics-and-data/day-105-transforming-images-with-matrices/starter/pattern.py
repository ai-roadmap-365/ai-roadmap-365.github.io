"""The test image, generated in code rather than downloaded.

Nothing here loads a file. The pattern is built from arithmetic so that every
pixel value in this lab has a reason, and so that the lab needs no network and
ships no photograph.

The glyph is a capital F on a 9 by 9 grid. An F is the standard test shape in
image processing for one reason: it is asymmetric under every operation this
lab performs. A square survives a horizontal flip unchanged, so a square would
let a broken flip pass. An F does not survive anything -- flip it, rotate it,
transpose it, and you can see immediately which one happened.

Coordinates. This is the single most common source of confusion in the whole
subject, so it is stated once, here, and every function in `warp.py` obeys it:

    image[row, column]  ==  image[y, x]

A NumPy array is indexed rows first. The maths of Week 15 wrote points as
(x, y). Those are the SAME two numbers in the OPPOSITE order. Row is y, column
is x. And y grows DOWNWARD, because row 0 is the top of the picture, which is
the reverse of the graphs on Day 102 where y grew upward.
"""

import numpy as np

# Grey levels. Distinct, well separated, and none of them 0 or 255 by accident.
INK = 255  # the glyph itself
PAPER = 0  # the background
MARK = 96  # a single corner pixel, so a 180 degree turn is distinguishable
FILL = 32  # what lands in an output pixel whose source is off the image

SIZE = 9  # the pattern is SIZE by SIZE

# The exact cells of the F, written out rather than computed, so the values in
# the tests can be read off this list by eye.
TOP_BAR = [(0, c) for c in range(1, 7)]  # row 0, columns 1..6
MIDDLE_BAR = [(4, c) for c in range(1, 5)]  # row 4, columns 1..4
STEM = [(r, 1) for r in range(1, 9)] + [(r, 2) for r in range(1, 9)]

# Where the single corner mark goes: bottom-right, the corner the F never
# reaches, so it can never be confused with part of the glyph.
MARK_CELL = (8, 8)


def make_pattern():
    """Return the 9 by 9 greyscale test image as a uint8 array of shape (9, 9).

    Shape is (height, width) -- rows then columns -- which is (y, x).
    """
    img = np.full((SIZE, SIZE), PAPER, dtype=np.uint8)
    for row, col in TOP_BAR + MIDDLE_BAR + STEM:
        img[row, col] = INK
    img[MARK_CELL] = MARK
    return img


def make_colour_pattern():
    """Return the same glyph as a colour image of shape (9, 9, 3).

    Colour is three greyscale planes stacked on the last axis: red, green,
    blue. Each plane is a matrix in its own right, and every transformation in
    this lab acts on the coordinates, which the three planes share. That is
    why transforming a colour image is the same work as transforming a
    greyscale one, done three times.
    """
    grey = make_pattern()
    img = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    img[:, :, 0] = grey  # red plane: the glyph
    img[:, :, 1] = np.fliplr(grey)  # green plane: the glyph mirrored
    img[:, :, 2] = MARK  # blue plane: flat, so a channel mix-up is obvious
    return img


def as_text(img, ink_char="#", paper_char=".", mark_char="o", fill_char="~"):
    """Render a greyscale array as ASCII so a transformation can be SEEN.

    Anything that is not one of the four known levels prints as `?`, which is
    how an interpolation artefact announces itself.
    """
    table = {INK: ink_char, PAPER: paper_char, MARK: mark_char, FILL: fill_char}
    return "\n".join(
        "".join(table.get(int(v), "?") for v in row) for row in np.asarray(img)
    )


def ink_cells(img):
    """Return the sorted (row, column) pairs whose value is INK.

    Comparing two images by their ink cells is exact -- these are integers, not
    floats -- which is why the rotation tests in this lab can assert equality
    rather than a tolerance.
    """
    rows, cols = np.nonzero(np.asarray(img) == INK)
    return sorted(zip(rows.tolist(), cols.tolist()))


# The values the tests assert against, written here once so that a change to
# the pattern cannot quietly change what "correct" means somewhere else.
EXPECTED_SHAPE = (9, 9)
EXPECTED_COLOUR_SHAPE = (9, 9, 3)
EXPECTED_INK_COUNT = len(set(TOP_BAR + MIDDLE_BAR + STEM))
EXPECTED_TEXT = "\n".join(
    [
        ".######..",
        ".##......",
        ".##......",
        ".##......",
        ".####....",
        ".##......",
        ".##......",
        ".##......",
        ".##.....o",
    ]
)

# Tolerances. Every float comparison in this lab names one of these.
TOL = 1e-12  # for matrix arithmetic done in floating point
PIXEL_TOL = 0  # for nearest-neighbour pixel values: they must match EXACTLY
