"""01 — An image is a matrix, and the ordering trap that comes with it.

Run from the examples directory:

    ../.venv/bin/python3 01_an_image_is_a_matrix.py

Nothing is downloaded. The picture is built from arithmetic, its exact pixel
values are asserted, and the (row, column) versus (x, y) mismatch is measured
rather than described.
"""

import numpy as np

import pattern
import warp

SCRIPT = "01_an_image_is_a_matrix.py"


def main():
    img = pattern.make_pattern()

    print("An image IS a matrix. Here is the whole of this lab's test picture,")
    print("printed twice: once as characters, once as the numbers it really is.")
    print()
    print(pattern.as_text(img))
    print()
    print("The same array, as numbers:")
    print()
    for r, row in enumerate(img):
        print(f"  row {r}: " + " ".join(f"{int(v):3d}" for v in row))
    print()

    # ----------------------------------------------------------------------
    print("Shape and dtype")
    print("-" * 60)
    print(f"  img.shape       = {img.shape}   <- (height, width) = (rows, columns)")
    print(f"  img.dtype       = {img.dtype}      <- one byte per pixel, 0 to 255")
    print(f"  img.size        = {img.size}       <- total pixels")
    print(f"  img.nbytes      = {img.nbytes}       <- one byte each, so size == nbytes")
    print()
    assert img.shape == pattern.EXPECTED_SHAPE
    assert img.dtype == np.uint8
    assert img.size == 81
    assert img.nbytes == 81

    # ----------------------------------------------------------------------
    print("The ordering trap, measured")
    print("-" * 60)
    print("  All week a point was written (x, y). A NumPy array is indexed")
    print("  rows first. Those are the same two numbers in the OPPOSITE order.")
    print()
    # The corner mark is at row 8, column 8, which is symmetric and therefore
    # useless for showing the swap. Use a cell where row and column differ.
    row, col = 4, 3  # inside the middle bar of the F
    print(f"  img[{row}, {col}] = {int(img[row, col])}   (row {row}, column {col})")
    print(f"  img[{col}, {row}] = {int(img[col, row])}   (row {col}, column {row})")
    print("  Different pixels. Swapping the two numbers silently reads the")
    print("  wrong place -- it does not raise, it just returns a wrong answer.")
    print()
    assert int(img[row, col]) == pattern.INK
    assert int(img[col, row]) == pattern.PAPER
    assert img[row, col] != img[col, row]

    print("  As a point in the language of Week 15, that same pixel is")
    print(f"    (x, y) = ({col}, {row})   because x is the COLUMN and y is the ROW")
    print("  and to read it back you must swap again: img[y, x].")
    print()
    x, y = col, row
    assert int(img[y, x]) == pattern.INK

    # ----------------------------------------------------------------------
    print("Why the origin is top-left here and bottom-left on Day 102")
    print("-" * 60)
    print("  Row 0 is the first row of memory, and screens have always been")
    print("  drawn top row first. So y = 0 is the TOP and y grows DOWNWARD.")
    print("  Day 102's graphs had y growing upward. The matrices are identical;")
    print("  the picture is flipped relative to the graph paper, which is why a")
    print("  counter-clockwise rotation matrix turns an image clockwise.")
    print()
    top_row_ink = int((img[0] == pattern.INK).sum())
    bottom_row_ink = int((img[8] == pattern.INK).sum())
    print(f"  ink pixels in row 0 (the TOP bar of the F): {top_row_ink}")
    print(f"  ink pixels in row 8 (the bottom of the stem): {bottom_row_ink}")
    print()
    assert top_row_ink == 6, top_row_ink
    assert bottom_row_ink == 2, bottom_row_ink

    # ----------------------------------------------------------------------
    print("The asymmetry, and why the pattern was chosen this way")
    print("-" * 60)
    flipped_lr = np.fliplr(img)
    flipped_ud = np.flipud(img)
    transposed = img.T
    print(f"  equal to its left-right mirror?  {np.array_equal(img, flipped_lr)}")
    print(f"  equal to its up-down mirror?     {np.array_equal(img, flipped_ud)}")
    print(f"  equal to its transpose?          {np.array_equal(img, transposed)}")
    print("  Three Falses. A square would have given three Trues, and a broken")
    print("  flip would then have passed its test. That is the whole reason the")
    print("  test image is an F.")
    print()
    assert not np.array_equal(img, flipped_lr)
    assert not np.array_equal(img, flipped_ud)
    assert not np.array_equal(img, transposed)

    # ----------------------------------------------------------------------
    print("Colour: the same thing, three times")
    print("-" * 60)
    colour = pattern.make_colour_pattern()
    print(f"  colour.shape = {colour.shape}   <- (height, width, 3)")
    print("  The last axis is the channel. Three stacked planes, each one a")
    print("  matrix of exactly the kind printed above.")
    print()
    for c, name in enumerate(("red", "green", "blue")):
        plane = colour[:, :, c]
        print(f"  {name:<6} plane: shape {plane.shape}, "
              f"{int((plane == pattern.INK).sum())} pixels at {pattern.INK}, "
              f"mean {plane.mean():.2f}")
    print()
    assert colour.shape == pattern.EXPECTED_COLOUR_SHAPE
    assert np.array_equal(colour[:, :, 0], img)
    assert np.array_equal(colour[:, :, 1], np.fliplr(img))
    assert int(colour[:, :, 2].min()) == int(colour[:, :, 2].max()) == pattern.MARK

    print("  One pixel of the colour image is three numbers:")
    print(f"    colour[0, 1] = {tuple(int(v) for v in colour[0, 1])}  (red, green, blue)")
    print()
    assert tuple(int(v) for v in colour[0, 1]) == (pattern.INK, pattern.PAPER, pattern.MARK)

    # ----------------------------------------------------------------------
    print("A pixel is a point, and a point can be transformed")
    print("-" * 60)
    print("  That is the whole of the rest of this lab. The corner mark sits at")
    print(f"  row {pattern.MARK_CELL[0]}, column {pattern.MARK_CELL[1]}, so as a")
    print(f"  point it is (x, y) = ({pattern.MARK_CELL[1]}, {pattern.MARK_CELL[0]}).")
    moved = warp.apply_point(warp.translation(2, -3), (8.0, 8.0))
    print(f"  Move it by (+2, -3):  {moved}")
    print("  Nothing was done to any pixel VALUE. The coordinate moved.")
    print()
    assert moved == (10.0, 5.0)

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
