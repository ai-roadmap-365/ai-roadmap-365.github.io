#!/usr/bin/env bash
# Tests for the Day 108 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * the average rate of x**2 over [3, 3 + h] is 6 + h for every h, and the
#     four-term sequence 7, 6.1, 6.01, 6.001 gets closer to 6 every time;
#   * the central difference is exact on a parabola and beats the forward
#     difference by more than two hundred thousand times on e**x at h = 1e-5;
#   * the error across 27 step sizes from 1e-1 to 1e-14 is U-shaped -- it
#     falls, reaches an interior minimum, and rises again -- and the measured
#     best h is reported rather than asserted to a fixed value;
#   * a forward difference at h = 1e-300 returns exactly 0.0, with no warning;
#   * the first derivative is zero at a minimum, a maximum and a flat step
#     alike, and only the second derivative tells them apart -- and at x**3
#     and x**4 it cannot, which the suite asserts rather than glosses;
#   * the central difference of |x| at 0 returns 0.0 and the one-sided rules
#     return +1 and -1, so a value was produced where no derivative exists;
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

echo "Day 108 — Watch the Slope Settle"
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

for script in 01_average_rate_of_change 02_shrinking_intervals \
              03_rules_checked_numerically 04_forward_and_central \
              05_the_u_shaped_error 06_zero_derivative_and_curvature \
              07_where_the_derivative_fails; do
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
if [ "${ref_passed:-0}" -ge 150 ]; then
  check "the reference suite ran at least 150 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 150 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `derivatives` and
# `dataset`, and pytest imports test files by putting their directory on
# sys.path -- so collecting both suites at once would otherwise let the starter
# tests import the REFERENCE solution and report unwritten exercises as
# passing. Each directory's conftest.py prevents that. This check proves it
# still does: across both suites, the skip count must be unchanged.
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

import numpy as np

import dataset as D
from derivatives import (
    average_rate,
    backward_difference,
    best_step,
    central_difference,
    classify_stationary_point,
    error_curve,
    forward_difference,
    is_u_shaped,
    numpy_gradient_slope,
    numpy_gradient_slope_from_coordinates,
    second_difference,
    shrinking_slopes,
    tangent_at,
)


def car(t):
    return 4.0 * t * t


# -- average rates ---------------------------------------------------------
print("car_whole_trip", average_rate(car, 0.0, 6.0))
print("car_fourth_second", average_rate(car, 3.0, 4.0))
print("car_third_second", average_rate(car, 2.0, 3.0))
try:
    average_rate(car, 3.0, 3.0)
except Exception as exc:  # deliberately broad: the TYPE is what is asserted
    print("zero_width_raises", type(exc).__name__)
else:
    print("zero_width_raises", "NOTHING_RAISED")

# -- the shrinking sequence -------------------------------------------------
slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
print("settle_sequence", "|".join(f"{s:.6f}" for s in slopes))
print("settle_matches_six_plus_h",
      all(abs(s - e) < D.EXACT_TOL for s, e in zip(slopes, D.SETTLE_EXPECTED_SLOPES)))
gaps = [abs(s - 6.0) for s in slopes]
print("settle_monotone", gaps == sorted(gaps, reverse=True))
print("settle_from_above", all(s > 6.0 for s in slopes))
left = shrinking_slopes(D.square, D.SETTLE_POINT, [-w for w in D.SETTLE_WIDTHS])
print("settle_from_below", all(s < 6.0 for s in left))
slope, intercept = tangent_at(D.square, 3.0, D.COMPARE_WIDTH)
print("tangent_slope", round(slope, 6))
print("tangent_intercept", round(intercept, 6))

# -- the rules --------------------------------------------------------------
measured = [central_difference(f, x, D.COMPARE_WIDTH) for _, f, _, x in D.RULE_CASES]
print("rules_all_within_tolerance",
      all(abs(m - e) < D.RULE_TOL for m, e in zip(measured, D.RULE_EXPECTED)))
