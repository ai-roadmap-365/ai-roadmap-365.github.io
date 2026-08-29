"""Exercise 1 -- your linear transformations, built from arithmetic alone.

Ten functions to write. Each one has a docstring saying exactly what it must
do, a worked example you can check on paper, and a `raise NotImplementedError`
to delete when you write it.

Check yourself as you go, from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED rather than failed. A skip means
"not attempted"; a failure means "attempted and wrong", and it prints your
answer beside the real one.

Use only `math` from the standard library in this file. NumPy appears in the
tests, where it checks your work -- which is the right way round. Writing it
yourself and then having a mature library agree is worth far more than either
half on its own.

The one idea everything here is built on:

    A matrix IS a function. Its columns are where the basis vectors land.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
Matrix = list[list[float]]


class SingularMatrix(ValueError):
    """Raised when a matrix has no inverse.

    Written for you. It subclasses ValueError to match NumPy, whose
    `numpy.linalg.LinAlgError` is itself a ValueError -- so `except ValueError`
    catches your version and NumPy's alike.
    """


# -- Exercise 1.1 -------------------------------------------------------------


def from_landings(e1_lands_at: Point, e2_lands_at: Point) -> Matrix:
    """Build the 2 by 2 matrix that sends (1, 0) and (0, 1) to these two points.

    A matrix is written as a list of ROWS, but it MEANS its columns. So if
    (1, 0) lands at (3, 1) and (0, 1) lands at (-1, 2), the matrix is

        [[3, -1],
         [1,  2]]

    -- the first landing place read downwards in the left-hand column, the
    second read downwards in the right-hand column.

    >>> from_landings((3.0, 1.0), (-1.0, 2.0))
    [[3.0, -1.0], [1.0, 2.0]]
    """
    raise NotImplementedError("exercise 1.1: from_landings")


# -- Exercise 1.2 -------------------------------------------------------------


def columns_of(matrix: Matrix) -> tuple[Point, Point]:
    """Return the two columns as points: (where e1 lands, where e2 lands).

    The exact inverse of exercise 1.1. For [[a, b], [c, d]] the answer is
    ((a, c), (b, d)).

    >>> columns_of([[3.0, -1.0], [1.0, 2.0]])
    ((3.0, 1.0), (-1.0, 2.0))
    """
    raise NotImplementedError("exercise 1.2: columns_of")


# -- Exercise 1.3 -------------------------------------------------------------


def apply(matrix: Matrix, point: Point) -> Point:
    """Send one point through the transformation.

    Write it the way the idea is stated, not the way a textbook writes it: the
    answer is x lots of the first column, plus y lots of the second.

        apply(M, (x, y)) = x * (where e1 landed) + y * (where e2 landed)

    That is the same arithmetic as the row-by-row rule and it says out loud why
    the columns are the landing places. Hint: `columns_of` is already written
    by the time you get here.

    >>> apply([[3.0, -1.0], [1.0, 2.0]], (2.0, 1.0))
    (5.0, 4.0)
    """
    raise NotImplementedError("exercise 1.3: apply")


# -- Exercise 1.4 -------------------------------------------------------------


def scaling(sx: float, sy: float) -> Matrix:
    """Stretch by sx across and sy up.

    Derive it, do not look it up. Where does (1, 0) -- one step right -- go
    when the plane is stretched sx times horizontally? Where does (0, 1) go?
    Write the two answers down as columns with `from_landings`.

    >>> scaling(2.0, 3.0)
    [[2.0, 0.0], [0.0, 3.0]]
    """
    raise NotImplementedError("exercise 1.4: scaling")


# -- Exercise 1.5 -------------------------------------------------------------


def reflection_in_x_axis() -> Matrix:
    """Mirror the plane in the horizontal axis: up becomes down.

    Derive it. (1, 0) lies ON the mirror line, so ask yourself whether it can
    move at all. (0, 1) is one step up -- where is its reflection?

    >>> reflection_in_x_axis()
    [[1.0, 0.0], [0.0, -1.0]]
    """
    raise NotImplementedError("exercise 1.5: reflection_in_x_axis")


# -- Exercise 1.6 -------------------------------------------------------------


def shear_x(k: float) -> Matrix:
    """Push the plane sideways by k times its height.

    A shear slides each point sideways in proportion to how high it is -- the
    deck of cards pushed over, where the bottom card does not move and the top
    one moves furthest.

    Derive it. (1, 0) has height 0, so how far is it pushed? (0, 1) has height
    1, so how far is it pushed, and where does it end up?

    >>> shear_x(2.0)
    [[1.0, 2.0], [0.0, 1.0]]
    """
    raise NotImplementedError("exercise 1.6: shear_x")


# -- Exercise 1.7 -------------------------------------------------------------


def rotation(theta: float) -> Matrix:
    """Turn the plane anticlockwise by theta RADIANS about the origin.

    The derivation, which needs the unit circle and nothing else:

      * draw a circle of radius 1 about the origin;
      * start at (1, 0) and walk anticlockwise around the rim until you have
        turned through theta;
      * the coordinates of where you now stand are, BY DEFINITION,
        (cos(theta), sin(theta)). That is what cosine and sine ARE.

    So (1, 0) lands at (cos(theta), sin(theta)).

    For (0, 1): it is (1, 0) already turned a quarter turn, so after turning by
    theta it sits a quarter turn ahead of the first landing place. A quarter
    turn anticlockwise sends any (x, y) to (-y, x). Apply that to
    (cos(theta), sin(theta)) and you have the second column.

    Radians: an angle measured as distance walked around the rim of that unit
    circle. A full turn is 2 * pi, so a quarter turn is pi / 2. Use
    `math.cos`, `math.sin`, and `math.radians` if you would rather think in
    degrees.

    >>> [round(v, 10) for row in rotation(math.pi / 2) for v in row]
    [0.0, -1.0, 1.0, 0.0]
    """
    raise NotImplementedError("exercise 1.7: rotation")


# -- Exercise 1.8 -------------------------------------------------------------


def compose(second: Matrix, first: Matrix) -> Matrix:
    """Return the single matrix that does `first` and then `second`.

    Mind the argument order, and mind that it is not arbitrary. Applying
    `first` and then `second` to a vector v is

        second @ (first @ v)

    so the single matrix that does both is `second @ first`: the step that
    happens FIRST is written on the RIGHT, because it is the one standing next
    to the vector.

    Build it the day's way rather than with the row-by-column rule: column 0 of
    the answer is wherever (1, 0) ends up after BOTH steps, and column 1 is
    wherever (0, 1) ends up. Two calls to `apply` and one to `from_landings`.

    >>> compose([[0.0, -1.0], [1.0, 0.0]], [[1.0, 2.0], [0.0, 1.0]])
    [[0.0, -1.0], [1.0, 2.0]]
    """
    raise NotImplementedError("exercise 1.8: compose")


# -- Exercise 1.9 -------------------------------------------------------------


def determinant(matrix: Matrix) -> float:
    """The factor by which this transformation multiplies area, sign included.

    For [[a, b], [c, d]] it is a*d - b*c. Compute exactly that -- one multiply,
    one multiply, one subtract -- so that whole-number inputs give an exact
    whole-number answer.

    What the number means, which matters more than the formula:

      * its size is the area factor: a unit square of area 1 comes out with
        area |determinant|;
      * negative means the plane was flipped over;
      * zero means the plane was flattened onto a line, and nothing can undo it.

    >>> determinant([[3.0, -1.0], [1.0, 2.0]])
    7.0
    >>> determinant([[1.0, 2.0], [2.0, 4.0]])
    0.0
    """
    raise NotImplementedError("exercise 1.9: determinant")


# -- Exercise 1.10 ------------------------------------------------------------


def inverse(matrix: Matrix) -> Matrix:
    """The transformation that undoes this one.

    For 2 by 2, the inverse of [[a, b], [c, d]] is

        1 / determinant  *  [[d, -b], [-c, a]]

    and it exists exactly when the determinant is not zero -- which is the same
    sentence as "exactly when no area was destroyed". If two starting points
    landed on the same place, no rule could send that place back to both, so
    there is nothing to return.

    So: compute the determinant first. If it is zero, `raise SingularMatrix`
    with a message that says why. Otherwise divide each of the four rearranged
    entries by it.

    >>> inverse([[1.0, 2.0], [0.0, 1.0]])
    [[1.0, -2.0], [0.0, 1.0]]
    """
    raise NotImplementedError("exercise 1.10: inverse")


# =============================================================================
# Written for you below this line -- read them, they are used by the tests.
# =============================================================================


def identity() -> Matrix:
    """The do-nothing transformation."""
    return [[1.0, 0.0], [0.0, 1.0]]


def transform_polygon(matrix: Matrix, polygon: list[Point]) -> list[Point]:
    """Send every corner of a polygon through the transformation.

    Corners are enough, because a linear transformation sends straight lines to
    straight lines -- which is exactly what makes it cheap, and exactly what
    stops any stack of them ever drawing a curve.
    """
    return [apply(matrix, point) for point in polygon]


def signed_area(polygon: list[Point]) -> float:
    """The area of a polygon, negative if its corners run clockwise.

    The shoelace formula, given to you because measuring polygons is not what
    today is about: walk the corners in order and for each edge add
    x_here * y_next - x_next * y_here, then halve the total.

    The SIGN is the part this lab uses. Corners listed anticlockwise give a
    positive area; a transformation with a negative determinant turns the shape
    over and the same corners now run clockwise, so the answer comes out
    negative. That is "the plane was flipped" measured rather than asserted.
    """
    total = 0.0
    count = len(polygon)
    for i in range(count):
        x_here, y_here = polygon[i]
        x_next, y_next = polygon[(i + 1) % count]
        total += x_here * y_next - x_next * y_here
    return total / 2.0


def rank(matrix: Matrix, tol: float = 1e-12) -> int:
    """How many dimensions survive: 2 fills the plane, 1 a line, 0 the origin."""
    if abs(determinant(matrix)) > tol:
        return 2
    if any(abs(entry) > tol for row in matrix for entry in row):
        return 1
    return 0
