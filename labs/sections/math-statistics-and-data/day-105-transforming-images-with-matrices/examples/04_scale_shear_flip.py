"""04 — Scale, shear and flip, each checked against a known-exact answer.

Run from the examples directory:

    ../.venv/bin/python3 04_scale_shear_flip.py

Every transformation here is chosen so that the correct output is something
NumPy can produce a different way -- `numpy.fliplr`, `numpy.kron`, a strided
slice. Agreement between two independent routes to the same array is worth more
than any single implementation's say-so.
"""

import numpy as np

import pattern
import warp

SCRIPT = "04_scale_shear_flip.py"


def side_by_side(left, right, gap="        "):
    a = pattern.as_text(left).split("\n")
    b = pattern.as_text(right).split("\n")
    width = max(len(line) for line in a)
    for i in range(max(len(a), len(b))):
        la = a[i] if i < len(a) else ""
        lb = b[i] if i < len(b) else ""
        print(f"    {la:<{width}}{gap}{lb}")


def main():
    img = pattern.make_pattern()
    height, width = img.shape

    # ----------------------------------------------------------------------
    print("Flip: a reflection plus a translation, in one matrix")
    print("=" * 60)
    print("  A bare reflection sends x to -x, which puts the whole picture off")
    print("  the left edge. What is wanted is a reflection about the image's")
    print("  centre line: x becomes width - x. That is a reflection FOLLOWED BY")
    print("  a translation -- and translation is not linear, which is exactly why")
    print("  the matrix is 3 by 3 and not 2 by 2.")
    print()
    print("  flip_horizontal(9):")
    for row in warp.flip_horizontal(width):
        print("      [" + "  ".join(f"{v:5.1f}" for v in row) + " ]")
    print()

    flipped = warp.warp_nearest(img, warp.flip_horizontal(width), fill=pattern.FILL)
    print("  before                  after")
    side_by_side(img, flipped)
    print()
    print(f"  identical to numpy.fliplr(img)?  {np.array_equal(flipped, np.fliplr(img))}")
    print(f"  pixels at the fill value:        {int((flipped == pattern.FILL).sum())}")
    print()
    assert np.array_equal(flipped, np.fliplr(img))
    assert int((flipped == pattern.FILL).sum()) == 0

    flipped_v = warp.warp_nearest(img, warp.flip_vertical(height), fill=pattern.FILL)
    print(f"  flip_vertical matches numpy.flipud(img)? "
          f"{np.array_equal(flipped_v, np.flipud(img))}")
    assert np.array_equal(flipped_v, np.flipud(img))

    print("  Individual pixels, checked by hand:")
    mark_after = tuple(int(v) for v in np.argwhere(flipped == pattern.MARK)[0])
    print(f"    the corner mark was at (row 8, column 8); after the horizontal")
    print(f"    flip it is at (row {mark_after[0]}, column {mark_after[1]}).")
    print("    Column 8 became column 9 - 1 - 8 = 0, and the row did not move.")
    print()
    assert mark_after == (8, 0)

    print("  Two flips are the identity, and the matrices say so before any")
    print("  pixel is touched:")
    twice = warp.compose(warp.flip_horizontal(width), warp.flip_horizontal(width))
    print(f"    flip . flip == identity?  {warp.matrices_close(twice, warp.identity())}")
    print(f"    determinant of one flip:  {warp.determinant(warp.flip_horizontal(width))}")
    print("    A negative determinant is a reflection -- Day 102's signed area,")
    print("    unchanged in size and reversed in orientation.")
    print()
    assert warp.matrices_close(twice, warp.identity())
    assert warp.determinant(warp.flip_horizontal(width)) == -1.0
    assert np.array_equal(
        warp.warp_nearest(flipped, warp.flip_horizontal(width), fill=pattern.FILL), img
    )

    # ----------------------------------------------------------------------
    print("Scale up: exact pixel replication, and no new information")
    print("=" * 60)
    doubled = warp.warp_nearest(
        img, warp.scaling(2.0, 2.0), out_shape=(height * 2, width * 2),
        fill=pattern.FILL,
    )
    print(f"  output shape {doubled.shape}, "
          f"pixels at the fill value: {int((doubled == pattern.FILL).sum())}")
    print()
    print(pattern.as_text(doubled))
    print()
    kron = np.kron(img, np.ones((2, 2), dtype=np.uint8))
    print(f"  identical to numpy.kron(img, ones((2, 2)))?  "
          f"{np.array_equal(doubled, kron)}")
    print()
    assert np.array_equal(doubled, kron)
    assert int((doubled == pattern.FILL).sum()) == 0
    assert doubled.shape == (18, 18)

    print("  Zero holes -- compare script 02, where forward mapping left 243 of")
    print("  these 324 pixels unwritten. And notice what the enlargement did NOT")
    print("  do: it made every pixel into a 2 by 2 block. There are four times as")
    print("  many pixels and exactly as much information. Nearest-neighbour")
    print("  cannot invent detail, and nothing else can either.")
    print(f"    distinct values before: {len(np.unique(img))}, "
          f"after: {len(np.unique(doubled))}")
    print()
    assert len(np.unique(doubled)) == len(np.unique(img)) == 3

    # ----------------------------------------------------------------------
    print("Scale down: information is thrown away, and you can name which")
    print("=" * 60)
    halved = warp.warp_nearest(
        img, warp.scaling(0.5, 0.5), out_shape=(4, 4), fill=pattern.FILL
    )
    print(f"  output shape {halved.shape}")
    print()
    print(pattern.as_text(halved))
    print()
    strided = img[1::2, 1::2]
    print(f"  identical to img[1::2, 1::2]?  {np.array_equal(halved, strided)}")
    print("  Which is to say: nearest-neighbour downscaling by 2 keeps every")
    print("  second pixel starting at index 1, and discards the rest. The odd")
    print("  starting index is the half-pixel sampling offset showing itself --")
    print("  output pixel 0 has its centre at 0.5, which doubles to 1.0.")
    print()
    assert np.array_equal(halved, strided)

    print("  The corner mark did not survive, and that is correct behaviour:")
    print(f"    mark pixels in the input:  {int((img == pattern.MARK).sum())}")
    print(f"    mark pixels in the output: {int((halved == pattern.MARK).sum())}")
    print("    Row 8 and column 8 are both odd-one-out under this sampling, so")
    print("    the pixel at (8, 8) is one of the ones dropped. A single-pixel")
    print("    feature disappearing under a downscale is not a bug; it is what")
    print("    downscaling is. Averaging instead of sampling would have kept a")
    print("    trace of it, which is the argument for the next script's blending.")
    print()
    assert int((img == pattern.MARK).sum()) == 1
    assert int((halved == pattern.MARK).sum()) == 0

    # ----------------------------------------------------------------------
    print("Shear: each row slid sideways in proportion to its own y")
    print("=" * 60)
    print("  shear_x(k) sends (x, y) to (x + k*y, y). Row 0 has y = 0, so the")
    print("  textbook says row 0 does not move. Watch what the half-pixel")
    print("  sampling offset does to that claim.")
    print()

    for k, out_w in ((0.5, 14), (1.0, 18), (2.0, 27)):
        sheared = warp.warp_nearest(
            img, warp.shear_x(k), out_shape=(height, out_w), fill=pattern.FILL
        )
        # Where did the left edge of the stem (input column 1) end up in row 0?
        row0 = sheared[0]
        first_ink = int(np.argmax(row0 == pattern.INK))
        shift = first_ink - 1
        print(f"  shear_x({k}): row 0's first ink pixel is at column {first_ink}, "
              f"a shift of {shift}")
        assert warp.determinant(warp.shear_x(k)) == 1.0

    print()
    print("  k = 0.5 and k = 1.0 leave row 0 alone; k = 2.0 moves it by one whole")
    print("  pixel. The reason is arithmetic, not magic. The output pixel in row 0")
    print("  is sampled at its CENTRE, y = 0.5, not at y = 0:")
    print("    x_source = floor((x + 0.5) - k * 0.5)")
    for k in (0.5, 1.0, 2.0):
        inside = 0.5 - k * 0.5
        shift = -int(np.floor(inside))
        print(f"    k = {k}:  floor(x {inside:+.2f}) = x {-shift:+d}"
              f"   ->  the content moves right by {shift}")
    print()
    print("  Day 102 flagged this as the open question and deferred it to today.")
    print("  It is settled: the shear term is multiplied by the pixel CENTRE's y,")
    print("  and row 0's centre is at y = 0.5, so a large enough k moves row 0.")
    print()

    sheared2 = warp.warp_nearest(
        img, warp.shear_x(2.0), out_shape=(height, 27), fill=pattern.FILL
    )
    assert int(np.argmax(sheared2[0] == pattern.INK)) == 2, \
        int(np.argmax(sheared2[0] == pattern.INK))
    sheared1 = warp.warp_nearest(
        img, warp.shear_x(1.0), out_shape=(height, 18), fill=pattern.FILL
    )
    assert int(np.argmax(sheared1[0] == pattern.INK)) == 1

    print("  A shear with k = 1.0, drawn:")
    print()
    print(pattern.as_text(sheared1))
    print()
    print("  Straight lines are still straight and the two vertical edges of the")
    print("  stem are still parallel. Every transformation in this lab is AFFINE,")
    print("  and that is exactly what affine guarantees.")
    print()

    print("  Area is unchanged: a shear's determinant is 1, so it cannot lose or")
    print("  gain ink. Counting the surviving ink pixels checks that claim, once")
    print("  the output is wide enough to hold the sheared glyph:")
    ink_before = int((img == pattern.INK).sum())
    ink_after = int((sheared1 == pattern.INK).sum())
    print(f"    ink before: {ink_before}, ink after: {ink_after}")
    print()
    assert ink_before == ink_after == 24

    print("  Shear the other way and it comes back -- with one caveat that is")
    print("  worth more than the rule it breaks.")
    print()
    round_trip = warp.compose(warp.shear_x(-1.0), warp.shear_x(1.0))
    print(f"    as MATRICES, shear_x(-1) . shear_x(1) == identity?  "
          f"{warp.matrices_close(round_trip, warp.identity())}")
    one_pass = warp.warp_nearest(img, round_trip, fill=pattern.FILL)
    print(f"    applied as ONE matrix, differing pixels: "
          f"{int((one_pass != img).sum())}")
    assert warp.matrices_close(round_trip, warp.identity())
    assert np.array_equal(one_pass, img)
    print()

    print("    applied as TWO separate resampling passes:")
    for k, wide in ((0.5, 14), (1.0, 18)):
        out = warp.warp_nearest(
            img, warp.shear_x(k), out_shape=(height, wide), fill=pattern.FILL
        )
        back = warp.warp_nearest(
            out, warp.shear_x(-k), out_shape=(height, width), fill=pattern.FILL
        )
        print(f"      k = {k}:  differing pixels {int((back != img).sum()):>3}")
    print()
    print("    k = 0.5 round-trips exactly. k = 1.0 does not, and loses 28 of 81")
    print("    pixels -- the whole image slides one column left. That is not a")
    print("    bug that was found and left in; it is a boundary case that is")
    print("    worth naming, because it will bite you in real code.")
    print()
    print("    Why: with k = 1.0 the sampled position is (x + 0.5) - 1.0 * 0.5,")
    print("    which is x EXACTLY -- a pixel boundary, where floor has to make an")
    print("    arbitrary choice between two neighbours. With k = 0.5 the position")
    print("    is x + 0.25, safely inside one pixel, and floor is unambiguous.")
    print("    Every integer-valued shear coefficient puts every sample on a")
    print("    boundary at once, so the arbitrary choice is made 81 times in the")
    print("    same direction and the error accumulates into a visible shift.")
    print()
    half_out = warp.warp_nearest(
        img, warp.shear_x(0.5), out_shape=(height, 14), fill=pattern.FILL
    )
    half_back = warp.warp_nearest(
        half_out, warp.shear_x(-0.5), out_shape=(height, width), fill=pattern.FILL
    )
    assert np.array_equal(half_back, img)
    unit_out = warp.warp_nearest(
        img, warp.shear_x(1.0), out_shape=(height, 18), fill=pattern.FILL
    )
    unit_back = warp.warp_nearest(
        unit_out, warp.shear_x(-1.0), out_shape=(height, width), fill=pattern.FILL
    )
    assert int((unit_back != img).sum()) == 28, int((unit_back != img).sum())
    print("    The lesson is the same one script 03 drew from twelve rotations:")
    print("    compose the matrices and resample ONCE. Done that way, this round")
    print("    trip is exact for every k, including 1.0.")
    print()

    # ----------------------------------------------------------------------
    print("What none of this can do")
    print("=" * 60)
    print("  Every matrix in this script is affine: straight lines stay straight,")
    print("  parallel lines stay parallel, and the ratio of lengths along any one")
    print("  line is preserved. Six numbers, and that is the whole family.")
    print()
    print("  What that rules out:")
    print("    * perspective -- railway tracks converging toward a horizon needs")
    print("      a PROJECTIVE transform, whose bottom row is not (0, 0, 1), so")
    print("      the third coordinate stops being 1 and has to be divided out;")
    print("    * lens distortion -- a barrel or pincushion bend is not linear in")
    print("      the coordinates at all, and no matrix of any size expresses it;")
    print("    * warping one face into another -- that is a dense displacement")
    print("      field, a different vector for every pixel.")
    print()
    print("  A quick proof that affine cannot do perspective: an affine map sends")
    print("  parallel lines to parallel lines, because it sends the direction")
    print("  vector of a line through the LINEAR part only, and two lines with")
    print("  the same direction keep the same direction.")
    top_edge = (1.0, 0.0)
    for name, matrix in (
        ("rotation(0.7)", warp.rotation(0.7)),
        ("shear_x(2)", warp.shear_x(2.0)),
        ("scaling(3, 0.5)", warp.scaling(3.0, 0.5)),
    ):
        d0 = warp.apply_point(matrix, (0.0, 0.0))
        d1 = warp.apply_point(matrix, top_edge)
        d2 = warp.apply_point(matrix, (0.0, 5.0))
        d3 = warp.apply_point(matrix, (1.0, 5.0))
        v1 = (d1[0] - d0[0], d1[1] - d0[1])
        v2 = (d3[0] - d2[0], d3[1] - d2[1])
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        print(f"    {name:<16} two parallel edges stay parallel "
              f"(cross product {cross:.1e})")
        assert abs(cross) <= warp.TOL
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
