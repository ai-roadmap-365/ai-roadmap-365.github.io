"""Rendering, and measuring what was actually rendered.

"That chart looks better" is not testable. "That chart spends 37% of its
ink on the data where this one spends 93%, and both carry the same eight
numbers" is. Everything in this module exists to turn a claim about a
picture into a number a test can assert on.

Every function here renders through matplotlib's **Agg** backend, which
draws into a memory buffer and needs no display, no window server and no
X11 forwarding. `matplotlib.use("Agg")` is called BEFORE `pyplot` is
imported, because the backend is chosen at import time and switching
afterwards is unreliable. `plt.show()` is never called, and every figure
is closed on the way out so a long test run does not leak them.

Every function takes an explicit output path. Nothing here writes to a
default location, so a test that hands it a `tmp_path` leaves nothing on
disk once pytest cleans up.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # must precede the pyplot import

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402
from PIL import Image  # noqa: E402

WHITE = (255, 255, 255)

# The flat colour the bars are drawn in, as an sRGB 8-bit triple, so a
# test can isolate the data ink from the furniture.
BAR_RGB: tuple[int, int, int] = (0x1D, 0x4E, 0xD8)
BAR_HEX = "#%02x%02x%02x" % BAR_RGB

# The eight-region growth figures the lesson opens with. Deliberately
# close together at the top: 18.9 against 17.4 is a gap a sorted bar chart
# shows instantly and a pie chart cannot resolve at all.
REGION_GROWTH: dict[str, float] = {
    "Nordics": 12.1,
    "Iberia": 18.9,
    "Benelux": 7.4,
    "DACH": 17.4,
    "France": 9.8,
    "Italy": 4.2,
    "Poland": 15.6,
    "Ireland": 11.3,
}


# --------------------------------------------------------------------------
# Pixel measurement
# --------------------------------------------------------------------------


def _load_rgb(path: Path) -> np.ndarray:
    """Load a PNG as an (H, W, 3) uint8 array, discarding any alpha."""
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def count_non_background_pixels(path: Path, background: tuple[int, int, int] = WHITE) -> int:
    """Count pixels that are not the background colour. This is the ink."""
    arr = _load_rgb(path)
    bg = np.array(background, dtype=np.uint8)
    return int(np.count_nonzero(np.any(arr != bg, axis=-1)))


def count_pixels_of_color(path: Path, rgb: tuple[int, int, int]) -> int:
    """Count pixels exactly matching one colour.

    The bars in `render_region_bar_chart` are drawn in one flat colour and
    nothing else in either figure uses it, so this isolates the DATA ink
    from every other mark on the page -- which is what makes Tufte's
    data-ink ratio a number this lab can measure rather than assert.
    """
    arr = _load_rgb(path)
    target = np.array(rgb, dtype=np.uint8)
    return int(np.count_nonzero(np.all(arr == target, axis=-1)))


def data_ink_ratio(path: Path, data_rgb: tuple[int, int, int]) -> float:
    """Data ink divided by total ink, both counted in pixels.

    Tufte's definition, made literal: of every mark on the page, what
    fraction is the data itself? Erasing non-data ink -- gridlines, a
    tinted panel, a heavy box -- raises this without removing a single
    fact from the chart.
    """
    total = count_non_background_pixels(path)
    if total == 0:
        raise ValueError("the image has no ink at all; a data-ink ratio is undefined")
    return count_pixels_of_color(path, data_rgb) / total


def count_distinct_luminance_levels(path: Path) -> int:
    """Count how many distinct grey levels the image contains.

    This is the measurable trace of density information. Opaque marks that
    overlap produce exactly two levels -- paper and ink -- no matter how
    many marks landed on the same pixel, because the tenth mark on a pixel
    changes nothing. Semi-transparent marks accumulate, so the number of
    levels tells you the image is carrying how MANY marks landed, not just
    whether any did.
    """
    arr = _load_rgb(path).astype(np.float64)
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    return int(np.unique(np.round(lum).astype(np.int64)).size)


# --------------------------------------------------------------------------
# Exercise 1 -- circles drawn at a known radius, then measured
# --------------------------------------------------------------------------


def render_circle(path: Path, radius_px: float, canvas_px: int = 400) -> None:
    """Draw one filled circle of exactly `radius_px` pixels on white.

    The axes fill the whole figure and the data limits are set equal to
    the pixel dimensions, so one data unit is one pixel exactly and the
    circle's radius in data units is its radius on screen. Antialiasing is
    switched off so the edge is a hard boundary and the pixel count is a
    measurement of area rather than of area plus a soft fringe.
    """
    dpi = 100
    fig = plt.figure(figsize=(canvas_px / dpi, canvas_px / dpi), dpi=dpi, facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, canvas_px)
    ax.set_ylim(0, canvas_px)
    ax.set_axis_off()
    ax.add_patch(
        Circle(
            (canvas_px / 2, canvas_px / 2),
            radius_px,
            facecolor="black",
            edgecolor="none",
            antialiased=False,
        )
    )
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)


def measure_circle_area_px(path: Path) -> int:
    """The circle's drawn area, in painted pixels."""
    return count_non_background_pixels(path)


