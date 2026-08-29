"""02 — Forward mapping, done wrong on purpose, and the holes counted.

Run from the examples directory:

    ../.venv/bin/python3 02_forward_mapping_leaves_holes.py

The obvious way to rotate an image is to walk the input, work out where each
pixel goes, and put it there. This script does exactly that and then counts the
damage. The holes are not a bug in the code below; they are a property of the
method, and no amount of care in the loop removes them.
"""

import math

import numpy as np

import pattern
import warp

SCRIPT = "02_forward_mapping_leaves_holes.py"


def report(label, matrix, img):
    forward, holes = warp.warp_forward(img, matrix, fill=pattern.FILL)
    inverse = warp.warp_nearest(img, matrix, fill=pattern.FILL)
    n_holes = int(holes.sum())
    print(f"{label}")
    print("-" * 60)
    print(f"  forward mapping: {n_holes} of {holes.size} output pixels were never "
          f"written ({100.0 * n_holes / holes.size:.1f}%)")
    print()
    print("  forward mapping (holes show as ~)      inverse mapping")
    left = pattern.as_text(forward).split("\n")
    right = pattern.as_text(inverse).split("\n")
    for a, b in zip(left, right):
        print(f"    {a}                          {b}")
    print()
    return forward, holes, inverse, n_holes


def main():
    img = pattern.make_pattern()
    height, width = img.shape

    print("The idea that does not work")
    print("=" * 60)
    print("  for each INPUT pixel:")
    print("      send its centre through the matrix")
    print("      round to the nearest output pixel")
    print("      write the value there")
    print()
    print("  It reads like the definition of the transformation, and it is.")
    print("  The problem is not the arithmetic. The problem is that the loop is")
    print("  over the WRONG array: it iterates the input, so nothing guarantees")
    print("  every output pixel gets visited.")
    print()

    # ----------------------------------------------------------------------
    # A rotation: pixels spread apart, and gaps open between them.
    # ----------------------------------------------------------------------
    rot30 = warp.about_centre(warp.rotation(math.radians(30)), width, height)
    _, holes30, _, n30 = report("A 30 degree rotation about the centre", rot30, img)
    assert n30 == 22, n30
    assert holes30.sum() > 0

    print("  Look at where the holes are. They are not only round the edges,")
    print("  where the picture genuinely ran out of source. They are INSIDE the")
    print("  glyph -- single missing pixels punched through solid ink. A rotation")
    print("  is area-preserving (its determinant is 1), so it cannot create more")
    print("  room; what it does is land the input pixels on non-integer positions")
    print("  that round unevenly, so some output pixels collect two input pixels")
    print("  and their neighbours collect none.")
    print()
    assert abs(warp.determinant(rot30) - 1.0) <= warp.TOL

    # ----------------------------------------------------------------------
    # Enlarging: the worst case, because there are simply more output pixels
    # than input pixels to fill them.
    # ----------------------------------------------------------------------
    print("Enlarging: the same failure, but arithmetically unavoidable")
    print("=" * 60)
    grow = warp.scaling(2.0, 2.0)
    forward_big, holes_big = warp.warp_forward(
        img, grow, out_shape=(height * 2, width * 2), fill=pattern.FILL
    )
    n_big = int(holes_big.sum())
    print(f"  Scale by 2. Input has {img.size} pixels; output has "
          f"{holes_big.size}.")
    print(f"  At most {img.size} output pixels can ever be written, so at least")
    print(f"  {holes_big.size - img.size} MUST be holes. Measured: {n_big}.")
    print()
    print(pattern.as_text(forward_big))
    print()
    assert n_big >= holes_big.size - img.size
    assert n_big == 243, n_big
    assert holes_big.size == 324

    print("  Three quarters of the output is missing, in a regular lattice. This")
    print("  is a counting argument, not a rounding accident: 81 input pixels")
    print("  cannot fill 324 output pixels however carefully you place them.")
    print()

    # ----------------------------------------------------------------------
    # Shrinking: no holes, but a different loss.
    # ----------------------------------------------------------------------
    print("Shrinking: no holes, and still not right")
    print("=" * 60)
    shrink = warp.scaling(0.5, 0.5)
    forward_small, holes_small = warp.warp_forward(
        img, shrink, out_shape=(5, 5), fill=pattern.FILL
    )
    n_small = int(holes_small.sum())
    print(f"  Scale by a half into a 5 by 5 output: {n_small} holes.")
    print("  No holes at all -- but now several input pixels land on the SAME")
    print("  output pixel and overwrite each other, so which one survives is")
    print("  decided by the order of the loop rather than by the picture.")
    print()
    print(pattern.as_text(forward_small))
    print()
    assert n_small == 0, n_small

    # Prove the overwriting rather than describing it: count how many input
    # pixels land on each output pixel.
    landings = {}
    for y in range(height):
        for x in range(width):
            fx, fy = warp.apply_point(shrink, (x + 0.5, y + 0.5))
            key = (math.floor(fy), math.floor(fx))
            landings.setdefault(key, []).append((y, x))
    collisions = {k: v for k, v in landings.items() if len(v) > 1}
    worst = max(len(v) for v in landings.values())
    print(f"  {len(collisions)} of the 25 output pixels were written more than")
    print(f"  once; the busiest received {worst} input pixels.")
    print(f"  Example: output pixel {sorted(collisions)[0]} was written by input "
          f"pixels {collisions[sorted(collisions)[0]]}.")
    print()
    # 24, not 25. The 9 input rows map to output rows 0,0,1,1,2,2,3,3,4 -- row 8
    # is odd one out and lands alone. The same happens in x, so output pixel
    # (4, 4) is the single one that receives exactly one input pixel.
    assert len(collisions) == 24, len(collisions)
    assert worst == 4, worst
    assert len(landings[(4, 4)]) == 1, landings[(4, 4)]

    # ----------------------------------------------------------------------
    print("Why patching the holes is the wrong instinct")
    print("=" * 60)
    print("  The tempting fix is to find the holes and fill each one from its")
    print("  neighbours. That is more code, it is slower, it needs a second pass")
    print("  over the image, and it still guesses. Turning the loop inside out")
    print("  costs nothing and removes the problem entirely, because a loop over")
    print("  the OUTPUT visits every output pixel exactly once by construction.")
    print()
    print("  That is the next script. The count to beat is:")
    print(f"    30 degree rotation, forward mapping: {n30} holes")
    print()

    inverse30 = warp.warp_nearest(img, rot30, fill=pattern.FILL)
    unset = int((inverse30 == pattern.FILL).sum())
    print(f"  Inverse mapping on the same rotation leaves {unset} pixels at the")
    print("  fill value -- and every one of those is a CORNER whose source lies")
    print("  outside the input image, which is clipping, not a hole. Proof: each")
    print("  one maps back outside the picture.")
    print()

    genuinely_outside = 0
    back = warp.invert(rot30)
    for oy in range(height):
        for ox in range(width):
            if inverse30[oy, ox] == pattern.FILL:
                sx, sy = warp.apply_point(back, (ox + 0.5, oy + 0.5))
                if not (0 <= math.floor(sx) < width and 0 <= math.floor(sy) < height):
                    genuinely_outside += 1
    print(f"  fill-valued output pixels: {unset}")
    print(f"  of those, sourced from outside the input: {genuinely_outside}")
    assert unset == genuinely_outside, (unset, genuinely_outside)
    assert genuinely_outside > 0
    print("  All of them. Inverse mapping has no holes at all.")
    print()

    assert np.array_equal(inverse30, warp.warp_nearest(img, rot30, fill=pattern.FILL))

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
