"""The reference suite: every claim this lab makes, checked against a value.

Run from the lab directory:

    .venv/bin/pytest examples -q -p no:cacheprovider

Nothing here asserts that a function exists or that a file is present. Every
test runs code and compares a number, and every float comparison names the
tolerance it uses and why that tolerance rather than another.
"""

import math

import numpy as np
import pytest

import dataset as D
import network as N
from autodiff import (
    Dual,
    Value,
    forward_mode_gradient,
    graph_size,
    numeric_gradient,
    parameters_of,
    reverse_mode_gradient,
    sum_values,
    topological_order,
)
from chainrule import (
    central_difference,
    chain_derivative,
    chain_function,
    chain_local_rates,
    chain_rule,
    chain_values,
    compose,
    gear_ratio,
    order_of_magnitude,
    partial_difference,
    path_contributions,
    product,
    product_trace,
    repeated_product,
    running_products,
    total_derivative,
    wrong_single_path_derivative,
)

# --------------------------------------------------------------------------
# The tolerances themselves
# --------------------------------------------------------------------------


def test_epsilon_is_numpy_float64_epsilon():
    assert D.EPSILON == float(np.finfo(np.float64).eps)


def test_this_interpreter_uses_ieee754_doubles():
    import sys

    assert sys.float_info.mant_dig == 53


def test_step_size_sits_inside_day_108s_measured_band():
    # Day 108 found the central rule's best step for e**x in 1e-7 to 1e-4.
    assert 1e-7 <= D.H <= 1e-4


@pytest.mark.parametrize(
    "name,value,ceiling",
    [
        ("NUMERIC_TOL", D.NUMERIC_TOL, 1e-5),
        ("NUMERIC_REL_TOL", D.NUMERIC_REL_TOL, 1e-5),
        ("ANALYTIC_TOL", D.ANALYTIC_TOL, 1e-10),
    ],
)
def test_no_tolerance_is_loose_enough_to_be_meaningless(name, value, ceiling):
    # A tolerance large enough to pass anything is not a test.
    assert 0.0 < value < ceiling, name


def test_the_analytic_tolerance_is_far_tighter_than_the_numeric_one():
    # Comparing two analytic routes must be much stricter than comparing an
    # analytic route against a measurement. A thousandfold, here.
    assert D.ANALYTIC_TOL * 1000.0 < D.NUMERIC_TOL


def test_the_numeric_tolerance_has_headroom_over_the_error_bound():
    # truncation ~ (h^2/6)|f'''| and rounding ~ EPSILON|f|/h, at |f|,|f'''| <= 250
    bound = 250.0 * (D.H * D.H / 6.0 + D.EPSILON / D.H)
    assert bound < D.NUMERIC_TOL / 50.0


# --------------------------------------------------------------------------
# Rates multiply, with no calculus in sight
# --------------------------------------------------------------------------


def test_two_gears_multiply_to_six():
    assert gear_ratio(D.GEAR_RATIOS) == D.GEAR_RATIO_PRODUCT


def test_a_four_stage_gear_train_multiplies_to_thirty_six():
    assert gear_ratio(D.GEAR_TRAIN) == D.GEAR_TRAIN_PRODUCT


def test_three_currency_rates_multiply_to_one_hundred_and_fifty():
    assert product(D.CURRENCY_RATES) == D.CURRENCY_PRODUCT


def test_an_empty_product_is_one():
    # The identity for multiplication, and the right answer to "how much does
    # x change per unit of x".
    assert product([]) == 1.0


def test_the_order_of_the_gear_stages_does_not_change_the_ratio():
    assert gear_ratio(D.GEAR_TRAIN) == gear_ratio(tuple(reversed(D.GEAR_TRAIN)))


# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------


def test_composition_runs_the_inner_function_first():
    assert compose(D.square, D.line)(2.0) == 49.0
    # The other order gives a different answer, which is why order matters.
    assert compose(D.line, D.square)(2.0) == 13.0


def test_composition_is_not_commutative():
    assert compose(D.square, D.line)(2.0) != compose(D.line, D.square)(2.0)


@pytest.mark.parametrize("case", D.COMPOSITIONS, ids=lambda c: c.name)
def test_chain_rule_matches_the_closed_form(case):
    got = chain_rule(case.d_outer, case.inner, case.d_inner, case.x)
    assert abs(got - case.exact) < D.ANALYTIC_TOL


