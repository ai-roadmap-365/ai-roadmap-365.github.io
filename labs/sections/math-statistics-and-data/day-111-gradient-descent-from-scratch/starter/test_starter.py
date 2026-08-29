"""Your running score. Unattempted work SKIPS; wrong work FAILS with both
values printed.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports everything skipped except the one
test that proves the suite itself runs. A skip means "not attempted". A
failure means "attempted and wrong", and shows your answer next to the
real one.
"""

import math

import numpy as np
import pytest

import dataset as D
import descent as S  # your work


def need(value, what):
    """Skip if the exercise has not been attempted yet, otherwise hand the
    value back."""
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def close(got, want, tol, what):
    assert abs(got - want) < tol, (
        f"{what}: your answer {got!r}, expected {want!r} "
        f"(difference {abs(got - want):.3e}, tolerance {tol:g})"
    )


def test_the_suite_itself_runs():
    """Always passes, so a green run is distinguishable from a collection
    error that quietly ran nothing at all."""
    assert D.EPSILON > 0.0


# ---------------------------------------------------------------------------
# Exercise 1 -- numeric_gradient
# ---------------------------------------------------------------------------


def test_1_numeric_gradient_matches_quadratic():
    f = lambda x: 0.5 * D.A * x * x
    got = need(S.numeric_gradient(f, 3.0, D.NUMERIC_H), "numeric_gradient")
    close(got, D.A * 3.0, D.NUMERIC_TOL, "numeric_gradient(0.5*a*x^2, x=3)")


def test_1_numeric_gradient_matches_composed_function():
    g = lambda x: math.sin(x * x)
    got = need(S.numeric_gradient(g, 1.5, D.NUMERIC_H), "numeric_gradient")
    close(got, 2.0 * 1.5 * math.cos(1.5 * 1.5), D.NUMERIC_TOL, "numeric_gradient(sin(x^2), x=1.5)")


def test_1_numeric_gradient_handles_a_vector():
    got = need(S.numeric_gradient(D.check_function, D.CHECK_POINT, D.NUMERIC_H), "numeric_gradient (vector)")
    correct = D.check_gradient_correct(D.CHECK_POINT)
    assert np.max(np.abs(np.asarray(got) - correct)) < D.NUMERIC_TOL


# ---------------------------------------------------------------------------
# Exercise 2 -- gradient_descent
# ---------------------------------------------------------------------------


def test_2_gradient_descent_returns_whole_path():
    path = need(S.gradient_descent(lambda x: D.A * x, D.X0_1D, D.LR_MONOTONE, 10), "gradient_descent")
    assert len(path) == 11, f"expected a path of length 11, got {len(path)}"
    assert path[0] == D.X0_1D


def test_2_gradient_descent_matches_closed_form():
    lr = D.LR_MONOTONE
    path = need(S.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, 20), "gradient_descent")
    for n, x_n in enumerate(path):
        closed_form = D.X0_1D * (1.0 - lr * D.A) ** n
        close(x_n, closed_form, D.EXACT_TOL, f"gradient_descent step {n}")


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
def test_3_regime_classification(lr, expected):
    path = need(S.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, D.REGIME_ITERS), "gradient_descent")
    got = need(S.classify_regime(path, D.A, lr), "classify_regime")
    assert got == expected, f"classify_regime at eta={lr}: your answer {got!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# Exercise 4 -- the contraction ratio
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lr", [D.LR_MONOTONE, D.LR_OSCILLATING, D.LR_DIVERGENT])
def test_4_contraction_ratio_matches_prediction(lr):
    path = need(S.gradient_descent(lambda x: D.A * x, D.X0_1D, lr, 15), "gradient_descent")
    ratios = need(S.per_step_ratios(path), "per_step_ratios")
    predicted = abs(1.0 - lr * D.A)
    for ratio in ratios:
        close(ratio, predicted, D.EXACT_TOL, f"per_step_ratios at eta={lr}")


# ---------------------------------------------------------------------------
# Exercise 5 -- ill-conditioning
# ---------------------------------------------------------------------------


