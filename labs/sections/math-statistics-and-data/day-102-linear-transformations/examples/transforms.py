"""Linear transformations of the plane, built from nothing but arithmetic.

The reference implementation. Everything here works on plain Python lists and
tuples, uses only `math` from the standard library, and never imports NumPy --
so you can read every line and see exactly what a transformation is doing. The
scripts beside this file then check all of it against NumPy, which is the only
way to know that "I wrote it myself" and "it is right" are both true.

The one idea the whole module is built on:

    A matrix IS a function. Its columns are where the basis vectors land.

Column 0 is where (1, 0) goes. Column 1 is where (0, 1) goes. Everything else
follows, because every vector (x, y) is x * (1, 0) + y * (0, 1), and a linear
transformation is exactly one that keeps that combination intact.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
Matrix = list[list[float]]


class SingularMatrix(ValueError):
    """Raised when a matrix has no inverse.

    Subclasses ValueError deliberately, to match NumPy: `numpy.linalg.inv` on a
    matrix with no inverse raises `numpy.linalg.LinAlgError`, and that class is
    itself a subclass of ValueError. So `except ValueError` catches both, and
    code written against one behaves the same against the other.
    """


# -- Reading a matrix, and reading it back -------------------------------------


def columns_of(matrix: Matrix) -> tuple[Point, Point]:
    """Return the two columns as points: (where e1 lands, where e2 lands).

    A 2 by 2 matrix is written as rows -- [[a, b], [c, d]] -- but it MEANS its
    columns. Column 0 is (a, c) and column 1 is (b, d). Half of all confusion
    about transformation matrices is reading (a, b) as a landing place when it
    is a row.
    """
    (a, b), (c, d) = matrix
    return (a, c), (b, d)


def from_landings(e1_lands_at: Point, e2_lands_at: Point) -> Matrix:
    """Build the matrix that sends (1, 0) and (0, 1) to the two given points.

    This is the whole day in four lines. If you can see where the basis vectors
    land, you can write the matrix down, and the matrix then tells you where
    every other vector lands without you having to look at the picture again.
    """
    (a, c), (b, d) = e1_lands_at, e2_lands_at
    return [[a, b], [c, d]]


# -- Applying and composing ----------------------------------------------------


def apply(matrix: Matrix, point: Point) -> Point:
    """Send one point through the transformation.

    Written the way the idea is stated rather than the way a textbook writes
    it: the answer is x lots of the first column plus y lots of the second.
    That is the same arithmetic as the usual row-by-row rule, but it says out
    loud why the columns are the landing places.
    """
    x, y = point
    (e1x, e1y), (e2x, e2y) = columns_of(matrix)
    return (x * e1x + y * e2x, x * e1y + y * e2y)


def compose(second: Matrix, first: Matrix) -> Matrix:
    """Return the single matrix that does `first` and then `second`.

    Note the argument order, and note that it is not an accident. Written out,
    applying `first` and then `second` to a vector v is

        second @ (first @ v)

    and the matrix that does both in one step is `second @ first` -- the one
    that happens FIRST is written on the RIGHT, because it is the one standing
    next to the vector. Reading a product right to left is not a quirk to
    memorise; it is what the notation means.

    The product is built one column at a time, which is again the day's idea:
    column 0 of the answer is wherever (1, 0) ends up after both steps.
    """
    e1, e2 = columns_of(first)
    return from_landings(apply(second, e1), apply(second, e2))


def identity() -> Matrix:
    """The do-nothing transformation: e1 stays at (1, 0), e2 stays at (0, 1)."""
    return [[1.0, 0.0], [0.0, 1.0]]


# -- The four standard transformations, each DERIVED from its landings ---------


def scaling(sx: float, sy: float) -> Matrix:
    """Stretch by sx horizontally and sy vertically.

    Derivation: (1, 0) is one step right, and stretching horizontally by sx
    makes it sx steps right, so it lands at (sx, 0). (0, 1) is one step up and
    lands at (0, sy). Write those two down as columns and you have the matrix.
    """
    return from_landings((sx, 0.0), (0.0, sy))


def reflection_in_x_axis() -> Matrix:
    """Mirror the plane in the horizontal axis: up becomes down.

    Derivation: (1, 0) already lies on the mirror line, so it does not move.
    (0, 1) is one step up, and its mirror image is one step down, at (0, -1).
    """
    return from_landings((1.0, 0.0), (0.0, -1.0))


def reflection_in_y_axis() -> Matrix:
    """Mirror the plane in the vertical axis: right becomes left."""
    return from_landings((-1.0, 0.0), (0.0, 1.0))


def shear_x(k: float) -> Matrix:
    """Push the plane sideways by k times its height.

    Derivation: a point's sideways push is proportional to how high it is.
    (1, 0) has height 0, so it is pushed by nothing and does not move. (0, 1)
    has height 1, so it is pushed k to the right and lands at (k, 1).

    This is the transformation to picture when someone says a deck of cards
    slid sideways: the bottom card stays put, every card above it slides
    further, and the deck's volume never changes.
    """
    return from_landings((1.0, 0.0), (k, 1.0))


def shear_y(k: float) -> Matrix:
    """Push the plane upwards by k times its horizontal distance."""
    return from_landings((1.0, k), (0.0, 1.0))


def rotation(theta: float) -> Matrix:
    """Turn the whole plane anticlockwise by theta RADIANS about the origin.

    Derivation, which needs the unit circle and nothing else. Draw a circle of
    radius 1 around the origin. Start at (1, 0) and walk anticlockwise around
    the rim until you have turned through an angle theta. The two numbers that
    name where you now stand are, by definition, the cosine and the sine of
    theta: cos(theta) across, sin(theta) up. That is what those two functions
    ARE -- the coordinates of a point on the unit circle -- and every identity
    about them is a fact about that picture.

    So (1, 0) lands at (cos(theta), sin(theta)).

    (0, 1) is (1, 0) already turned a quarter of a turn anticlockwise, and
    turning it a further theta puts it a quarter turn ahead of the first
    landing place. A quarter turn anticlockwise sends any point (x, y) to
    (-y, x) -- push it round and the across-ness becomes up-ness. Applying
    that to (cos(theta), sin(theta)) gives (-sin(theta), cos(theta)).

    Write the two landings as columns:

        [[cos(theta), -sin(theta)],
         [sin(theta),  cos(theta)]]

    which is the rotation matrix, derived rather than remembered.

    Radians, briefly: an angle measured as the distance you walked around the
    rim of that unit circle. A full turn is the whole circumference, 2 * pi. So
    a quarter turn is pi / 2, and `math.radians(90)` converts if you would
    rather think in degrees.
    """
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    return from_landings((cos_t, sin_t), (-sin_t, cos_t))


# -- Determinant, inverse, rank ------------------------------------------------


def determinant(matrix: Matrix) -> float:
    """The factor by which the transformation multiplies area, sign included.

    For a 2 by 2 matrix [[a, b], [c, d]] the answer is a*d - b*c, and this
    function computes that exactly -- one multiply, one multiply, one subtract.
    No rearrangement, so no rounding beyond the inputs themselves.

    What the number means:

      * its SIZE is the area factor. A unit square of area 1 comes out with
        area |determinant|.
      * its SIGN is the orientation. Positive means the plane was not flipped
        over; negative means it was, and a shape listed anticlockwise comes out
        listed clockwise.
      * ZERO means the plane was flattened onto a line or onto a point. Area
        1 became area 0, information was destroyed, and nothing can undo it.
    """
    (a, b), (c, d) = matrix
    return a * d - b * c


def inverse(matrix: Matrix) -> Matrix:
    """The transformation that undoes this one.

    Derived by asking the only question that matters: which matrix, composed
    with this one, leaves everything where it started? For 2 by 2 the answer is
    the standard formula, one over the determinant times [[d, -b], [-c, a]].

    It exists precisely when the determinant is not zero, which is the same
    sentence as "precisely when no area was destroyed". If two different
    starting points landed on the same place, no rule could send that place
    back to both of them, so there is nothing to return.
    """
    det = determinant(matrix)
    if det == 0.0:
        raise SingularMatrix(
            "Singular matrix: the determinant is 0, so this transformation "
            "collapses the plane and cannot be undone"
        )
    (a, b), (c, d) = matrix
    return [[d / det, -b / det], [-c / det, a / det]]


def rank(matrix: Matrix, tol: float = 1e-12) -> int:
    """How many dimensions survive the transformation.

    Plain language: feed the whole plane in, and look at what comes out. If the
    output fills the plane, the rank is 2. If it is squashed onto a line, the
    rank is 1. If everything lands on the origin, the rank is 0.

    For a 2 by 2 matrix that reads straight off the columns. If the determinant
    is not zero the two columns point in genuinely different directions and
    between them they reach everywhere, so the rank is 2. If the determinant is
    zero but at least one column is not the zero vector, everything lands on
    the line through that column, so the rank is 1. If both columns are zero,
    everything lands on the origin and the rank is 0.

    `tol` is here because the determinant of a matrix built from cosines will
    rarely be exactly 0.0, and asking `== 0` of a computed float is how you get
    a rank of 2 for a matrix that has plainly collapsed.
    """
    if abs(determinant(matrix)) > tol:
        return 2
    if any(abs(entry) > tol for row in matrix for entry in row):
        return 1
    return 0


# -- Polygons ------------------------------------------------------------------


def transform_polygon(matrix: Matrix, polygon: list[Point]) -> list[Point]:
    """Send every corner of a polygon through the transformation.

    Corners are enough. A linear transformation sends straight lines to
    straight lines, so the edges take care of themselves -- which is exactly
    the property that makes these transformations cheap, and exactly the
    property that stops a stack of them ever drawing a curve.
    """
    return [apply(matrix, point) for point in polygon]


def signed_area(polygon: list[Point]) -> float:
    """The area of a polygon, negative if its corners run clockwise.

    The shoelace formula: walk the corners in order, and for each edge add
    x_here * y_next - x_next * y_here. Halve the total. It is called the
    shoelace formula because the cross-multiplied pairs criss-cross like the
    lacing on a shoe.

    The sign is the part this lab uses. List the unit square anticlockwise and
    the signed area is +1; transform it by a matrix with a negative determinant
    and the signed area comes out negative, because the corners now run the
    other way round. That is what "the plane was flipped over" means when it is
    measured rather than described.
    """
    total = 0.0
    count = len(polygon)
    for i in range(count):
        x_here, y_here = polygon[i]
        x_next, y_next = polygon[(i + 1) % count]
        total += x_here * y_next - x_next * y_here
    return total / 2.0


# -- Linearity -----------------------------------------------------------------


def preserves_addition(
    func, u: Point, v: Point, tol: float = 1e-12
) -> tuple[bool, Point, Point]:
    """Test whether func(u + v) equals func(u) + func(v).

    The first half of the definition of linear. Returns the verdict and both
    sides, because when a function fails this test the interesting part is not
    that it failed -- it is by how much, and whether the gap is the same every
    time.
    """
    together = func((u[0] + v[0], u[1] + v[1]))
    separately = tuple(a + b for a, b in zip(func(u), func(v)))
    ok = all(abs(a - b) <= tol for a, b in zip(together, separately))
    return ok, together, separately  # type: ignore[return-value]


def preserves_scaling(
    func, u: Point, s: float, tol: float = 1e-12
) -> tuple[bool, Point, Point]:
    """Test whether func(s * u) equals s * func(u).

    The second half of the definition. A function needs BOTH halves to be
    linear, and a function that fails either one cannot be written as a matrix,
    no matter how simple it looks.
    """
    scaled_first = func((s * u[0], s * u[1]))
    scaled_after = tuple(s * component for component in func(u))
    ok = all(abs(a - b) <= tol for a, b in zip(scaled_first, scaled_after))
    return ok, scaled_first, scaled_after  # type: ignore[return-value]


def is_linear(func, u: Point, v: Point, s: float, tol: float = 1e-12) -> bool:
    """Both halves at once, on one chosen pair of vectors and one scalar.

    An honest caveat, and it matters: passing this on one example does not
    prove a function is linear. The definition quantifies over EVERY pair of
    vectors and every scalar, and no finite number of examples can settle that.
    What a test like this does well is the other direction -- a single failure
    is a complete disproof, and that is how it is used here.
    """
    return (
        preserves_addition(func, u, v, tol)[0]
        and preserves_scaling(func, u, s, tol)[0]
    )
