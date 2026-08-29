#!/usr/bin/env bash
# Tests for the Day 110 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * rates multiply -- two gears at 2 and 3 give 6, and a four-stage train
#     gives 36 -- and the same arithmetic drives every chain in the lab;
#   * the one-variable chain rule agrees with Day 108's central difference on
#     six compositions, and evaluating the outer derivative at x instead of at
#     u is asserted to give the wrong answer rather than merely warned about;
#   * a chain of five functions has derivative 2 x 1 x 10 x 0.1 x 0.2 = 0.4,
#     which the collapsed formula ln(2x + 3) and a measurement both confirm;
#   * when a variable reaches the output by two paths the contributions ADD --
#     24 + 12 = 36 -- and the suite asserts that neither single path and not
#     their product matches the measurement;
#   * a reverse-mode autodiff engine written from scratch reproduces every
#     gradient, agrees with forward mode to the last bit, and agrees with a
#     central difference to about a part in a billion;
#   * a two-layer network is backpropagated by hand, by the engine and by
#     central differences, and all three agree on all sixteen gradients;
#   * fifty factors of 0.9 collapse and fifty of 1.1 blow up, asserted as
#     orders of magnitude rather than digits -- and one measured result that
#     contradicts the naive story is reported rather than hidden;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside the lab, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

check_eq() {
  # check_eq <label> <expected> <actual>
  if [ "$2" = "$3" ]; then
    check "$1" "yes"
  else
    check "$1 (expected [$2], got [$3])" "no"
  fi
}

# Resolve pytest: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping checks.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest:" >&2
  echo "    PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

# The Python that owns that pytest is the one with numpy installed.
python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import numpy" >/dev/null 2>&1; then
  echo "FAIL: numpy is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 110 — Rates Multiply"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("numpy", "pytest"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

pinned_numpy="$(grep -E '^numpy==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_numpy="$("${python_bin}" -c "from importlib.metadata import version; print(version('numpy'))")"
check_eq "installed numpy matches requirements.txt" "${pinned_numpy}" "${installed_numpy}"

major="$("${python_bin}" -c "import numpy; print(numpy.__version__.split('.')[0])")"
check_eq "numpy is version 2 or later" "2" "${major}"

float_width="$("${python_bin}" -c "import sys; print(sys.float_info.mant_dig)")"
check_eq "Python floats are IEEE-754 doubles with a 53-bit significand" "53" "${float_width}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_gears_and_rates 02_composition_and_the_chain_rule \
              03_deeper_chains 04_two_paths_add 05_the_value_engine \
              06_backprop_by_hand 07_vanishing_and_exploding; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -5 | sed 's/^/      /'
  else
    check "${script}.py exits 0" "yes"
  fi
  case "${out}" in
    *"${script}.py: every assertion held."*)
      check "${script}.py reports every assertion held" "yes" ;;
    *) check "${script}.py reports every assertion held" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "3. The reference pytest suite: real values, real exceptions"
# --------------------------------------------------------------------------

ref_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
ref_status=$?
echo "${ref_out}" | tail -3 | sed 's/^/  /'
if [ "${ref_status}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0" "no"
fi
case "${ref_out}" in
  *" failed"*) check "no test in the reference suite failed" "no" ;;
  *)           check "no test in the reference suite failed" "yes" ;;
esac
ref_passed="$(printf '%s\n' "${ref_out}" | grep -o '[0-9][0-9]* passed' | head -1 | cut -d' ' -f1)"
if [ "${ref_passed:-0}" -ge 200 ]; then
  check "the reference suite ran at least 200 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 200 tests (ran ${ref_passed:-0})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The starter suite skips unattempted work instead of failing it"
# --------------------------------------------------------------------------

start_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
start_status=$?
echo "${start_out}" | tail -3 | sed 's/^/  /'
if [ "${start_status}" -eq 0 ]; then
  check "pytest starter exits 0 on an untouched checkout" "yes"
else
  check "pytest starter exits 0 on an untouched checkout" "no"
