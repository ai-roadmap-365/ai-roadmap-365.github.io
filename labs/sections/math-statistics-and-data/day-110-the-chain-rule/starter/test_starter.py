"""Your running score. Unattempted work SKIPS; wrong work FAILS with both values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap rather
than guess at it.

Nothing in here checks that a function exists or that a file is present.
Every test runs your code and compares a value.
"""

import math

import pytest

import answers
import autodiff as A
import chainrule as C
import dataset as D
import network as N

# --------------------------------------------------------------------------
# The skip machinery
# --------------------------------------------------------------------------


def need(value, what):
    """Skip if the exercise has not been attempted, otherwise hand it back."""
    if value is None:
        pytest.skip(f"not attempted yet: {what}")
    return value


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not.

    An unwritten `__add__` returns None, so the next operation on it raises a
    TypeError or an AttributeError. That is "not attempted", not "wrong".
    """
    try:
        result = fn()
    except (TypeError, AttributeError, NotImplementedError):
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


def close(got, want, tol, what):
    assert abs(got - want) < tol, (
        f"{what}: your answer {got!r}, expected {want!r} "
        f"(difference {abs(got - want):.3e}, tolerance {tol:g})"
    )


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from
    a collection error that quietly ran nothing at all."""
    assert D.EPSILON > 0.0


# --------------------------------------------------------------------------
# Exercise 1 -- the fourteen functions
# --------------------------------------------------------------------------


def test_1_product_multiplies():
    assert need(C.product([2.0, 3.0, 4.0]), "product") == 24.0


def test_1_product_of_nothing_is_one():
    assert need(C.product([]), "product") == 1.0, "the empty product must be 1.0"


def test_1_gear_ratio_of_two_stages():
    assert need(C.gear_ratio(D.GEAR_RATIOS), "gear_ratio") == 6.0


def test_1_gear_ratio_of_four_stages():
    assert need(C.gear_ratio(D.GEAR_TRAIN), "gear_ratio") == 36.0


def test_1_central_difference_on_a_parabola_is_exact():
    got = need(C.central_difference(D.square, 3.0, 0.1), "central_difference")
    close(got, 6.0, 1e-11, "central difference of x squared at 3")


def test_1_central_difference_divides_by_two_h_not_h():
    # Dividing by h instead of 2h gives exactly double. This is the most
    # common way to get this function half right.
    got = need(C.central_difference(D.square, 3.0, 0.1), "central_difference")
    assert abs(got - 12.0) > 1.0, "you divided by h instead of 2h"


def test_1_central_difference_refuses_a_zero_step():
    try:
        C.central_difference(D.square, 1.0, 0.0)
    except ValueError:
        return
    except ZeroDivisionError:
        pytest.fail("raise ValueError for a non-positive h, not ZeroDivisionError")
    pytest.skip("not attempted yet: central_difference guard")


def test_1_central_difference_refuses_a_negative_step():
    try:
        C.central_difference(D.square, 1.0, -1e-5)
    except ValueError:
        return
    pytest.skip("not attempted yet: central_difference guard")


def test_1_partial_difference_on_the_surface():
    got = need(
        C.partial_difference(D.surface, D.SURFACE_POINT, 0, D.H),
        "partial_difference",
    )
    close(got, 34.0, D.NUMERIC_TOL, "dz/ds at (2, 3)")


def test_1_partial_difference_holds_the_other_coordinate_still():
    got = need(
        C.partial_difference(D.surface, D.SURFACE_POINT, 1, D.H),
        "partial_difference",
    )
    close(got, 26.0, D.NUMERIC_TOL, "dz/dt at (2, 3)")


def test_1_compose_returns_a_function_that_runs_the_inner_one_first():
    composed = need(C.compose(D.square, D.line), "compose")
    assert composed(2.0) == 49.0, "inner runs first: (3*2 + 1) squared"


def test_1_compose_is_not_commutative():
    other = need(C.compose(D.line, D.square), "compose")
    assert other(2.0) == 13.0, "3*(2 squared) + 1"


