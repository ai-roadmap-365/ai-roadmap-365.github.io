"""Exercises 3, 4 and 6: turning arrays into pictures with nothing but NumPy
and Pillow's ImageDraw.

No matplotlib, no scipy. A heatmap is a NumPy array of colours turned into an
Image; a path is a polyline and a handful of circles drawn with ImageDraw; an
animation is a list of frames saved with save_all=True. That is the entire
technique stack this module needs.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from gridviz import world_to_pixel

# -- the colour ramp -----------------------------------------------------
#
# Four control points, dark blue (low) through teal and gold to dark red
# (high). Perceptual accuracy is not the point here -- matplotlib's "viridis"
# and friends exist for that, and are covered in the lesson's tools section --
# the point is that a value maps to a colour through an explicit, inspectable
# rule with named stops, not a library call whose internals are invisible.

_STOPS_T = np.array([0.0, 0.35, 0.65, 1.0])
_STOPS_RGB = np.array(
    [
        [13, 27, 84],  # low value: dark blue
        [29, 78, 216],  # blue
        [250, 204, 21],  # gold
        [185, 28, 28],  # high value: dark red
    ]
)


def ramp_color(t: np.ndarray) -> np.ndarray:
    """Map an array of values in [0, 1] to an (..., 3) array of uint8 RGB.

    Piecewise-linear interpolation through the four stops above, one channel
    at a time via numpy.interp -- the same technique matplotlib's own
    colormaps use internally, just with four hand-picked stops instead of
    a few hundred.
    """
    t = np.clip(t, 0.0, 1.0)
    r = np.interp(t, _STOPS_T, _STOPS_RGB[:, 0])
    g = np.interp(t, _STOPS_T, _STOPS_RGB[:, 1])
    b = np.interp(t, _STOPS_T, _STOPS_RGB[:, 2])
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def heatmap_array(Z: np.ndarray) -> np.ndarray:
    """Turn a 2D value array into an (n, n, 3) uint8 RGB array, ready for
    Image.fromarray.

    Z's row 0 corresponds to ylim[0] (evaluate_grid's convention, since
    numpy.meshgrid puts the smallest y in the first row) -- but the TOP of an
    image is the LARGEST y, so the array is flipped vertically before it
    becomes an image. This is the one deliberate axis flip in this function;
    world_to_pixel performs the matching flip for anything drawn on top.
    """
    zmin, zmax = float(Z.min()), float(Z.max())
    span = zmax - zmin if zmax > zmin else 1.0
    t = (Z - zmin) / span
    colors = ramp_color(t)
    return np.flipud(colors)


def heatmap_png(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path: str,
    width: int | None = None,
    height: int | None = None,
) -> Image.Image:
    """Save Z as a heatmap PNG and return the Image.

    width/height default to Z's own resolution (one pixel per grid cell),
    which keeps world_to_pixel exact: pixel (0, 0) is (xlim[0], ylim[1]) and
    pixel (n-1, n-1) is (xlim[1], ylim[0]).
    """
    arr = heatmap_array(Z)
    img = Image.fromarray(arr, mode="RGB")
    if width is not None and height is not None and (width, height) != (arr.shape[1], arr.shape[0]):
        img = img.resize((width, height), Image.NEAREST)
    img.save(path)
    return img


def draw_path_on_heatmap(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path_xy: np.ndarray,
    out_path: str,
    marker_radius: int = 3,
) -> Image.Image:
    """Draw a descent path over its heatmap: a line through every point, plus
    a small circle marking each step.

    The heatmap is built at the grid's own resolution and the path is drawn
    on top of it at that SAME resolution, so world_to_pixel(xlim, ylim,
    width, height) uses the image's actual size rather than a guess -- the
    one place a mismatched width/height would silently misplace every point.
    """
    height, width = Z.shape[0], Z.shape[1]
    img = heatmap_png(Z, xlim, ylim, out_path, width=width, height=height)
    draw = ImageDraw.Draw(img)

    pixels = [world_to_pixel(x, y, xlim, ylim, width, height) for x, y in path_xy]
    if len(pixels) >= 2:
        draw.line(pixels, fill=(255, 255, 255), width=2)
    for px, py in pixels:
        draw.ellipse(
            [px - marker_radius, py - marker_radius, px + marker_radius, py + marker_radius],
            fill=(255, 255, 255),
            outline=(20, 20, 20),
        )
    img.save(out_path)
    return img


def loss_curve_points(
    losses: np.ndarray, width: int, height: int, margin: int, log: bool
) -> list[tuple[float, float]]:
    """Map a loss sequence to pixel coordinates, for drawing OR for testing
    that the log-scale points are collinear.

    Kept separate from loss_curve_png so a test can check the geometry the
    picture is actually built from, rather than re-deriving it in prose.
    """
    losses = np.asarray(losses, dtype=float)
    n = len(losses)
    xs_data = np.arange(n, dtype=float)
    ys_data = np.log10(np.clip(losses, 1e-300, None)) if log else losses

    x0, x1 = 0.0, float(n - 1) if n > 1 else 1.0
    y0, y1 = float(ys_data.min()), float(ys_data.max())
    xspan = x1 - x0 if x1 > x0 else 1.0
    yspan = y1 - y0 if y1 > y0 else 1.0

    points = []
    for xd, yd in zip(xs_data, ys_data):
        px = margin + (xd - x0) / xspan * (width - 2 * margin)
        py = (height - margin) - (yd - y0) / yspan * (height - 2 * margin)
        points.append((px, py))
    return points


def loss_curve_png(
    losses: np.ndarray,
    out_path: str,
    log: bool = False,
    width: int = 500,
    height: int = 350,
    margin: int = 50,
) -> Image.Image:
    """Draw loss against iteration as a PNG: axes, a polyline, and a marker
    per point. log=True plots log10(loss) on the y-axis instead of loss."""
    img = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.line([(margin, margin // 2), (margin, height - margin)], fill=(26, 32, 44), width=2)
    draw.line(
        [(margin, height - margin), (width - margin // 2, height - margin)],
        fill=(26, 32, 44),
        width=2,
    )
    points = loss_curve_points(losses, width, height, margin, log)
    if len(points) >= 2:
        draw.line(points, fill=(29, 78, 216), width=2)
    for px, py in points:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(29, 78, 216))
    img.save(out_path)
    return img


def animated_descent_gif(
    Z: np.ndarray,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    path_xy: np.ndarray,
    out_path: str,
    duration_ms: int = 150,
) -> None:
    """Save one GIF frame per step of a descent, the path built up one point
    at a time, over the same heatmap.

    Frame k shows path_xy[0 : k + 1] -- so the FIRST frame is a single
    marker at the start, and the LAST frame is the complete path drawn by
    draw_path_on_heatmap. Pillow's save(..., save_all=True) is the entire
    animation mechanism: it writes each frame's own image data plus a small
    GIF-format header saying "loop through these N frames".
    """
    height, width = Z.shape[0], Z.shape[1]
    background = heatmap_array(Z)
    frames = []
    for k in range(1, len(path_xy) + 1):
        img = Image.fromarray(background, mode="RGB").copy()
        draw = ImageDraw.Draw(img)
        pixels = [world_to_pixel(x, y, xlim, ylim, width, height) for x, y in path_xy[:k]]
        if len(pixels) >= 2:
            draw.line(pixels, fill=(255, 255, 255), width=2)
        px, py = pixels[-1]
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255), outline=(20, 20, 20))
        frames.append(img.convert("P", palette=Image.ADAPTIVE))
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        format="GIF",
    )