@pytest.mark.parametrize("case", D.COMPOSITIONS, ids=lambda c: c.name)
def test_chain_rule_matches_a_central_difference(case):
    got = chain_rule(case.d_outer, case.inner, case.d_inner, case.x)
    measured = central_difference(compose(case.outer, case.inner), case.x, D.H)
    assert abs(got - measured) < D.NUMERIC_TOL


@pytest.mark.parametrize("case", D.COMPOSITIONS, ids=lambda c: c.name)
def test_the_composed_function_is_finite_at_the_test_point(case):
    assert math.isfinite(compose(case.outer, case.inner)(case.x))


def test_evaluating_the_outer_derivative_at_x_gives_the_wrong_answer():
    # The single most common chain-rule mistake, asserted as a mistake so a
    # future edit cannot make it accidentally right.
    correct = D.d_square(D.line(2.0)) * D.d_line(2.0)
    mistake = D.d_square(2.0) * D.d_line(2.0)
    assert correct == 42.0
    assert mistake == 12.0
    assert abs(correct - mistake) > 1.0


def test_the_sigmoid_slope_at_zero_is_exactly_a_quarter():
    case = D.COMPOSITIONS[4]
    assert chain_rule(case.d_outer, case.inner, case.d_inner, 0.0) == 0.25


def test_a_quarter_is_the_sigmoids_largest_slope_anywhere():
    case = D.COMPOSITIONS[4]
    for x in (-4.0, -2.0, -0.5, 0.5, 2.0, 4.0):
        assert chain_rule(case.d_outer, case.inner, case.d_inner, x) < 0.25


def test_tanh_of_a_line_at_minus_a_half_is_exactly_two():
    case = D.COMPOSITIONS[5]
    assert chain_rule(case.d_outer, case.inner, case.d_inner, -0.5) == 2.0


# --------------------------------------------------------------------------
# Chains of any depth
# --------------------------------------------------------------------------


def test_the_forward_pass_returns_one_more_value_than_there_are_stages():
    values = chain_values(D.FIVE_STAGES, D.FIVE_START)
    assert len(values) == len(D.FIVE_STAGES) + 1
    assert values[0] == D.FIVE_START


def test_the_five_stage_forward_values_are_the_documented_ones():
    assert chain_values(D.FIVE_STAGES, D.FIVE_START) == list(D.FIVE_VALUES)


def test_the_five_local_rates_are_the_documented_ones():
    got = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    assert got == list(D.FIVE_LOCAL_RATES)


def test_the_five_rates_multiply_to_the_derivative():
    assert chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START) == 0.4


def test_the_collapsed_formula_agrees_with_the_product_of_local_rates():
    closed = D.d_five_chain_closed_form(D.FIVE_START)
    chained = chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    assert abs(closed - chained) < D.ANALYTIC_TOL


def test_the_five_stage_chain_collapses_to_the_logarithm_of_two_x_plus_three():
    composed = chain_function(D.FIVE_STAGES)
    for x in (0.5, 1.0, 2.0, 7.5):
        assert abs(composed(x) - D.five_chain_closed_form(x)) < D.ANALYTIC_TOL


@pytest.mark.parametrize("x", [0.5, 1.0, 2.0, 7.5])
def test_the_chain_derivative_matches_a_measurement_at_several_points(x):
    analytic = chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, x)
    measured = central_difference(chain_function(D.FIVE_STAGES), x, D.H)
    assert abs(analytic - measured) < D.NUMERIC_TOL


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_every_prefix_of_the_chain_agrees_with_a_measurement(depth):
    stages = D.FIVE_STAGES[:depth]
    rates = D.FIVE_RATES[:depth]
    analytic = chain_derivative(stages, rates, D.FIVE_START)
    measured = central_difference(chain_function(stages), D.FIVE_START, D.H)
    assert abs(analytic - measured) < D.NUMERIC_TOL


def test_a_chain_of_zero_stages_has_derivative_one():
    assert chain_derivative((), (), 3.0) == 1.0


def test_mismatched_stages_and_rates_are_refused_rather_than_guessed():
    with pytest.raises(ValueError):
        chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES[:2], 1.0)