fi
case "${start_out}" in
  *" failed"*) check "the starter suite reports no failures" "no" ;;
  *)           check "the starter suite reports no failures" "yes" ;;
esac
case "${start_out}" in
  *skipped*) check "unwritten exercises are reported as skipped, not passed" "yes" ;;
  *) check "unwritten exercises are reported as skipped, not passed" "no" ;;
esac

# The import guard. Both directories contain modules called `autodiff`,
# `chainrule`, `dataset` and `network`, and pytest imports test files by
# putting their directory on sys.path -- so collecting both suites at once
# would otherwise let the starter tests import the REFERENCE solution and
# report unwritten exercises as passing. Each directory's conftest.py prevents
# that. This check proves it still does: across both suites, the skip count
# must be unchanged.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The lesson's claims, checked one value at a time"
# --------------------------------------------------------------------------

facts="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
import math

import dataset as D
import network as N
from autodiff import (
    Dual,
    Value,
    forward_mode_gradient,
    graph_size,
    numeric_gradient,
    reverse_mode_gradient,
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
    repeated_product,
    running_products,
    total_derivative,
    wrong_single_path_derivative,
)

# -- rates multiply ---------------------------------------------------------
print("gears_two", gear_ratio(D.GEAR_RATIOS))
print("gears_four", gear_ratio(D.GEAR_TRAIN))
print("currency", product(D.CURRENCY_RATES))
print("empty_product", product([]))
print("gear_order_irrelevant", gear_ratio(D.GEAR_TRAIN) == gear_ratio(tuple(reversed(D.GEAR_TRAIN))))

# -- composition ------------------------------------------------------------
print("composed_value", compose(D.square, D.line)(2.0))
print("composed_other_order", compose(D.line, D.square)(2.0))
print("chain_rule_correct", chain_rule(D.d_square, D.line, D.d_line, 2.0))
print("chain_rule_mistake", D.d_square(2.0) * D.d_line(2.0))
gaps = []
for case in D.COMPOSITIONS:
    analytic = chain_rule(case.d_outer, case.inner, case.d_inner, case.x)
    measured = central_difference(compose(case.outer, case.inner), case.x, D.H)
    gaps.append(abs(analytic - measured))
    print(f"exact_{case.name.replace(' ', '_')}", abs(analytic - case.exact) < D.ANALYTIC_TOL)
print("all_six_match_measurement", all(g < D.NUMERIC_TOL for g in gaps))
print("worst_composition_gap", f"{max(gaps):.3e}")
print("sigmoid_slope_at_zero", chain_rule(D.COMPOSITIONS[4].d_outer, D.COMPOSITIONS[4].inner, D.COMPOSITIONS[4].d_inner, 0.0))
print("sigmoid_quarter_is_max", all(
    chain_rule(D.COMPOSITIONS[4].d_outer, D.COMPOSITIONS[4].inner,
               D.COMPOSITIONS[4].d_inner, x) < 0.25
    for x in (-4.0, -2.0, -0.5, 0.5, 2.0, 4.0)))
print("tanh_of_line_slope", chain_rule(D.COMPOSITIONS[5].d_outer, D.COMPOSITIONS[5].inner, D.COMPOSITIONS[5].d_inner, -0.5))

# -- deep chains ------------------------------------------------------------
values = chain_values(D.FIVE_STAGES, D.FIVE_START)
rates = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
print("five_values", "|".join(f"{v:g}" for v in values))
print("five_rates", "|".join(f"{r:g}" for r in rates))
print("five_derivative", chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START))
print("five_closed_form", D.d_five_chain_closed_form(1.0))
print("five_measured", f"{central_difference(chain_function(D.FIVE_STAGES), 1.0, D.H):.9f}")
carried = running_products(rates)
print("running_first", f"{carried[0]:.10g}")
print("running_last", carried[-1])
print("orders_differ_by_rounding", abs(product(rates) - carried[0]) < 4.0 * D.EPSILON)
print("orders_are_not_identical", product(rates) != carried[0])

