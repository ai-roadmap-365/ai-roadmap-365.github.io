"""The starter test suite: skips unattempted work instead of failing it.

Every exercise function returns None until you write it. A test whose
function still returns None is SKIPPED ("not attempted"). A test whose
function returns something else is checked for real -- a wrong answer FAILS
and prints what you got beside what was expected.

Run at any point:

    .venv/bin/pytest starter -q
"""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

import dataset as D
import descent as DS
import gridviz as G
import imaging as IM

XLIM = (-4.0, 4.0)
YLIM = (-4.0, 4.0)
GRID_N = 101


def skip_if_none(value, label):
    if value is None:
        pytest.skip(f"{label} not attempted yet")


def get_grid(f=None, xlim=XLIM, ylim=YLIM, n=GRID_N):
    """Every later exercise needs a working evaluate_grid. Skip cleanly
    rather than crashing on an unpack of None if it is not attempted yet."""
    f = D.WELL_F if f is None else f
    result = G.evaluate_grid(f, xlim, ylim, n)
    skip_if_none(result, "evaluate_grid (needed by this exercise)")
    return result


# -- exercise 1: evaluate_grid ------------------------------------------------


def test_1_evaluate_grid_shape_and_minimum():
    result = G.evaluate_grid(D.WELL_F, XLIM, YLIM, GRID_N)
    skip_if_none(result, "evaluate_grid")
    X, Y, Z = result
    assert X.shape == (GRID_N, GRID_N)
    assert Y.shape == (GRID_N, GRID_N)
    assert Z.shape == (GRID_N, GRID_N)
    iy, ix = np.unravel_index(np.argmin(Z), Z.shape)
    assert abs(X[iy, ix]) < 1e-9
    assert abs(Y[iy, ix]) < 1e-9


# -- exercise 2: ascii contour renderer --------------------------------------


def test_2_ascii_contour_exact_characters():
    grid = G.evaluate_grid(lambda x, y: x**2 + y**2, (-2, 2), (-2, 2), 5)
    skip_if_none(grid, "evaluate_grid")
    _, _, Z = grid
    rendered = G.ascii_contour(Z)
    skip_if_none(rendered, "ascii_contour")
    rows = rendered.split("\n")
    assert rows[2][2] == " "
    for r, c in [(0, 0), (0, 4), (4, 0), (4, 4)]:
        assert rows[r][c] == "#"


# -- exercise 3: Pillow heatmap PNG ------------------------------------------


def test_3_heatmap_array_shape_and_dtype():
    _, _, Z = get_grid()
    arr = IM.heatmap_array(Z)
    skip_if_none(arr, "heatmap_array")
    assert arr.shape == (GRID_N, GRID_N, 3)
    assert arr.dtype == np.uint8


def test_3_heatmap_png_size_and_minimum_color(tmp_path):
    _, _, Z = get_grid()
    out = tmp_path / "heat.png"
    img = IM.heatmap_png(Z, XLIM, YLIM, str(out))
    skip_if_none(img, "heatmap_png")
    assert out.exists()
    assert img.size == (GRID_N, GRID_N)
    px, py = G.world_to_pixel(0.0, 0.0, XLIM, YLIM, GRID_N, GRID_N) or (None, None)
    if px is None:
        pytest.skip("world_to_pixel not attempted yet")
    reopened = Image.open(out).convert("RGB")
    assert reopened.getpixel((round(px), round(py))) == (13, 27, 84)


# -- exercise 4: world_to_pixel and the drawn path ---------------------------


def test_4_world_to_pixel_corners():
    result = G.world_to_pixel(-4.0, 4.0, XLIM, YLIM, 101, 101)
    skip_if_none(result, "world_to_pixel")
    assert result == (0.0, 0.0)
    assert G.world_to_pixel(4.0, -4.0, XLIM, YLIM, 101, 101) == (100.0, 100.0)
    assert G.world_to_pixel(0.0, 0.0, XLIM, YLIM, 101, 101) == (50.0, 50.0)


