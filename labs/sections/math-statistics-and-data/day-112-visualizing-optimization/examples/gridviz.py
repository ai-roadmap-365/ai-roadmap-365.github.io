"""Exercise 1, 2 and the world-to-pixel half of exercise 4: seeing a surface
before drawing anything on top of it.

Every picture in this lab starts from the same three-step recipe: evaluate a
function over a grid, decide how a value maps to something visible (a
character, a colour, a pixel), and read the result back to confirm the axes
did not get flipped along the way. This module is that recipe with nothing
plotted yet -- the terminal-only version of a contour plot.
"""

from __future__ import annotations

import numpy as np

# A five-character ramp, darkest (lowest value) to densest (highest value).
# Five bands is deliberately coarse: it is legible in a terminal and it is
# small enough that a specific character at a specific cell is a real
# assertion, not a fuzzy visual check.
ASCII_RAMP = " .:+#"


def evaluate_grid(f, xlim: tuple[float, float], ylim: tuple[float, float], n: int):
    """Evaluate f over an n x n grid spanning xlim x ylim.

    Returns (X, Y, Z), each an (n, n) array from numpy.meshgrid: X varies
    along columns, Y varies along rows, and Z = f(X, Y). This is the one
    building block every picture in this lab is made from -- a contour plot,
    a heatmap and a 3D surface are three different ways of drawing the same
    (X, Y, Z) triple.
    """
    xs = np.linspace(xlim[0], xlim[1], n)
    ys = np.linspace(ylim[0], ylim[1], n)
    X, Y = np.meshgrid(xs, ys)
    Z = f(X, Y)
    return X, Y, Z


def ascii_contour(Z: np.ndarray, chars: str = ASCII_RAMP) -> str:
    """Render a 2D array as text: one character per cell, chosen by level band.

    Values are rescaled to [0, len(chars)) linearly between Z's own min and
    max, then floored into a band index. This is the crudest possible contour
    renderer -- level BANDS shaded by character, not level LINES traced
    between them -- and that crudeness is the point: get it wrong (a
    transposed grid, a flipped row order) and a symmetric bowl stops looking
    symmetric immediately, in a terminal, with no image viewer required.
    """
    zmin, zmax = float(Z.min()), float(Z.max())
    span = zmax - zmin if zmax > zmin else 1.0
    n_bands = len(chars)
    idx = np.clip(((Z - zmin) / span * n_bands).astype(int), 0, n_bands - 1)
    return "\n".join("".join(chars[i] for i in row) for row in idx)


def world_to_pixel(
    x: float,
    y: float,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    width: int,
    height: int,
) -> tuple[float, float]:
    """Map one (x, y) point in data coordinates to a (column, row) pixel.

    Two axis flips have to happen correctly here and nowhere else in the
    lab -- every drawing function in imaging.py calls this one function
    instead of repeating the arithmetic, so a bug in the mapping shows up
    once, here, and is testable in isolation:

      * x grows to the RIGHT in both spaces, so columns increase with x --
        no flip.
      * y grows UPWARD in data space but DOWNWARD in pixel rows (row 0 is the
        top of the image), so pixel row is computed from (ylim[1] - y), not
        (y - ylim[0]).

    Getting the y flip backwards is the single most common bug in this lab:
    the heatmap looks fine on its own (it is vertically symmetric for a bowl
    centred at the origin) but the path drawn on top of it walks toward the
    WRONG edge, and exercise 4 is built to catch exactly that.
    """
    px = (x - xlim[0]) / (xlim[1] - xlim[0]) * (width - 1)
    py = (ylim[1] - y) / (ylim[1] - ylim[0]) * (height - 1)
    return px, py
