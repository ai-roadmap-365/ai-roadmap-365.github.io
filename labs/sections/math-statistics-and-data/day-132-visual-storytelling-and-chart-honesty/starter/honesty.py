"""Starter — Day 132 — "Charts That Cannot Lie To You".

Fourteen functions to write, grouped into the nine exercises described in
`00_brief.md`. Each one currently raises NotImplementedError. Read the
docstring, write the body, and check yourself with:

    ../.venv/bin/pytest . -q      (run from inside starter/)

An unattempted function skips its test rather than failing it. A wrong
answer fails and prints both your value and the expected one.

Everything NOT stubbed out below is working code you can lean on: the
functions that build the figures, generate the demonstration data and
read a drawn line's trace are already written. What you write is the
MEASUREMENT -- the part that turns "this chart is misleading" from an
opinion into a number.

Every measurement must come from the chart's own rendered geometry, never
from the numbers that were passed in. That is the whole point: a chart's
honesty is a property of what got *drawn*.

matplotlib is forced onto the headless Agg backend before pyplot is
imported, so nothing here opens a window. Never call plt.show().
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)
import numpy as np  # noqa: E402


# ===========================================================================
# Exercise 1 — the lie factor
# ===========================================================================


def lie_factor(shown_ratio, data_ratio):
    """Tufte's lie factor: the size of the effect shown in the graphic
    divided by the size of the effect in the data.

    A value of 1.0 means the graphic shows exactly the effect the data
    contains. Tufte's own rule of thumb calls anything outside roughly
    0.95 to 1.05 a distortion. The number is unitless and is a plain
    ratio of two ratios, which is what makes "this chart is misleading"
    into an arithmetic claim instead of an opinion.

    Write it: return shown_ratio / data_ratio, but raise
    ZeroDivisionError with a clear message first if data_ratio == 0.
    """
    raise NotImplementedError


def bar_pair(values, ylim=None, labels=("A", "B")):
    """Draw two bars for `values` and return (fig, ax).

    `ylim` is passed straight to ax.set_ylim. Pass None to keep
    matplotlib's autoscaled limits, which for a bar chart always include
    zero -- matplotlib is honest by default here, and the distortion in
    this lab is something an author has to reach out and add.
    """
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(list(labels), list(values), color="#1d4ed8")
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_ylabel("value")
    return fig, ax


def drawn_bar_heights(ax):
    """The heights of `ax`'s bars as the reader actually sees them, in
    axes-fraction units (0.0 at the bottom of the plotting box, 1.0 at
    the top), clipped to the visible box.

    This reads the patches' real bounding boxes and pushes them through
    the Axes' own data-to-axes transform, so it reports what got drawn.
    A bar whose top is off the top of the axes contributes 1.0, and a
    bar whose top is below the axes floor contributes 0.0 -- exactly what
    a reader would see.

    Write it: build the transform with
    `to_axes = ax.transData + ax.transAxes.inverted()`, then for each
    `patch` in `ax.patches` call `patch.get_bbox().transformed(to_axes)`
    and take `min(bbox.y1, 1.0) - max(bbox.y0, 0.0)`, floored at 0.0.
    """
    raise NotImplementedError


def bar_pair_lie_factor(values, ylim=None):
    """Build a two-bar chart, measure the drawn bar heights, and return
    (lie_factor, shown_ratio, data_ratio).

    The shown ratio comes from the rendered geometry, not from `values`.
    """
    fig, ax = bar_pair(values, ylim=ylim)
    try:
        fig.canvas.draw()
        heights = drawn_bar_heights(ax)
        if heights[0] == 0:
            raise ZeroDivisionError("the first bar has zero drawn height")
        shown = heights[1] / heights[0]
        data = values[1] / values[0]
        return lie_factor(shown, data), shown, data
    finally:
        plt.close(fig)


# ===========================================================================
# Exercise 2 — truncation for bars versus lines
# ===========================================================================


def line_pair(values, ylim=None, xs=(0, 1)):
    """Draw the same two numbers as a two-point line and return (fig, ax)."""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(list(xs), list(values), marker="o", color="#1d4ed8")
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_ylabel("value")
    return fig, ax


def drawn_change(ax):
    """The change a line encodes, recovered from the drawn geometry.

    A line encodes *change* as vertical displacement. A reader recovers
    that change by measuring the displacement as a fraction of the
    plotting box and multiplying by the labelled axis range -- which is
    exactly what this function does. The answer is in data units.

    Write it: same `ax.transData + ax.transAxes.inverted()` transform.
    Take `ax.lines[0].get_xydata()`, transform the first and last points,
    subtract their y values to get the displacement as a fraction of the
    box, then multiply by `ax.get_ylim()[1] - ax.get_ylim()[0]`.
    """
    raise NotImplementedError


def line_pair_lie_factor(values, ylim=None):
    """Build a two-point line chart on the given limits and return
    (lie_factor, shown_change, data_change) for the change it encodes."""
    fig, ax = line_pair(values, ylim=ylim)
    try:
        fig.canvas.draw()
        shown = drawn_change(ax)
        data = values[1] - values[0]
        return lie_factor(shown, data), shown, data
    finally:
        plt.close(fig)


# ===========================================================================
# Exercise 3 — dual axes
# ===========================================================================


def pearson(a, b):
    """Pearson correlation coefficient, written out rather than imported,
    so nothing about this measurement is hidden behind a library call.
    Write it by hand rather than calling np.corrcoef: centre both
    arrays on their means, then divide the sum of their product by
    `math.sqrt(sum(a_centred**2) * sum(b_centred**2))`. Raise
    ZeroDivisionError if that denominator is zero.
    """
    raise NotImplementedError


def uncorrelated_pair(n=60, seed=416):
    """Two series with a near-zero sample correlation, drawn once from a
    fixed seed so every run of this lab sees the same two series.

    Seed 416 was not the first seed tried. It was chosen by scanning
    seeds 1-599 for the one giving the smallest absolute correlation, to
    get a clean demonstration series. That is a cherry-pick, and this
    docstring is the disclosure -- which is the entire rule this lab
    teaches, applied to the lab's own data.
    """
    rng = np.random.default_rng(seed)
    a = rng.normal(50.0, 8.0, n)
    b = rng.normal(0.004, 0.0006, n)
    return a, b


def dual_axis_figure(a, b, ylim_a=None, ylim_b=None):
    """Plot `a` on a left axis and `b` on a right twinx axis, each with
    its own limits, and return (fig, ax_left, ax_right)."""
    fig, ax = plt.subplots(figsize=(6, 3))
    x = np.arange(len(a))
    ax.plot(x, a, color="#1d4ed8", label="series A (left axis)")
    ax2 = ax.twinx()
    ax2.plot(x, b, color="#b91c1c", label="series B (right axis)")
    if ylim_a is not None:
        ax.set_ylim(*ylim_a)
    if ylim_b is not None:
        ax2.set_ylim(*ylim_b)
    ax.set_ylabel("series A")
    ax2.set_ylabel("series B")
    return fig, ax, ax2


def drawn_trace(ax, line_index=0):
    """A drawn line's y-coordinates in axes-fraction units -- the shape
    the reader's eye actually follows, independent of what the numbers on
    the axis say."""
    to_axes = ax.transData + ax.transAxes.inverted()
    xy = ax.lines[line_index].get_xydata()
    return np.array([to_axes.transform((px, py))[1] for px, py in xy])


def tracking_gap(trace_a, trace_b):
    """How far apart two drawn curves sit, as a root-mean-square vertical
    distance in axes fractions. 0.0 means they lie exactly on top of one
    another; a value near 0.5 means they occupy different halves of the
    plot. This is the quantity a dual-axis chart actually manipulates.
    Write it: subtract the two arrays elementwise, square, take
    the mean, take the square root -- a plain root-mean-square distance.
    """
    raise NotImplementedError


def widened_limits(values, factor=20.0):
    """Limits `factor` times wider than the data, centred on it. Every
    series flattens toward the middle of the plotting box, which is how
    two unrelated curves get made to lie on top of each other.
    Write it: take the data's min and max, find the midpoint, and
    return `(mid - span, mid + span)` where `span` is
    `(max - min) * factor / 2`. Guard against a zero span.
    """
    raise NotImplementedError


def banded_limits(values, low_frac, high_frac):
    """Limits that place the data inside the vertical band running from
    `low_frac` to `high_frac` of the plotting box, so a series can be
    parked in the top half or the bottom half at will."""
    lo = float(np.min(values))
    hi = float(np.max(values))
    span = hi - lo
    if span == 0:
        span = 1.0
    unit = span / (high_frac - low_frac)
    return lo - low_frac * unit, hi + (1.0 - high_frac) * unit


def correlated_pair(n=60, seed=7, rho=0.9):
    """A genuinely, strongly correlated pair -- the control that makes
    the dual-axis result mean something. Without it, a small tracking gap
    for uncorrelated data proves nothing; with it, the same small gap for
    both proves that the gap carries no information at all."""
    rng = np.random.default_rng(seed)
    c = rng.normal(0.0, 1.0, n)
    d = rho * c + math.sqrt(1.0 - rho**2) * rng.normal(0.0, 1.0, n)
    return c, d


def matched_limits(values, pad=0.15):
    """Limits that centre a series in the plotting box with equal padding
    above and below -- the scaling that makes any series fill the frame
    the same way, and therefore the scaling that makes any two series
    lie on top of each other."""
    lo = float(np.min(values))
    hi = float(np.max(values))
    span = hi - lo
    if span == 0:
        span = 1.0
    return lo - pad * span, hi + pad * span


# ===========================================================================
# Exercise 4 — cherry-picked windows
# ===========================================================================


def trend_slope(y):
    """The slope of the least-squares line through `y` against 0..n-1,
    in units of y per step.
    Write it: `np.polyfit(np.arange(len(y)), y, 1)` returns
    `(slope, intercept)`. Return the slope as a float.
    """
    raise NotImplementedError


def dipping_series(n=48, seed=132):
    """A series that falls for its first stretch and rises for its
    second, so the sign of its trend depends entirely on where a reader
    is allowed to start looking. Noise is drawn from a fixed seed."""
    rng = np.random.default_rng(seed)
    x = np.arange(n, dtype=float)
    shape = 0.03 * (x - n / 2.0) ** 2
    return shape - shape.mean() + rng.normal(0.0, 1.2, n) + 100.0


# ===========================================================================
# Exercise 5 — binning
# ===========================================================================


def bimodal_sample(n=400, seed=21):
    """A sample drawn from two separated normal components, so it really
    does have two modes -- and a histogram of it can still be made to
    show one.

    The components sit at -0.85 and +0.85 with a standard deviation of
    0.95, so they overlap enough that the answer to "how many humps?"
    depends on the bin width. That fragility is the finding, not a flaw
    in the data.

    These separations and this seed were chosen by scanning a grid of
    separations, spreads, sample sizes and seeds for a case where the two
    standard bin rules genuinely disagree -- Sturges strictly rising then
    strictly falling, Freedman-Diaconis showing two humps with a valley
    at least 15% below the lower peak. Most parameter settings do not
    disagree. That search is a cherry-pick, and this docstring is the
    disclosure. The claim being demonstrated is that the disagreement is
    POSSIBLE with two citable rules, not that it is typical.
    """
    rng = np.random.default_rng(seed)
    left = rng.normal(-0.85, 0.95, n // 2)
    right = rng.normal(0.85, 0.95, n - n // 2)
    return np.concatenate([left, right])


def histogram_counts(sample, bins):
    """Draw a real histogram on a real Axes and read the bar heights back
    off the drawn patches, so the counts under test are the counts the
    reader sees."""
    fig, ax = plt.subplots(figsize=(4, 3))
    try:
        ax.hist(sample, bins=bins, color="#1d4ed8")
        fig.canvas.draw()
        return [float(p.get_height()) for p in ax.patches]
    finally:
        plt.close(fig)


def count_modes(counts):
    """The number of local maxima in a sequence of bar heights: a bar
    strictly taller than both of its neighbours, with the two end bars
    compared against their single neighbour. This is how a reader counts
    humps, and it is the whole conclusion a histogram is used to reach.
    Write it: walk the list and count entries strictly greater
    than BOTH neighbours. Treat the missing neighbour of each end entry
    as `-math.inf` so the ends can count as modes.
    """
    raise NotImplementedError


# ===========================================================================
# Exercise 6 — radius versus area
# ===========================================================================


def bubble_pair(values, encode="area"):
    """Draw two bubbles for `values` and return (fig, ax).

    encode="area"   -- marker area is proportional to the value, which is
                       the correct encoding.
    encode="radius" -- marker *radius* is proportional to the value,
                       which is the convenient-looking mistake.

    matplotlib's scatter takes `s` as marker area in points squared, so
    the correct encoding is the one that looks like it is doing less.
    """
    values = np.asarray(values, dtype=float)
    if encode == "area":
        sizes = values * 40.0
    elif encode == "radius":
        sizes = (values * 1.4) ** 2
    else:
        raise ValueError("encode must be 'area' or 'radius'")
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.scatter([0, 1], [0, 0], s=sizes, color="#1d4ed8")
    ax.set_xlim(-1, 2)
    ax.set_ylim(-1, 1)
    return fig, ax


def drawn_area_ratio(ax):
    """The ratio of the two drawn marker areas, read off the collection's
    own sizes -- which matplotlib stores in points squared, i.e. area.
    Write it: `ax.collections[0].get_sizes()` returns the marker
    sizes matplotlib will draw, already in points squared -- that is an
    AREA. Return `sizes[1] / sizes[0]`.
    """
    raise NotImplementedError


# ===========================================================================
# Exercise 7 — 3D perspective
# ===========================================================================


def bar3d_projected_areas(heights, depths, focal_length=0.2):
    """Draw two 3D bars of the given heights at the given depths, and
    return the drawn 2D area of each bar's front face in figure units.

    Every corner is pushed through the Axes' own projection matrix, so
    the areas are the areas matplotlib really draws, perspective and all.
    """
    from mpl_toolkits.mplot3d import proj3d

    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(projection="3d")
    try:
        ax.set_proj_type("persp", focal_length=focal_length)
        width = 0.6
        for i, (height, depth) in enumerate(zip(heights, depths)):
            ax.bar3d(i * 2.0, depth, 0, width, width, height, color="#1d4ed8")
        ax.set_xlim(-1, 4)
        ax.set_ylim(min(depths) - 1, max(depths) + 1)
        ax.set_zlim(0, max(heights) * 1.2)
        fig.canvas.draw()
        proj = ax.get_proj()

        areas = []
        for i, (height, depth) in enumerate(zip(heights, depths)):
            x0 = i * 2.0
            corners = [
                (x0, depth, 0.0),
                (x0 + width, depth, 0.0),
                (x0 + width, depth, height),
                (x0, depth, height),
            ]
            flat = [proj3d.proj_transform(cx, cy, cz, proj)[:2] for cx, cy, cz in corners]
            areas.append(_polygon_area(flat))
        return areas
    finally:
        plt.close(fig)


def _polygon_area(points):
    """The area of a simple polygon by the shoelace formula.
    Write it with the shoelace formula: sum `x1*y2 - x2*y1` over
    consecutive pairs, wrapping the last point back to the first, then
    take `abs(total) / 2`.
    """
    raise NotImplementedError


# ===========================================================================
# Exercise 8 — ordering and annotation
# ===========================================================================


def comparisons_to_find_max(values):
    """An idealised model of the reader effort a bar chart demands to
    answer "which is biggest?".

    When the bars are already in descending order, position encodes rank
    and the answer is the first bar: zero comparisons. When they are not,
    the reader must hold a running maximum and compare it against every
    remaining bar: n - 1 comparisons.

    This is a model of reading effort, not a measurement of human
    behaviour. It is stated as a model everywhere it is used, and its
    only claim is the ordering of the two numbers, not their exact size.

    Write it: return 0 if the list is already in non-increasing
    order (position then encodes rank), otherwise `len(values) - 1`.
    Return 0 for a list of fewer than two entries.
    """
    raise NotImplementedError


def annotated_bar_chart(labels, values, claim):
    """A bar chart carrying its claim as retrievable text: the claim goes
    in the title and is also anchored to the winning bar with annotate,
    so the chart states what it wants the reader to conclude."""
    order = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    labels = [labels[i] for i in order]
    values = [values[i] for i in order]

    fig, ax = plt.subplots(figsize=(5, 3))
    colours = ["#1d4ed8"] + ["#cbd5e1"] * (len(values) - 1)
    ax.bar(labels, values, color=colours)
    ax.set_ylabel("value")
    ax.set_title(claim)
    ax.annotate(
        claim,
        xy=(0, values[0]),
        xytext=(0.35, 0.85),
        textcoords="axes fraction",
        arrowprops={"arrowstyle": "->", "color": "#1a202c"},
    )
    return fig, ax


def axes_text(ax):
    """Every piece of text a reader can retrieve from an Axes: its title,
    both axis labels, and every Text artist placed on it.
    Write it: collect `ax.get_title()`, `ax.get_xlabel()`,
    `ax.get_ylabel()` and `t.get_text() for t in ax.texts`, then drop the
    empty strings.
    """
    raise NotImplementedError


# ===========================================================================
# Exercise 9 — the caption contract
# ===========================================================================

CLAIM_WORDS = (
    "higher",
    "lower",
    "more",
    "less",
    "greater",
    "smaller",
    "rose",
    "fell",
    "grew",
    "shrank",
    "increase",
    "decrease",
    "than",
    "no difference",
    "unchanged",
    "%",
)

DISCLOSURE_WORDS = (
    "axis starts at",
    "baseline",
    "does not start at zero",
    "log scale",
    "logarithmic",
    "clipped",
    "truncated",
    "excludes",
)


def review_chart(ax, caption):
    """Check one chart against the day's review contract and return
    (passed, failures).

    The four rules:

    1. The caption states a claim, so a reader has something to disagree
       with. Checked by looking for comparative or quantitative language;
       this is a keyword heuristic, and it is honest about being one -- it
       catches a missing claim, it cannot judge a wrong one.
    2. The y axis is labelled, so the reader knows what is being measured.
    3. The baseline the chart was drawn on is stated in the caption
       whenever it is not zero.
    4. Either the baseline is zero, or the caption discloses that it is
       not. Breaking the rule is allowed; breaking it silently is not.

    Write it: lowercase the caption, read `low, _ = ax.get_ylim()`,
    and append one message to `failures` per broken rule. Use the module
    constants CLAIM_WORDS and DISCLOSURE_WORDS. The exact substrings the
    tests look for are 'caption is empty', 'no claim', 'no label',
    'does not say so' and 'without disclosure'. Return
    `(not failures, failures)`.
    """
    raise NotImplementedError


# ===========================================================================
# Exercise 8, second half — emphasis that survives a greyscale printer
# ===========================================================================

HIGHLIGHT = "#1d4ed8"
MUTED = "#cbd5e1"
CLASSIC_RED = "#d62728"
CLASSIC_GREEN = "#2ca02c"


def relative_luminance(colour):
    """The Rec. 709 relative luminance of a colour, as defined by WCAG:
    each sRGB channel is linearised, then weighted 0.2126 / 0.7152 /
    0.0722 and summed. The result runs from 0.0 (black) to 1.0 (white).

    Luminance is the channel that survives every form of colour-vision
    deficiency, every greyscale printer and every bad projector. It is
    *one* component of whether two colours can be told apart, not the
    whole of it -- a full colour-deficiency simulation needs a proper
    colour-appearance model, which this lab does not implement and does
    not pretend to. What this function supports is a narrow, checkable
    claim: two colours with nearly equal luminance are distinguishable by
    hue alone, and hue alone is exactly what some readers do not have.

    Write it: `mcolors.to_rgb(colour)` gives three channels in
    0..1. Linearise each with `c/12.92` if `c <= 0.04045` else
    `((c + 0.055) / 1.055) ** 2.4`, then weight them 0.2126, 0.7152 and
    0.0722 and sum.
    """
    raise NotImplementedError


def luminance_separation(colour_a, colour_b):
    """How far apart two colours sit on the one axis every reader has."""
    return abs(relative_luminance(colour_a) - relative_luminance(colour_b))