@pytest.mark.parametrize("case", D.COMPOSITIONS, ids=lambda c: c.name)
def test_1_chain_rule_matches_the_closed_form(case):
    got = need(
        C.chain_rule(case.d_outer, case.inner, case.d_inner, case.x),
        "chain_rule",
    )
    close(got, case.exact, D.ANALYTIC_TOL, f"chain rule on {case.name}")


@pytest.mark.parametrize("case", D.COMPOSITIONS, ids=lambda c: c.name)
def test_1_chain_rule_matches_a_measurement(case):
    got = need(
        C.chain_rule(case.d_outer, case.inner, case.d_inner, case.x),
        "chain_rule",
    )
    measured = (
        case.outer(case.inner(case.x + D.H)) - case.outer(case.inner(case.x - D.H))
    ) / (2.0 * D.H)
    close(got, measured, D.NUMERIC_TOL, f"chain rule vs measurement, {case.name}")


def test_1_chain_rule_evaluates_the_outer_derivative_at_the_inner_value():
    got = need(C.chain_rule(D.d_square, D.line, D.d_line, 2.0), "chain_rule")
    assert got != 12.0, (
        "12.0 means the outer derivative was evaluated at x rather than at "
        "u = inner(x). The answer is 42.0."
    )


def test_1_chain_values_returns_one_more_than_the_stage_count():
    got = need(C.chain_values(D.FIVE_STAGES, D.FIVE_START), "chain_values")
    assert len(got) == 6, "n stages give n + 1 values, starting with x itself"


def test_1_chain_values_are_the_documented_ones():
    got = need(C.chain_values(D.FIVE_STAGES, D.FIVE_START), "chain_values")
    assert got == list(D.FIVE_VALUES)


def test_1_chain_local_rates_are_the_documented_ones():
    got = need(
        C.chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START),
        "chain_local_rates",
    )
    assert got == list(D.FIVE_LOCAL_RATES), (
        "each rate is evaluated at the value ARRIVING at its stage"
    )


def test_1_chain_local_rates_refuses_a_mismatched_length():
    try:
        C.chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES[:2], 1.0)
    except ValueError:
        return
    except (TypeError, IndexError):
        pytest.fail("raise ValueError when stages and rates disagree in length")
    pytest.skip("not attempted yet: chain_local_rates guard")


def test_1_chain_derivative_is_the_product_of_the_local_rates():
    got = need(
        C.chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START),
        "chain_derivative",
    )
    close(got, 0.4, D.ANALYTIC_TOL, "the five-stage derivative")


def test_1_chain_function_collapses_the_stages():
    composed = need(C.chain_function(D.FIVE_STAGES), "chain_function")
    close(composed(1.0), math.log(5.0), D.ANALYTIC_TOL, "the five-stage value")


def test_1_chain_derivative_matches_a_measurement():
    composed = need(C.chain_function(D.FIVE_STAGES), "chain_function")
    analytic = need(
        C.chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, 2.0), "chain_derivative"
    )
    measured = (composed(2.0 + D.H) - composed(2.0 - D.H)) / (2.0 * D.H)
    close(analytic, measured, D.NUMERIC_TOL, "chain derivative at x = 2")


def test_1_running_products_starts_at_the_whole_derivative():
    got = need(C.running_products(list(D.FIVE_LOCAL_RATES)), "running_products")
    close(got[0], 0.4, D.ANALYTIC_TOL, "the first running product")


def test_1_running_products_ends_at_the_last_local_rate():
    got = need(C.running_products(list(D.FIVE_LOCAL_RATES)), "running_products")
    assert got[-1] == 0.2, "the last entry is the final local rate alone"


def test_1_running_products_has_one_entry_per_rate():
    got = need(C.running_products(list(D.FIVE_LOCAL_RATES)), "running_products")
    assert len(got) == 5


def test_1_path_contributions_multiplies_along_each_path():
    paths = [[6.0, 4.0], [4.0, 3.0]]
    got = need(C.path_contributions(paths), "path_contributions")
    assert got == [24.0, 12.0]


