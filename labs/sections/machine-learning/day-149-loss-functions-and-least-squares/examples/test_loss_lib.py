"""Machinery checks: the helpers behave, before any claim is made.

These four tests are solved in both `starter/` and `examples/`. They exist
so that a broken helper reports itself as a broken helper rather than as a
surprising scientific result.
"""

import numpy as np

import loss_lib as L


def test_sse_and_sae_are_zero_at_a_perfect_fit_and_positive_elsewhere():
    values = [1.0, 2.0, 3.0]
    assert L.sse(values, 2.0) == 2.0  # (1-2)^2 + (2-2)^2 + (3-2)^2
    assert L.sae(values, 2.0) == 2.0  # |1-2| + |2-2| + |3-2|
    assert L.sse(values, 100.0) > 0
    assert L.sae(values, 100.0) > 0


def test_make_line_data_is_deterministic_given_a_seed():
    x1, y1 = L.make_line_data(n=20, seed=42)
    x2, y2 = L.make_line_data(n=20, seed=42)
    assert np.array_equal(x1, x2)
    assert np.array_equal(y1, y2)
    x3, _y3 = L.make_line_data(n=20, seed=43)
    assert not np.array_equal(x1, x3)


def test_grid_minimize_finds_the_minimum_of_a_simple_quadratic():
    # sse(values, c) for a single value v is (v - c)^2, minimised at c = v.
    best = L.grid_minimize([7.0], L.sse, 0.0, 14.0, steps=14001)
    assert abs(best - 7.0) < 0.01


def test_normal_equations_recovers_a_known_line_exactly_when_there_is_no_noise():
    x = np.linspace(0.0, 10.0, 30)
    y = 5.0 + 3.0 * x  # no noise at all
    intercept, slope = L.normal_equations(x, y)
    assert abs(intercept - 5.0) < 1e-9
    assert abs(slope - 3.0) < 1e-9