print("rules_exact_values", "|".join(f"{v:.4f}" for v in D.RULE_EXPECTED))
print("slope_of_two_to_the_x_at_zero", round(central_difference(lambda x: 2.0**x, 0.0, D.COMPARE_WIDTH), 9))
print("ln_two", round(math.log(2.0), 9))
print("slope_of_e_to_the_x_at_zero", round(central_difference(D.exponential, 0.0, D.COMPARE_WIDTH), 9))

# -- forward, backward, central ---------------------------------------------
print("forward_on_parabola", forward_difference(D.square, 3.0, 0.1))
print("backward_on_parabola", backward_difference(D.square, 3.0, 0.1))
print("central_on_parabola_is_six", abs(central_difference(D.square, 3.0, 0.1) - 6.0) < 1e-11)
fwd_err = abs(forward_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
cen_err = abs(central_difference(D.exponential, 1.0, D.COMPARE_WIDTH) - math.e)
print("forward_error_at_1e5", f"{fwd_err:.6e}")
print("central_error_at_1e5", f"{cen_err:.6e}")
print("central_beats_forward_thousandfold", cen_err * 1000.0 < fwd_err)
print("central_advantage_ratio", int(fwd_err / cen_err))
coarse = abs(central_difference(D.exponential, 1.0, 1e-2) - math.e)
fine = abs(central_difference(D.exponential, 1.0, 5e-3) - math.e)
print("halving_h_quarters_central_error", 3.9 < coarse / fine < 4.1)
coarse_f = abs(forward_difference(D.exponential, 1.0, 1e-2) - math.e)
fine_f = abs(forward_difference(D.exponential, 1.0, 5e-3) - math.e)
print("halving_h_halves_forward_error", 1.9 < coarse_f / fine_f < 2.1)

# -- the U ------------------------------------------------------------------
fe = error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, forward_difference)
ce = error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)
print("grid_size", len(D.U_WIDTHS))
print("grid_first", f"{D.U_WIDTHS[0]:.0e}")
print("grid_last", f"{D.U_WIDTHS[-1]:.0e}")
print("forward_curve_is_u", is_u_shaped(fe))
print("central_curve_is_u", is_u_shaped(ce))
bf_h, bf_e = best_step(D.U_WIDTHS, fe)
bc_h, bc_e = best_step(D.U_WIDTHS, ce)
print("best_forward_h", f"{bf_h:.3e}")
print("best_forward_error", f"{bf_e:.6e}")
print("best_central_h", f"{bc_h:.3e}")
print("best_central_error", f"{bc_e:.6e}")
print("best_central_in_band", 1e-7 <= bc_h <= 1e-4)
print("best_forward_in_band", 1e-9 <= bf_h <= 1e-6)
print("best_central_beats_best_forward", bc_e < bf_e)
print("large_h_end_far_worse", ce[0] > 100.0 * bc_e)
print("small_h_end_far_worse", ce[-1] > 100.0 * bc_e)
print("minimum_is_interior", 0 < ce.index(min(ce)) < len(ce) - 1)
print("balance_prediction_forward",
      0.1 < bf_h / math.sqrt(2.0 * D.EPSILON) < 10.0)
print("balance_prediction_central",
      0.1 < bc_h / (3.0 * D.EPSILON) ** (1.0 / 3.0) < 10.0)
print("tiny_h_returns_zero", forward_difference(D.exponential, 1.0, 1e-300))
print("tiny_h_samples_collide", math.exp(1.0 + 1e-300) == math.exp(1.0))
print("epsilon", D.EPSILON == float(np.finfo(np.float64).eps))

# -- stationary points ------------------------------------------------------
H, TOL = D.STATIONARY_WIDTH, D.STATIONARY_TOL
print("parabola_vertex_slope", central_difference(D.parabola, 2.0, H))
print("cubic_min_slope_is_zero", abs(central_difference(D.cubic, 1.0, H)) < TOL)
print("cubic_max_slope_is_zero", abs(central_difference(D.cubic, -1.0, H)) < TOL)
print("cube_step_slope_is_zero", abs(central_difference(D.plain_cube, 0.0, H)) < TOL)
print("parabola_curvature", round(second_difference(D.parabola, 2.0, H), 5))
print("cubic_min_curvature", round(second_difference(D.cubic, 1.0, H), 5))
print("cubic_max_curvature", round(second_difference(D.cubic, -1.0, H), 5))
print("cube_step_curvature", round(second_difference(D.plain_cube, 0.0, H), 5))
print("curvature_separates_min_from_max",
      second_difference(D.cubic, 1.0, H) > 0.0 > second_difference(D.cubic, -1.0, H))