# --------------------------------------------------------------------------
# Exercise 7 -- the same chart, decorated and undecorated
# --------------------------------------------------------------------------


def render_region_bar_chart(path: Path, decorated: bool) -> None:
    """Render the eight-region bar chart with or without the furniture.

    Identical data, identical figure size, identical bars. The only
    difference is the non-data ink: a tinted plot background, a full box
    of spines, gridlines on both axes, and a heavy frame. Everything the
    reader needs -- the eight labels, the eight lengths, a common baseline
    -- is present in BOTH.
    """
    dpi = 100
    fig = plt.figure(figsize=(6, 4), dpi=dpi, facecolor="white")
    ax = fig.add_subplot(111)

    names = list(REGION_GROWTH)
    values = [REGION_GROWTH[n] for n in names]
    order = sorted(range(len(values)), key=lambda i: values[i])
    names = [names[i] for i in order]
    values = [values[i] for i in order]

    ax.barh(names, values, color=BAR_HEX)
    ax.set_xlabel("growth %")

    if decorated:
        ax.set_facecolor("#e2e8f0")
        ax.grid(True, which="both", axis="both", color="#64748b", linewidth=1.0)
        ax.set_axisbelow(False)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(3.0)
            spine.set_color("#334155")
    else:
        ax.set_facecolor("white")
        ax.grid(False)
        for name, spine in ax.spines.items():
            spine.set_visible(name == "bottom")
        ax.tick_params(left=False)

    fig.tight_layout()
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------
# Exercise 8 -- overplotting, and two ways out of it
# --------------------------------------------------------------------------


def sample_points(n: int = 10_000, seed: int = 127) -> tuple[np.ndarray, np.ndarray]:
    """A fixed, seeded cloud of `n` correlated points.

    Seeded, so every machine plots the same cloud and every pixel count in
    this lab is reproducible rather than merely typical.
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, n)
    y = 0.6 * x + rng.normal(0.0, 0.8, n)
    return x, y


# The scatter canvas. Both limits are wide enough that every one of the
# 10,000 sampled points falls inside the axes -- nothing is clipped, so
# the painted-pixel count can be compared against the full point count
# without an "and some were off the edge" caveat.
SCATTER_INCHES = 3
SCATTER_LIMIT = 5


def render_scatter(path: Path, x: np.ndarray, y: np.ndarray, alpha: float) -> None:
    """Plot the cloud with one-pixel marks at the given opacity.

    The `,` marker is matplotlib's single-pixel marker and antialiasing is
    off, so each point paints exactly one pixel. That makes the painted
    pixel count a direct measurement of how many DISTINCT screen positions
    the data occupies, with no marker-size confound: any shortfall against
    the point count is overplotting and nothing else.
    """
    dpi = 100
    fig = plt.figure(figsize=(SCATTER_INCHES, SCATTER_INCHES), dpi=dpi, facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(-SCATTER_LIMIT, SCATTER_LIMIT)
    ax.set_ylim(-SCATTER_LIMIT, SCATTER_LIMIT)
    ax.set_axis_off()
    ax.plot(x, y, ",", color="black", alpha=alpha, antialiased=False, linestyle="none")
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)


def render_hexbin(path: Path, x: np.ndarray, y: np.ndarray, gridsize: int = 30) -> None:
    """Plot the same cloud as a hexagonal density map.

    Where the scatter throws density away by painting the same pixel over
    and over, hexbin counts the points per cell and encodes the count as
    luminance -- the information the scatter destroyed, recovered by
    aggregating before drawing instead of after.
    """
    dpi = 100
    lim = SCATTER_LIMIT
    fig = plt.figure(figsize=(SCATTER_INCHES, SCATTER_INCHES), dpi=dpi, facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_axis_off()
    ax.hexbin(x, y, gridsize=gridsize, cmap="Greys", extent=(-lim, lim, -lim, lim))
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)


def count_painted_pixels(path: Path) -> int:
    """Distinct screen positions carrying at least one mark."""
    return count_non_background_pixels(path)


def points_inside_axes(x: np.ndarray, y: np.ndarray, limit: float = SCATTER_LIMIT) -> int:
    """How many of the sampled points fall inside the scatter's axes.

    Used to confirm that nothing is clipped, so a painted-pixel count
    below the point count means overplotting and never "the rest fell off
    the edge of the picture".
    """
    return int(np.count_nonzero((np.abs(x) <= limit) & (np.abs(y) <= limit)))