# -- two paths --------------------------------------------------------------
paths = [[D.TWO_PATH_V, 2.0 * D.TWO_PATH_X], [D.TWO_PATH_U, 3.0]]
measured_two = central_difference(D.two_path_direct, D.TWO_PATH_X, D.H)
print("two_path_contributions", "|".join(f"{c:g}" for c in path_contributions(paths)))
print("two_path_sum", total_derivative(paths))
print("two_path_closed_form", D.d_two_path_direct(D.TWO_PATH_X))
print("two_path_sum_matches", abs(total_derivative(paths) - measured_two) < D.NUMERIC_TOL)
print("path_a_alone_is_wrong", abs(wrong_single_path_derivative(paths, 0) - measured_two) > 1.0)
print("path_b_alone_is_wrong", abs(wrong_single_path_derivative(paths, 1) - measured_two) > 1.0)
print("product_of_paths_is_wrong", abs(24.0 * 12.0 - measured_two) > 1.0)
print("surface_z", D.surface(*D.SURFACE_POINT))
print("surface_ds", D.SURFACE_DZ_DU * 3.0 + D.SURFACE_DZ_DV * 1.0)
print("surface_dt", D.SURFACE_DZ_DU * 2.0 + D.SURFACE_DZ_DV * -1.0)
print("surface_ds_measured", f"{partial_difference(D.surface, D.SURFACE_POINT, 0, D.H):.9f}")
print("surface_dt_measured", f"{partial_difference(D.surface, D.SURFACE_POINT, 1, D.H):.9f}")

# -- the engine -------------------------------------------------------------
a, b = Value(3.0), Value(4.0)
c = a * b
c.backward()
print("mul_grads", f"{a.grad:g}|{b.grad:g}")
x = Value(3.0)
(x + x).backward()
print("used_twice_grad", x.grad)
x2 = Value(3.0)
(x2 * x2).backward()
print("squared_grad", x2.grad)
z = Value(0.0)
z.tanh().backward()
print("tanh_slope_at_zero", z.grad)
z2 = Value(D.HALF_LN3)
t2 = z2.tanh()
t2.backward()
print("tanh_at_half_ln3", t2.data)
print("tanh_slope_at_half_ln3", z2.grad)
p, q = Value(2.0), Value(-3.0)
order = topological_order((p * q) + p)
position = {id(n): i for i, n in enumerate(order)}
print("topo_children_first", all(
    position[id(child)] < position[id(node)]
    for node in order for child in node._children))
deep = Value(1.0)
for _ in range(10000):
    deep = deep * 1.0
deep.backward()
print("deep_graph_nodes", graph_size(deep))
print("deep_graph_grad", deep.grad)
d = Dual(3.0, 1.0) * Dual(4.0, 0.0)
print("dual_product_rule", f"{d.value:g}|{d.dot:g}")

# -- the network ------------------------------------------------------------
fw = N.forward(D.NET_X1, D.NET_X2, N.default_parameter_values())
hand = N.hand_gradients()
engine = N.engine_gradients()
numeric = {**N.numeric_parameter_gradients(D.H), **N.numeric_input_gradients(D.H)}
print("net_a", fw["a"])
print("net_b", fw["b"])
print("net_out", fw["out"])
print("net_loss", fw["loss"])
print("net_b_slope_exact", (1.0 - fw["b"] * fw["b"]) == 0.75)
print("net_d_out", hand["out"])
print("net_d_vA_is_zero", hand["vA"] == 0.0)
print("net_d_vA_repr", repr(hand["vA"]))
print("net_d_vB", hand["vB"])
print("net_d_b_pre", hand["b_pre"])
print("net_d_wA2", hand["wA2"])
print("net_d_wB2", hand["wB2"])
print("net_d_x1", hand["x1"])
print("net_d_x2", hand["x2"])
print("net_x1_contributions", "|".join(f"{v:g}" for v in D.NET_X1_CONTRIBUTIONS))
print("net_x1_single_path_wrong", abs(D.NET_X1_CONTRIBUTIONS[0] - numeric["x1"]) > 1.0)
print("net_engine_equals_hand", all(engine[k] == hand[k] for k in D.NET_GRADIENTS))
print("net_numeric_agrees", all(abs(engine[k] - numeric[k]) < D.NUMERIC_TOL for k in numeric))
print("net_worst_numeric_gap", f"{max(abs(engine[k] - numeric[k]) for k in numeric):.3e}")
fwd_grads, fwd_passes = N.forward_mode_parameter_gradients()
print("net_forward_mode_agrees", all(abs(fwd_grads[k] - hand[k]) < D.ANALYTIC_TOL for k in fwd_grads))
print("net_forward_passes", fwd_passes)
print("net_parameter_count", len(D.NET_PARAMETERS))

