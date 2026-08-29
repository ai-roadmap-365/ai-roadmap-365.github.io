"""05 — Homogeneous coordinates, and several transformations folded into one.

Run from the examples directory:

    ../.venv/bin/python3 05_homogeneous_and_composition.py

Day 102 proved that a linear map cannot move the origin, and translation moves
the origin, so translation is not linear and no 2 by 2 matrix performs it. This
script shows the fix -- a third coordinate, fixed at 1 -- and then uses it to
fold a rotation about the image centre into a single matrix.
"""

import math

import numpy as np

import pattern
import warp

SCRIPT = "05_homogeneous_and_composition.py"


def show_matrix(label, matrix):
    print(f"  {label}")
    for row in matrix:
        print("      [" + "  ".join(f"{v:8.4f}" for v in row) + " ]")
    print()


def main():
    img = pattern.make_pattern()
    height, width = img.shape

    # ----------------------------------------------------------------------
    print("The problem: translation is not linear")
    print("=" * 60)
    print("  Day 102's test for linearity was whether the map preserves addition")
    print("  and scalar multiplication, and one consequence is that a linear map")
    print("  must send the origin to the origin. Translation does not.")
    print()

    def move_by_three(point):
        return (point[0] + 3.0, point[1] + 0.0)

    origin = (0.0, 0.0)
    print(f"    moving by (3, 0) sends the origin to {move_by_three(origin)}")
    print("    -- so no 2 by 2 matrix can do it, because every 2 by 2 matrix")
    print("    sends (0, 0) to (0, 0) by construction: the sum of the columns")
    print("    weighted by zero and zero.")
    print()
    for name, matrix in (
        ("rotation(1.1)", warp.rotation(1.1)),
        ("scaling(4, 0.2)", warp.scaling(4.0, 0.2)),
        ("shear_x(9)", warp.shear_x(9.0)),
    ):
        landed = warp.apply_point(matrix, origin)
        print(f"    {name:<16} sends the origin to {landed}")
        assert landed == (0.0, 0.0)
    print()
    assert move_by_three(origin) != origin

    # ----------------------------------------------------------------------
    print("The fix: add a coordinate that is always 1")
    print("=" * 60)
    print("  Write the point (x, y) as the triple (x, y, 1). Now a 3 by 3 matrix")
    print("  can add a constant, because the constant is multiplied by that 1:")
    print()
    print("      [ 1  0  tx ] [ x ]   [ x + tx ]")
    print("      [ 0  1  ty ] [ y ] = [ y + ty ]")
    print("      [ 0  0   1 ] [ 1 ]   [   1    ]")
    print()
    print("  The third coordinate is not a z axis and the picture is not 3-D.")
    print("  It is a bookkeeping device: one extra slot whose only job is to")
    print("  give the translation something to multiply.")
    print()

    shift = warp.translation(3.0, -2.0)
    show_matrix("translation(3, -2):", shift)
    for point in ((0.0, 0.0), (1.0, 1.0), (8.0, 8.0)):
        print(f"    {point} -> {warp.apply_point(shift, point)}")
    print()
    assert warp.apply_point(shift, (0.0, 0.0)) == (3.0, -2.0)
    assert warp.apply_point(shift, (8.0, 8.0)) == (11.0, 6.0)

    print("  And now translation composes with everything else, because it is")
    print("  the same kind of object. A translation's determinant is 1 -- it")
    print("  moves the picture without changing its area -- and its inverse is")
    print("  the opposite translation:")
    print(f"    determinant(translation(3, -2)) = {warp.determinant(shift)}")
    back = warp.invert(shift)
    print(f"    its inverse is translation(-3, 2)?  "
          f"{warp.matrices_close(back, warp.translation(-3.0, 2.0))}")
    print()
    assert warp.determinant(shift) == 1.0
    assert warp.matrices_close(back, warp.translation(-3.0, 2.0))

    print("  On the actual image, translation by (2, 1):")
    moved = warp.warp_nearest(img, warp.translation(2.0, 1.0), fill=pattern.FILL)
    print()
    print("  before                  after")
    a = pattern.as_text(img).split("\n")
    b = pattern.as_text(moved).split("\n")
    for la, lb in zip(a, b):
        print(f"    {la}        {lb}")
    print()
    print("  Two columns right and one row down, with the vacated edges taking")
    print("  the fill value. Check it against a plain NumPy slice, which is what")
    print("  an integer translation ought to be:")
    reference = np.full_like(img, pattern.FILL)
    reference[1:, 2:] = img[:-1, :-2]
    print(f"    matches the slice-and-pad reference?  "
          f"{np.array_equal(moved, reference)}")
    print()
    assert np.array_equal(moved, reference)
    # Two vacated columns (2 * 9 pixels) plus one vacated row (9 pixels), minus
    # the 2 pixels counted twice where the vacated row and columns overlap.
    assert int((moved == pattern.FILL).sum()) == 2 * 9 + 9 - 2

    # ----------------------------------------------------------------------
    print("Composition: three matrices become one")
    print("=" * 60)
    print("  Rotating about the image's centre rather than its top-left corner")
    print("  is three steps: move the centre to the origin, rotate, move it back.")
    print("  It is also ONE matrix, and this is where homogeneous coordinates")
    print("  earn their place -- without them the middle step is a matrix and the")
    print("  two outer steps are not, so they cannot be multiplied together.")
    print()

    cx, cy = width / 2.0, height / 2.0
    to_origin = warp.translation(-cx, -cy)
    turn = warp.rotation_quarter_turns(1)
    back_again = warp.translation(cx, cy)

    show_matrix(f"1. translation({-cx}, {-cy})", to_origin)
    show_matrix("2. rotation, a quarter turn", turn)
    show_matrix(f"3. translation({cx}, {cy})", back_again)

    combined = warp.compose(back_again, turn, to_origin)
    show_matrix("combined = T(+c) . R . T(-c)", combined)

    print("  Read the product RIGHT to LEFT: the rightmost matrix acts first.")
    print("  That is the Day 101 convention and it has not changed.")
    print()
    print(f"  same as about_centre(rotation_quarter_turns(1), 9, 9)?  "
          f"{warp.matrices_close(combined, warp.about_centre(turn, width, height))}")
    print()
    assert warp.matrices_close(combined, warp.about_centre(turn, width, height))

    print("  One matrix must reproduce the three separate steps on every point.")
    print("  Checked on all 81 pixel centres:")
    worst = 0.0
    for y in range(height):
        for x in range(width):
            point = (x + 0.5, y + 0.5)
            stepwise = warp.apply_point(
                back_again, warp.apply_point(turn, warp.apply_point(to_origin, point))
            )
            at_once = warp.apply_point(combined, point)
            worst = max(worst, max(abs(p - q) for p, q in zip(stepwise, at_once)))
    print(f"    largest disagreement over 81 points: {worst:.3e}  "
          f"(tolerance {warp.TOL:g})")
    print()
    assert worst <= warp.TOL

    # ----------------------------------------------------------------------
    print("Order matters, and the images prove it")
    print("=" * 60)
    rotate = warp.about_centre(warp.rotation_quarter_turns(1), width, height)
    stretch = warp.scaling(1.0, 2.0)

    rotate_then_stretch = warp.compose(stretch, rotate)
    stretch_then_rotate = warp.compose(rotate, stretch)

    print(f"  the two products are different matrices?  "
          f"{not warp.matrices_close(rotate_then_stretch, stretch_then_rotate)}")
    print()
    a_img = warp.warp_nearest(
        img, rotate_then_stretch, out_shape=(18, 9), fill=pattern.FILL
    )
    b_img = warp.warp_nearest(
        img, stretch_then_rotate, out_shape=(18, 9), fill=pattern.FILL
    )
    print("  rotate then stretch      stretch then rotate")
    for la, lb in zip(pattern.as_text(a_img).split("\n"),
                      pattern.as_text(b_img).split("\n")):
        print(f"    {la}                {lb}")
    print()
    print(f"  identical images?  {np.array_equal(a_img, b_img)}")
    print("  Two different pictures from the same two operations. Matrix")
    print("  multiplication does not commute, and neither does the darkroom.")
    print()
    assert not warp.matrices_close(rotate_then_stretch, stretch_then_rotate)
    assert not np.array_equal(a_img, b_img)

    # ----------------------------------------------------------------------
    print("One matrix, one resample: the whole argument for composing")
    print("=" * 60)
    print("  A rotation, then a shear, then a scale. Two ways to get there.")
    print()
    steps = [
        ("rotate 30 degrees about the centre",
         warp.about_centre(warp.rotation(math.radians(30)), width, height)),
        ("shear x by 0.5", warp.shear_x(0.5)),
        ("scale by 1.5", warp.about_centre(warp.scaling(1.5, 1.5), width, height)),
    ]
    out_shape = (18, 18)

    sequential = img
    for _, matrix in steps:
        sequential = warp.warp_nearest(
            sequential, matrix, out_shape=out_shape, fill=pattern.FILL
        )

    single = warp.identity()
    for _, matrix in steps:
        single = warp.compose(matrix, single)
    at_once = warp.warp_nearest(img, single, out_shape=out_shape, fill=pattern.FILL)

    differing = int((sequential != at_once).sum())
    print(f"  three resampling passes vs one: {differing} of {sequential.size} "
          f"pixels differ ({100.0 * differing / sequential.size:.1f}%)")
    print()
    print("  three passes            one composed matrix")
    for la, lb in zip(pattern.as_text(sequential).split("\n"),
                      pattern.as_text(at_once).split("\n")):
        print(f"    {la}      {lb}")
    print()
    print("  The composed version is the correct one. Each intermediate resample")
    print("  in the three-pass version quantised the picture to whole pixels and")
    print("  threw the remainder away, and the next pass had no way to know. The")
    print("  matrices cost nine multiplications each to combine; the pixels cost")
    print("  a full pass over the image. Composing is both more accurate and")
    print("  cheaper, which is a rare combination and worth taking.")
    print()
    assert differing > 0
    assert single[2] == [0.0, 0.0, 1.0]

    print("  Composition also keeps the determinant honest -- the area factor of")
    print("  the whole is the product of the parts, exactly as on Day 102:")
    product = 1.0
    for name, matrix in steps:
        d = warp.determinant(matrix)
        product *= d
        print(f"    {name:<38} det {d:.6f}")
    print(f"    {'composed':<38} det {warp.determinant(single):.6f}")
    print(f"    {'product of the three':<38}     {product:.6f}")
    print()
    assert abs(warp.determinant(single) - product) <= 1e-12

    # ----------------------------------------------------------------------
    print("The inverse, and when there is not one")
    print("=" * 60)
    combo = warp.compose(warp.shear_x(0.5), warp.about_centre(
        warp.rotation(math.radians(37)), width, height))
    inverse = warp.invert(combo)
    identity_check = warp.compose(inverse, combo)
    print(f"  M . M^-1 is the identity within {warp.TOL:g}?  "
          f"{warp.matrices_close(identity_check, warp.identity())}")
    print(f"  det(M) = {warp.determinant(combo):.12f}, "
          f"det(M^-1) = {warp.determinant(inverse):.12f}, "
          f"product = {warp.determinant(combo) * warp.determinant(inverse):.12f}")
    print()
    assert warp.matrices_close(identity_check, warp.identity())

    print("  A transformation that flattens the image onto a line has")
    print("  determinant 0 and no inverse -- and because inverse mapping needs")
    print("  the inverse, such a transformation cannot be applied at all:")
    collapse = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    print(f"    determinant: {warp.determinant(collapse)}")
    try:
        warp.warp_nearest(img, collapse, fill=pattern.FILL)
    except warp.SingularTransform as exc:
        print(f"    warp_nearest raised {type(exc).__name__}")
        print(f"    message: {exc}")
        raised = type(exc).__name__
    else:
        raised = "NOTHING"
    print()
    assert raised == "SingularTransform"
    assert issubclass(warp.SingularTransform, ValueError)
    print("  SingularTransform is a ValueError, the same relationship")
    print("  numpy.linalg.LinAlgError has, so an existing `except ValueError`")
    print("  keeps working. Day 102 established that; nothing here changes it.")
    print()

    print(f"{SCRIPT}: every assertion held.")


if __name__ == "__main__":
    main()