def test_the_running_products_end_at_the_last_local_rate():
    rates = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    assert running_products(rates)[-1] == rates[-1]


def test_the_running_products_start_at_the_whole_derivative():
    rates = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    assert abs(running_products(rates)[0] - 0.4) < D.ANALYTIC_TOL


def test_the_two_multiplication_orders_differ_only_by_rounding():
    rates = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    forwards = product(rates)
    backwards = running_products(rates)[0]
    # They are NOT equal -- float64 multiplication is not associative -- and
    # this test asserts both halves of that: close, but not identical.
    assert abs(forwards - backwards) < D.ANALYTIC_TOL
    assert abs(forwards - backwards) < 4.0 * D.EPSILON


@pytest.mark.parametrize("i", range(5))
def test_each_running_product_is_the_derivative_of_the_rest_of_the_chain(i):
    rates = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
    carried = running_products(rates)
    assert abs(carried[i] - product(rates[i:])) < D.ANALYTIC_TOL


def test_central_difference_refuses_a_non_positive_step():
    with pytest.raises(ValueError):
        central_difference(D.square, 1.0, 0.0)
    with pytest.raises(ValueError):
        central_difference(D.square, 1.0, -1e-5)


def test_partial_difference_refuses_a_non_positive_step():
    with pytest.raises(ValueError):
        partial_difference(D.surface, (1.0, 1.0), 0, 0.0)


# --------------------------------------------------------------------------
# Two paths, and the sum
# --------------------------------------------------------------------------

TWO_PATHS = [[D.TWO_PATH_V, 2.0 * D.TWO_PATH_X], [D.TWO_PATH_U, 3.0]]


def test_the_two_path_contributions_are_twenty_four_and_twelve():
    assert path_contributions(TWO_PATHS) == list(D.TWO_PATH_CONTRIBUTIONS)


def test_the_contributions_are_added_not_multiplied():
    assert total_derivative(TWO_PATHS) == 36.0
    assert total_derivative(TWO_PATHS) != 24.0 * 12.0


def test_the_sum_of_the_paths_matches_a_central_difference():
    measured = central_difference(D.two_path_direct, D.TWO_PATH_X, D.H)
    assert abs(total_derivative(TWO_PATHS) - measured) < D.NUMERIC_TOL


def test_the_sum_of_the_paths_matches_the_closed_form():
    closed = D.d_two_path_direct(D.TWO_PATH_X)
    assert abs(total_derivative(TWO_PATHS) - closed) < D.ANALYTIC_TOL


@pytest.mark.parametrize("path_index", [0, 1])
def test_neither_single_path_is_the_answer(path_index):
    # The instructive failure, asserted AS a failure. If a future edit made
    # one path accidentally correct, this test would notice.
    measured = central_difference(D.two_path_direct, D.TWO_PATH_X, D.H)
    wrong = wrong_single_path_derivative(TWO_PATHS, path_index)
    assert abs(wrong - measured) > 1.0


@pytest.mark.parametrize("x", [0.5, 1.0, 2.0, 3.5])
def test_the_two_path_rule_holds_away_from_the_documented_point(x):
    paths = [[3.0 * x, 2.0 * x], [x * x, 3.0]]
    measured = central_difference(D.two_path_direct, x, D.H)
    assert abs(total_derivative(paths) - measured) < D.NUMERIC_TOL
    assert abs(9.0 * x * x - measured) < D.NUMERIC_TOL


def test_the_surface_value_at_the_documented_point():
    assert D.surface(*D.SURFACE_POINT) == D.SURFACE_Z


def test_the_surface_intermediates_are_the_documented_ones():
    s, t = D.SURFACE_POINT
    assert s * t == D.SURFACE_U
    assert s - t == D.SURFACE_V


@pytest.mark.parametrize("index,expected", [(0, 34.0), (1, 26.0)])
def test_the_multivariable_chain_rule_matches_a_partial_difference(index, expected):
    measured = partial_difference(D.surface, D.SURFACE_POINT, index, D.H)
    assert abs(expected - measured) < D.NUMERIC_TOL


