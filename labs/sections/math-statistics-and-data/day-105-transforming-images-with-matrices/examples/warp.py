"""Image transformation from first principles: no NumPy in the matrix algebra.

The 3 by 3 matrices here are plain nested lists and the arithmetic is written
out by hand, for the same reason Day 102 gave: if `rotation` returned a NumPy
array built by a NumPy helper, then checking it against NumPy would be checking
NumPy against itself. The arrays that hold PIXELS are NumPy arrays, because an
image is exactly the kind of thing NumPy exists for. The MATHS is ours.

Two conventions, fixed here and obeyed everywhere:

1. A point is written (x, y): x is the COLUMN, y is the ROW. An image array is
   indexed `img[y, x]`. Row is y, column is x, and y grows downward.

2. A transformation matrix is a 3 by 3 homogeneous matrix that maps an INPUT
   point to an OUTPUT point -- the direction you can see. Translation is not a
   linear map (Day 102 proved a linear map cannot move the origin), so a third
   coordinate fixed at 1 is added and translation becomes an ordinary matrix
   multiply:

       [ a  b  tx ] [ x ]   [ a*x + b*y + tx ]
       [ c  d  ty ] [ y ] = [ c*x + d*y + ty ]
       [ 0  0   1 ] [ 1 ]   [        1       ]

   The top-left 2 by 2 block is exactly the linear part from Day 102 -- its
   columns are still where the basis vectors land. The third column is the
   translation, and the bottom row is always (0, 0, 1) for an affine map.
"""

import math

# Every output pixel is a little square. Its CENTRE, not its corner, is the
# point the transformation is evaluated at. Pixel (x, y) covers the square
# from (x, y) to (x + 1, y + 1), so its centre is at (x + 0.5, y + 0.5).
#
# This half is not a detail. It is what makes a shear coefficient move row 0
# even though the shear term is multiplied by y, and it is exactly what Pillow
# does -- verified in `06_against_pillow.py`, not assumed.
SAMPLE_OFFSET = 0.5

TOL = 1e-12


class SingularTransform(ValueError):
    """Raised when a transformation cannot be inverted, so it cannot be applied.

    Inheriting from ValueError mirrors numpy.linalg.LinAlgError, which Day 102
    showed is also a ValueError -- so existing `except ValueError` handlers
    keep working.
    """


# --------------------------------------------------------------------------
# Building the matrices
# --------------------------------------------------------------------------


def identity():
    """The transformation that changes nothing."""
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def translation(tx, ty):
    """Move every point by (tx, ty). NOT a linear map -- it moves the origin.

    This is the whole reason homogeneous coordinates exist. In 2 by 2 there is
    no matrix that adds a constant; in 3 by 3 there is, and it is this one.
    """
    return [[1.0, 0.0, float(tx)], [0.0, 1.0, float(ty)], [0.0, 0.0, 1.0]]


def scaling(sx, sy):
    """Stretch x by sx and y by sy about the origin (the top-left corner)."""
    return [[float(sx), 0.0, 0.0], [0.0, float(sy), 0.0], [0.0, 0.0, 1.0]]


def rotation(theta):
    """Rotate by theta radians about the origin.

    In a y-UP coordinate system this turns counter-clockwise, which is what
    Day 102 drew. On an image y grows DOWNWARD, so the same matrix turns
    CLOCKWISE on screen. Nothing about the matrix changed; the picture is
    upside down relative to the graph paper.
    """
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    return [[cos_t, -sin_t, 0.0], [sin_t, cos_t, 0.0], [0.0, 0.0, 1.0]]


def rotation_quarter_turns(turns):
    """Rotate by an exact multiple of 90 degrees, with integer entries.

    `rotation(math.pi / 2)` is correct but its cosine is 6.123233995736766e-17
    rather than 0.0 -- the Day 102 result. For the cases where the answer
    should be checkable to the exact pixel, build the matrix from integers
    instead of from trigonometry and the float noise never enters.
    """
    cos_t, sin_t = [(1, 0), (0, 1), (-1, 0), (0, -1)][turns % 4]
    return [
        [float(cos_t), float(-sin_t), 0.0],
        [float(sin_t), float(cos_t), 0.0],
        [0.0, 0.0, 1.0],
    ]