def test_1_total_derivative_adds_across_paths():
    paths = [[6.0, 4.0], [4.0, 3.0]]
    got = need(C.total_derivative(paths), "total_derivative")
    assert got == 36.0, (
        "24 and 12 are added, not multiplied and not chosen between"
    )


def test_1_total_derivative_matches_a_measurement():
    paths = [[6.0, 4.0], [4.0, 3.0]]
    got = need(C.total_derivative(paths), "total_derivative")
    measured = (D.two_path_direct(2.0 + D.H) - D.two_path_direct(2.0 - D.H)) / (
        2.0 * D.H
    )
    close(got, measured, D.NUMERIC_TOL, "the two-path derivative")


def test_1_repeated_product_of_fifty_nine_tenths():
    got = need(C.repeated_product(0.9, 50), "repeated_product")
    close(got, 0.9**50, 1e-18, "0.9 to the fiftieth")


def test_1_repeated_product_of_zero_factors_is_one():
    assert need(C.repeated_product(0.9, 0), "repeated_product") == 1.0


def test_1_repeated_product_refuses_a_negative_count():
    try:
        C.repeated_product(0.9, -1)
    except ValueError:
        return
    pytest.skip("not attempted yet: repeated_product guard")


@pytest.mark.parametrize(
    "value,expected", [(1.0, 0), (9.99, 0), (10.0, 1), (0.1, -1), (-500.0, 2)]
)
def test_1_order_of_magnitude_reads_the_exponent(value, expected):
    assert need(C.order_of_magnitude(value), "order_of_magnitude") == expected


def test_1_order_of_magnitude_refuses_zero():
    try:
        C.order_of_magnitude(0.0)
    except ValueError:
        return
    except ValueError:
        return
    pytest.skip("not attempted yet: order_of_magnitude guard")


# --------------------------------------------------------------------------
# Exercise 2 -- the engine
# --------------------------------------------------------------------------


def test_2a_addition_computes_the_value():
    out = attempt(lambda: A.Value(3.0) + A.Value(4.0), "Value.__add__")
    assert out.data == 7.0


def test_2a_addition_passes_the_gradient_through():
    def build():
        a, b = A.Value(3.0), A.Value(4.0)
        c = a + b
        c.backward()
        return (a.grad, b.grad) if a.grad or b.grad else None

    grads = attempt(build, "Value.__add__ and backward")
    assert grads == (1.0, 1.0)


def test_2a_a_plain_float_can_be_added():
    out = attempt(lambda: A.Value(3.0) + 4.0, "Value.__add__ with a float")
    assert out.data == 7.0


def test_2b_multiplication_computes_the_value():
    out = attempt(lambda: A.Value(3.0) * A.Value(4.0), "Value.__mul__")
    assert out.data == 12.0


def test_2b_each_factors_local_rate_is_the_other_factor():
    def build():
        a, b = A.Value(3.0), A.Value(4.0)
        c = a * b
        c.backward()
        return (a.grad, b.grad) if a.grad or b.grad else None

    grads = attempt(build, "Value.__mul__ and backward")
    assert grads == (4.0, 3.0)


def test_2b_a_value_used_twice_accumulates_both_contributions():
    def build():
        x = A.Value(3.0)
        y = x + x
        y.backward()
        return x.grad or None

    grad = attempt(build, "Value.__add__ and backward")
    assert grad == 2.0, (
        "1.0 means the gradient was assigned instead of accumulated. "
        "Use += in every backward step."
    )


def test_2b_multiplying_a_value_by_itself_gives_the_power_rule():
    def build():
        x = A.Value(3.0)
        y = x * x
        y.backward()
        return x.grad or None

    grad = attempt(build, "Value.__mul__ and backward")
    assert grad == 6.0, "d/dx of x squared at 3 is 6, not 3"


def test_2b_a_value_cubed_gives_the_power_rule_too():
    def build():
        x = A.Value(2.0)
        y = x * x * x
        y.backward()
        return x.grad or None

    grad = attempt(build, "Value.__mul__ and backward")
    assert grad == 12.0


