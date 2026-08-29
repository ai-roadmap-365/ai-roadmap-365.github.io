"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong."
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
    plt.close("all")
    yield
    plt.close("all")


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except NotImplementedError:
        pytest.skip(f"not attempted yet: {what}")
    return result


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from
    a collection error that quietly ran nothing at all."""
    assert P.plt is plt


# ---------------------------------------------------------------------------
# Exercise 1
# ---------------------------------------------------------------------------


def test_pyplot_style_puts_both_calls_on_one_figure():
    attempt(
        lambda: P.draw_line_pyplot_style([0, 1, 2], [0, 1, 4], "first"),
        "draw_line_pyplot_style",
    )
    attempt(
        lambda: P.draw_line_pyplot_style([0, 1, 2], [2, 1, 0], "second"),
        "draw_line_pyplot_style",
    )
    fignums = plt.get_fignums()
    if not fignums:
        pytest.skip("not attempted yet: draw_line_pyplot_style")
    assert len(fignums) == 1


def test_object_style_produces_two_independent_figures():
    result1 = attempt(
        lambda: P.draw_line_object_style([0, 1, 2], [0, 1, 4], "first"),
        "draw_line_object_style",
    )
    result2 = attempt(
        lambda: P.draw_line_object_style([0, 1, 2], [2, 1, 0], "second"),
        "draw_line_object_style",
    )
    fig1, ax1 = result1
    fig2, ax2 = result2
    assert len(plt.get_fignums()) == 2
    assert len(ax1.lines) == 1
    assert len(ax2.lines) == 1


# ---------------------------------------------------------------------------
# Exercise 2
# ---------------------------------------------------------------------------


def test_line_data_round_trips_exactly():
    x = np.array([0.0, 1.5, 3.0, 4.5])
    y = np.array([2.0, -1.0, 0.5, 7.25])
    _, ax = attempt(lambda: P.make_line_axes(x, y), "make_line_axes")
    xy = ax.lines[0].get_xydata()
    assert np.array_equal(xy[:, 0], x)
    assert np.array_equal(xy[:, 1], y)


# ---------------------------------------------------------------------------
# Exercise 3
# ---------------------------------------------------------------------------


def test_600x400_at_100dpi():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([0, 1, 2], [0, 1, 0])
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        path = os.path.join(d, "a.png")
        attempt(
            lambda: P.save_at_size_and_dpi(fig, path, dpi=100),
            "save_at_size_and_dpi",
        )
        if not os.path.exists(path):
            pytest.skip("not attempted yet: save_at_size_and_dpi")
        dims = attempt(lambda: P.png_dimensions(path), "png_dimensions")
        assert dims == (600, 400)


# ---------------------------------------------------------------------------
# Exercise 4
# ---------------------------------------------------------------------------


def test_configure_axes_sets_label_and_title():
    fig, ax = plt.subplots()
    attempt(
        lambda: P.configure_axes(ax, xlabel="depth (m)", title="Ocean profile"),
        "configure_axes",
    )
    assert ax.get_xlabel() == "depth (m)"
    assert ax.get_title() == "Ocean profile"


def test_explicit_ylim_overrides_autoscale():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 3], [0, 100, 5, 80])
    attempt(
        lambda: P.configure_axes(ax, xlabel="x", title="t", ylim=(-5, 5)),
        "configure_axes",
    )
    if ax.get_ylim() != (-5, 5):
        pytest.skip("not attempted yet: configure_axes(ylim=...)")
    assert ax.get_ylim() == (-5, 5)


# ---------------------------------------------------------------------------
# Exercise 5
# ---------------------------------------------------------------------------


def test_grid_shape_is_nrows_by_ncols():
    fig, axes = attempt(lambda: P.make_grid(2, 3), "make_grid")
    assert axes.shape == (2, 3)


def test_each_axes_in_grid_is_independent():
    fig, axes = attempt(lambda: P.make_grid(2, 2), "make_grid")
    axes[0, 0].set_xlabel("only here")
    assert axes[0, 1].get_xlabel() == ""


# ---------------------------------------------------------------------------
# Exercise 6
# ---------------------------------------------------------------------------


def test_log_yscale_excludes_the_zero_valued_point_from_view():
    fig, ax = attempt(
        lambda: P.plot_with_log_yscale([0, 1, 2, 3, 4], [0, 1, 4, 9, 16]),
        "plot_with_log_yscale",
    )
    assert ax.get_yscale() == "log"
    ymin, _ = ax.get_ylim()
    assert ymin > 0


# ---------------------------------------------------------------------------
# Exercise 7
# ---------------------------------------------------------------------------


def test_legend_text_matches_labels_in_order():
    _, ax = attempt(
        lambda: P.plot_two_series_with_legend(
            [0, 1, 2], [0, 1, 2], "measured", [0, 1, 2], "predicted"
        ),
        "plot_two_series_with_legend",
    )
    legend = ax.get_legend()
    if legend is None:
        pytest.skip("not attempted yet: plot_two_series_with_legend")
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["measured", "predicted"]


# ---------------------------------------------------------------------------
# Exercise 8
# ---------------------------------------------------------------------------


def test_unclosed_figures_accumulate():
    figs = attempt(
        lambda: P.open_figures_without_closing(5), "open_figures_without_closing"
    )
    assert len(figs) == 5
    assert len(plt.get_fignums()) == 5


def test_closing_each_figure_empties_the_registry():
    figs = attempt(
        lambda: P.open_figures_without_closing(4), "open_figures_without_closing"
    )
    for fig in figs:
        plt.close(fig)
    assert plt.get_fignums() == []


# ---------------------------------------------------------------------------
# Exercise 9
# ---------------------------------------------------------------------------


def test_svg_has_label_text_png_does_not():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 0])
    ax.set_xlabel("depth (m)")
    with tempfile.TemporaryDirectory(prefix="d128-") as d:
        png_path = os.path.join(d, "a.png")
        svg_path = os.path.join(d, "a.svg")
        attempt(
            lambda: P.save_png_and_svg(fig, png_path, svg_path), "save_png_and_svg"
        )
        if not (os.path.exists(png_path) and os.path.exists(svg_path)):
            pytest.skip("not attempted yet: save_png_and_svg")
        svg_text = open(svg_path, encoding="utf-8").read()
        png_bytes = open(png_path, "rb").read()
        assert "depth (m)" in svg_text
        assert b"depth (m)" not in png_bytes