def test_the_multivariable_gradient_is_built_from_two_products_each():
    s, t = D.SURFACE_POINT
    dz_ds = D.SURFACE_DZ_DU * t + D.SURFACE_DZ_DV * 1.0
    dz_dt = D.SURFACE_DZ_DU * s + D.SURFACE_DZ_DV * -1.0
    assert (dz_ds, dz_dt) == D.SURFACE_GRADIENT


def test_dropping_the_second_path_of_the_surface_gets_it_wrong():
    s, t = D.SURFACE_POINT
    only_u = D.SURFACE_DZ_DU * t
    assert only_u != D.SURFACE_GRADIENT[0]
    assert abs(only_u - D.SURFACE_GRADIENT[0]) == 2.0


# --------------------------------------------------------------------------
# The Value engine
# --------------------------------------------------------------------------


def test_a_leaf_starts_with_a_zero_gradient():
    assert Value(3.0).grad == 0.0


def test_addition_computes_the_right_value_and_gradients():
    a, b = Value(3.0), Value(4.0)
    c = a + b
    c.backward()
    assert c.data == 7.0
    assert a.grad == 1.0
    assert b.grad == 1.0


def test_multiplication_computes_the_right_value_and_gradients():
    a, b = Value(3.0), Value(4.0)
    c = a * b
    c.backward()
    assert c.data == 12.0
    assert a.grad == 4.0
    assert b.grad == 3.0


def test_a_value_added_to_itself_accumulates_both_contributions():
    # If `+=` were `=` this would be 1.0. That one character is the entire
    # multivariable chain rule.
    x = Value(3.0)
    y = x + x
    y.backward()
    assert y.data == 6.0
    assert x.grad == 2.0


def test_a_value_multiplied_by_itself_reproduces_the_power_rule():
    x = Value(3.0)
    y = x * x
    y.backward()
    assert x.grad == 6.0


def test_a_value_cubed_reproduces_the_power_rule_too():
    x = Value(2.0)
    y = x * x * x
    y.backward()
    assert x.grad == 12.0  # 3 x squared


def test_the_output_seeds_its_own_gradient_with_one():
    x = Value(3.0)
    y = x * 2.0
    y.backward()
    assert y.grad == 1.0


def test_backward_resets_gradients_so_it_can_be_run_twice():
    x = Value(3.0)
    y = x * x
    y.backward()
    first = x.grad
    y.backward()
    assert x.grad == first


def test_scalars_can_be_mixed_in_from_either_side():
    x = Value(2.0)
    assert (x + 3.0).data == 5.0
    assert (3.0 + x).data == 5.0
    assert (x * 3.0).data == 6.0
    assert (3.0 * x).data == 6.0
    assert (x - 1.0).data == 1.0
    assert (1.0 - x).data == -1.0
    assert (-x).data == -2.0


def test_subtraction_gradients_have_the_right_signs():
    a, b = Value(5.0), Value(3.0)
    c = a - b
    c.backward()
    assert c.data == 2.0
    assert a.grad == 1.0
    assert b.grad == -1.0


def test_tanh_computes_the_right_value():
    assert abs(Value(0.6).tanh().data - math.tanh(0.6)) < D.ANALYTIC_TOL


def test_tanh_gradient_is_one_minus_tanh_squared():
    z = Value(0.6)
    t = z.tanh()
    t.backward()
    assert abs(z.grad - (1.0 - t.data * t.data)) < D.ANALYTIC_TOL


def test_tanh_gradient_at_zero_is_exactly_one():
    z = Value(0.0)
    z.tanh().backward()
    assert z.grad == 1.0


def test_tanh_at_half_ln_three_is_exactly_a_half():
    # The fact the whole hand-worked network rests on. Asserted, not assumed.
    assert math.tanh(D.HALF_LN3) == 0.5


def test_tanh_slope_at_half_ln_three_is_exactly_three_quarters():
    z = Value(D.HALF_LN3)
    z.tanh().backward()
    assert z.grad == 0.75


def test_tanh_saturates_and_its_slope_goes_to_nearly_nothing():
    z = Value(5.0)
    z.tanh().backward()
    assert z.grad < 1e-3


def test_the_topological_order_puts_children_before_parents():
    p, q = Value(2.0), Value(-3.0)
    r = p * q
    out = r + p
    order = topological_order(out)
    position = {id(node): i for i, node in enumerate(order)}
    for node in order:
        for child in node._children:
            assert position[id(child)] < position[id(node)]