print("classify_parabola", classify_stationary_point(D.parabola, 2.0, H, TOL))
print("classify_cubic_min", classify_stationary_point(D.cubic, 1.0, H, TOL))
print("classify_cubic_max", classify_stationary_point(D.cubic, -1.0, H, TOL))
print("classify_cube_step", classify_stationary_point(D.plain_cube, 0.0, H, TOL))
print("classify_quartic", classify_stationary_point(lambda x: x**4, 0.0, H, TOL))
print("classify_sloping", classify_stationary_point(D.cubic, 0.0, H, TOL))
print("downhill_signs", "|".join(
    "left" if central_difference(D.parabola, x, H) > TOL else "right"
    for x in (-1.0, 0.5, 1.5, 2.5, 4.0)))

# -- corners ----------------------------------------------------------------
print("abs_forward_at_zero", forward_difference(D.absolute, 0.0, D.CORNER_WIDTH))
print("abs_backward_at_zero", backward_difference(D.absolute, 0.0, D.CORNER_WIDTH))
print("abs_central_at_zero", central_difference(D.absolute, 0.0, D.CORNER_WIDTH))
print("abs_central_never_converges",
      all(central_difference(D.absolute, 0.0, h) == 0.0
          for h in (1e-2, 1e-5, 1e-8, 1e-11, 1e-14)))
print("abs_curvature_at_1e3", round(second_difference(D.absolute, 0.0, 1e-3), 1))
print("abs_curvature_at_1e5", round(second_difference(D.absolute, 0.0, 1e-5), 1))
print("relu_forward_at_zero", forward_difference(D.relu, 0.0, D.CORNER_WIDTH))
print("relu_backward_at_zero", backward_difference(D.relu, 0.0, D.CORNER_WIDTH))
print("relu_central_at_zero", central_difference(D.relu, 0.0, D.CORNER_WIDTH))
print("one_sided_gap_at_corner",
      abs(forward_difference(D.absolute, 0.0, D.CORNER_WIDTH)
          - backward_difference(D.absolute, 0.0, D.CORNER_WIDTH)))
print("one_sided_gap_when_smooth",
      abs(forward_difference(D.square, 3.0, D.CORNER_WIDTH)
          - backward_difference(D.square, 3.0, D.CORNER_WIDTH)) < 1e-3)

# -- numpy ------------------------------------------------------------------
print("numpy_gradient_matches_bit_for_bit",
      numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH)
      == central_difference(D.exponential, 1.0, D.COMPARE_WIDTH))
print("numpy_coordinates_route_differs",
      numpy_gradient_slope_from_coordinates(D.exponential, 1.0, D.COMPARE_WIDTH)
      != numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH))
print("numpy_coordinates_route_differs_slightly",
      abs(numpy_gradient_slope_from_coordinates(D.exponential, 1.0, D.COMPARE_WIDTH)
          - numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH)) < 1e-10)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the car's average speed over six seconds is 24 m/s" "24.0" "$(get car_whole_trip)"
check_eq "over the fourth second alone it is 28 m/s" "28.0" "$(get car_fourth_second)"
check_eq "over the third second it is 20 m/s" "20.0" "$(get car_third_second)"
check_eq "an interval of zero width raises ZeroDivisionError rather than guessing" \
  "ZeroDivisionError" "$(get zero_width_raises)"

check_eq "the shrinking sequence is 7, 6.1, 6.01, 6.001" \
  "7.000000|6.100000|6.010000|6.001000" "$(get settle_sequence)"
