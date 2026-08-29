"""Exercises 1, 2 and 4a -- write the three functions below.

Every function has a working signature, a docstring saying exactly what it
must do, and `return None` where your code goes. Returning None is how the
test suite knows you have not attempted it yet: `pytest starter -q` will
SKIP an unattempted function rather than fail it.

Check yourself as you go:

    .venv/bin/pytest starter -q
"""

from __future__ import annotations

import numpy as np

ASCII_RAMP = " .:+#"


def evaluate_grid(f, xlim: tuple[float, float], ylim: tuple[float, float], n: int):
    """Exercise 1 -- evaluate f over an n x n grid spanning xlim x ylim.

    Return (X, Y, Z), each an (n, n) array from numpy.meshgrid: X varies
    along columns, Y varies along rows, and Z = f(X, Y).

    Approach: `xs = np.linspace(xlim[0], xlim[1], n)`, same for ys, then
    `X, Y = np.meshgrid(xs, ys)` and `Z = f(X, Y)`.
    """
    return None


def ascii_contour(Z: np.ndarray, chars: str = ASCII_RAMP) -> str:
    """Exercise 2 -- render a 2D array as text: one character per cell,
    chosen by level band.

    Rescale Z linearly between its own min and max to [0, len(chars)), floor
    to an integer band index, clip to [0, len(chars) - 1], and join each
    row's characters with "\\n" between rows.

    Approach: `zmin, zmax = Z.min(), Z.max()`; `idx = np.clip(((Z - zmin) /
    span * len(chars)).astype(int), 0, len(chars) - 1)`; build one string per
    row from `chars[i]` and join the rows with newlines.
    """
    return None


def world_to_pixel(
    x: float,
    y: float,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    width: int,
    height: int,
) -> tuple[float, float]:
    """Exercise 4a -- map one (x, y) data point to a (column, row) pixel.

    x grows to the right in both spaces (columns increase with x, no flip).
    y grows UPWARD in data space but pixel row 0 is the TOP of the image, so
    row must be computed from (ylim[1] - y), not (y - ylim[0]).

    Approach: `px = (x - xlim[0]) / (xlim[1] - xlim[0]) * (width - 1)`;
    `py = (ylim[1] - y) / (ylim[1] - ylim[0]) * (height - 1)`.
    """
    return None