# -- cost -------------------------------------------------------------------
def many(vals):
    total = vals[0] * 1.0
    for v in vals[1:]:
        total = total + v * v
    return (total * 0.1).tanh()

point = [0.1 * (i + 1) for i in range(25)]
r_grads, r_passes = reverse_mode_gradient(many, point)
f_grads, f_passes = forward_mode_gradient(many, point)
n_grads, n_passes = numeric_gradient(lambda v: many([Value(q) for q in v]).data, point, D.H)
print("reverse_passes_25", r_passes)
print("forward_passes_25", f_passes)
print("numeric_passes_25", n_passes)
print("modes_agree_exactly", all(abs(r - f) < D.ANALYTIC_TOL for r, f in zip(r_grads, f_grads)))
print("modes_agree_with_measurement", all(abs(r - n) < D.NUMERIC_TOL for r, n in zip(r_grads, n_grads)))

# -- vanishing and exploding ------------------------------------------------
decay = repeated_product(D.DECAY_FACTOR, D.CHAIN_LENGTH)
growth = repeated_product(D.GROWTH_FACTOR, D.CHAIN_LENGTH)
mild = repeated_product(D.MILD_DECAY, D.CHAIN_LENGTH)
sharp = repeated_product(D.SHARP_DECAY, D.CHAIN_LENGTH)
print("decay_50", f"{decay:.6e}")
print("growth_50", f"{growth:.6e}")
print("decay_order", order_of_magnitude(decay))
print("growth_order", order_of_magnitude(growth))
print("decay_200_order", order_of_magnitude(repeated_product(D.DECAY_FACTOR, D.LONG_CHAIN_LENGTH)))
print("growth_200_order", order_of_magnitude(repeated_product(D.GROWTH_FACTOR, D.LONG_CHAIN_LENGTH)))
print("mild_is_four_epsilons", mild == 4.0 * D.EPSILON)
print("mild_still_moves_a_weight", (1.0 + mild) != 1.0)
print("three_more_halvings_vanish", (1.0 + repeated_product(D.MILD_DECAY, 53)) == 1.0)
print("sharp_vanishes", (1.0 + sharp) == 1.0)
print("sharp_order", order_of_magnitude(sharp))

def stacked(depth):
    def f(vals):
        node = vals[0]
        for _ in range(depth):
            node = node.tanh()
        return node
    return f

single = reverse_mode_gradient(stacked(1), [0.9])[0][0]
depth40 = reverse_mode_gradient(stacked(40), [0.9])[0][0]
print("tanh_stack_single", f"{single:.6f}")
print("tanh_stack_40", f"{depth40:.6e}")
print("tanh_stack_naive_prediction", f"{single ** 40:.6e}")
print("tanh_stack_beats_prediction_by", f"{depth40 / single ** 40:.3e}")
print("tanh_stack_gap_is_over_nine_orders", depth40 > 1e9 * single ** 40)
print("tanh_stack_monotone", [
    reverse_mode_gradient(stacked(d), [0.9])[0][0] for d in (1, 5, 10, 20, 40, 80, 160)
] == sorted([
    reverse_mode_gradient(stacked(d), [0.9])[0][0] for d in (1, 5, 10, 20, 40, 80, 160)
], reverse=True))
print("constant_factor_does_vanish", repeated_product(0.487, 40) < 1e-12)
print("epsilon", D.EPSILON == float(__import__("numpy").finfo(__import__("numpy").float64).eps))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "two gears at 2 and 3 give an overall ratio of 6" "6.0" "$(get gears_two)"
check_eq "a four-stage train at 2, 3, 1.5 and 4 gives 36" "36.0" "$(get gears_four)"
check_eq "three currency rates multiply to 150" "150.0" "$(get currency)"
check_eq "the empty product is 1.0, not 0.0" "1.0" "$(get empty_product)"
check_eq "reversing the gear stages does not change the ratio" "True" "$(get gear_order_irrelevant)"