check_eq "and every term equals 6 + h to within 1e-12" "True" "$(get settle_matches_six_plus_h)"
check_eq "each interval lands closer to 6 than the one before" "True" "$(get settle_monotone)"
check_eq "approaching from the right comes down from above" "True" "$(get settle_from_above)"
check_eq "approaching from the left comes up from below" "True" "$(get settle_from_below)"
check_eq "the tangent at x = 3 has slope 6" "6.0" "$(get tangent_slope)"
check_eq "and intercept -9, so the line is y = 6x - 9" "-9.0" "$(get tangent_intercept)"

check_eq "all eight derivative rules agree with the arithmetic" "True" "$(get rules_all_within_tolerance)"
check_eq "and their exact values are the eight documented numbers" \
  "0.0000|6.0000|25.3125|-0.2500|30.0000|16.0000|2.7183|0.2500" "$(get rules_exact_values)"
check_eq "the slope of 2**x at zero is the natural log of 2, not 1" \
  "$(get ln_two)" "$(get slope_of_two_to_the_x_at_zero)"
check_eq "the slope of e**x at zero IS 1, which is what makes e special" \
  "1.0" "$(get slope_of_e_to_the_x_at_zero)"

check_eq "the forward difference of x**2 at 3 with h = 0.1 is 6.1" \
  "6.100000000000012" "$(get forward_on_parabola)"
check_eq "the backward difference is 5.9" "5.899999999999999" "$(get backward_on_parabola)"
check_eq "the central difference is exactly 6 on a parabola" "True" "$(get central_on_parabola_is_six)"
check_eq "at h = 1e-5 on e**x the central error is a thousand times smaller" \
  "True" "$(get central_beats_forward_thousandfold)"
check_eq "halving h quarters the central error" "True" "$(get halving_h_quarters_central_error)"
check_eq "halving h only halves the forward error" "True" "$(get halving_h_halves_forward_error)"
echo "  (measured on this run: forward error $(get forward_error_at_1e5), central error $(get central_error_at_1e5), a factor of $(get central_advantage_ratio) -- reported, not asserted)"

check_eq "the error grid holds 27 step sizes" "27" "$(get grid_size)"
check_eq "starting at 1e-1" "1e-01" "$(get grid_first)"
check_eq "and ending at 1e-14" "1e-14" "$(get grid_last)"
check_eq "the forward error curve is U-shaped" "True" "$(get forward_curve_is_u)"
check_eq "the central error curve is U-shaped" "True" "$(get central_curve_is_u)"
check_eq "the minimum is in the interior, not at either end" "True" "$(get minimum_is_interior)"
check_eq "the largest step is more than a hundred times worse than the best" \
  "True" "$(get large_h_end_far_worse)"
check_eq "and so is the smallest, which is the surprising half" \
  "True" "$(get small_h_end_far_worse)"
check_eq "the best central step is in the 1e-7 to 1e-4 band" "True" "$(get best_central_in_band)"
check_eq "the best forward step is in the 1e-9 to 1e-6 band" "True" "$(get best_forward_in_band)"
check_eq "the best central step beats the best forward step" "True" "$(get best_central_beats_best_forward)"
check_eq "the measured forward optimum is within 10x of sqrt(2*EPSILON)" \
  "True" "$(get balance_prediction_forward)"
check_eq "the measured central optimum is within 10x of (3*EPSILON)**(1/3)" \
  "True" "$(get balance_prediction_central)"
check_eq "a step of 1e-300 returns exactly 0.0, silently" "0.0" "$(get tiny_h_returns_zero)"
check_eq "because exp(1 + 1e-300) and exp(1) are the same float64" \
  "True" "$(get tiny_h_samples_collide)"
check_eq "the EPSILON in dataset.py is numpy's float64 epsilon" "True" "$(get epsilon)"
echo "  (measured on this run: best forward h $(get best_forward_h) at error $(get best_forward_error); best central h $(get best_central_h) at error $(get best_central_error) -- reported, not asserted)"