def test_2c_tanh_computes_the_value():
    out = attempt(lambda: A.Value(0.6).tanh(), "Value.tanh")
    close(out.data, math.tanh(0.6), D.ANALYTIC_TOL, "tanh(0.6)")


def test_2c_tanh_gradient_is_one_minus_tanh_squared():
    def build():
        z = A.Value(0.6)
        t = z.tanh()
        t.backward()
        return z.grad or None

    grad = attempt(build, "Value.tanh and backward")
    close(grad, 1.0 - math.tanh(0.6) ** 2, D.ANALYTIC_TOL, "tanh's slope at 0.6")


def test_2c_tanh_slope_at_zero_is_exactly_one():
    def build():
        z = A.Value(0.0)
        z.tanh().backward()
        return z.grad or None

    assert attempt(build, "Value.tanh and backward") == 1.0


def test_2c_tanh_at_half_ln_three_is_exactly_a_half():
    out = attempt(lambda: A.Value(D.HALF_LN3).tanh(), "Value.tanh")
    assert out.data == 0.5


def test_2d_topological_order_puts_children_before_parents():
    def build():
        p, q = A.Value(2.0), A.Value(-3.0)
        r = p * q
        out = r + p
        return A.topological_order(out)

    order = attempt(build, "topological_order")
    position = {id(node): i for i, node in enumerate(order)}
    for node in order:
        for child in node._children:
            assert position[id(child)] < position[id(node)], (
                "every node must come after everything it was computed from"
            )


def test_2d_a_node_used_twice_appears_once():
    def build():
        p = A.Value(2.0)
        out = p * p + p
        order = A.topological_order(out)
        return (order, p) if order is not None else None

    order, p = attempt(build, "topological_order")
    assert sum(1 for node in order if node is p) == 1


def test_2d_graph_size_counts_the_nodes():
    def build():
        p = A.Value(2.0)
        out = p * p + p
        return A.graph_size(out)

    # p, (p*p) and (p*p + p). The reused p is counted once, not twice.
    assert attempt(build, "graph_size") == 3


def test_2d_the_order_is_iterative_and_survives_ten_thousand_nodes():
    def build():
        node = A.Value(1.0)
        for _ in range(10_000):
            node = node * 1.0
        return A.graph_size(node)

    try:
        size = attempt(build, "topological_order on a deep graph")
    except RecursionError:
        pytest.fail(
            "a recursive topological sort overflows here; write it iteratively"
        )
    assert size > 10_000


def test_2e_backward_can_be_run_twice_with_the_same_answer():
    def build():
        x = A.Value(3.0)
        y = x * x
        y.backward()
        first = x.grad
        y.backward()
        return (first, x.grad) if first else None

    first, second = attempt(build, "Value.backward")
    assert first == second, "backward must zero the gradients before it runs"


def test_2e_the_output_seeds_its_own_gradient_with_one():
    def build():
        x = A.Value(3.0)
        y = x * 2.0
        y.backward()
        return y.grad or None

    assert attempt(build, "Value.backward") == 1.0


def test_2f_dual_addition_adds_both_parts():
    d = attempt(lambda: A.Dual(3.0, 1.0) + A.Dual(4.0, 0.0), "Dual.__add__")
    assert (d.value, d.dot) == (7.0, 1.0)


def test_2f_dual_multiplication_uses_the_product_rule():
    d = attempt(lambda: A.Dual(3.0, 1.0) * A.Dual(4.0, 0.0), "Dual.__mul__")
    assert (d.value, d.dot) == (12.0, 4.0)


def test_2f_dual_tanh_scales_the_derivative():
    d = attempt(lambda: A.Dual(0.6, 1.0).tanh(), "Dual.tanh")
    close(d.dot, 1.0 - math.tanh(0.6) ** 2, D.ANALYTIC_TOL, "Dual tanh slope")


def test_2f_an_unseeded_dual_reports_nothing():
    d = attempt(lambda: A.Dual(3.0, 0.0) * A.Dual(4.0, 0.0), "Dual.__mul__")
    assert d.dot == 0.0


# --------------------------------------------------------------------------
# Exercise 3 -- the two modes and their cost
# --------------------------------------------------------------------------