check_eq "composing square after 3x + 1 at x = 2 gives 49" "49.0" "$(get composed_value)"
check_eq "composing the other way gives 13, so order matters" "13.0" "$(get composed_other_order)"
check_eq "the chain rule gives 42 for (3x + 1) squared at x = 2" "42.0" "$(get chain_rule_correct)"
check_eq "evaluating the outer derivative at x instead gives 12, which is wrong" \
  "12.0" "$(get chain_rule_mistake)"
check_eq "all six compositions agree with a central difference" "True" "$(get all_six_match_measurement)"
for name in square_of_a_line sine_of_a_square gaussian_bump log_of_a_shifted_square the_sigmoid tanh_of_a_line; do
  check_eq "the chain rule matches the closed form for ${name//_/ }" "True" "$(get "exact_${name}")"
done
check_eq "the sigmoid's slope at zero is exactly 0.25" "0.25" "$(get sigmoid_slope_at_zero)"
check_eq "and 0.25 is the largest slope the sigmoid ever has" "True" "$(get sigmoid_quarter_is_max)"
check_eq "tanh(2x + 1) has slope exactly 2 at x = -0.5" "2.0" "$(get tanh_of_line_slope)"
echo "  (measured on this run: the worst gap between the chain rule and a central difference across the six compositions was $(get worst_composition_gap) -- reported, not asserted)"

check_eq "the five-stage forward pass is 1, 2, 5, 25, 5, ln 5" \
  "1|2|5|25|5|1.60944" "$(get five_values)"
check_eq "its five local rates are 2, 1, 10, 0.1, 0.2" "2|1|10|0.1|0.2" "$(get five_rates)"
check_eq "their product is 0.4" "0.4" "$(get five_derivative)"
check_eq "and the collapsed formula 2/(2x + 3) agrees" "0.4" "$(get five_closed_form)"
check_eq "as does a central difference of the whole chain" "0.400000000" "$(get five_measured)"
check_eq "the backward walk's first carried value is the whole derivative" \
  "0.4" "$(get running_first)"
check_eq "and its last is the final local rate alone" "0.2" "$(get running_last)"
check_eq "multiplying forwards and backwards differs by under four epsilons" \
  "True" "$(get orders_differ_by_rounding)"
check_eq "but the two orders are NOT bit-identical, which is float64, not a bug" \
  "True" "$(get orders_are_not_identical)"

check_eq "the two path contributions are 24 and 12" "24|12" "$(get two_path_contributions)"
check_eq "and the derivative is their SUM, 36" "36.0" "$(get two_path_sum)"
check_eq "which the closed form 9x squared confirms" "36.0" "$(get two_path_closed_form)"
check_eq "and a central difference confirms" "True" "$(get two_path_sum_matches)"
check_eq "the u path alone does not match the measurement" "True" "$(get path_a_alone_is_wrong)"
check_eq "the v path alone does not match the measurement" "True" "$(get path_b_alone_is_wrong)"
check_eq "and multiplying the paths does not match either" "True" "$(get product_of_paths_is_wrong)"
check_eq "the surface z at (2, 3) is 37" "37.0" "$(get surface_z)"
check_eq "dz/ds is 12x3 + (-2)x1 = 34" "34.0" "$(get surface_ds)"
check_eq "dz/dt is 12x2 + (-2)x(-1) = 26" "26.0" "$(get surface_dt)"
check_eq "and a partial difference measures dz/ds as 34" "34.000000001" "$(get surface_ds_measured)"
check_eq "and dz/dt as 26" "26.000000000" "$(get surface_dt_measured)"

