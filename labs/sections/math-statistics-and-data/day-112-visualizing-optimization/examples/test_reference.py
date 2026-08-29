"""The reference test suite: nine numbered checks, one per lab exercise.

Every test writes into pytest's own tmp_path fixture (a directory pytest
creates and cleans up itself, outside this lab), never into the lab
directory. That is what makes exercise 9's cleanup check meaningful: nothing
in this suite is exempt from it.
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


# -- exercise 1: evaluate_grid ------------------------------------------------


def test_evaluate_grid_shape_and_minimum():
    X, Y, Z = G.evaluate_grid(D.WELL_F, XLIM, YLIM, GRID_N)
    assert X.shape == (GRID_N, GRID_N)
    assert Y.shape == (GRID_N, GRID_N)
    assert Z.shape == (GRID_N, GRID_N)
    iy, ix = np.unravel_index(np.argmin(Z), Z.shape)
    assert abs(X[iy, ix]) < 1e-9
    assert abs(Y[iy, ix]) < 1e-9
    assert Z[iy, ix] == pytest.approx(0.0, abs=1e-9)


# -- exercise 2: ascii contour renderer --------------------------------------


def test_ascii_contour_exact_characters():
    _, _, Z = G.evaluate_grid(lambda x, y: x**2 + y**2, (-2, 2), (-2, 2), 5)
    rendered = G.ascii_contour(Z)
    rows = rendered.split("\n")
    assert len(rows) == 5
    # Centre cell: value 0, the minimum -> the lightest character (a space).
    assert rows[2][2] == " "
    # Every corner: value 8, the maximum -> the densest character.
    for r, c in [(0, 0), (0, 4), (4, 0), (4, 4)]:
        assert rows[r][c] == "#"
    # A transposed grid or a flipped row order would break this symmetry:
    # x^2 + y^2 is symmetric under both left-right and top-bottom mirror.
    assert all(rows[r] == rows[4 - r] for r in range(5))
    assert all(rows[r] == rows[r][::-1] for r in range(5))


# -- exercise 3: Pillow heatmap PNG ------------------------------------------


def test_heatmap_png_size_and_minimum_color(tmp_path):
    _, _, Z = G.evaluate_grid(D.WELL_F, XLIM, YLIM, GRID_N)
    out = tmp_path / "heat.png"
    img = IM.heatmap_png(Z, XLIM, YLIM, str(out))
    assert out.exists()
    assert img.size == (GRID_N, GRID_N)
    reopened = Image.open(out)
    assert reopened.size == (GRID_N, GRID_N)
    px, py = G.world_to_pixel(0.0, 0.0, XLIM, YLIM, GRID_N, GRID_N)
    assert reopened.convert("RGB").getpixel((round(px), round(py))) == (13, 27, 84)


# -- exercise 4: path drawn over the heatmap, and the pixel transform --------


def test_world_to_pixel_corners():
    # x grows right: no flip. y grows up in data space, down in pixel rows.
    assert G.world_to_pixel(-4.0, 4.0, XLIM, YLIM, 101, 101) == (0.0, 0.0)
    assert G.world_to_pixel(4.0, -4.0, XLIM, YLIM, 101, 101) == (100.0, 100.0)
    assert G.world_to_pixel(0.0, 0.0, XLIM, YLIM, 101, 101) == (50.0, 50.0)


def test_descent_path_drawn_over_heatmap(tmp_path):
    _, _, Z = G.evaluate_grid(D.WELL_F, XLIM, YLIM, GRID_N)
    path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    out = tmp_path / "path.png"
    IM.draw_path_on_heatmap(Z, XLIM, YLIM, path, str(out))
    assert out.exists()
    img = Image.open(out)
    assert img.size == (GRID_N, GRID_N)

    first_px = G.world_to_pixel(*path[0], XLIM, YLIM, GRID_N, GRID_N)
    expected_first = G.world_to_pixel(*D.START, XLIM, YLIM, GRID_N, GRID_N)
    assert first_px == expected_first

    last_px = G.world_to_pixel(*path[-1], XLIM, YLIM, GRID_N, GRID_N)
    minimum_px = G.world_to_pixel(0.0, 0.0, XLIM, YLIM, GRID_N, GRID_N)
    distance = ((last_px[0] - minimum_px[0]) ** 2 + (last_px[1] - minimum_px[1]) ** 2) ** 0.5
    assert distance < D.PIXEL_TOL


# -- exercise 5: loss curve, linear and log, and the collinearity proof -----


def test_loss_curve_png_linear_and_log(tmp_path):
    path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    losses = DS.losses_along(D.WELL_F, path)

    lin_out = tmp_path / "loss_linear.png"
    log_out = tmp_path / "loss_log.png"
    IM.loss_curve_png(losses, str(lin_out), log=False)
    IM.loss_curve_png(losses, str(log_out), log=True)
    assert lin_out.exists() and log_out.exists()
    assert Image.open(lin_out).size == (500, 350)
    assert Image.open(log_out).size == (500, 350)


def test_log_axis_points_are_collinear():
    # a = b = 1: the update x <- (1 - 2 * lr * a) x is an EXACT geometric
    # recursion, so loss = a x^2 + b y^2 decays as a single power of a
    # constant ratio and log10(loss) against iteration is a straight line
    # by construction, not by approximation.
    path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    losses = DS.losses_along(D.WELL_F, path)
    points = IM.loss_curve_points(losses, width=500, height=350, margin=50, log=True)
    xs = np.array([p[0] for p in points])
    ys = np.array([p[1] for p in points])
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    residual = np.max(np.abs(ys - (slope * xs + intercept)))
    assert residual < 1e-6  # pixel units: far below one pixel


# -- exercise 6: animated GIF -------------------------------------------------


def test_animated_gif_frame_count(tmp_path):
    _, _, Z = G.evaluate_grid(D.WELL_F, XLIM, YLIM, GRID_N)
    path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, 20)
    out = tmp_path / "descent.gif"
    IM.animated_descent_gif(Z, XLIM, YLIM, path, str(out))
    assert out.exists()
    reopened = Image.open(out)
    assert reopened.format == "GIF"
    assert reopened.n_frames == len(path)


# -- exercise 7: the learning-rate sweep -------------------------------------


def test_learning_rate_sweep_shape():
    etas = np.round(np.arange(0.05, 2.55, 0.1), 2)
    sweep = DS.learning_rate_sweep(D.sweep_grad, D.sweep_f, D.SWEEP_X0, etas, D.SWEEP_STEPS)
    assert [e for e, _ in sweep] == list(etas)

    finite = [(e, loss) for e, loss in sweep if np.isfinite(loss)]
    divergent = [(e, loss) for e, loss in sweep if not np.isfinite(loss)]

    # A basin, not a single magic number: more than one eta converges well.
    good = [e for e, loss in finite if loss < 1e-6]
    assert len(good) >= 3

    # The argmin sits strictly inside the swept range, not at either edge.
    best_eta = min(finite, key=lambda pair: pair[1])[0]
    assert etas[0] < best_eta < etas[-1]

    # And the sweep actually reaches the cliff: some etas genuinely diverge,
    # caught as float('inf') rather than raising.
    assert len(divergent) >= 1
    assert all(loss == float("inf") for _, loss in divergent)
    # Divergence only happens on the far side of the theoretical threshold
    # eta = 1 / a = 1.0 for f(x) = x^2.
    assert all(e > 1.0 for e, _ in divergent)


# -- exercise 8: two runs, same loss, very different paths -------------------


def test_two_runs_same_loss_different_path_length():
    well_path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
    ill_path = DS.gradient_descent(D.ILL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)

    well_loss = DS.losses_along(D.WELL_F, well_path)[-1]
    ill_loss = DS.losses_along(D.ILL_F, ill_path)[-1]
    relative_gap = abs(well_loss - ill_loss) / max(well_loss, ill_loss)
    assert relative_gap < D.LOSS_MATCH_TOL

    well_len = DS.path_length(well_path)
    ill_len = DS.path_length(ill_path)
    assert ill_len / well_len > D.PATH_LENGTH_RATIO_MIN


# -- exercise 9 (the cleanup check) lives in tests/run_tests.sh, which
# inspects the whole lab directory after every other check has run -- a
# single pytest test cannot see "did the ENTIRE suite leave anything behind"
# from inside one test function.