def test_5_steps_to_tolerance_nondecreasing_in_kappa():
    counts = []
    for k in D.KAPPA_VALUES:
        steps = need(
            S.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), D.kappa_lr(k), D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS),
            "steps_to_tolerance",
        )
        counts.append(steps)
    assert all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1)), f"steps should not decrease as kappa grows: {counts}"
    assert counts[-1] >= 10 * max(counts[0], 1), (
        f"kappa={D.KAPPA_VALUES[-1]} should need at least 10x the steps of kappa={D.KAPPA_VALUES[0]}: {counts}"
    )


def test_5_isotropic_bowl_converges_in_one_step():
    steps = need(
        S.steps_to_tolerance(D.bowl_grad(1), np.array(D.KAPPA_START), D.kappa_lr(1), D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS),
        "steps_to_tolerance",
    )
    assert steps == 1, f"the optimal step size should solve an isotropic bowl in one step, got {steps}"


# ---------------------------------------------------------------------------
# Exercise 6 -- momentum
# ---------------------------------------------------------------------------


def test_6_momentum_needs_fewer_steps_than_plain_descent():
    k = D.MOMENTUM_KAPPA
    lr = D.kappa_lr(k)
    plain = need(
        S.steps_to_tolerance(D.bowl_grad(k), np.array(D.KAPPA_START), lr, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS),
        "steps_to_tolerance",
    )
    momentum = need(
        S.steps_to_tolerance_momentum(
            D.bowl_grad(k), np.array(D.KAPPA_START), D.MOMENTUM_LR, D.MOMENTUM_BETA, D.KAPPA_GRAD_TOL, D.KAPPA_MAX_ITERS
        ),
        "steps_to_tolerance_momentum",
    )
    assert momentum < plain, f"momentum ({momentum} steps) should beat plain descent ({plain} steps) at the same learning rate"


def test_6_momentum_path_has_the_right_length():
    path = need(
        S.gradient_descent_momentum(D.bowl_grad(D.MOMENTUM_KAPPA), np.array(D.KAPPA_START), D.MOMENTUM_LR, D.MOMENTUM_BETA, 10),
        "gradient_descent_momentum",
    )
    assert len(path) == 11


# ---------------------------------------------------------------------------
# Exercise 7 -- gradient checking
# ---------------------------------------------------------------------------


def test_7_gradient_check_passes_correct_gradient():
    flags = need(
        S.gradient_check(D.check_function, D.check_gradient_correct, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL),
        "gradient_check",
    )
    assert all(flags), f"the correct gradient should pass every component, got {flags}"


def test_7_gradient_check_flags_exactly_the_buggy_component():
    flags = need(
        S.gradient_check(D.check_function, D.check_gradient_buggy, D.CHECK_POINT, D.NUMERIC_H, D.CHECK_TOL),
        "gradient_check",
    )
    assert list(flags) == [True, False, True], f"expected [True, False, True], got {flags}"


# ---------------------------------------------------------------------------
# Exercise 8 -- two minima
# ---------------------------------------------------------------------------


def test_8_two_initialisations_reach_different_minima():
    left = need(
        S.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_LEFT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS),
        "gradient_descent",
    )
    right = need(
        S.gradient_descent(D.two_minima_grad, D.TWO_MINIMA_RIGHT_START, D.TWO_MINIMA_LR, D.TWO_MINIMA_ITERS),
        "gradient_descent",
    )
    differ = need(S.minima_differ(left[-1], right[-1], D.TWO_MINIMA_MARGIN), "minima_differ")
    assert differ, f"left ({left[-1]}) and right ({right[-1]}) should differ by more than {D.TWO_MINIMA_MARGIN}"
    close(left[-1], -1.0, 1e-3, "left minimum")
    close(right[-1], 1.0, 1e-3, "right minimum")


# ---------------------------------------------------------------------------
# Exercise 9 -- the stopping-criterion trap
# ---------------------------------------------------------------------------


def test_9_naive_delta_f_criterion_stops_early_on_the_plateau():
    result = need(
        S.stopping_criteria_disagree(
            D.PLATEAU_X0, D.plateau_grad, D.plateau_value, D.PLATEAU_LR, D.PLATEAU_GRAD_TOL, D.PLATEAU_DELTA_F_TOL
        ),
        "stopping_criteria_disagree",
    )
    assert result["grad_norm"] >= D.PLATEAU_GRAD_TOL, result
    assert result["delta_f"] < D.PLATEAU_DELTA_F_TOL, result
    assert result["naive_stops_early"] is True, result