check_eq "a product's two local rates are each the other input" "4|3" "$(get mul_grads)"
check_eq "a value used twice accumulates both contributions, giving 2" \
  "2.0" "$(get used_twice_grad)"
check_eq "so x times x reproduces the power rule without being told it" \
  "6.0" "$(get squared_grad)"
check_eq "tanh's slope at zero is exactly 1" "1.0" "$(get tanh_slope_at_zero)"
check_eq "tanh at half the log of 3 is exactly 0.5" "0.5" "$(get tanh_at_half_ln3)"
check_eq "and its slope there is exactly 0.75" "0.75" "$(get tanh_slope_at_half_ln3)"
check_eq "the topological order puts every child before its parent" "True" "$(get topo_children_first)"
# 20001, not 10001: each `node * 1.0` creates a Value for the constant as well
# as a Value for the product, so ten thousand operations leave twenty thousand
# nodes plus the original leaf. Counting them is the point -- this is the
# memory reverse mode pays for its speed.
check_eq "a ten-thousand-operation graph is walked without recursion limits" \
  "20001" "$(get deep_graph_nodes)"
check_eq "and its gradient is exactly 1 after ten thousand multiplications by 1" \
  "1.0" "$(get deep_graph_grad)"
check_eq "a dual number applies the product rule" "12|4" "$(get dual_product_rule)"

check_eq "hidden unit A activates at exactly 0" "0.0" "$(get net_a)"
check_eq "hidden unit B activates at exactly 0.5" "0.5" "$(get net_b)"
check_eq "so tanh's slope at B is exactly 0.75" "True" "$(get net_b_slope_exact)"
check_eq "the network output is -0.5" "-0.5" "$(get net_out)"
check_eq "and the loss is 2.25" "2.25" "$(get net_loss)"
check_eq "d loss / d out is 2 x (-1.5) = -3" "-3.0" "$(get net_d_out)"
check_eq "d loss / d vA is exactly zero, because it multiplies a dead unit" \
  "True" "$(get net_d_vA_is_zero)"
# The hand computation reaches it as -3.0 x 0.0, which in IEEE-754 is negative
# zero. It compares equal to 0.0 and behaves as zero everywhere in this lab, so
# the check above asks the question that matters; the repr is reported rather
# than asserted, because the sign of a zero is arithmetic trivia and not the
# lesson.
echo "  (measured on this run: the hand route reaches that gradient as $(get net_d_vA_repr), IEEE-754 negative zero, which compares equal to 0.0 -- reported, not asserted)"
check_eq "d loss / d vB is -1.5" "-1.5" "$(get net_d_vB)"
check_eq "d loss / d b_pre is 9 x 0.75 = 6.75" "6.75" "$(get net_d_b_pre)"
check_eq "d loss / d wA2 is -12" "-12.0" "$(get net_d_wA2)"
check_eq "d loss / d wB2 is 13.5" "13.5" "$(get net_d_wB2)"
check_eq "x1 reaches the loss twice, contributing -6 and -3.375" \
  "-6|-3.375" "$(get net_x1_contributions)"
# Section 6 re-runs this script with D110_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_d_x1="-9.375"
if [ -n "${D110_SELF_TEST:-}" ]; then
  expected_d_x1="-6.0"   # the belief that a gradient follows one path only
fi
check_eq "so d loss / d x1 is their SUM, -9.375" "${expected_d_x1}" "$(get net_d_x1)"
check_eq "and d loss / d x2 is 4.6875" "4.6875" "$(get net_d_x2)"
check_eq "taking only x1's first path is measurably wrong" "True" "$(get net_x1_single_path_wrong)"
check_eq "the engine matches the hand computation on all sixteen, bit for bit" \
  "True" "$(get net_engine_equals_hand)"
check_eq "and a central difference agrees with both within tolerance" \
  "True" "$(get net_numeric_agrees)"
check_eq "forward mode reproduces every parameter gradient" "True" "$(get net_forward_mode_agrees)"
check_eq "forward mode needed one pass per parameter" "9" "$(get net_forward_passes)"
check_eq "the network has nine parameters" "9" "$(get net_parameter_count)"
echo "  (measured on this run: the worst gap between the engine and a central difference across all sixteen network gradients was $(get net_worst_numeric_gap) -- reported, not asserted)"