def test_a_node_used_twice_appears_once_in_the_order():
    p = Value(2.0)
    out = p * p + p
    order = topological_order(out)
    assert sum(1 for node in order if node is p) == 1


def test_graph_size_counts_every_node_once():
    p = Value(2.0)
    out = p * p + p
    assert graph_size(out) == len(topological_order(out))


def test_the_engine_handles_a_deep_chain_without_recursion_limits():
    # Ten thousand operations. A recursive topological sort would fail here.
    node = Value(1.0)
    for _ in range(10_000):
        node = node * 1.0
    node.backward()
    assert graph_size(node) > 10_000


def test_parameters_of_finds_exactly_the_leaves():
    a, b = Value(1.0), Value(2.0)
    out = a * b + a
    leaves = parameters_of(out)
    assert a in leaves
    assert b in leaves
    assert out not in leaves


def test_sum_values_adds_a_list_of_values():
    total = sum_values([Value(1.0), Value(2.0), Value(3.5)])
    total.backward()
    assert total.data == 6.5


def test_repr_shows_the_data_and_the_gradient():
    x = Value(2.0, label="x")
    text = repr(x)
    assert "x=" in text
    assert "grad" in text


ENGINE_CASES = [
    ("square_of_line", lambda v: (3.0 * v[0] + 1.0) * (3.0 * v[0] + 1.0), [2.0]),
    ("cubic", lambda v: v[0] * v[0] * v[0] + (-2.0) * v[0], [1.5]),
    ("product_pair", lambda v: (v[0] * v[1] + v[0]) * (v[1] + 3.0), [2.0, -1.0]),
    ("tanh_mix", lambda v: ((v[0] * v[1]).tanh() * v[2] + v[0] * v[2]) * (1.0 + v[1]),
     [0.7, 0.4, -1.3]),
    ("shared_input", lambda v: (v[0] * v[0]) * (3.0 * v[0]), [2.0]),
    ("deep_tanh", lambda v: ((v[0] * 0.5).tanh() * 2.0 + v[0]).tanh(), [1.1]),
]


@pytest.mark.parametrize("name,build,point", ENGINE_CASES, ids=[c[0] for c in ENGINE_CASES])
def test_reverse_mode_matches_a_central_difference(name, build, point):
    def plain(vals):
        return build([Value(v) for v in vals]).data

    grads, _ = reverse_mode_gradient(build, point)
    numeric, _ = numeric_gradient(plain, point, D.H)
    for got, want in zip(grads, numeric):
        assert abs(got - want) < D.NUMERIC_TOL + D.NUMERIC_REL_TOL * abs(want)


@pytest.mark.parametrize("name,build,point", ENGINE_CASES, ids=[c[0] for c in ENGINE_CASES])
def test_reverse_mode_matches_forward_mode_to_the_last_bits(name, build, point):
    reverse, _ = reverse_mode_gradient(build, point)
    forward, _ = forward_mode_gradient(build, point)
    for got, want in zip(reverse, forward):
        assert abs(got - want) < D.ANALYTIC_TOL


@pytest.mark.parametrize("name,build,point", ENGINE_CASES, ids=[c[0] for c in ENGINE_CASES])
def test_reverse_mode_always_uses_exactly_one_pass(name, build, point):
    _, passes = reverse_mode_gradient(build, point)
    assert passes == 1


@pytest.mark.parametrize("name,build,point", ENGINE_CASES, ids=[c[0] for c in ENGINE_CASES])
def test_forward_mode_uses_one_pass_per_input(name, build, point):
    _, passes = forward_mode_gradient(build, point)
    assert passes == len(point)


@pytest.mark.parametrize("name,build,point", ENGINE_CASES, ids=[c[0] for c in ENGINE_CASES])
def test_a_central_difference_uses_two_evaluations_per_input(name, build, point):
    def plain(vals):
        return build([Value(v) for v in vals]).data

    _, passes = numeric_gradient(plain, point, D.H)
    assert passes == 2 * len(point)