def test_4_descent_path_drawn_over_heatmap(tmp_path):
    _, _, Z = get_grid()
    path = D.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    out = tmp_path / "path.png"
    img = IM.draw_path_on_heatmap(Z, XLIM, YLIM, path, str(out))
    skip_if_none(img, "draw_path_on_heatmap")
    assert out.exists()
    last_px = G.world_to_pixel(*path[-1], XLIM, YLIM, GRID_N, GRID_N)
    min_px = G.world_to_pixel(0.0, 0.0, XLIM, YLIM, GRID_N, GRID_N)
    distance = ((last_px[0] - min_px[0]) ** 2 + (last_px[1] - min_px[1]) ** 2) ** 0.5
    assert distance < D.PIXEL_TOL


# -- exercise 5: loss curves --------------------------------------------------


def test_5_loss_curve_points_collinear_on_log_axis():
    path = D.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    losses = D.losses_along(D.WELL_F, path)
    points = IM.loss_curve_points(losses, width=500, height=350, margin=50, log=True)
    skip_if_none(points, "loss_curve_points")
    xs = np.array([p[0] for p in points])
    ys = np.array([p[1] for p in points])
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    residual = np.max(np.abs(ys - (slope * xs + intercept)))
    assert residual < 1e-6


def test_5_loss_curve_png(tmp_path):
    path = D.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    losses = D.losses_along(D.WELL_F, path)
    out = tmp_path / "loss.png"
    img = IM.loss_curve_png(losses, str(out), log=True)
    skip_if_none(img, "loss_curve_png")
    assert out.exists()
    assert Image.open(out).size == (500, 350)


# -- exercise 6: animated GIF -------------------------------------------------


def test_6_animated_gif_frame_count(tmp_path):
    _, _, Z = get_grid()
    path = D.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, 20)
    out = tmp_path / "descent.gif"
    result = IM.animated_descent_gif(Z, XLIM, YLIM, path, str(out))
    if not out.exists():
        pytest.skip("animated_descent_gif not attempted yet")
    reopened = Image.open(out)
    assert reopened.format == "GIF"
    assert reopened.n_frames == len(path)


# -- exercise 7: the learning-rate sweep -------------------------------------


def test_7_sweep_final_loss_catches_divergence():
    result = DS.sweep_final_loss(D.sweep_grad, D.sweep_f, D.SWEEP_X0, 2.5, D.SWEEP_STEPS)
    skip_if_none(result, "sweep_final_loss")
    assert result == float("inf")
    converged = DS.sweep_final_loss(D.sweep_grad, D.sweep_f, D.SWEEP_X0, 0.45, D.SWEEP_STEPS)
    assert converged < 1e-6


def test_7_learning_rate_sweep_shape():
    etas = np.round(np.arange(0.05, 2.55, 0.1), 2)
    sweep = DS.learning_rate_sweep(D.sweep_grad, D.sweep_f, D.SWEEP_X0, etas, D.SWEEP_STEPS)
    skip_if_none(sweep, "learning_rate_sweep")
    assert [e for e, _ in sweep] == list(etas)
    divergent = [(e, loss) for e, loss in sweep if not np.isfinite(loss)]
    assert len(divergent) >= 1


# -- exercise 8: path_length, and two runs at nearly the same loss ----------


def test_8_path_length_of_a_known_path():
    # A path that steps (0,0) -> (3,0) -> (3,4) has length 3 + 4 = 7 exactly
    # (a 3-4-5 triangle's two legs).
    known_path = np.array([[0.0, 0.0], [3.0, 0.0], [3.0, 4.0]])
    result = DS.path_length(known_path)
    skip_if_none(result, "path_length")
    assert result == pytest.approx(7.0)


def test_8_two_runs_same_loss_different_path_length():
    well_path = D.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    ill_path = D.gradient_descent(D.ILL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)

    well_loss = D.losses_along(D.WELL_F, well_path)[-1]
    ill_loss = D.losses_along(D.ILL_F, ill_path)[-1]
    relative_gap = abs(well_loss - ill_loss) / max(well_loss, ill_loss)
    assert relative_gap < D.LOSS_MATCH_TOL

    well_len = DS.path_length(well_path)
    ill_len = DS.path_length(ill_path)
    skip_if_none(well_len, "path_length")
    skip_if_none(ill_len, "path_length")
    assert ill_len / well_len > D.PATH_LENGTH_RATIO_MIN
