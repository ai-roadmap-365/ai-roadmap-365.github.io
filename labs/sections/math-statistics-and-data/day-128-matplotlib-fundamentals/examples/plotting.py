"""Reference implementation for Day 128 — Matplotlib Fundamentals.

Nine exercises, each a plain function that draws or measures a chart, with
no dependency beyond matplotlib and the standard library. Every function
is designed to be called from a test that asserts on the returned Figure
or Axes object's *state* — never on rendered image bytes, except in
exercise 9, where the whole point is comparing raster bytes to vector
markup.

Matplotlib is forced onto the non-interactive Agg backend at import time,
before pyplot is imported, so this module never opens a window and never
calls plt.show(). Every script and test in this lab imports plotting
first, which is what makes that guarantee hold everywhere.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)


# ---------------------------------------------------------------------------
# Exercise 1 — the two APIs
# ---------------------------------------------------------------------------


def draw_line_pyplot_style(x, y, label):
    """Draw one line using the pyplot state machine.

    Every call routes through whichever figure and axes are currently
    "current" — plt.gcf() and plt.gca() — rather than naming one. Call this
    twice in a row without an intervening plt.figure() and both lines land
    on the SAME figure, because nothing here ever asked for a new one.
    """
    plt.plot(x, y, label=label)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("drawn with the pyplot state machine")
    plt.legend()


def draw_line_object_style(x, y, label):
    """Draw one line using the object API.

    fig, ax = plt.subplots() creates a genuinely new Figure and Axes every
    call, and every following instruction is a method call on that specific
    ax — there is no "current" anything to get confused about. Call this
    twice and you get two independent figures, guaranteed by construction
    rather than by remembering to call plt.figure() first.
    """
    fig, ax = plt.subplots()
    ax.plot(x, y, label=label)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("drawn with the object API")
    ax.legend()
    return fig, ax


# ---------------------------------------------------------------------------
# Exercise 2 — data round-trip
# ---------------------------------------------------------------------------


def make_line_axes(x, y):
    """Plot x, y on a fresh Axes and return (fig, ax).

    Nothing here transforms the data — no normalisation, no sorting, no
    resampling. What goes onto the Axes is exactly what was passed in,
    which is a claim ax.lines[0].get_xydata() can check exactly, not
    approximately.
    """
    fig, ax = plt.subplots()
    ax.plot(x, y)
    return fig, ax


# ---------------------------------------------------------------------------
# Exercise 3 — pixel arithmetic
# ---------------------------------------------------------------------------


def png_dimensions(path):
    """Read a PNG file's (width, height) in pixels from its IHDR chunk.

    Deliberately avoids adding an image-reading dependency: every PNG
    starts with an 8-byte signature, then a 4-byte chunk length, a 4-byte
    chunk type ("IHDR" for the first chunk always), then width and height
    as big-endian 4-byte integers. That is a fixed, documented format, not
    a guess — reading 24 bytes is enough.
    """
    with open(path, "rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG file with a leading IHDR chunk")
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width, height


def save_at_size_and_dpi(fig, path, dpi):
    """Save fig to path at the given dpi, with no bbox trimming.

    bbox_inches='tight' is deliberately NOT used here: it crops the saved
    image to the drawn content's bounding box, which means the output size
    is no longer figsize * dpi exactly — it is figsize * dpi minus
    whatever margin got trimmed. Pixel arithmetic needs the untrimmed size,
    so this function saves with matplotlib's default bounding box.
    """
    fig.savefig(path, dpi=dpi)


# ---------------------------------------------------------------------------
# Exercise 4 — labels, limits, ticks, scales
# ---------------------------------------------------------------------------


def configure_axes(ax, xlabel, title, ylim=None):
    """Apply a label, a title, and — optionally — an explicit y-limit.

    set_ylim, when given, OVERRIDES autoscaling: matplotlib's default
    behaviour is to pick y-limits that fit the plotted data with a small
    margin, but a caller who calls set_ylim afterwards is asking for
    exactly those bounds, data be damned. That is worth asserting
    explicitly, because it is easy to assume autoscale always wins.
    """
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    if ylim is not None:
        ax.set_ylim(*ylim)


# ---------------------------------------------------------------------------
# Exercise 5 — subplots
# ---------------------------------------------------------------------------


def make_grid(nrows, ncols):
    """Return (fig, axes) for an nrows x ncols grid of independent Axes.

    plt.subplots(nrows, ncols) with either dimension greater than 1 returns
    a 2-D numpy array of Axes objects, shaped (nrows, ncols) — not a flat
    list, and not a single Axes. Each entry is its own object: setting a
    label on axes[0, 0] never touches axes[0, 1].
    """
    fig, axes = plt.subplots(nrows, ncols)
    return fig, axes


# ---------------------------------------------------------------------------
# Exercise 6 — log scale and non-positive data
# ---------------------------------------------------------------------------


def plot_with_log_yscale(x, y):
    """Plot x, y, then switch the y-axis to a log scale, and return ax.

    A logarithmic scale has no representation for zero or negative values
    (log(0) is undefined, log of a negative number is not real), and
    matplotlib does not raise an error over this — it silently narrows the
    rendered y-limits to exclude non-positive values. The underlying line
    data is untouched (ax.lines[0].get_xydata() still returns the original
    array, zero included); only the VISIBLE range changes, which is what
    makes this failure mode easy to miss in a real report.
    """
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_yscale("log")
    # Force a draw so the axes limits are actually recomputed for the new
    # scale rather than left at whatever the linear autoscale produced.
    fig.canvas.draw()
    return fig, ax


# ---------------------------------------------------------------------------
# Exercise 7 — legends
# ---------------------------------------------------------------------------


def plot_two_series_with_legend(x, y1, label1, y2, label2):
    """Plot two labelled series and call legend() once, at the end.

    The label-then-legend pattern: every artist that should appear in the
    legend gets a label= at creation time, and a single ax.legend() call
    afterwards collects them, in the order they were plotted.
    """
    fig, ax = plt.subplots()
    ax.plot(x, y1, label=label1)
    ax.plot(x, y2, label=label2)
    ax.legend()
    return fig, ax


# ---------------------------------------------------------------------------
# Exercise 8 — figure lifecycle
# ---------------------------------------------------------------------------


def open_figures_without_closing(n):
    """Open n figures via plt.subplots() and return them without closing any.

    Every open figure lives in pyplot's global registry until plt.close()
    (or plt.close('all')) removes it — a loop that plots in a function and
    returns without closing leaks one figure per iteration. This function
    exists to make that leak reproducible and countable via
    plt.get_fignums(), not to recommend the pattern.
    """
    figs = []
    for _ in range(n):
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        figs.append(fig)
    return figs


# ---------------------------------------------------------------------------
# Exercise 9 — vector versus raster
# ---------------------------------------------------------------------------


def save_png_and_svg(fig, png_path, svg_path):
    """Save the same figure as PNG (raster) and SVG (vector)."""
    fig.savefig(png_path, format="png")
    fig.savefig(svg_path, format="svg")