check_eq "the slope at the parabola's vertex is exactly zero" "0.0" "$(get parabola_vertex_slope)"
check_eq "the slope at the cubic's minimum is zero" "True" "$(get cubic_min_slope_is_zero)"
check_eq "the slope at the cubic's maximum is zero too" "True" "$(get cubic_max_slope_is_zero)"
check_eq "and so is the slope at the cubic's flat step" "True" "$(get cube_step_slope_is_zero)"
check_eq "the parabola's curvature is 2" "2.0" "$(get parabola_curvature)"
check_eq "the curvature at the cubic's minimum is +6" "6.0" "$(get cubic_min_curvature)"
check_eq "the curvature at the cubic's maximum is -6" "-6.0" "$(get cubic_max_curvature)"
check_eq "the curvature at the flat step is 0, which decides nothing" \
  "0.0" "$(get cube_step_curvature)"
check_eq "so the second derivative separates the minimum from the maximum" \
  "True" "$(get curvature_separates_min_from_max)"
check_eq "the parabola vertex classifies as a minimum" "minimum" "$(get classify_parabola)"
check_eq "the cubic at +1 classifies as a minimum" "minimum" "$(get classify_cubic_min)"
check_eq "the cubic at -1 classifies as a maximum" "maximum" "$(get classify_cubic_max)"
check_eq "x**3 at 0 classifies as undecided rather than as a minimum" \
  "undecided" "$(get classify_cube_step)"
check_eq "and so does x**4 at 0, which genuinely IS a minimum" \
  "undecided" "$(get classify_quartic)"
check_eq "a point with a real slope is not stationary at all" \
  "not stationary" "$(get classify_sloping)"
check_eq "the sign of the slope points downhill towards the minimum at every x" \
  "right|right|right|left|left" "$(get downhill_signs)"

check_eq "the forward difference of |x| at 0 is +1" "1.0" "$(get abs_forward_at_zero)"
check_eq "the backward difference of |x| at 0 is -1" "-1.0" "$(get abs_backward_at_zero)"
check_eq "the central difference of |x| at 0 is 0.0, where no derivative exists" \
  "0.0" "$(get abs_central_at_zero)"
check_eq "and no smaller h ever reveals a limit that is not there" \
  "True" "$(get abs_central_never_converges)"
check_eq "the curvature at the corner is 2/h: 2,000 at h = 1e-3" "2000.0" "$(get abs_curvature_at_1e3)"
check_eq "and 200,000 at h = 1e-5, so it diverges rather than converging" \
  "200000.0" "$(get abs_curvature_at_1e5)"
check_eq "relu's forward difference at 0 is 1" "1.0" "$(get relu_forward_at_zero)"
check_eq "relu's backward difference at 0 is 0" "0.0" "$(get relu_backward_at_zero)"
# Section 6 re-runs this script with D108_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_relu_central="0.5"
if [ -n "${D108_SELF_TEST:-}" ]; then
  expected_relu_central="1.0"   # the belief that a corner has its right-hand slope
fi
check_eq "relu's central difference at 0 is 0.5, the average of two disagreeing slopes" \
  "${expected_relu_central}" "$(get relu_central_at_zero)"
check_eq "the one-sided rules disagree by 2 at the corner" "2.0" "$(get one_sided_gap_at_corner)"
check_eq "and agree where a derivative really exists" "True" "$(get one_sided_gap_when_smooth)"

check_eq "np.gradient with scalar spacing is our central difference, bit for bit" \
  "True" "$(get numpy_gradient_matches_bit_for_bit)"
check_eq "but passing coordinates instead takes a different arithmetic route" \
  "True" "$(get numpy_coordinates_route_differs)"
check_eq "which differs only in the last few bits" \
  "True" "$(get numpy_coordinates_route_differs_slightly)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong one -- 1.0, which is what you would believe if you assumed a
# corner simply takes its right-hand slope -- and asserts that the re-run
# reports the failure and exits non-zero. If this section passes, section 5 is
# not decorative.
if [ -z "${D108_SELF_TEST:-}" ]; then
  self_out="$(D108_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: relu's central difference at 0 is 0.5"*)
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
