"""The reference test suite for Day 111. Every test checks REAL behaviour
of the functions in this directory -- real numbers, real convergence, real
overflow -- never source text.
"""

import math

import numpy as np
import pytest

import dataset as D
import descent as G

# ---------------------------------------------------------------------------
# Exercise 1 -- numeric_gradient
# ---------------------------------------------------------------------------


def test_numeric_gradient_matches_quadratic():
    f = lambda x: 0.5 * D.A * x * x
    for x in (-2.0, -0.5, 0.0, 0.5, 3.0):
        assert abs(G.numeric_gradient(f, x, D.NUMERIC_H) - D.A * x) < D.NUMERIC_TOL


def test_numeric_gradient_matches_composed_function():
    # d/dx sin(x**2) = 2x cos(x**2)
    f = lambda x: math.sin(x * x)
    for x in (0.3, 1.5, -0.8):
        analytic = 2.0 * x * math.cos(x * x)
        assert abs(G.numeric_gradient(f, x, D.NUMERIC_H) - analytic) < D.NUMERIC_TOL


def test_numeric_gradient_handles_vector_input():
    grad = G.numeric_gradient(D.check_function, D.CHECK_POINT, D.NUMERIC_H)
    correct = D.check_gradient_correct(D.CHECK_POINT)
    assert np.max(np.abs(grad - correct)) < D.NUMERIC_TOL


# ---------------------------------------------------------------------------
# Exercise 2 -- gradient_descent returns the whole path
# ---------------------------------------------------------------------------


def test_gradient_descent_returns_whole_path():
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_MONOTONE, 10)
    assert len(path) == 11
    assert path[0] == D.X0_1D


def test_gradient_descent_matches_closed_form():
    lr = D.LR_MONOTONE
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, 20)
    for n, x_n in enumerate(path):
        closed_form = D.X0_1D * (1.0 - lr * D.A) ** n
        assert abs(x_n - closed_form) < D.EXACT_TOL


# ---------------------------------------------------------------------------
# Exercise 3 -- the three regimes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "lr,expected",
    [
        (D.LR_MONOTONE, "monotone"),
        (D.LR_EXACT, "exact"),
        (D.LR_OSCILLATING, "oscillating"),
        (D.LR_DIVERGENT, "divergent"),
    ],
)
def test_regime_classification(lr, expected):
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, D.REGIME_ITERS)
    assert G.classify_regime(path, D.A, lr) == expected


def test_exact_regime_lands_on_zero_in_one_step():
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_EXACT, 1)
    assert path[1] == 0.0


def test_oscillating_regime_alternates_sign():
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_OSCILLATING, 6)
    signs = [1 if v > 0 else -1 for v in path]
    assert all(signs[i] != signs[i + 1] for i in range(len(signs) - 1))


def test_divergent_regime_grows_without_shrinking():
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_DIVERGENT, D.REGIME_ITERS)
    assert abs(path[-1]) > abs(path[0]) * 10


# ---------------------------------------------------------------------------
# Exercise 4 -- the contraction ratio is exactly |1 - lr * a|
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lr", [D.LR_MONOTONE, D.LR_OSCILLATING, D.LR_DIVERGENT])
def test_contraction_ratio_matches_prediction(lr):
    path = G.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, 15)
    predicted = abs(1.0 - lr * D.A)
    for ratio in G.per_step_ratios(path):
        assert abs(ratio - predicted) < D.EXACT_TOL


# ---------------------------------------------------------------------------
# Exercise 5 -- ill-conditioning: steps grow with kappa
# ---------------------------------------------------------------------------


def test_steps_to_tolerance_nondecreasing_in_kappa():
    counts = [
        G.steps_to_tolerance(
            D.bowl_grad(k), np.array(D.KAPPA_START), D.kappa_lr(k),
            D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS,
        )
        for k in D.KAPPA_VALUES
    ]
    assert all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1))
    assert counts[-1] >= 10 * max(counts[0], 1)


def test_isotropic_bowl_converges_in_one_step():
    steps = G.steps_to_tolerance(
        D.bowl_grad(1), np.array(D.KAPPA_START), D.kappa_lr(1),
        D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS,
    )
    assert steps == 1


# ---------------------------------------------------------------------------
# Exercise 6 -- momentum beats plain descent on the same learning rate
# ---------------------------------------------------------------------------


def test_momentum_needs_fewer_steps_than_plain_descent():
    k = D.MOMENTUM_KAPPA
    lr = D.kappa_lr(k)
    plain = G.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), lr, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS)
    momentum = G.steps_to_tolerance_momentum(
        D.bowl_grad(k), np.array(D.KAPPA_START), D.MOMENTUM_LR, D.MOMENTUM_BETA,
        D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS,
    )
    assert momentum < plain


# ---------------------------------------------------------------------------
# Exercise 7 -- gradient checking catches a sign-error bug
# ---------------------------------------------------------------------------


def test_gradient_check_passes_correct_gradient():
    flags = G.gradient_check(D.check_function, D.check_gradient_correct, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
    assert all(flags)


def test_gradient_check_flags_exactly_the_buggy_component():
    flags = G.gradient_check(D.check_function, D.check_gradient_buggy, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL)
    assert flags == [True, False, True]


# ---------------------------------------------------------------------------
# Exercise 8 -- non-convexity: initialisation decides the minimum
# ---------------------------------------------------------------------------


def test_two_initialisations_reach_different_minima():
    left = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_LEFT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
    right = G.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_RIGHT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS)
    assert G.minima_differ(left[-1], right[-1], D.TWO_MINIMA_MARGIN)
    assert left[-1] < 0 < right[-1]
    assert abs(left[-1] + 1.0) < 1e-3
    assert abs(right[-1] - 1.0) < 1e-3


# ---------------------------------------------------------------------------
# Exercise 9 -- the stopping-criterion trap
# ---------------------------------------------------------------------------


def test_naive_delta_f_criterion_stops_early_on_the_plateau():
    result = G.stopping_criteria_disagree(
        D.PLATEAU_X0, D.plateau_grad, D.plateau_value, D.PLATEAU_LR,
        D.PLATEAU_GRAD_TOL, D.PLATEAU_DELTA_F_TOL,
    )
    assert result["grad_norm"] >= D.PLATEAU_GRAD_TOL
    assert result["delta_f"] < D.PLATEAU_DELTA_F_TOL
    assert result["naive_stops_early"] is True


# ---------------------------------------------------------------------------
# The hook: overflow, then nan, handled without crashing
# ---------------------------------------------------------------------------


def test_divergent_run_overflows_to_inf_then_nan_without_raising():
    path = G.gradient_descent(lambda x: D.HOOK_A * x, D.HOOK_X0, D.HOOK_LR, D.HOOK_ITERS)
    assert any(math.isinf(v) for v in path)
    assert any(math.isnan(v) for v in path)
    first_inf = next(i for i, v in enumerate(path) if math.isinf(v))
    first_nan = next(i for i, v in enumerate(path) if math.isnan(v))
    assert first_nan == first_inf + 1


def test_loss_increases_every_step_before_it_overflows():
    path = G.gradient_descent(lambda x: D.HOOK_A * x, D.HOOK_X0, D.HOOK_LR, 20)
    losses = [0.5 * D.HOOK_A * v * v for v in path]
    assert all(losses[i + 1] > losses[i] for i in range(len(losses) - 1))
