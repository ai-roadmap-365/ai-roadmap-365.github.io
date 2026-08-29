"""Reference test suite for Day 128 — "Plots You Can Assert On".

Every test asserts on artist state — labels, limits, line data, the
number of open figures, legend text, file bytes — never on rendered
pixels compared to a golden image. A chart is an object graph, and object
graphs are testable.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider
"""

from __future__ import annotations

import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pytest

import plotting as P


@pytest.fixture(autouse=True)
def _close_all_figures_between_tests():
    """Every test starts and ends with zero open figures, so one test's
    figures can never leak into the next test's fignum count."""
    plt.close("all")
    yield
    plt.close("all")


@pytest.fixture
def tmp_out_dir():
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        yield d


# ---------------------------------------------------------------------------
# Exercise 1 — the two APIs
# ---------------------------------------------------------------------------


def test_pyplot_style_puts_both_calls_on_one_figure():
    P.draw_line_pyplot_style([0, 1, 2], [0, 1, 4], "first")
    P.draw_line_pyplot_style([0, 1, 2], [2, 1, 0], "second")
    fignums = plt.get_fignums()
    assert len(fignums) == 1, f"expected one figure, got {len(fignums)}: {fignums}"
    current = plt.figure(fignums[0])
    assert len(current.axes[0].lines) == 2


def test_object_style_produces_two_independent_figures():
    fig1, ax1 = P.draw_line_object_style([0, 1, 2], [0, 1, 4], "first")
    fig2, ax2 = P.draw_line_object_style([0, 1, 2], [2, 1, 0], "second")
    fignums = plt.get_fignums()
    assert len(fignums) == 2, f"expected two figures, got {len(fignums)}: {fignums}"
    assert len(ax1.lines) == 1
    assert len(ax2.lines) == 1
    assert fig1.number != fig2.number


def test_titles_use_the_exact_specified_strings():
    _, ax_obj = P.draw_line_object_style([0, 1], [0, 1], "x")
    assert ax_obj.get_title() == "drawn with the object API"
    P.draw_line_pyplot_style([0, 1], [0, 1], "x")
    assert plt.gca().get_title() == "drawn with the pyplot state machine"


# ---------------------------------------------------------------------------
# Exercise 2 — data round-trip
# ---------------------------------------------------------------------------


def test_line_data_round_trips_exactly():
    x = np.array([0.0, 1.5, 3.0, 4.5])
    y = np.array([2.0, -1.0, 0.5, 7.25])
    _, ax = P.make_line_axes(x, y)
    xy = ax.lines[0].get_xydata()
    assert np.array_equal(xy[:, 0], x)
    assert np.array_equal(xy[:, 1], y)


# ---------------------------------------------------------------------------
# Exercise 3 — pixel arithmetic
# ---------------------------------------------------------------------------


def test_600x400_at_100dpi():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([0, 1, 2], [0, 1, 0])
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        path = os.path.join(d, "a.png")
        P.save_at_size_and_dpi(fig, path, dpi=100)
        assert P.png_dimensions(path) == (600, 400)


def test_doubling_dpi_doubles_pixel_dimensions():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([0, 1, 2], [0, 1, 0])
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        p100 = os.path.join(d, "p100.png")
        p200 = os.path.join(d, "p200.png")
        P.save_at_size_and_dpi(fig, p100, dpi=100)
        P.save_at_size_and_dpi(fig, p200, dpi=200)
        w100, h100 = P.png_dimensions(p100)
        w200, h200 = P.png_dimensions(p200)
        assert (w200, h200) == (w100 * 2, h100 * 2)


# ---------------------------------------------------------------------------
# Exercise 4 — labels, limits, ticks, scales
# ---------------------------------------------------------------------------


def test_configure_axes_sets_label_and_title():
    fig, ax = plt.subplots()
    P.configure_axes(ax, xlabel="depth (m)", title="Ocean profile")
    assert ax.get_xlabel() == "depth (m)"
    assert ax.get_title() == "Ocean profile"


def test_explicit_ylim_overrides_autoscale():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 3], [0, 100, 5, 80])
    fig.canvas.draw()
    autoscaled = ax.get_ylim()
    # the data ranges 0-100; autoscale should NOT already be (-5, 5)
    assert not (abs(autoscaled[0] - (-5)) < 1e-9 and abs(autoscaled[1] - 5) < 1e-9)
    P.configure_axes(ax, xlabel="x", title="t", ylim=(-5, 5))
    assert ax.get_ylim() == (-5, 5)


