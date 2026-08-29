"""03 — Inverse mapping and nearest-neighbour, with exact answers asserted.

Run from the examples directory:

    ../.venv/bin/python3 03_inverse_mapping.py

The loop is turned inside out. Instead of asking "where does this input pixel
go", ask "where did this output pixel come from". Every output pixel is visited
exactly once, so holes are impossible by construction rather than by care.
"""

import math

import numpy as np

import pattern
import warp

SCRIPT = "03_inverse_mapping.py"


def main():
    img = pattern.make_pattern()
    height, width = img.shape

    print("The loop, inside out")
    print("=" * 60)
    print("  for each OUTPUT pixel:")
    print("      take its centre, (x + 0.5, y + 0.5)")
    print("      send it BACKWARD through the inverse matrix")
    print("      take the value of the input pixel containing that point")
    print()
    print("  Every output pixel is assigned. That is not a claim about the")
    print("  arithmetic; it is a property of iterating over the array you are")
    print("  filling. This is why every real implementation works this way.")
    print()

    # ----------------------------------------------------------------------
    print("A quarter turn, with the answer known in advance")
    print("=" * 60)
    print("  90 degrees is the angle to test first, because the right answer is")
    print("  exact: every pixel lands on a pixel, so this can be asserted with")
    print("  == rather than with a tolerance.")
    print()

    quarter = warp.about_centre(warp.rotation_quarter_turns(1), width, height)
    turned = warp.warp_nearest(img, quarter, fill=pattern.FILL)

    print("  before                     after")
    for a, b in zip(pattern.as_text(img).split("\n"),
                    pattern.as_text(turned).split("\n")):
        print(f"    {a}                {b}")
    print()

    print("  The F turned CLOCKWISE, from a counter-clockwise rotation matrix.")
    print("  That is the y-down coordinate system, not a sign error. Day 102's")
    print("  graphs had y growing upward; here row 0 is the top.")
    print()

    expected = np.rot90(img, -1)
    same = np.array_equal(turned, expected)
    print(f"  identical to numpy.rot90(img, -1)?  {same}")
    print(f"  differing pixels: {int((turned != expected).sum())}")
    print()
    assert same
    assert int((turned != expected).sum()) == pattern.PIXEL_TOL

    print("  No pixel took the fill value, because a quarter turn of a square")
    print("  image lands entirely inside the frame:")
    print(f"    pixels at the fill value: {int((turned == pattern.FILL).sum())}")
    print(f"    ink pixels before: {len(pattern.ink_cells(img))}, "
          f"after: {len(pattern.ink_cells(turned))}")
    print()
    assert int((turned == pattern.FILL).sum()) == 0
    assert len(pattern.ink_cells(turned)) == len(pattern.ink_cells(img)) == 24

    # ----------------------------------------------------------------------
    print("Where individual pixels went, checked one at a time")
    print("=" * 60)
    print("  The corner mark is the easiest thing to follow, because there is")
    print("  exactly one pixel of that value in the whole image.")
    before_mark = tuple(int(v) for v in np.argwhere(img == pattern.MARK)[0])
    after_mark = tuple(int(v) for v in np.argwhere(turned == pattern.MARK)[0])
    print(f"    before: row {before_mark[0]}, column {before_mark[1]}")
    print(f"    after:  row {after_mark[0]}, column {after_mark[1]}")
    print("  Bottom-right to bottom-left, which is what a clockwise quarter turn")
    print("  does to a bottom-right corner.")
    print()
    assert before_mark == (8, 8)
    assert after_mark == (8, 0)

    print("  And the whole top bar of the F, which was row 0, columns 1 to 6:")
    top_bar_after = sorted(
        (int(r), int(c)) for r, c in np.argwhere(turned == pattern.INK)
        if c == 8
    )
    print(f"    it is now column 8, rows {[r for r, _ in top_bar_after]}")
    print()
    assert [r for r, _ in top_bar_after] == list(range(1, 7))

    # ----------------------------------------------------------------------
    print("All four quarter turns")
    print("=" * 60)
    for turns in (1, 2, 3, 4):
        matrix = warp.about_centre(warp.rotation_quarter_turns(turns), width, height)
        out = warp.warp_nearest(img, matrix, fill=pattern.FILL)
        reference = np.rot90(img, -turns)
        ok = np.array_equal(out, reference)
        print(f"  {90 * turns:>3} degrees: matches numpy.rot90(img, -{turns})  ->  {ok}")
        assert ok, turns
    print()

    # ----------------------------------------------------------------------
    print("Does the float version of a quarter turn agree?")
    print("=" * 60)
    print(f"  math.cos(math.pi / 2) = {math.cos(math.pi / 2)!r}")
    print("  Not 0.0 -- the Day 102 result. So the trigonometric rotation matrix")
    print("  is a hair off the exact one. Does it change any pixel?")
    print()
    trig = warp.about_centre(warp.rotation(math.pi / 2), width, height)
    trig_out = warp.warp_nearest(img, trig, fill=pattern.FILL)
    print(f"    matrices identical?      "
          f"{trig == warp.about_centre(warp.rotation_quarter_turns(1), width, height)}")
    print(f"    matrices within {warp.TOL:g}?   "
          f"{warp.matrices_close(trig, quarter)}")
    print(f"    output images identical? {np.array_equal(trig_out, turned)}")
    print()
    assert not warp.matrices_close(trig, quarter, tol=0.0)
    assert warp.matrices_close(trig, quarter)
    assert np.array_equal(trig_out, turned)
    print("  The matrices differ; the images do not. Nearest-neighbour rounds to")
    print("  a whole pixel, and an error of 1e-16 never reaches a rounding")
    print("  boundary. The float noise is real and it is absorbed. That will not")
    print("  be true of every angle, which is why the exact-integer matrix exists")
    print("  and is used wherever the answer is meant to be checkable.")
    print()

    # ----------------------------------------------------------------------
    print("A full turn: exact, and only because it is ONE matrix")
    print("=" * 60)
    full = warp.about_centre(warp.rotation(2.0 * math.pi), width, height)
    full_out = warp.warp_nearest(img, full, fill=pattern.FILL)
    print(f"  rotation(2*pi) applied once, differing pixels: "
          f"{int((full_out != img).sum())}")
    assert np.array_equal(full_out, img)

    twelve = img
    for _ in range(12):
        twelve = warp.warp_nearest(
            twelve,
            warp.about_centre(warp.rotation(math.radians(30)), width, height),
            fill=pattern.FILL,
        )
    n_lost = int((twelve != img).sum())
    print(f"  twelve separate 30 degree rotations, differing pixels: {n_lost}")
    print()
    print(pattern.as_text(twelve))
    print()
    assert n_lost == 16, n_lost
    assert not np.array_equal(twelve, img)

    print("  Both routes are 360 degrees. One is exact and one loses 16 of 81")
    print("  pixels. The difference is not the angle -- it is the number of times")
    print("  the image was RESAMPLED. Each nearest-neighbour pass throws away the")
    print("  sub-pixel position, and twelve passes cannot recover what the first")
    print("  one discarded. Compose the matrices, resample once.")
    print()

    composed = warp.identity()
    for _ in range(12):
        composed = warp.compose(
            warp.about_centre(warp.rotation(math.radians(30)), width, height),
            composed,
        )
    composed_out = warp.warp_nearest(img, composed, fill=pattern.FILL)
    print(f"  the same twelve rotations COMPOSED into one matrix and applied")
    print(f"  once, differing pixels: {int((composed_out != img).sum())}")
    print()
    assert np.array_equal(composed_out, img)
    assert warp.matrices_close(composed, warp.identity(), tol=1e-12)

    # ----------------------------------------------------------------------
    print("Colour is not a new problem")
    print("=" * 60)
    colour = pattern.make_colour_pattern()
    turned_colour = warp.warp_colour(colour, quarter, fill=pattern.FILL)
    print(f"  input  shape {colour.shape}")
    print(f"  output shape {turned_colour.shape}")
    for c, name in enumerate(("red", "green", "blue")):
        ok = np.array_equal(turned_colour[:, :, c], np.rot90(colour[:, :, c], -1))
        print(f"  {name:<6} plane rotated correctly: {ok}")
        assert ok
    print("  Same matrix, three planes. The transformation acts on coordinates,")
    print("  and the three planes share their coordinates.")
    print()
    assert turned_colour.shape == (9, 9, 3)

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