CUBIC = ("x cubed - 2x", lambda v: v[0] * v[0] * v[0] + (-2.0) * v[0], [1.5])
PAIR = ("(xy + x)(y + 3)", lambda v: (v[0] * v[1] + v[0]) * (v[1] + 3.0), [2.0, -1.0])


@pytest.mark.parametrize("name,build,point", [CUBIC, PAIR], ids=["cubic", "pair"])
def test_3_reverse_mode_matches_a_measurement(name, build, point):
    result = attempt(
        lambda: A.reverse_mode_gradient(build, point), "reverse_mode_gradient"
    )
    grads, _ = result

    def plain(vals):
        return build([A.Value(v) for v in vals]).data

    for i, got in enumerate(grads):
        ahead, behind = list(point), list(point)
        ahead[i] += D.H
        behind[i] -= D.H
        measured = (plain(ahead) - plain(behind)) / (2.0 * D.H)
        close(got, measured, D.NUMERIC_TOL, f"{name}, input {i}")


@pytest.mark.parametrize("name,build,point", [CUBIC, PAIR], ids=["cubic", "pair"])
def test_3_reverse_mode_always_uses_one_pass(name, build, point):
    _, passes = attempt(
        lambda: A.reverse_mode_gradient(build, point), "reverse_mode_gradient"
    )
    assert passes == 1


@pytest.mark.parametrize("name,build,point", [CUBIC, PAIR], ids=["cubic", "pair"])
def test_3_forward_mode_agrees_with_reverse_mode(name, build, point):
    forward, _ = attempt(
        lambda: A.forward_mode_gradient(build, point), "forward_mode_gradient"
    )
    reverse, _ = attempt(
        lambda: A.reverse_mode_gradient(build, point), "reverse_mode_gradient"
    )
    for got, want in zip(forward, reverse):
        close(got, want, D.ANALYTIC_TOL, f"{name}, forward vs reverse")


@pytest.mark.parametrize("name,build,point", [CUBIC, PAIR], ids=["cubic", "pair"])
def test_3_forward_mode_uses_one_pass_per_input(name, build, point):
    _, passes = attempt(
        lambda: A.forward_mode_gradient(build, point), "forward_mode_gradient"
    )
    assert passes == len(point)


def test_3_numeric_gradient_uses_two_evaluations_per_input():
    def plain(vals):
        return vals[0] * vals[0] + vals[1]

    _, passes = attempt(
        lambda: A.numeric_gradient(plain, [1.0, 2.0], D.H), "numeric_gradient"
    )
    assert passes == 4


# --------------------------------------------------------------------------
# Exercise 4 -- the network
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", sorted(D.NET_GRADIENTS))
def test_4a_the_hand_worked_gradients(key):
    grads = need(N.hand_gradients(), "network.hand_gradients")
    assert key in grads, f"hand_gradients is missing the key {key!r}"
    close(grads[key], D.NET_GRADIENTS[key], D.ANALYTIC_TOL, f"d loss / d {key}")


@pytest.mark.parametrize("key", sorted(D.NET_GRADIENTS))
def test_4b_the_engine_matches_the_hand_computation_exactly(key):
    hand = need(N.hand_gradients(), "network.hand_gradients")
    engine = attempt(N.engine_gradients, "network.engine_gradients")
    assert engine[key] == hand[key], (
        f"d loss/d {key}: engine {engine[key]!r} vs hand {hand[key]!r}. "
        "These perform the same multiplications on the same exact values, "
        "so they should agree bit for bit."
    )


def test_4b_the_engine_gets_the_loss_right():
    engine = attempt(N.engine_gradients, "network.engine_gradients")
    assert "out" in engine


@pytest.mark.parametrize("key", D.NET_PARAMETERS)
def test_4c_the_numerical_gradients_agree_within_tolerance(key):
    numeric = need(
        N.numeric_parameter_gradients(D.H), "network.numeric_parameter_gradients"
    )
    close(numeric[key], D.NET_GRADIENTS[key], D.NUMERIC_TOL, f"numeric d/d {key}")