# ---------------------------------------------------------------------------
# Exercise 5 — subplots
# ---------------------------------------------------------------------------


def test_grid_shape_is_nrows_by_ncols():
    fig, axes = P.make_grid(2, 3)
    assert axes.shape == (2, 3)


def test_each_axes_in_grid_is_independent():
    fig, axes = P.make_grid(2, 2)
    axes[0, 0].set_xlabel("only here")
    assert axes[0, 0].get_xlabel() == "only here"
    assert axes[0, 1].get_xlabel() == ""
    assert axes[1, 0].get_xlabel() == ""
    assert axes[1, 1].get_xlabel() == ""


# ---------------------------------------------------------------------------
# Exercise 6 — log scale and non-positive data
# ---------------------------------------------------------------------------


def test_log_yscale_is_applied():
    fig, ax = P.plot_with_log_yscale([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
    assert ax.get_yscale() == "log"


def test_log_yscale_excludes_the_zero_valued_point_from_view():
    fig, ax = P.plot_with_log_yscale([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
    ymin, ymax = ax.get_ylim()
    # A log axis cannot include zero or below: the lower rendered limit
    # must sit strictly above zero, which means the (x=0, y=0) point --
    # still present in the line's own data -- falls outside the visible
    # range. The data itself is not dropped; only what gets drawn is.
    assert ymin > 0, f"expected the log-scale lower limit to exceed 0, got {ymin}"
    xy = ax.lines[0].get_xydata()
    assert xy[0, 1] == 0, "the original data should still contain the zero point"


# ---------------------------------------------------------------------------
# Exercise 7 — legends
# ---------------------------------------------------------------------------


def test_legend_text_matches_labels_in_order():
    _, ax = P.plot_two_series_with_legend(
        [0, 1, 2], [0, 1, 2], "measured", [0, 1, 2], "predicted"
    )
    legend = ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["measured", "predicted"]


# ---------------------------------------------------------------------------
# Exercise 8 — figure lifecycle
# ---------------------------------------------------------------------------


def test_unclosed_figures_accumulate():
    figs = P.open_figures_without_closing(5)
    assert len(figs) == 5
    assert len(plt.get_fignums()) == 5


def test_closing_each_figure_empties_the_registry():
    figs = P.open_figures_without_closing(4)
    assert len(plt.get_fignums()) == 4
    for fig in figs:
        plt.close(fig)
    assert plt.get_fignums() == []


def test_opening_more_than_twenty_figures_warns():
    with pytest.warns(RuntimeWarning, match="More than 20 figures"):
        figs = P.open_figures_without_closing(22)
    assert len(plt.get_fignums()) == 22
    for fig in figs:
        plt.close(fig)


# ---------------------------------------------------------------------------
# Exercise 9 — vector versus raster
# ---------------------------------------------------------------------------


def test_svg_contains_the_axis_label_as_searchable_text():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 0])
    ax.set_xlabel("depth (m)")
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        png_path = os.path.join(d, "a.png")
        svg_path = os.path.join(d, "a.svg")
        P.save_png_and_svg(fig, png_path, svg_path)
        svg_text = open(svg_path, encoding="utf-8").read()
        assert "depth (m)" in svg_text


def test_png_does_not_contain_the_axis_label_as_bytes():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 0])
    ax.set_xlabel("depth (m)")
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        png_path = os.path.join(d, "a.png")
        svg_path = os.path.join(d, "a.svg")
        P.save_png_and_svg(fig, png_path, svg_path)
        png_bytes = open(png_path, "rb").read()
        assert b"depth (m)" not in png_bytes


# ---------------------------------------------------------------------------
# Housekeeping — the lab must leave no image files behind
# ---------------------------------------------------------------------------


def test_no_image_files_left_in_the_lab_directory():
    lab_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    leftovers = []
    for root, _dirs, files in os.walk(lab_dir):
        if ".venv" in root or ".pytest_cache" in root or "__pycache__" in root:
            continue
        for name in files:
            if name.endswith((".png", ".svg", ".pdf")):
                leftovers.append(os.path.join(root, name))
    assert leftovers == [], f"image files left behind: {leftovers}"
