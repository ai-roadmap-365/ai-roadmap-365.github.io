"""06 — Twenty lines of ours against a mature library, on the same input.

Run from the examples directory:

    ../.venv/bin/python3 06_against_pillow.py

This is the day's strongest artifact and the reason the from-scratch code was
written with plain lists. If `warp.py` had been built out of NumPy helpers,
agreeing with a library would prove nothing. It was not, so agreement is
evidence.

It also settles the question Day 102 deliberately left open: what exactly is
Pillow's sampling convention, and why does a shear coefficient appear to move
row 0 when the mathematics says row 0 has y = 0?
"""

import math
import os
import random
import tempfile

import numpy as np
from PIL import Image

import pattern
import warp

SCRIPT = "06_against_pillow.py"

FILL = pattern.FILL


def pillow_affine(array, coefficients, out_shape=None, resample=None):
    """Run Pillow's own affine transform on the same array and coefficients."""
    height, width = array.shape
    out_h, out_w = out_shape or (height, width)
    image = Image.fromarray(array, mode="L")
    result = image.transform(
        (out_w, out_h),
        Image.Transform.AFFINE,
        coefficients,
        resample=resample or Image.Resampling.NEAREST,
        fillcolor=FILL,
    )
    return np.asarray(result)


def main():
    import PIL

    img = pattern.make_pattern()
    height, width = img.shape

    print(f"Pillow {PIL.__version__}, NumPy {np.__version__}")
    print()

    # ----------------------------------------------------------------------
    print("1. The convention: Pillow's coefficients run OUTPUT to INPUT")
    print("=" * 66)
    print("  Image.transform(size, AFFINE, (a, b, c, d, e, f)) means")
    print()
    print("      input_x  =  a * output_x  +  b * output_y  +  c")
    print("      input_y  =  d * output_x  +  e * output_y  +  f")
    print()
    print("  -- the inverse of the effect you see. Day 102 confirmed the")
    print("  DIRECTION by experiment. Here it is again, in one line, because a")
    print("  convention you have not checked today is a convention you are")
    print("  guessing at.")
    print()

    probe = np.zeros((1, 8), dtype=np.uint8)
    probe[0, 3] = 255
    shifted = pillow_affine(probe, (1, 0, 1, 0, 1, 0))
    before = int(np.argmax(probe[0]))
    after = int(np.argmax(shifted[0]))
    print(f"    a single bright pixel at input x = {before}")
    print(f"    coefficients (1, 0, 1, 0, 1, 0), so c = +1")
    print(f"    the bright pixel comes out at x = {after}")
    print(f"    the content moved LEFT by {before - after} when c said +1.")
    print()
    print("  That is the output-to-input direction, confirmed. If you want the")
    print("  picture to move right, you pass a NEGATIVE c -- or, better, you")
    print("  build the matrix you mean and let `to_pillow_coefficients` invert")
    print("  it for you, which is what this lab does everywhere below.")
    print()
    assert before == 3 and after == 2

    coeffs = warp.to_pillow_coefficients(warp.translation(1.0, 0.0))
    print(f"    to_pillow_coefficients(translation(1, 0)) = "
          f"{tuple(round(v, 12) for v in coeffs)}")
    print("    -- the c is -1, because the coefficients are read off the")
    print("    INVERSE of the matrix you asked for.")
    print()
    assert tuple(round(v, 12) for v in coeffs) == (1.0, 0.0, -1.0, 0.0, 1.0, 0.0)

    # ----------------------------------------------------------------------
    print("2. The open question from Day 102: where is the sample taken?")
    print("=" * 66)
    print("  Two candidate rules. Both agree on integer translations, which is")
    print("  why Day 102 could not tell them apart and said so rather than")
    print("  guessing:")
    print()
    print("    A (pixel centres):  source = floor(a*(x + 0.5) + b*(y + 0.5) + c)")
    print("    B (integer corners): source = floor(a*x + b*y + c + 0.5)")
    print()
    print("  A scale factor separates them in one measurement. Take the row")
    print("  0, 10, 20, ..., 70 and halve the image with a = 2:")
    print()

    row = (np.arange(8, dtype=np.uint8) * 10).reshape(1, 8)
    observed = [int(v) for v in pillow_affine(row, (2, 0, 0, 0, 1, 0))[0]]

    def predict(rule):
        out = []
        for x in range(8):
            i = rule(x)
            out.append(int(row[0, i]) if 0 <= i < 8 else FILL)
        return out

    model_a = predict(lambda x: math.floor(2 * (x + 0.5)))
    model_b = predict(lambda x: math.floor(2 * x + 0.5))
    print(f"    input             {[int(v) for v in row[0]]}")
    print(f"    Pillow observed   {observed}")
    print(f"    rule A predicts   {model_a}")
    print(f"    rule B predicts   {model_b}")
    print()
    print(f"    matches rule A?  {observed == model_a}")
    print(f"    matches rule B?  {observed == model_b}")
    print()
    assert observed == model_a
    assert observed != model_b

    print("  Rule A. Pillow evaluates the affine at the output pixel's CENTRE,")
    print("  (x + 0.5, y + 0.5), and takes the input pixel whose unit square")
    print("  contains the result. That is the answer Day 102 deferred, and it")
    print("  explains the shear puzzle exactly:")
    print()

    strip = np.zeros((3, 9), dtype=np.uint8)
    strip[:, 4] = 255
    sheared = pillow_affine(strip, (1, 2, 0, 0, 1, 0))
    print("    a vertical line at x = 4, with b = 2 (a shear in the")
    print("    output-to-input direction):")
    for y in range(3):
        found = np.flatnonzero(sheared[y] == 255)
        where = int(found[0]) if found.size else None
        predicted = math.floor(0.5 + 2 * (y + 0.5))
        print(f"      row {y}: line now at x = {where!s:<4} "
              f"shift predicted by rule A: {predicted}")
    print()
    print("    Row 0 MOVED, by one pixel, even though the shear term is")
    print("    multiplied by y and row 0 is 'at y = 0'. It is not at y = 0.")
    print("    Its centre is at y = 0.5, and 2 * 0.5 = 1. There is nothing")
    print("    mysterious left in it.")
    print()
    assert int(np.flatnonzero(sheared[0] == 255)[0]) == 3
    assert int(np.flatnonzero(sheared[1] == 255)[0]) == 1

    print("  `warp.py` uses the same rule -- see SAMPLE_OFFSET = 0.5 -- which is")
    print("  why the comparison below can be exact rather than approximate.")
    print()
    assert warp.SAMPLE_OFFSET == 0.5

    # ----------------------------------------------------------------------
    print("3. Ours against theirs, on 510 affine transformations")
    print("=" * 66)
    print("  500 random rotate-scale-shear-translate combinations plus 10")
    print("  deliberate edge cases, each handed to both implementations as the")
    print("  identical six numbers. Nearest-neighbour, same fill colour, same")
    print("  output size.")
    print()

    rng = random.Random(105)
    cases = []
    for _ in range(500):
        theta = rng.uniform(-math.pi, math.pi)
        scale = rng.uniform(0.4, 2.5)
        skew = rng.uniform(-2.5, 2.5)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        cases.append((
            scale * cos_t,
            scale * (cos_t * skew - sin_t),
            rng.uniform(-6, 6),
            scale * sin_t,
            scale * (sin_t * skew + cos_t),
            rng.uniform(-6, 6),
        ))
    edge_cases = [
        (1, 0, 0, 0, 1, 0),        # identity
        (1, 0, 1, 0, 1, 0),        # whole-pixel translation
        (1, 0, 0.5, 0, 1, 0),      # half-pixel translation: floor on a boundary
        (1, 2, 0, 0, 1, 0),        # the shear that moves row 0
        (2, 0, 0, 0, 2, 0),        # exact halving
        (0.5, 0, 0, 0, 0.5, 0),    # exact doubling
        (0, -1, 9, 1, 0, 0),       # a quarter turn
        (-1, 0, 9, 0, -1, 9),      # a half turn
        (1, 0, -3, 0, 1, -3),      # translation clean off the edge
        (1, 0.5, 0, 0, 1, 0),      # a gentle shear
    ]
    cases.extend(edge_cases)

    mismatches = 0
    worst_pixels = 0
    for coefficients in cases:
        inverse = warp.coefficients_to_matrix(coefficients)
        mine = warp.warp_nearest_with_inverse(img, inverse, fill=FILL)
        theirs = pillow_affine(img, coefficients)
        differing = int((mine != theirs).sum())
        worst_pixels = max(worst_pixels, differing)
        if differing:
            mismatches += 1

    print(f"    transformations compared:            {len(cases)}")
    print(f"    transformations matching EXACTLY:    {len(cases) - mismatches}")
    print(f"    worst case, pixels differing:        {worst_pixels}")
    print(f"    stated tolerance for this comparison: {pattern.PIXEL_TOL} "
          f"(exact equality)")
    print()
    assert mismatches == 0, mismatches
    assert worst_pixels == pattern.PIXEL_TOL

    print("  Every pixel of every one of them. Not 'close enough' -- identical.")
    print("  Twenty-odd lines of arithmetic in `warp_nearest_with_inverse` and a")
    print("  library maintained since 2010 produce byte-for-byte the same array.")
    print()

    # ----------------------------------------------------------------------
    print("4. Where the agreement DOES break, and why")
    print("=" * 66)
    print("  It would be easy to stop at the line above. It would also be")
    print("  misleading. Sweep every whole-degree rotation about the centre --")
    print("  360 transformations chosen to be nothing like random -- and the")
    print("  picture changes:")
    print()

    disagreeing = []
    worst_rot = 0
    furthest_from_boundary = 0.0
    for degrees in range(360):
        matrix = warp.about_centre(warp.rotation(math.radians(degrees)), width, height)
        coefficients = warp.to_pillow_coefficients(matrix)
        mine = warp.warp_nearest(img, matrix, fill=FILL)
        theirs = pillow_affine(img, coefficients)
        wrong = np.argwhere(mine != theirs)
        if len(wrong):
            disagreeing.append((degrees, len(wrong)))
            worst_rot = max(worst_rot, len(wrong))
        a, b, c, d, e, f = coefficients
        for oy, ox in wrong:
            xs = a * (ox + 0.5) + b * (oy + 0.5) + c
            ys = d * (ox + 0.5) + e * (oy + 0.5) + f
            gap = min(abs(xs - round(xs)), abs(ys - round(ys)))
            furthest_from_boundary = max(furthest_from_boundary, gap)

    print(f"    rotations compared:                 360")
    print(f"    identical, pixel for pixel:         {360 - len(disagreeing)}")
    print(f"    disagreeing in at least one pixel:  {len(disagreeing)}")
    print(f"    worst case, pixels differing:       {worst_rot} of 81")
    print(f"    the angles: {[deg for deg, _ in disagreeing]}")
    print()
    assert len(disagreeing) == 8, disagreeing
    assert worst_rot == 2, worst_rot

    print("  Eight angles out of 360, never more than 2 pixels out of 81. Now the")
    print("  useful part -- every single disagreeing sample landed within")
    print(f"  {furthest_from_boundary:.3e} of a pixel BOUNDARY:")
    print()
    assert furthest_from_boundary < 1e-9, furthest_from_boundary

    matrix = warp.about_centre(warp.rotation(math.radians(30)), width, height)
    coefficients = warp.to_pillow_coefficients(matrix)
    mine = warp.warp_nearest(img, matrix, fill=FILL)
    theirs = pillow_affine(img, coefficients)
    wrong = np.argwhere(mine != theirs)
    print("  30 degrees about the centre, the smallest failing case.")
    print(f"  coefficients passed to Pillow: "
          f"({', '.join(f'{v!r}' for v in coefficients)})")
    print()
    print("  ours                    Pillow")
    for a_line, b_line in zip(pattern.as_text(mine).split("\n"),
                              pattern.as_text(theirs).split("\n")):
        print(f"    {a_line}                {b_line}")
    print()
    a, b, c, d, e, f = coefficients
    for oy, ox in wrong:
        xs = a * (ox + 0.5) + b * (oy + 0.5) + c
        ys = d * (ox + 0.5) + e * (oy + 0.5) + f
        print(f"    output pixel (row {oy}, column {ox}): ours {int(mine[oy, ox])}, "
              f"Pillow {int(theirs[oy, ox])}")
        print(f"      our source y = {float(ys)!r}")
        print(f"      floor of that = {math.floor(ys)}; Pillow took row "
              f"{math.floor(ys) + 1}")
    print()
    assert len(wrong) == 1, len(wrong)
    assert int(wrong[0][0]) == 4 and int(wrong[0][1]) == 3

    print("  The source row is 4.999999999999999. The exact answer is 5. Ours")
    print("  floors to 4, Pillow's arithmetic reaches 5.0 or a hair above and")
    print("  floors to 5. Neither is wrong: the true sample sits exactly on the")
    print("  boundary between two pixels, and which one you get is decided by the")
    print("  ORDER the floating-point additions happen in. Pillow's C loop walks")
    print("  along each output row accumulating the source coordinate step by")
    print("  step; our Python evaluates the whole expression per pixel. Same")
    print("  formula, different rounding in the last bit.")
    print()
    print("  Look at WHICH angles failed: 30, 60, 120, 150, 210, 240, 300, 330.")
    print("  Every one of them is a 'nice' angle whose sine or cosine is exactly")
    print("  0.5 or exactly half the square root of 3. Nice angles are precisely")
    print("  the ones that put samples on boundaries. The angles nobody would")
    print("  choose for a test -- 37 degrees, 113 degrees -- all agreed. That is")
    print("  the opposite of the usual intuition and it is worth remembering:")
    print("  round numbers are where floating-point ties live.")
    print()
    print("  This is the real shape of the result, and it is more useful than")
    print("  'they always agree' would have been:")
    print("    * for a transformation whose numbers are not special, the two")
    print("      implementations are byte-for-byte identical -- 510 of 510;")
    print("    * for transformations that place samples exactly on pixel")
    print("      boundaries, they can differ by a pixel, and 8 of the 360 whole-")
    print("      degree rotations do;")
    print("    * the disagreement is never larger than the rounding step, and it")
    print("      is a property of floating point, not of either implementation.")
    print()
    print("  If you need bit-identical output across libraries, do not rely on")
    print("  ties breaking the same way. Use angles and offsets that keep samples")
    print("  away from boundaries, or accept a one-pixel tolerance and say so.")
    print()

    print("  And a non-square output, to check that the two agree about which")
    print("  way round a size tuple goes -- Pillow takes (width, height) and")
    print("  NumPy reports (height, width), which is one more place the two")
    print("  orderings can be swapped without any error being raised:")
    wide = warp.warp_nearest(img, warp.shear_x(1.0), out_shape=(9, 18), fill=FILL)
    wide_theirs = pillow_affine(
        img, warp.to_pillow_coefficients(warp.shear_x(1.0)), out_shape=(9, 18)
    )
    print(f"    ours   shape {wide.shape}")
    print(f"    Pillow shape {wide_theirs.shape}")
    print(f"    identical:   {np.array_equal(wide, wide_theirs)}")
    print()
    assert wide.shape == wide_theirs.shape == (9, 18)
    assert np.array_equal(wide, wide_theirs)

    # ----------------------------------------------------------------------
    print("5. A full turn: exact, and Pillow agrees it is exact")
    print("=" * 66)
    full = warp.about_centre(warp.rotation(2.0 * math.pi), width, height)
    ours_full = warp.warp_nearest(img, full, fill=FILL)
    theirs_full = pillow_affine(img, warp.to_pillow_coefficients(full))
    print(f"  rotation(2*pi) as ONE matrix:")
    print(f"    ours   differs from the original in {int((ours_full != img).sum())} pixels")
    print(f"    Pillow differs from the original in {int((theirs_full != img).sum())} pixels")
    print()
    assert np.array_equal(ours_full, img)
    assert np.array_equal(theirs_full, img)
    print("  Exactly zero, in both. Not 'within a tolerance' -- exact, and the")
    print("  reason is worth being precise about. The matrix is not exactly the")
    print("  identity: cos(2*pi) is 1.0 but sin(2*pi) is "
          f"{math.sin(2 * math.pi):.6e},")
    print("  not 0. The residual displacement is around 1e-15 of a pixel, and")
    print("  nearest-neighbour rounds to a whole pixel, so an error fifteen")
    print("  orders of magnitude below the rounding step cannot change the")
    print("  answer. The float error is real and it is absorbed.")
    print()
    assert math.sin(2 * math.pi) != 0.0
    assert not warp.matrices_close(full, warp.identity(), tol=0.0)
    assert warp.matrices_close(full, warp.identity(), tol=1e-12)

    print("  Twelve 30-degree passes is a different story, and script 03 measured")
    print("  it: 16 of 81 pixels lost. Same 360 degrees, resampled twelve times")
    print("  instead of once. Both implementations lose about the same amount,")
    print("  because the loss is in the METHOD and not in either of them:")
    ours_twelve, theirs_twelve = img, img
    step = warp.about_centre(warp.rotation(math.radians(30)), width, height)
    step_coeffs = warp.to_pillow_coefficients(step)
    for _ in range(12):
        ours_twelve = warp.warp_nearest(ours_twelve, step, fill=FILL)
        theirs_twelve = pillow_affine(theirs_twelve, step_coeffs)
    print(f"    ours   differs from the original in "
          f"{int((ours_twelve != img).sum())} pixels")
    print(f"    Pillow differs from the original in "
          f"{int((theirs_twelve != img).sum())} pixels")
    print(f"    ours and Pillow differ from each other in "
          f"{int((ours_twelve != theirs_twelve).sum())} pixels")
    print()
    assert int((ours_twelve != img).sum()) == 16
    assert int((theirs_twelve != img).sum()) == 17
    assert int((ours_twelve != theirs_twelve).sum()) == 3
    print("  16 against 17, and the two results differ from EACH OTHER in 3")
    print("  pixels. That is section 4 compounding: 30 degrees is one of the")
    print("  eight tie-prone angles, so each of the twelve passes can take a")
    print("  different branch, and twelve passes of a one-pixel difference is")
    print("  three pixels apart at the end rather than one. A single pass agreed")
    print("  exactly. Repeated resampling does not just lose information -- it")
    print("  amplifies the disagreements too. One more reason to compose.")
    print()

    # ----------------------------------------------------------------------
    print("6. Bilinear: where the agreement stops, stated plainly")
    print("=" * 66)
    print("  Nearest-neighbour picks the closest pixel. Bilinear averages the")
    print("  four surrounding pixels, weighted by distance -- which is what you")
    print("  want when the inverse-mapped position lands between pixels, because")
    print("  it usually does.")
    print()
    print("  The visible difference: nearest-neighbour gives hard, stair-stepped")
    print("  edges and keeps every value exactly as it was; bilinear gives smooth")
    print("  edges and INVENTS intermediate values that were not in the input.")
    print()

    small_shift = warp.translation(0.5, 0.0)
    nn = warp.warp_nearest(img, small_shift, fill=FILL)
    bl = warp.warp_bilinear_with_inverse(
        img, warp.invert(small_shift), fill=float(FILL)
    )
    print(f"    distinct values, input:              {sorted(np.unique(img).tolist())}")
    print(f"    distinct values, nearest-neighbour:  {sorted(np.unique(nn).tolist())}")
    print(f"    distinct values, bilinear:           "
          f"{len(np.unique(np.round(bl, 6)))} different levels")
    print()
    assert len(np.unique(nn)) <= 4
    assert len(np.unique(np.round(bl, 6))) > len(np.unique(nn))

    print("  Now the honest part. Our bilinear does NOT reproduce Pillow's")
    print("  bilinear pixel-for-pixel, and the lab says so rather than quietly")
    print("  loosening a tolerance until it passes.")
    print()

    print("  The split turns out to be clean, and it is worth stating exactly")
    print("  rather than as 'roughly agrees'. Separate the output pixels into")
    print("  those whose four contributing input pixels are ALL inside the")
    print("  image, and those where at least one contributor lies outside it.")
    print()

    bilinear_cases = [
        ("translate (0.25, 0.25)", warp.translation(0.25, 0.25)),
        ("rotate 30 about the centre",
         warp.about_centre(warp.rotation(math.radians(30)), width, height)),
        ("rotate 17 about the centre",
         warp.about_centre(warp.rotation(math.radians(17)), width, height)),
        ("scale 1.5 about the centre",
         warp.about_centre(warp.scaling(1.5, 1.5), width, height)),
        ("shear x by 0.4", warp.shear_x(0.4)),
    ]

    worst_inside = 0.0
    worst_anywhere = 0.0
    print(f"    {'transformation':<28}{'all 4 inside':>14}{'anywhere':>12}")
    for name, matrix in bilinear_cases:
        inverse = warp.invert(matrix)
        ours_bl = warp.warp_bilinear_with_inverse(img, inverse, fill=0.0)
        theirs_bl = pillow_affine(
            img,
            warp.to_pillow_coefficients(matrix),
            resample=Image.Resampling.BILINEAR,
        ).astype(float)
        difference = np.abs(ours_bl - theirs_bl)

        inside = np.zeros((height, width), dtype=bool)
        for oy in range(height):
            for ox in range(width):
                sx, sy = warp.apply_point(inverse, (ox + 0.5, oy + 0.5))
                x0 = math.floor(sx - warp.SAMPLE_OFFSET)
                y0 = math.floor(sy - warp.SAMPLE_OFFSET)
                inside[oy, ox] = (
                    0 <= x0 and x0 + 1 < width and 0 <= y0 and y0 + 1 < height
                )

        in_max = float(difference[inside].max()) if inside.any() else 0.0
        any_max = float(difference.max())
        worst_inside = max(worst_inside, in_max)
        worst_anywhere = max(worst_anywhere, any_max)
        print(f"    {name:<28}{in_max:>14.3f}{any_max:>12.3f}")
    print()
    print(f"    worst difference where all four contributors are inside: "
          f"{worst_inside:.3f}")
    print(f"    worst difference anywhere:                               "
          f"{worst_anywhere:.3f}")
    print()
    assert worst_inside <= 1.0, worst_inside
    assert worst_anywhere > 100.0, worst_anywhere

    print("  So the claim this lab makes is precise, and it is a better claim")
    print("  than 'they agree' would have been:")
    print()
    print("    * NEAREST-NEIGHBOUR: identical to Pillow, 510 of 510 random and")
    print("      edge cases, zero differing pixels; and identical on 352 of the")
    print("      360 whole-degree rotations, the other 8 differing by at most 2")
    print("      pixels at floating-point ties.")
    print()
    print("    * BILINEAR: wherever all four contributing pixels are inside the")
    print(f"      image, the two agree to within {worst_inside:.0f} grey level --")
    print("      which is exactly the rounding of a float average back into a")
    print("      byte, and cannot be improved on. Wherever a contributor lies")
    print("      OUTSIDE the image, they diverge by up to "
          f"{worst_anywhere:.0f} levels,")
    print("      because they extrapolate differently: ours averages the fill")
    print("      value in, Pillow does not.")
    print()
    print("  The border behaviour was measured, not assumed, and it was not")
    print("  chased further. Naming the boundary of what agrees is more useful")
    print("  than widening a tolerance until a test goes green.")
    print()

    # ----------------------------------------------------------------------
    print("7. Through a real file, and cleaned up afterwards")
    print("=" * 66)
    print("  Everything above happened in memory. One round trip through an")
    print("  actual PNG, to show that the file format is not where information")
    print("  is lost -- PNG is lossless, so the array survives byte for byte.")
    print()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "pattern.png")
        Image.fromarray(img, mode="L").save(path)
        size = os.path.getsize(path)
        reloaded = np.asarray(Image.open(path).convert("L"))
        print(f"    written, {size} bytes on disk for {img.size} pixels")
        print(f"    reloaded array identical to the original?  "
              f"{np.array_equal(reloaded, img)}")
        assert np.array_equal(reloaded, img)
        assert os.path.exists(path)
    print(f"    temporary directory removed?  {not os.path.exists(path)}")
    print()
    assert not os.path.exists(path)
    print("  The file lived in the operating system's temporary directory and is")
    print("  gone. This lab writes no image into its own tree, which is why there")
    print("  is nothing to commit and nothing to clean up by hand.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
