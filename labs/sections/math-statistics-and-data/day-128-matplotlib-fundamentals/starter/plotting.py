"""Starter — Day 128 — Matplotlib Fundamentals — "Plots You Can Assert On".

Nine functions, one per exercise in `00_brief.md`. Each currently raises
NotImplementedError. Read the docstring, write the body, and check yourself
with:

    ../.venv/bin/pytest . -q      (run from inside starter/)

An unattempted function skips its test (not a failure). A wrong answer
fails and prints both your value and the expected one.

matplotlib is forced onto the Agg backend before pyplot is imported, so
every function you write here runs headless. Never call plt.show().
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)


# ---------------------------------------------------------------------------
# Exercise 1 — the two APIs
# ---------------------------------------------------------------------------


def draw_line_pyplot_style(x, y, label):
    """Draw one line using the pyplot state machine: plt.plot, plt.xlabel,
    plt.ylabel, plt.title (with the exact string 'drawn with the pyplot
    state machine'), plt.legend(). Every call should go through plt.*, not
    an ax you create yourself — that is the point of this exercise.
    """
    raise NotImplementedError


def draw_line_object_style(x, y, label):
    """Create fig, ax = plt.subplots(), then call ax.plot, ax.set_xlabel,
    ax.set_ylabel, ax.set_title (with the exact string 'drawn with the
    object API'), ax.legend(). Return (fig, ax).
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 2 — data round-trip
# ---------------------------------------------------------------------------


def make_line_axes(x, y):
    """Create fig, ax = plt.subplots(), plot x, y with ax.plot(x, y), and
    return (fig, ax). Do not transform x or y in any way.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 3 — pixel arithmetic
# ---------------------------------------------------------------------------


def png_dimensions(path):
    """Read a PNG file's (width, height) in pixels without any imaging
    library. A PNG file is: an 8-byte signature, then a 4-byte chunk
    length, a 4-byte chunk type (always b"IHDR" for the first chunk), then
    width and height as big-endian 4-byte unsigned integers — 24 bytes
    total to read. Return (width, height) as a tuple of ints.
    """
    raise NotImplementedError


def save_at_size_and_dpi(fig, path, dpi):
    """Save fig to path at the given dpi. Do NOT pass bbox_inches='tight'
    — this exercise is about exact figsize * dpi pixel arithmetic, and
    tight bounding boxes trim the output to the drawn content instead.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 4 — labels, limits, ticks, scales
# ---------------------------------------------------------------------------


def configure_axes(ax, xlabel, title, ylim=None):
    """Call ax.set_xlabel(xlabel) and ax.set_title(title). If ylim is not
    None, call ax.set_ylim(*ylim) too — this should override whatever
    autoscaling would otherwise have picked.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 5 — subplots
# ---------------------------------------------------------------------------


def make_grid(nrows, ncols):
    """Return (fig, axes) from plt.subplots(nrows, ncols). Do not flatten
    or reshape the returned axes array.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 6 — log scale and non-positive data
# ---------------------------------------------------------------------------


def plot_with_log_yscale(x, y):
    """Create fig, ax = plt.subplots(), plot x, y (use marker="o" so the
    points are visible), call ax.set_yscale("log"), force a draw with
    fig.canvas.draw() so the axes limits are recomputed, and return
    (fig, ax).
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 7 — legends
# ---------------------------------------------------------------------------


def plot_two_series_with_legend(x, y1, label1, y2, label2):
    """Plot y1 then y2 against x, each with its label= set at plot time,
    then call ax.legend() once at the end. Return (fig, ax).
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 8 — figure lifecycle
# ---------------------------------------------------------------------------


def open_figures_without_closing(n):
    """Call plt.subplots() n times, plot something trivial on each ax
    (e.g. ax.plot([0, 1], [0, 1])), and return a list of the n figures.
    Do not call plt.close() anywhere in this function — the leak is the
    exercise.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Exercise 9 — vector versus raster
# ---------------------------------------------------------------------------


def save_png_and_svg(fig, png_path, svg_path):
    """Save fig to png_path with format="png" and to svg_path with
    format="svg".
    """
    raise NotImplementedError