def test_the_shared_input_case_is_the_sum_over_paths_again():
    # (x*x)*(3x) is 3 x cubed, and x reaches the output three times.
    grads, _ = reverse_mode_gradient(lambda v: (v[0] * v[0]) * (3.0 * v[0]), [2.0])
    assert abs(grads[0] - 9.0 * 4.0) < D.ANALYTIC_TOL


# --------------------------------------------------------------------------
# Dual numbers (forward mode)
# --------------------------------------------------------------------------


def test_a_dual_carries_a_value_and_a_derivative():
    d = Dual(3.0, 1.0)
    assert d.value == 3.0
    assert d.dot == 1.0


def test_dual_addition_adds_both_parts():
    d = Dual(3.0, 1.0) + Dual(4.0, 0.0)
    assert (d.value, d.dot) == (7.0, 1.0)


def test_dual_multiplication_uses_the_product_rule():
    d = Dual(3.0, 1.0) * Dual(4.0, 0.0)
    assert (d.value, d.dot) == (12.0, 4.0)


def test_dual_tanh_uses_one_minus_tanh_squared():
    d = Dual(0.6, 1.0).tanh()
    assert abs(d.dot - (1.0 - math.tanh(0.6) ** 2)) < D.ANALYTIC_TOL


def test_dual_scalars_work_from_either_side():
    d = Dual(2.0, 1.0)
    assert (3.0 + d).value == 5.0
    assert (3.0 * d).dot == 3.0
    assert (1.0 - d).dot == -1.0
    assert repr(d).startswith("Dual(")


def test_an_unseeded_dual_reports_a_zero_derivative():
    # The reason forward mode needs one pass per input: an input that was not
    # seeded contributes nothing to this pass.
    d = Dual(3.0, 0.0) * Dual(4.0, 0.0)
    assert d.dot == 0.0


# --------------------------------------------------------------------------
# The tiny network
# --------------------------------------------------------------------------

FORWARD = N.forward(D.NET_X1, D.NET_X2, N.default_parameter_values())


@pytest.mark.parametrize(
    "key,expected",
    [
        ("a_pre", D.NET_A_PRE),
        ("a", D.NET_A),
        ("b_pre", D.NET_B_PRE),
        ("b", D.NET_B),
        ("out", D.NET_OUT),
        ("loss", D.NET_LOSS),
    ],
)
def test_the_forward_pass_is_exact(key, expected):
    assert FORWARD[key] == expected


def test_the_bias_of_unit_b_is_half_the_log_of_three():
    assert D.NET_BB == 0.5 * math.log(3.0)


def test_unit_b_lands_on_a_tanh_value_that_is_exactly_a_half():
    assert FORWARD["b"] == 0.5
    assert 1.0 - FORWARD["b"] ** 2 == 0.75


def test_unit_a_lands_on_a_tanh_value_that_is_exactly_zero():
    assert FORWARD["a"] == 0.0
    assert 1.0 - FORWARD["a"] ** 2 == 1.0


HAND = N.hand_gradients()
ENGINE = N.engine_gradients()
NUMERIC = {
    **N.numeric_parameter_gradients(D.H),
    **N.numeric_input_gradients(D.H),
}


@pytest.mark.parametrize("key", sorted(D.NET_GRADIENTS))
def test_the_hand_worked_gradient_matches_the_table(key):
    assert abs(HAND[key] - D.NET_GRADIENTS[key]) < D.ANALYTIC_TOL


@pytest.mark.parametrize("key", sorted(D.NET_GRADIENTS))
def test_the_engine_matches_the_hand_computation_bit_for_bit(key):
    # Same multiplications, same order, same exact values -- so equality is
    # the honest comparison here, not a tolerance.
    assert ENGINE[key] == HAND[key]


@pytest.mark.parametrize("key", sorted(NUMERIC))
def test_the_engine_matches_a_central_difference(key):
    assert abs(ENGINE[key] - NUMERIC[key]) < D.NUMERIC_TOL


def test_the_gradient_of_a_weight_feeding_a_dead_unit_is_exactly_zero():
    # vA multiplies an activation of exactly 0, so nudging it moves nothing.
    assert ENGINE["vA"] == 0.0


def test_the_input_gradients_are_sums_over_two_paths():
    first, second = D.NET_X1_CONTRIBUTIONS
    assert HAND["x1"] == first + second
    assert first != 0.0
    assert second != 0.0


