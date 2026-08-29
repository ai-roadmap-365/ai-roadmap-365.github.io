"""Exercise 1 -- your image transformations, built from arithmetic alone.

Twelve functions to write. Each has a docstring saying exactly what it must do,
a worked example you can check on paper, and a `raise NotImplementedError` to
delete when you write it.

Check yourself as you go, from the LAB DIRECTORY (the one above this file):

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED rather than failed. A skip means
"not attempted"; a failure means "attempted and wrong", and it prints your
answer beside the real one.

Use only `math` from the standard library for the MATRIX arithmetic. NumPy is
allowed for holding pixels -- that is what it is for -- and it appears in the
tests, where it checks your work. Writing the maths yourself and then having
Pillow agree with you pixel for pixel is the whole point of the day, and it
only means something if you did not build your answer out of someone else's.

Two conventions, fixed and used everywhere:

1. A point is (x, y): x is the COLUMN, y is the ROW, and y grows DOWNWARD.
   An image array is indexed `img[y, x]`.

2. A transformation matrix is 3 by 3 and maps INPUT to OUTPUT -- the direction
   you can see:

       [ a  b  tx ] [ x ]   [ a*x + b*y + tx ]
       [ c  d  ty ] [ y ] = [ c*x + d*y + ty ]
       [ 0  0   1 ] [ 1 ]   [        1       ]

   The top-left 2 by 2 block is Day 102's linear part; its columns are still
   where the basis vectors land. The third column is the translation.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
Matrix = list[list[float]]

# Written for you, and it matters more than it looks. Every output pixel is a
# little square; the point the transformation is evaluated at is its CENTRE,
# not its corner. Pixel (x, y) covers (x, y) to (x + 1, y + 1), so its centre
# is (x + 0.5, y + 0.5).
#
# Exercise 6 measures why this half is not optional.
SAMPLE_OFFSET = 0.5

TOL = 1e-12


class SingularTransform(ValueError):
    """Raised when a transformation has no inverse, so it cannot be applied.

    Written for you. It subclasses ValueError to match NumPy, whose
    `numpy.linalg.LinAlgError` is itself a ValueError -- so `except ValueError`
    catches your version and NumPy's alike.
    """


# -- Exercise 1.1 -------------------------------------------------------------


def translation(tx: float, ty: float) -> Matrix:
    """Move every point by (tx, ty).

    This is the function homogeneous coordinates exist for. Day 102 proved a
    linear map cannot move the origin, and this moves the origin, so no 2 by 2
    matrix can do it. In 3 by 3 it is easy: the constant gets multiplied by the
    third coordinate, which is always 1.

    Worked example. translation(3, -2) must be

        [[1, 0,  3],
         [0, 1, -2],
         [0, 0,  1]]

    and it must send (0, 0) to (3, -2) and (8, 8) to (11, 6).

    Return floats, not ints, so that later arithmetic does not surprise you.
    """
    raise NotImplementedError("Exercise 1.1: build the translation matrix")


# -- Exercise 1.2 -------------------------------------------------------------


def scaling(sx: float, sy: float) -> Matrix:
    """Stretch x by sx and y by sy, about the origin -- the top-left corner.

    Same derivation as Day 102: where does one step right go? To (sx, 0). Where
    does one step down go? To (0, sy). Those are the two columns. The
    translation column is zero, because scaling about the origin leaves the
    origin alone.

    Worked example. scaling(2, 3) sends (1, 1) to (2, 3) and (0, 0) to (0, 0).
    """
    raise NotImplementedError("Exercise 1.2: build the scaling matrix")


# -- Exercise 1.3 -------------------------------------------------------------


def rotation(theta: float) -> Matrix:
    """Rotate by theta RADIANS about the origin.

    The linear part is exactly Day 102's:

        [[cos, -sin],
         [sin,  cos]]

    Put it in the top-left of a 3 by 3 with a zero translation column.

    One thing to expect and NOT to treat as a bug: on an image, y grows
    DOWNWARD, so this turns the picture CLOCKWISE on screen even though it is
    the counter-clockwise matrix from Day 102. Nothing about the matrix
    changed; the picture is flipped relative to the graph paper.

    Worked example. rotation(math.pi / 2) sends (1, 0) to approximately
    (0, 1) -- approximately, because math.cos(math.pi / 2) is
    6.123233995736766e-17 and not 0.0. That is why every test here states a
    tolerance.
    """
    raise NotImplementedError("Exercise 1.3: build the rotation matrix")


# -- Exercise 1.4 -------------------------------------------------------------


def shear_x(k: float) -> Matrix:
    """Slide each row sideways in proportion to its y: x becomes x + k*y.

    Derive it the Day 102 way. Where does one step right, (1, 0), go? Its y is
    0, so it does not move: to (1, 0). Where does one step down, (0, 1), go?
    Its y is 1, so it slides k to the right: to (k, 1). Those two landings are
    the two columns.

    Worked example. shear_x(2) must be

        [[1, 2, 0],
         [0, 1, 0],
         [0, 0, 1]]

    and it must leave (5, 0) exactly where it was.
    """
    raise NotImplementedError("Exercise 1.4: build the shear matrix")


# -- Exercise 1.5 -------------------------------------------------------------


def flip_horizontal(width: float) -> Matrix:
    """Mirror left-to-right inside an image `width` pixels wide.

    The trap: a bare reflection sends x to -x, which puts the whole picture off
    the left-hand edge. What you want is a mirror about the image's own centre
    line, which sends x to width - x. That is a reflection FOLLOWED BY a
    translation of `width` -- and because you now have homogeneous
    coordinates, it is ONE matrix rather than two steps.

    Worked example. flip_horizontal(9) sends (0, 4) to (9, 4) and (9, 4) to
    (0, 4), and leaves every y alone.

    Hint: the linear part is [[-1, 0], [0, 1]] and the translation column is
    (width, 0).
    """
    raise NotImplementedError("Exercise 1.5: build the horizontal-flip matrix")


# -- Exercise 1.6 -------------------------------------------------------------


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """The 3 by 3 matrix product a @ b, computed by hand.

    Entry (i, j) of the result is row i of `a` dotted with column j of `b`:

        result[i][j] = sum over k of a[i][k] * b[k][j]

    Three nested loops, or one comprehension. Do not import NumPy for this --
    checking your matrix product against NumPy's is one of the tests, and it
    proves nothing if you used NumPy to compute it.
    """
    raise NotImplementedError("Exercise 1.6: multiply two 3 by 3 matrices")


def compose(*matrices: Matrix) -> Matrix:
    """Combine transformations into ONE matrix, applied RIGHT to LEFT.

    `compose(B, A)` means "do A first, then B" -- the Day 101 convention, and
    the same order as reading B(A(x)) from the inside out.

    Written for you, on top of your `matmul`, because the order convention is
    the part worth getting right and the loop is not. Read it.
    """
    if not matrices:
        return identity()
    result = matrices[0]
    for m in matrices[1:]:
        result = matmul(result, m)
    return result


# -- Exercise 1.7 -------------------------------------------------------------


def apply_point(matrix: Matrix, point: Point) -> Point:
    """Send one (x, y) point through the matrix and return the new (x, y).

    The third coordinate is always 1 going in, and for an affine matrix it is
    always 1 coming out, so you never have to build the triple explicitly:

        new_x = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]
        new_y = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]

    Worked example. With translation(3, -2), the point (8, 8) becomes
    (11.0, 6.0).
    """
    raise NotImplementedError("Exercise 1.7: apply a matrix to a point")


# -- Exercise 1.8 -------------------------------------------------------------


def determinant(matrix: Matrix) -> float:
    """The determinant of the LINEAR part -- the area factor, as on Day 102.

    The third row of an affine matrix is (0, 0, 1), so the full 3 by 3
    determinant equals the 2 by 2 determinant of the top-left block:

        a*d - b*c   where the block is [[a, b], [c, d]]

    Compute it directly rather than via NumPy, so that whole numbers stay
    exact. Day 102 measured this: numpy.linalg.det can return 7.000000000000001
    where the direct formula returns exactly 7.

    Worked example. determinant(shear_x(9)) is exactly 1.0.
    determinant(flip_horizontal(9)) is exactly -1.0.
    """
    raise NotImplementedError("Exercise 1.8: compute the determinant")


# -- Exercise 1.9 -------------------------------------------------------------


def invert(matrix: Matrix) -> Matrix:
    """Invert an affine 3 by 3 matrix, using its structure rather than brute force.

    Write the matrix as a linear part A and a translation column t:

        M = [ A  t ]      M^-1 = [ A^-1   -A^-1 t ]
            [ 0  1 ]             [  0         1   ]

    So: invert the 2 by 2 block the Day 102 way (swap a and d, negate b and c,
    divide everything by the determinant), then apply that inverted block to
    the translation column and negate the result.

        A^-1 = (1/det) * [[ d, -b],
                          [-c,  a]]

    Raise `SingularTransform` when abs(determinant) <= TOL. A transformation
    that flattens the picture onto a line has thrown information away, and no
    arithmetic puts it back.

    One cosmetic detail worth copying: add 0.0 to each entry before returning
    it. Negating a 0.0 -- which every translation and every axis-aligned scale
    has -- produces -0.0, which compares equal to 0.0 but PRINTS as "-0.0" and
    turns up as noise in every coefficient tuple. Adding 0.0 normalises it.

    Worked example. invert(translation(3, -2)) is translation(-3, 2).
    invert(shear_x(2)) is shear_x(-2).
    """
    raise NotImplementedError("Exercise 1.9: invert the matrix")


# -- Exercise 1.10 ------------------------------------------------------------


def warp_forward(image, matrix: Matrix, out_shape=None, fill=0):
    """Forward mapping: push every INPUT pixel to where it lands. This is WRONG.

    You are writing it anyway, because seeing it fail is the argument for the
    method in 1.11. Do not fix it. The holes are the result.

    The algorithm:

        make an output array of `out_shape`, filled with `fill`
        make a boolean array the same shape, all False, called `written`
        for each input pixel (y, x):
            send its CENTRE, (x + SAMPLE_OFFSET, y + SAMPLE_OFFSET), through
                the matrix with apply_point
            floor both results to get the output pixel (ox, oy)
            if that pixel is inside the output:
                out[oy, ox] = image[y, x]
                written[oy, ox] = True

    Return the pair `(out, holes)` where `holes` is the boolean array that is
    True wherever nothing was ever written -- that is, `~written`.

    NumPy is fine here: `numpy.full(shape, fill, dtype=src.dtype)` and
    `numpy.zeros(shape, dtype=bool)`. It is holding pixels, not doing your
    maths.

    Worked example. A 30 degree rotation of the 9 by 9 test pattern about its
    centre leaves 22 of the 81 output pixels unwritten. If you get 22, you have
    it right -- including the ones punched through the middle of the glyph.
    """
    raise NotImplementedError("Exercise 1.10: forward mapping, holes and all")


# -- Exercise 1.11 ------------------------------------------------------------


def warp_nearest_with_inverse(image, inverse: Matrix, out_shape=None, fill=0):
    """Inverse mapping with nearest-neighbour sampling. This is the RIGHT way.

    Turn the loop inside out. Walk the OUTPUT, not the input:

        make an output array of `out_shape`, filled with `fill`
        for each output pixel (oy, ox):
            take its CENTRE, (ox + SAMPLE_OFFSET, oy + SAMPLE_OFFSET)
            send it through `inverse` with apply_point
            floor both results to get the input pixel (ix, iy)
            if that pixel is inside the input:
                out[oy, ox] = image[iy, ix]
            otherwise leave the fill value -- the source is off the picture,
                which is clipping, and clipping is a decision, not an error

    Every output pixel is visited exactly once, so holes are impossible. Not
    because you were careful: because of which array the loop is over.

    Note the argument. This takes the OUTPUT-to-INPUT matrix, already inverted,
    because that is the form Pillow's coefficients come in and exercise 6
    hands both implementations the identical six numbers.

    Two details that decide whether you match Pillow exactly:
      * SAMPLE_OFFSET, the half. Leave it out and everything is half a pixel
        adrift, which looks like a mysterious blur rather than like an offset.
      * `math.floor`, not `round` and not `int`. You want the input pixel whose
        SQUARE contains the point. `int` truncates toward zero, which is wrong
        for negatives; `round` is a different rule entirely.

    Worked example. A quarter turn of the test pattern about its centre must
    equal numpy.rot90(img, -1) EXACTLY -- every one of the 81 pixels.
    """
    raise NotImplementedError("Exercise 1.11: inverse mapping, nearest neighbour")


def warp_nearest(image, matrix: Matrix, out_shape=None, fill=0):
    """`warp_nearest_with_inverse`, but taking the transformation you can SEE.

    Written for you, on top of your 1.9 and 1.11. It inverts here, once, rather
    than making every caller remember to.
    """
    return warp_nearest_with_inverse(
        image, invert(matrix), out_shape=out_shape, fill=fill
    )


# -- Exercise 1.12 ------------------------------------------------------------


def to_pillow_coefficients(matrix: Matrix):
    """Turn a visible input-to-output matrix into Pillow's six coefficients.

    Pillow's `Image.transform(size, Image.Transform.AFFINE, coeffs)` takes
    `(a, b, c, d, e, f)` meaning

        input_x = a * output_x + b * output_y + c
        input_y = d * output_x + e * output_y + f

    -- the OUTPUT-to-INPUT direction, which is the INVERSE of the effect you
    see. Day 102 confirmed that direction by experiment and exercise 6 confirms
    it again. Forgetting to invert is the single most common way to get a
    Pillow transform backwards, and it does not raise: it just moves the
    picture the wrong way.

    So: invert the matrix, then read the six numbers off the first two rows,
    left to right, top row first.

    Worked example. to_pillow_coefficients(translation(1, 0)) must be
    (1.0, 0.0, -1.0, 0.0, 1.0, 0.0). Note the minus.
    """
    raise NotImplementedError("Exercise 1.12: read off Pillow's coefficients")


# =============================================================================
# Written for you. Read these -- the tests use them, and two of them are the
# answers to questions the exercises above ask you to think about.
# =============================================================================


def identity() -> Matrix:
    """The transformation that changes nothing."""
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def rotation_quarter_turns(turns: int) -> Matrix:
    """Rotate by an exact multiple of 90 degrees, with integer entries.

    `rotation(math.pi / 2)` is correct but its cosine is 6.123233995736766e-17
    rather than 0.0. Where the answer is meant to be checkable to the exact
    pixel, build the matrix from integers and the float noise never enters.
    """
    cos_t, sin_t = [(1, 0), (0, 1), (-1, 0), (0, -1)][turns % 4]
    return [
        [float(cos_t), float(-sin_t), 0.0],
        [float(sin_t), float(cos_t), 0.0],
        [0.0, 0.0, 1.0],
    ]


def shear_y(k: float) -> Matrix:
    """The other shear: y becomes y + k*x."""
    return [[1.0, 0.0, 0.0], [float(k), 1.0, 0.0], [0.0, 0.0, 1.0]]


def flip_vertical(height: float) -> Matrix:
    """Mirror top-to-bottom inside an image `height` pixels tall."""
    return [[1.0, 0.0, 0.0], [0.0, -1.0, float(height)], [0.0, 0.0, 1.0]]


def about_centre(matrix: Matrix, width: float, height: float) -> Matrix:
    """Do `matrix` about the image's centre instead of its top-left corner.

    Move the centre to the origin, transform, move it back: T(+c) . M . T(-c).
    Three matrices folded into one, which is only possible because translation
    became a matrix. Uses your `compose` and your `translation`.
    """
    cx, cy = width / 2.0, height / 2.0
    return compose(translation(cx, cy), matrix, translation(-cx, -cy))


def matrices_close(a: Matrix, b: Matrix, tol: float = TOL) -> bool:
    """True when two 3 by 3 matrices agree entry by entry within `tol`."""
    return all(abs(a[i][j] - b[i][j]) <= tol for i in range(3) for j in range(3))


def coefficients_to_matrix(coeffs) -> Matrix:
    """Six Pillow coefficients back into a 3 by 3 matrix."""
    a, b, c, d, e, f = coeffs
    return [[a, b, c], [d, e, f], [0.0, 0.0, 1.0]]