check_eq "reverse mode needs 1 pass for 25 inputs" "1" "$(get reverse_passes_25)"
check_eq "forward mode needs 25" "25" "$(get forward_passes_25)"
check_eq "central differences need 50" "50" "$(get numeric_passes_25)"
check_eq "the two modes agree to the last bits" "True" "$(get modes_agree_exactly)"
check_eq "and both agree with the measurement" "True" "$(get modes_agree_with_measurement)"

check_eq "0.9 to the fiftieth is about 5.15e-3" "5.153775e-03" "$(get decay_50)"
check_eq "1.1 to the fiftieth is about 1.17e+2" "1.173909e+02" "$(get growth_50)"
check_eq "so the decayed order of magnitude is -3" "-3" "$(get decay_order)"
check_eq "and the grown one is +2" "2" "$(get growth_order)"
check_eq "at 200 layers the decay reaches order -10" "-10" "$(get decay_200_order)"
check_eq "and the growth reaches order +8" "8" "$(get growth_200_order)"
check_eq "0.5 to the fiftieth is exactly four epsilons" "True" "$(get mild_is_four_epsilons)"
check_eq "so it still moves a weight of 1, which contradicts the obvious guess" \
  "True" "$(get mild_still_moves_a_weight)"
check_eq "three more halvings do make it disappear" "True" "$(get three_more_halvings_vanish)"
check_eq "the sigmoid's best case vanishes completely in fifty layers" \
  "True" "$(get sharp_vanishes)"
check_eq "at order -31" "-31" "$(get sharp_order)"
check_eq "a stacked tanh beats the constant-factor prediction by over nine orders" \
  "True" "$(get tanh_stack_gap_is_over_nine_orders)"
check_eq "while still falling monotonically with depth" "True" "$(get tanh_stack_monotone)"
check_eq "and a genuinely constant factor does vanish geometrically" \
  "True" "$(get constant_factor_does_vanish)"
check_eq "the EPSILON in dataset.py is numpy's float64 epsilon" "True" "$(get epsilon)"
echo "  (measured on this run: 40 stacked tanh layers gave a gradient of $(get tanh_stack_40) against a naive prediction of $(get tanh_stack_naive_prediction) from a single-layer slope of $(get tanh_stack_single) -- larger by a factor of $(get tanh_stack_beats_prediction_by), reported and not asserted to a value)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong one -- -6.0, which is what you would get by following only the
# first of the two paths from x1 to the loss -- and asserts that the re-run
# reports the failure and exits non-zero. If this section passes, section 5 is
# not decorative.
if [ -z "${D110_SELF_TEST:-}" ]; then
  self_out="$(D110_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: so d loss / d x1 is their SUM, -9.375"*)
      check "the failing check is named in the output with both values" "yes" ;;
    *) check "the failing check is named in the output with both values" "no" ;;
  esac
  case "${self_out}" in
    *", 1 failure(s)."*)
      check "the summary line counts exactly one failure" "yes" ;;
    *) check "the summary line counts exactly one failure" "no" ;;
  esac
else
  echo "  (self-test run: section 6 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "7. Nothing was left behind"
# --------------------------------------------------------------------------

# `.venv` is pruned from both searches below. The virtual environment ships
# NumPy's and pytest's own precompiled bytecode -- hundreds of __pycache__
# directories that came with the packages and have nothing to do with whether
# THIS lab tidied up after itself. Searching them would report a failure the
# reader cannot fix and did not cause. Everything the lab itself writes lives
# outside `.venv`, which is exactly what these two checks look at.

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory left by the lab's own code" "no"
else
  check "no __pycache__ directory left by the lab's own code" "yes"
fi

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -print -quit 2>/dev/null | grep -q .; then
  check "no .pytest_cache directory left under the lab" "no"
else
  check "no .pytest_cache directory left under the lab" "yes"
fi

if grep -rqE 'urlopen|requests\.|socket\.|http://|https://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