def test_4_the_input_gradient_is_a_sum_over_two_paths():
    grads = need(N.hand_gradients(), "network.hand_gradients")
    first, second = D.NET_X1_CONTRIBUTIONS
    assert grads["x1"] != first, (
        "-6.0 is the contribution through hidden unit A alone. x1 also "
        "reaches the loss through unit B, and the two are added."
    )
    assert grads["x1"] != second
    close(grads["x1"], first + second, D.ANALYTIC_TOL, "d loss / d x1")


# --------------------------------------------------------------------------
# Exercises 5 to 9 -- the forty predictions
# --------------------------------------------------------------------------

EXPECTED: dict[str, object] = {
    "gears_two_stage": 6.0,
    "gears_four_stage": 36.0,
    "empty_product": 1.0,
    "gear_order_matters": False,
    "composed_value_at_two": 49.0,
    "composed_other_order_at_two": 13.0,
    "chain_rule_at_two": 42.0,
    "chain_rule_mistake_at_two": 12.0,
    "sigmoid_slope_at_zero": 0.25,
    "sigmoid_slope_is_maximum": True,
    "tanh_of_line_slope": 2.0,
    "five_chain_value_count": 6,
    "five_chain_third_rate": 10.0,
    "five_chain_derivative": 0.4,
    "five_chain_closed_form_derivative": 0.4,
    "running_products_last": 0.2,
    "two_path_u_contribution": 24.0,
    "two_path_v_contribution": 12.0,
    "two_path_total": 36.0,
    "two_path_closed_form": 36.0,
    "surface_value": 37.0,
    "surface_dz_ds": 34.0,
    "surface_dz_dt": 26.0,
    "engine_x_plus_x_grad": 2.0,
    "engine_x_times_x_grad": 6.0,
    "engine_x_cubed_grad": 12.0,
    "tanh_slope_at_zero": 1.0,
    "tanh_at_half_ln_three": 0.5,
    "tanh_slope_at_half_ln_three": 0.75,
    "network_loss": 2.25,
    "network_d_out": -3.0,
    "network_d_vA": 0.0,
    "network_d_b_pre": 6.75,
    "network_d_wB2": 13.5,
    "network_d_x1": -9.375,
    "reverse_passes_for_25_inputs": 1,
    "forward_passes_for_25_inputs": 25,
    "numeric_passes_for_25_inputs": 50,
    "decay_order": -3,
    "growth_order": 2,
    "half_to_the_fiftieth_vanishes": False,
    "quarter_to_the_fiftieth_vanishes": True,
}

HINTS: dict[str, str] = {
    "chain_rule_mistake_at_two": (
        "This one asks for the WRONG answer on purpose: the value you get by "
        "evaluating the outer derivative at x rather than at u."
    ),
    "network_d_vA": (
        "vA multiplies hidden unit A's activation, which is exactly 0. Nudging "
        "vA therefore moves the output by exactly nothing."
    ),
    "network_d_x1": (
        "x1 reaches the loss through BOTH hidden units. Add the two path "
        "contributions rather than picking one."
    ),
    "half_to_the_fiftieth_vanishes": (
        "0.5 to the fiftieth is four times float64's epsilon, so it is four "
        "representable gaps wide and still shifts a weight of 1. It takes "
        "three more halvings to disappear."
    ),
    "two_path_total": (
        "The two contributions are added. Not multiplied, and not chosen "
        "between."
    ),
}


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_5_to_9_predictions(key):
    got = need(answers.ANSWERS.get(key), f"answers.ANSWERS[{key!r}]")
    want = EXPECTED[key]
    hint = HINTS.get(key, "")
    if isinstance(want, bool) or isinstance(want, int):
        assert got == want, f"{key}: your answer {got!r}, expected {want!r}. {hint}"
    else:
        assert abs(float(got) - want) < D.ANALYTIC_TOL, (
            f"{key}: your answer {got!r}, expected {want!r}. {hint}"
        )


def test_every_answer_key_is_still_present():
    missing = sorted(set(EXPECTED) - set(answers.ANSWERS))
    assert not missing, f"answers.py is missing these keys: {missing}"