def shear_x(k):
    """Slide each row sideways in proportion to its y: x becomes x + k*y."""
    return [[1.0, float(k), 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def shear_y(k):
    """Slide each column vertically in proportion to its x: y becomes y + k*x."""
    return [[1.0, 0.0, 0.0], [float(k), 1.0, 0.0], [0.0, 0.0, 1.0]]


def flip_horizontal(width):
    """Mirror left-to-right inside an image `width` pixels wide.

    A bare reflection `x -> -x` sends the picture off the left edge. What is
    wanted is a reflection about the image's vertical centre line, which is a
    reflection FOLLOWED BY a translation of `width` -- and in homogeneous
    coordinates that is one matrix, not two steps.
    """
    return [[-1.0, 0.0, float(width)], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def flip_vertical(height):
    """Mirror top-to-bottom inside an image `height` pixels tall."""
    return [[1.0, 0.0, 0.0], [0.0, -1.0, float(height)], [0.0, 0.0, 1.0]]


def about_centre(matrix, width, height):
    """Do `matrix` about the image's centre instead of about its top-left corner.

    Move the centre to the origin, transform, move it back. Three matrices,
    composed into one:  T(+c) . M . T(-c).
    """
    cx, cy = width / 2.0, height / 2.0
    return compose(translation(cx, cy), matrix, translation(-cx, -cy))


# --------------------------------------------------------------------------
# Matrix arithmetic, written out
# --------------------------------------------------------------------------


def matmul(a, b):
    """The 3 by 3 product a @ b, computed by hand."""
    return [
        [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)
    ]


def compose(*matrices):
    """Combine transformations into ONE matrix, applied RIGHT to LEFT.

    `compose(B, A)` means "do A first, then B" -- the same order as Day 101's
    matrix product and the same order as reading `B(A(x))` inside out.
    """
    if not matrices:
        return identity()
    result = matrices[0]
    for m in matrices[1:]:
        result = matmul(result, m)
    return result


def apply_point(matrix, point):
    """Send one (x, y) point through the matrix and return the new (x, y)."""
    x, y = point
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2],
    )


def determinant(matrix):
    """The determinant of the LINEAR part -- the area factor, as on Day 102.

    The third row of an affine matrix is (0, 0, 1), so the full 3 by 3
    determinant equals the 2 by 2 determinant of the top-left block.
    """
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def invert(matrix):
    """Invert an affine 3 by 3 matrix, using its structure rather than brute force.

    Write the matrix as a linear part A and a translation t. Then the inverse
    is the inverse of A, followed by minus that inverse applied to t:

        M = [ A  t ]      M^-1 = [ A^-1   -A^-1 t ]
            [ 0  1 ]             [  0         1   ]

    Raises SingularTransform when the determinant is 0 -- a transformation that
    flattens the image onto a line throws information away, and no amount of
    arithmetic can put it back.
    """
    det = determinant(matrix)
    if abs(det) <= TOL:
        raise SingularTransform(
            f"determinant is {det!r}: this transformation collapses the image "
            "and cannot be undone"
        )
    a, b, tx = matrix[0]
    c, d, ty = matrix[1]
    ia, ib = d / det, -b / det
    ic, idd = -c / det, a / det
    # `+ 0.0` normalises negative zero. Negating a 0.0 entry -- which every
    # translation and every axis-aligned scale has -- produces -0.0, which
    # compares equal to 0.0 but PRINTS as "-0.0". That is noise in every
    # coefficient tuple this function feeds, so it is cleaned up once, here.
    return [
        [ia + 0.0, ib + 0.0, -(ia * tx + ib * ty) + 0.0],
        [ic + 0.0, idd + 0.0, -(ic * tx + idd * ty) + 0.0],
        [0.0, 0.0, 1.0],
    ]


def matrices_close(a, b, tol=TOL):
    """True when two 3 by 3 matrices agree entry by entry within `tol`."""
    return all(abs(a[i][j] - b[i][j]) <= tol for i in range(3) for j in range(3))


# --------------------------------------------------------------------------
# The two ways to move pixels
# --------------------------------------------------------------------------


def warp_forward(image, matrix, out_shape=None, fill=0):
    """Forward mapping: push every INPUT pixel to where it lands. This is wrong.

    It is written out in full because seeing it fail is the argument for the
    method that follows. Walk the input, send each pixel through the matrix,
    round to the nearest output pixel, and write the value there.

    The output is full of holes. Nothing in the arithmetic guarantees that the
    input pixels land on output pixels one-to-one: a rotation spreads them out
    so some output pixels are never written at all, and a shrink piles several
    input pixels onto the same output pixel so others are written repeatedly.

    Returns (output_image, hole_mask) where hole_mask is a boolean array that
    is True at every output pixel no input pixel ever reached.
    """
    src = _as_2d(image)
    height, width = src.shape
    out_h, out_w = out_shape or (height, width)

    out = _new_like(src, (out_h, out_w), fill)
    written = _zeros_bool(out_h, out_w)

    for y in range(height):
        for x in range(width):
            # The input pixel's centre, sent through the matrix.
            fx, fy = apply_point(
                matrix, (x + SAMPLE_OFFSET, y + SAMPLE_OFFSET)
            )
            # Which output pixel square does that point fall in?
            ox, oy = math.floor(fx), math.floor(fy)
            if 0 <= ox < out_w and 0 <= oy < out_h:
                out[oy, ox] = src[y, x]
                written[oy, ox] = True
    return out, ~written


def warp_nearest(image, matrix, out_shape=None, fill=0):
    """Inverse mapping with nearest-neighbour sampling. This is the right way.

    Walk the OUTPUT, not the input. For each output pixel, take its centre,
    send it BACKWARD through the inverse matrix to find the place in the input
    it came from, and take the value of whichever input pixel contains that
    place. Every output pixel is visited exactly once, so there are no holes --
    not because the holes were patched, but because the loop is over the array
    being filled.

    `matrix` is the transformation you can SEE: input to output. The inverse is
    taken here, once, rather than being demanded of the caller.
    """
    inverse = invert(matrix)
    return warp_nearest_with_inverse(image, inverse, out_shape=out_shape, fill=fill)


def warp_nearest_with_inverse(image, inverse, out_shape=None, fill=0):
    """The same as `warp_nearest`, but given the OUTPUT-to-INPUT matrix directly.

    This is the form Pillow's `Image.transform` takes its coefficients in, and
    having it separately is what lets `06_against_pillow.py` hand the two
    implementations the identical six numbers.
    """
    src = _as_2d(image)
    height, width = src.shape
    out_h, out_w = out_shape or (height, width)
    out = _new_like(src, (out_h, out_w), fill)

    for oy in range(out_h):
        for ox in range(out_w):
            sx, sy = apply_point(
                inverse, (ox + SAMPLE_OFFSET, oy + SAMPLE_OFFSET)
            )
            # floor, not round: the input pixel whose SQUARE contains the point.
            ix, iy = math.floor(sx), math.floor(sy)
            if 0 <= ix < width and 0 <= iy < height:
                out[oy, ox] = src[iy, ix]
            # Otherwise leave the fill value: the source lies outside the
            # picture. This is the clipping the corners of a rotated image run
            # into, and it is a decision, not an error.
    return out


def warp_bilinear_with_inverse(image, inverse, out_shape=None, fill=0.0):
    """Inverse mapping again, but blending the four pixels around the landing point.

    The inverse-mapped position almost never lands on a pixel exactly.
    Nearest-neighbour answers "which pixel is closest"; bilinear answers "what
    would the value be here", by taking a weighted average of the four
    surrounding pixels, weighted by how close the point is to each.

    The half-pixel bookkeeping is the fiddly part. Pixel (i, j) has its VALUE
    at its centre, (i + 0.5, j + 0.5). So to interpolate between pixel centres,
    subtract the half back off before splitting into whole and fractional
    parts. Getting this wrong shifts the whole image by half a pixel, which
    looks like a mysterious blur rather than like an offset.

    Returns a float array, because an average of integers is not an integer.
    Out-of-range contributions count as `fill`.
    """
    src = _as_2d(image).astype(float)
    height, width = src.shape
    out_h, out_w = out_shape or (height, width)
    out = _zeros_float(out_h, out_w)

    for oy in range(out_h):
        for ox in range(out_w):
            sx, sy = apply_point(
                inverse, (ox + SAMPLE_OFFSET, oy + SAMPLE_OFFSET)
            )
            gx, gy = sx - SAMPLE_OFFSET, sy - SAMPLE_OFFSET
            x0, y0 = math.floor(gx), math.floor(gy)
            tx, ty = gx - x0, gy - y0
            total = 0.0
            for dy in (0, 1):
                for dx in (0, 1):
                    weight = (tx if dx else 1.0 - tx) * (ty if dy else 1.0 - ty)
                    px, py = x0 + dx, y0 + dy
                    inside = 0 <= px < width and 0 <= py < height
                    total += weight * (src[py, px] if inside else float(fill))
            out[oy, ox] = total
    return out


def to_pillow_coefficients(matrix):
    """Turn a visible input-to-output matrix into Pillow's six coefficients.

    Pillow's `Image.transform(..., Image.Transform.AFFINE, coeffs)` takes
    `(a, b, c, d, e, f)` meaning

        input_x = a * output_x + b * output_y + c
        input_y = d * output_x + e * output_y + f

    -- the OUTPUT-to-INPUT direction, which is the inverse of the effect you
    see. Day 102 verified that direction by experiment. So the coefficients are
    read off the INVERSE of the matrix, and forgetting to invert is the single
    most common way to get a Pillow transform backwards.
    """
    inverse = invert(matrix)
    return (
        inverse[0][0],
        inverse[0][1],
        inverse[0][2],
        inverse[1][0],
        inverse[1][1],
        inverse[1][2],
    )


def coefficients_to_matrix(coeffs):
    """The reverse of `to_pillow_coefficients`: six numbers back to a 3 by 3."""
    a, b, c, d, e, f = coeffs
    return [[a, b, c], [d, e, f], [0.0, 0.0, 1.0]]


# --------------------------------------------------------------------------
# Small array helpers, kept apart so the maths above reads cleanly
# --------------------------------------------------------------------------


def _as_2d(image):
    import numpy as np

    arr = np.asarray(image)
    if arr.ndim != 2:
        raise ValueError(
            f"expected a 2-D greyscale array of shape (height, width), got "
            f"shape {arr.shape}. For a colour image, transform each of the "
            f"three planes: img[:, :, 0], img[:, :, 1], img[:, :, 2]."
        )
    return arr


def _new_like(src, shape, fill):
    import numpy as np

    return np.full(shape, fill, dtype=src.dtype)


def _zeros_bool(h, w):
    import numpy as np

    return np.zeros((h, w), dtype=bool)


def _zeros_float(h, w):
    import numpy as np

    return np.zeros((h, w), dtype=float)


def warp_colour(image, matrix, out_shape=None, fill=0):
    """Transform a (height, width, 3) colour image plane by plane.

    There is no new mathematics here, and that is the point worth noticing: the
    transformation acts on COORDINATES, and the three planes share their
    coordinates, so the same matrix does all three.
    """
    import numpy as np

    arr = np.asarray(image)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(
            f"expected a colour array of shape (height, width, 3), got {arr.shape}"
        )
    planes = [
        warp_nearest(arr[:, :, c], matrix, out_shape=out_shape, fill=fill)
        for c in range(3)
    ]
    return np.stack(planes, axis=2)