def test_taking_only_one_path_for_x1_is_visibly_wrong():
    first, second = D.NET_X1_CONTRIBUTIONS
    measured = NUMERIC["x1"]
    assert abs(first - measured) > 1.0
    assert abs(second - measured) > 1.0
    assert abs((first + second) - measured) < D.NUMERIC_TOL


def test_the_loss_gradient_chain_starts_at_two_times_the_residual():
    assert HAND["out"] == 2.0 * (D.NET_OUT - D.NET_TARGET)


def test_the_gradient_through_unit_b_is_scaled_by_three_quarters():
    assert HAND["b_pre"] == HAND["b"] * 0.75


def test_forward_mode_reproduces_every_parameter_gradient():
    grads, _ = N.forward_mode_parameter_gradients()
    for key, value in grads.items():
        assert abs(value - HAND[key]) < D.ANALYTIC_TOL


def test_forward_mode_needs_one_pass_per_parameter():
    _, passes = N.forward_mode_parameter_gradients()
    assert passes == len(D.NET_PARAMETERS)
    assert passes == 9


def test_reverse_mode_needs_one_pass_for_all_nine():
    # Built directly rather than via the helper, so the claim is about the
    # network and not about a convenience wrapper.
    x1, x2 = Value(D.NET_X1), Value(D.NET_X2)
    params = [Value(v) for v in N.default_parameter_values()]
    nodes = N.build_graph(x1, x2, params)
    nodes["loss"].backward()
    assert all(p.grad != 0.0 or name == "vA"
               for name, p in zip(D.NET_PARAMETERS, params))


def test_a_gradient_step_reduces_the_loss():
    # The point of having gradients at all, and the whole of Day 111.
    base = N.default_parameter_values()
    grads = N.numeric_parameter_gradients(D.H)
    step = 0.01
    moved = [
        v - step * grads[name] for name, v in zip(D.NET_PARAMETERS, base)
    ]
    before = N.loss_only(D.NET_X1, D.NET_X2, base)
    after = N.loss_only(D.NET_X1, D.NET_X2, moved)
    assert after < before


def test_the_network_has_nine_parameters():
    assert len(D.NET_PARAMETERS) == 9
    assert len(N.default_parameter_values()) == 9


# --------------------------------------------------------------------------
# Products that collapse and products that blow up
# --------------------------------------------------------------------------


def test_repeated_product_of_zero_factors_is_one():
    assert repeated_product(0.9, 0) == 1.0


def test_repeated_product_refuses_a_negative_count():
    with pytest.raises(ValueError):
        repeated_product(0.9, -1)


def test_a_product_trace_has_one_entry_per_factor():
    assert len(product_trace(0.9, D.CHAIN_LENGTH)) == D.CHAIN_LENGTH


def test_the_trace_ends_where_the_product_ends():
    trace = product_trace(0.9, D.CHAIN_LENGTH)
    assert trace[-1] == repeated_product(0.9, D.CHAIN_LENGTH)


def test_fifty_factors_of_nine_tenths_collapse_by_two_orders():
    value = repeated_product(D.DECAY_FACTOR, D.CHAIN_LENGTH)
    assert order_of_magnitude(value) == D.DECAY_ORDER
    assert value < 1e-2


def test_fifty_factors_of_eleven_tenths_grow_by_two_orders():
    value = repeated_product(D.GROWTH_FACTOR, D.CHAIN_LENGTH)
    assert order_of_magnitude(value) == D.GROWTH_ORDER
    assert value > 1e2


@pytest.mark.parametrize(
    "factor,count,expected_order",
    [
        (D.DECAY_FACTOR, D.LONG_CHAIN_LENGTH, -10),
        (D.GROWTH_FACTOR, D.LONG_CHAIN_LENGTH, 8),
        (D.MILD_DECAY, D.CHAIN_LENGTH, -16),
        (D.SHARP_DECAY, D.CHAIN_LENGTH, -31),
        (D.SHARP_GROWTH, D.CHAIN_LENGTH, 15),
    ],
)
def test_the_documented_orders_of_magnitude(factor, count, expected_order):
    assert order_of_magnitude(repeated_product(factor, count)) == expected_order


