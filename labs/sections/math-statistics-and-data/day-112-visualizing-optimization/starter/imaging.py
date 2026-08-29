"""Exercises 3, 4b, 5 and 6 -- turn arrays into pictures with NumPy and
Pillow's ImageDraw. Work top to bottom: exercise 4b needs your own
`world_to_pixel` from gridviz.py, and exercise 6 reuses exercise 4b's ideas.

`return None` where your code goes; `pytest starter -q` skips what you have
not attempted.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from gridviz import world_to_pixel

# -- given: the colour ramp ---------------------------------------------
#
# Four control points, dark blue (low) through teal and gold to dark red
# (high). The colour choice is not the exercise -- turning a value array
# into pixels is.

_STOPS_T = np.array([0.0, 0.35, 0.65, 1.0])
_STOPS_RGB = np.array(
    [
        [13, 27, 84],
        [29, 78, 216],
        [250, 204, 21],
        [185, 28, 28],
    ]
)


def ramp_color(t: np.ndarray) -> np.ndarray:
    """Given: map an array of values in [0, 1] to an (..., 3) uint8 RGB array."""
    t = np.clip(t, 0.0, 1.0)
    r = np.interp(t, _STOPS_T, _STOPS_RGB[:, 0])
    g = np.interp(t, _STOPS_T, _STOPS_RGB[:, 1])
    b = np.interp(t, _STOPS_T, _STOPS_RGB[:, 2])
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def heatmap_array(Z: np.ndarray) -> np.ndarray:
    """Exercise 3a -- turn a 2D value array into an (n, n, 3) uint8 RGB array.

    Rescale Z to [0, 1] with (Z - Z.min()) / (Z.max() - Z.min()), pass it to
    `ramp_color`, and flip the result vertically before returning it: Z's row
    0 is the SMALLEST y (evaluate_grid's convention), but the TOP of an image
    must show the LARGEST y.

    Approach: `t = (Z - Z.min()) / span`; `colors = ramp_color(t)`; return
    `np.flipud(colors)`.
    """
    return None


def heatmap_png(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path: str,
    width: int | None = None,
    height: int | None = None,
) -> Image.Image:
    """Exercise 3b -- save Z as a heatmap PNG (via heatmap_array) and return
    the Image. Default width/height to Z's own resolution.

    Approach: `arr = heatmap_array(Z)`; `img = Image.fromarray(arr,
    mode="RGB")`; resize if width/height were given and differ; `img.save(path)`;
    return `img`.
    """
    return None


def draw_path_on_heatmap(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path_xy: np.ndarray,
    out_path: str,
    marker_radius: int = 3,
) -> Image.Image:
    """Exercise 4b -- draw a descent path over its heatmap: a line through
    every point, plus a small circle marking each step.

    Build the heatmap at Z's own resolution, then map every (x, y) in
    path_xy to a pixel with `world_to_pixel` and draw a polyline plus a
    circle per point with `PIL.ImageDraw`.

    Approach: `height, width = Z.shape`; build the heatmap; `draw =
    ImageDraw.Draw(img)`; `pixels = [world_to_pixel(x, y, xlim, ylim, width,
    height) for x, y in path_xy]`; `draw.line(pixels, ...)`; loop over
    `pixels` calling `draw.ellipse` centred on each; save and return `img`.
    """
    return None


def loss_curve_points(
    losses: np.ndarray, width: int, height: int, margin: int, log: bool
) -> list[tuple[float, float]]:
    """Exercise 5a -- map a loss sequence to pixel coordinates.

    x data is the iteration index 0..len(losses)-1. y data is `losses`
    itself if log is False, or `np.log10(losses)` if log is True. Rescale
    both to fit inside [margin, width - margin] and [margin, height -
    margin] respectively, remembering that pixel row 0 is the TOP: a larger
    y-data value must produce a SMALLER pixel row.

    Approach: compute `xs_data = np.arange(len(losses))` and `ys_data =
    np.log10(losses) if log else losses`; find each span; for every (xd, yd)
    compute `px = margin + (xd - x0) / xspan * (width - 2*margin)` and
    `py = (height - margin) - (yd - y0) / yspan * (height - 2*margin)`.
    """
    return None


def loss_curve_png(
    losses: np.ndarray,
    out_path: str,
    log: bool = False,
    width: int = 500,
    height: int = 350,
    margin: int = 50,
) -> Image.Image:
    """Exercise 5b -- draw loss against iteration as a PNG: two axis lines,
    a polyline through `loss_curve_points`, and a small marker per point.

    Approach: create a blank `Image.new("RGB", (width, height), ...)`; draw
    the y-axis and x-axis with `ImageDraw.line`; get `points =
    loss_curve_points(...)`; `draw.line(points, ...)`; loop drawing a small
    `draw.ellipse` at each point; save and return the image.
    """
    return None


def animated_descent_gif(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path_xy: np.ndarray,
    out_path: str,
    duration_ms: int = 150,
) -> None:
    """Exercise 6 -- save one GIF frame per step of a descent: frame k shows
    path_xy[0 : k + 1] drawn over the (shared) heatmap background.

    Approach: build `background = heatmap_array(Z)` once; for k from 1 to
    len(path_xy), copy an Image from `background`, draw the partial path
    with `world_to_pixel` and `ImageDraw` the way exercise 4b does, and
    convert each frame to `"P"` mode (`img.convert("P",
    palette=Image.ADAPTIVE)`) before appending it to a list. Then call
    `frames[0].save(out_path, save_all=True, append_images=frames[1:],
    duration=duration_ms, loop=0, format="GIF")`.
    """
    return None