def test_half_to_the_fiftieth_is_four_epsilons_and_still_counts():
    # This contradicts the obvious guess, so it is asserted in both halves.
    value = repeated_product(D.MILD_DECAY, D.CHAIN_LENGTH)
    assert value == 4.0 * D.EPSILON
    assert 1.0 + value != 1.0


def test_three_more_halvings_do_make_it_disappear():
    value = repeated_product(D.MILD_DECAY, 53)
    assert value == 0.5 * D.EPSILON
    assert 1.0 + value == 1.0


def test_the_sigmoids_best_case_vanishes_completely_in_fifty_layers():
    value = repeated_product(D.SHARP_DECAY, D.CHAIN_LENGTH)
    assert value < D.EPSILON
    assert 1.0 + value == 1.0


def test_a_factor_of_exactly_one_neither_vanishes_nor_explodes():
    assert repeated_product(1.0, 10_000) == 1.0


def test_order_of_magnitude_refuses_zero():
    with pytest.raises(ValueError):
        order_of_magnitude(0.0)


@pytest.mark.parametrize(
    "value,expected", [(1.0, 0), (9.99, 0), (10.0, 1), (0.1, -1), (-500.0, 2)]
)
def test_order_of_magnitude_reads_the_exponent(value, expected):
    assert order_of_magnitude(value) == expected


def test_the_engine_reproduces_the_collapse_through_a_real_graph():
    def deep(vals):
        node = vals[0]
        for _ in range(D.CHAIN_LENGTH):
            node = node * D.DECAY_FACTOR
        return node

    grads, passes = reverse_mode_gradient(deep, [1.0])
    assert abs(grads[0] - repeated_product(D.DECAY_FACTOR, D.CHAIN_LENGTH)) < D.ANALYTIC_TOL
    assert passes == 1


def test_the_engine_reproduces_the_explosion_too():
    def deep(vals):
        node = vals[0]
        for _ in range(D.CHAIN_LENGTH):
            node = node * D.GROWTH_FACTOR
        return node

    grads, _ = reverse_mode_gradient(deep, [1.0])
    assert order_of_magnitude(grads[0]) == D.GROWTH_ORDER


def _stacked_tanh(depth):
    def deep(vals):
        node = vals[0]
        for _ in range(depth):
            node = node.tanh()
        return node

    return deep


@pytest.mark.parametrize("depth", [1, 5, 10, 20, 40, 80, 160])
def test_a_stacked_tanh_gradient_stays_positive_and_below_one(depth):
    grads, _ = reverse_mode_gradient(_stacked_tanh(depth), [0.9])
    assert 0.0 < grads[0] < 1.0


def test_a_stacked_tanh_gradient_falls_monotonically_with_depth():
    values = [
        reverse_mode_gradient(_stacked_tanh(d), [0.9])[0][0]
        for d in (1, 5, 10, 20, 40, 80, 160)
    ]
    assert values == sorted(values, reverse=True)


def test_stacked_tanh_decays_far_more_slowly_than_a_constant_factor_predicts():
    """A measured correction to the naive vanishing-gradient story.

    The obvious reasoning says: tanh's slope at the input is about 0.487, so
    forty tanh layers should multiply the gradient by 0.487 forty times and
    land near 1e-13. The measurement says otherwise, and by ten orders of
    magnitude.

    The reason is that the local rates are not constant. Each tanh pulls its
    input closer to 0, and tanh's slope at 0 is 1 -- so the deeper the stack
    goes, the closer each local rate creeps back towards 1. A product of
    constants is the wrong model for a product of rates that depend on where
    they are evaluated, and this test asserts the gap rather than glossing it.
    """
    single = reverse_mode_gradient(_stacked_tanh(1), [0.9])[0][0]
    deep = reverse_mode_gradient(_stacked_tanh(40), [0.9])[0][0]
    naive = single**40
    assert 1e-3 < deep < 1e-1
    assert naive < 1e-12
    assert deep > 1e9 * naive


def test_a_stack_of_constant_factors_does_vanish_geometrically():
    # The contrast: when the local rate really is a constant, the naive
    # reasoning is correct and the collapse is geometric.
    def deep(vals):
        node = vals[0]
        for _ in range(40):
            node = node * 0.487
        return node

    grads, _ = reverse_mode_gradient(deep, [0.9])
    assert grads[0] < 1e-12
