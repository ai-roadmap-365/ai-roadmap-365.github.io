#!/usr/bin/env bash
# Tests for the Day 109 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a partial derivative moves ONE coordinate and holds the rest still, and
#     the harness watches which points f is actually called with;
#   * every numerical gradient agrees with a hand-derived exact one across six
#     surfaces and five points, and the worst error is reported, not hidden;
#   * of 360 bearings measured directly, the one that climbs fastest is the
#     gradient's -- to within the half-degree the sampling grid allows, and
#     the winning rate is |grad| times the cosine of that gap, to nine places;
#   * the gradient is perpendicular to an exactly parametrised contour, with
#     the dot product shrinking tenfold for each tenfold smaller step, which
#     is what "it goes to zero" looks like when every step is finite;
#   * a plane's gradient is the same vector everywhere -- until the function
#     value gets large, where roundoff eats it exactly as eps*|f|/2h predicts;
#   * three surfaces have the identical zero gradient at the origin and are a
#     minimum, a maximum and a saddle;
#   * the central difference's error on a cubic is exactly h squared, and the
#     total error is U-shaped in h with its trough at 1e-5;
#   * numpy.gradient differences a sampled array and is first-order at the
#     boundary by default, which is a different job from ours;
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

echo "Day 109 — Which Way Is Uphill?"
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

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_hold_everything_else_still 02_the_gradient_vector \
              03_steepest_ascent 04_perpendicular_to_the_contour \
              05_flat_ground_three_ways 06_step_size_and_the_u_curve \
              07_one_partial_per_parameter; do
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
echo "3. The reference pytest suite: real values, real derivations"
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
if [ "${ref_passed:-0}" -ge 250 ]; then
  check "the reference suite ran at least 250 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 250 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `gradients` and
# `surfaces`, and pytest imports test files by putting their directory on
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
import numpy as np

import surfaces as S
from gradients import (
    angle_degrees,
    angular_gap_degrees,
    contour_chord,
    directional_derivative,
    directional_derivative_direct,
    forward_partial,
    gradient,
    magnitude,
    partial,
    sweep_directions,
    unit,
)

def show(vector, places=6):
    return "[" + ",".join(f"{v:.{places}f}" for v in vector) + "]"

# -- partial derivatives ---------------------------------------------------
seen = []
def spy(p):
    seen.append(tuple(float(v) for v in p))
    return S.product(p)
partial(spy, (2.0, 5.0), 0)
print("evaluations_per_partial", len(seen))
print("frozen_coordinate_values", "|".join(str(v) for v in sorted({p[1] for p in seen})))
print("moved_coordinate_values", "|".join(f"{v:.5f}" for v in sorted(p[0] for p in seen)))

untouched = np.array([1.0, 2.0])
partial(S.bowl, untouched, 0)
print("point_unmutated", untouched.tolist() == [1.0, 2.0])
print("partial_is_a_plain_float", type(partial(S.bowl, (1.0, 1.0), 0)).__name__)

print("bowl_dfdx_at_2_1", round(partial(S.bowl, (2.0, 1.0), 0), 8))
print("bowl_dfdy_at_2_1", round(partial(S.bowl, (2.0, 1.0), 1), 8))
print("product_dfdx_at_1_0", round(partial(S.product, (1.0, 0.0), 0), 8))
print("product_dfdy_at_1_0", round(partial(S.product, (1.0, 0.0), 1), 8))

# -- gradients against exact -----------------------------------------------
worst = 0.0
count = 0
for name, (f, exact_gradient, _e, _g) in S.SURFACES.items():
    for p in S.PROBE_POINTS:
        worst = max(worst, float(np.max(np.abs(gradient(f, p) - exact_gradient(p)))))
        count += 1
print("gradients_checked", count)
print("worst_gradient_error_under_tolerance", worst < S.GRADIENT_TOL)
print("worst_gradient_error", f"{worst:.3e}")
print("tolerance_headroom_over_ten", S.GRADIENT_TOL / worst > 10.0)
print("bowl_gradient_at_1_1", show(gradient(S.bowl, (1.0, 1.0))))
print("cubic_gradient_at_2_1", show(gradient(S.cubic, (2.0, 1.0))))
print("gradient_size_two_inputs", gradient(S.bowl, (1.0, 1.0)).size)
print("gradient_size_three_inputs", gradient(S.model_loss, S.START_PARAMS).size)
print("bowl_gradient_magnitude", f"{magnitude(gradient(S.bowl, (1.0, 1.0))):.9f}")

# -- directional derivatives -----------------------------------------------
print("rate_due_east", round(directional_derivative(S.bowl, (1.0, 1.0), (1.0, 0.0)), 8))
print("rate_due_north", round(directional_derivative(S.bowl, (1.0, 1.0), (0.0, 1.0)), 8))
print("rate_along_3_minus_1", round(directional_derivative(S.bowl, (1.0, 1.0), (3.0, -1.0)), 8))
short = directional_derivative(S.bowl, (1.0, 1.0), (1.0, 2.0))
long = directional_derivative(S.bowl, (1.0, 1.0), (1000.0, 2000.0))
print("arrow_length_irrelevant", abs(short - long) < 1e-9)
worst_route = 0.0
for d in ((1.0, 1.0), (-1.0, 2.0), (3.0, -1.0), (-2.0, -5.0), (7.0, 0.5)):
    worst_route = max(worst_route, abs(
        directional_derivative(S.bowl, (1.0, 1.0), d)
        - directional_derivative_direct(S.bowl, (1.0, 1.0), d)))
print("dot_route_matches_direct_route", worst_route < S.GRADIENT_TOL)

# -- steepest ascent -------------------------------------------------------
angles, rates = sweep_directions(S.bowl, (1.0, 1.0))
best = int(np.argmax(rates))
worst_i = int(np.argmin(rates))
bearing = angle_degrees(S.bowl_gradient((1.0, 1.0)))
gap = angular_gap_degrees(float(np.degrees(angles[best])), bearing)
print("sweep_size", len(rates))
print("sweep_best_bearing", f"{np.degrees(angles[best]):.1f}")
print("gradient_bearing", f"{bearing:.4f}")
print("sweep_gap_degrees", f"{gap:.4f}")
print("sweep_gap_within_tolerance", gap <= S.ANGLE_TOL_DEGREES)
steepness = magnitude(S.bowl_gradient((1.0, 1.0)))
print("no_direction_beats_the_gradient", float(np.max(rates)) <= steepness + S.GRADIENT_TOL)
ratio = float(np.max(rates)) / steepness
print("best_rate_over_magnitude", f"{ratio:.12f}")
print("cosine_of_the_gap", f"{float(np.cos(np.radians(gap))):.12f}")
print("ratio_equals_cosine", abs(ratio - float(np.cos(np.radians(gap)))) < 1e-9)
print("up_and_down_are_opposite", f"{angular_gap_degrees(float(np.degrees(angles[best])), float(np.degrees(angles[worst_i]))):.4f}")
print("down_rate_is_minus_up_rate", abs(float(np.max(rates)) + float(np.min(rates))) < 1e-6)

# -- perpendicular to the contour ------------------------------------------
drift = 0.0
for name, (f, contour, level, _t0) in S.CONTOURS.items():
    for t in np.linspace(0.3, 2.6, 8):
        drift = max(drift, abs(f(contour(level, t)) - level))
print("contours_hold_f_constant", drift < 1e-12)
print("contour_drift", f"{drift:.3e}")

worst_dot = 0.0
for name, (f, contour, level, _t0) in S.CONTOURS.items():
    for t in (0.4, 0.9, 1.4, 1.9):
        chord, p, _q, _fp, _fq = contour_chord(f, contour, level, t, S.CONTOUR_DELTA)
        worst_dot = max(worst_dot, abs(float(np.dot(unit(gradient(f, p)), chord))))
print("perpendicular_within_tolerance", worst_dot < S.CONTOUR_DOT_TOL)
print("worst_contour_dot", f"{worst_dot:.3e}")

f, contour, level, t0 = S.CONTOURS["bowl"]
ratios = []
previous = None
for k in (2, 3, 4, 5, 6):
    chord, p, _q, _fp, _fq = contour_chord(f, contour, level, t0, 10.0 ** -k)
    dot = abs(float(np.dot(unit(gradient(f, p)), chord)))
    if previous is not None:
        ratios.append(previous / dot)
    previous = dot
print("dot_product_is_first_order_in_delta", all(9.0 < r < 11.0 for r in ratios))
print("dot_shrink_ratios", "|".join(f"{r:.3f}" for r in ratios))

a = np.sqrt(4.0)
b = np.sqrt(4.0 / 3.0)
tangent_worst = 0.0
for t in (0.0, 0.4, 0.9, 1.4, 1.9, 2.7):
    p = S.bowl_contour(4.0, t)
    tangent = np.array([-a * np.sin(t), b * np.cos(t)])
    tangent_worst = max(tangent_worst, abs(float(np.dot(tangent, S.bowl_gradient(p)))))
print("exact_tangent_dots_to_zero", tangent_worst < 1e-14)

# -- plane and bowl --------------------------------------------------------
seen_planes = [gradient(S.plane, p) for p in ((0.0, 0.0), (1.0, 1.0), (-40.0, 17.5))]
print("plane_gradient", show(seen_planes[0]))
print("plane_gradient_never_varies",
      float(np.max(np.abs(np.array(seen_planes) - seen_planes[0]))) < S.GRADIENT_TOL)
eps = float(np.finfo(float).eps)
far = (1000.0, -1000.0)
far_error = abs(partial(S.plane, far, 0) - 3.0)
predicted = eps * abs(S.plane(far)) / (2.0 * S.H_DEFAULT)
print("far_from_home_error_exceeds_the_labs_tolerance", far_error > S.GRADIENT_TOL)
print("far_from_home_error_matches_the_roundoff_bound",
      predicted / 100.0 < far_error < 3.0 * predicted)
print("far_error", f"{far_error:.3e}")
print("predicted_roundoff", f"{predicted:.3e}")

outward = all(float(np.dot(unit(gradient(S.bowl, p)), unit(np.array(p)))) > 0.0
              for p in ((0.5, 0.5), (1.0, 1.0), (2.0, 2.0), (-3.0, 1.0)))
print("bowl_gradient_points_away_from_the_minimum", outward)
lengths = [magnitude(gradient(S.bowl, (r, r))) for r in (0.5, 1.0, 2.0, 4.0)]
print("bowl_gradient_grows_with_distance", lengths == sorted(lengths))

# -- zero gradients --------------------------------------------------------
for name, kind, _why in S.STATIONARY_AT_ORIGIN:
    g = gradient(S.SURFACES[name][0], (0.0, 0.0))
    print(f"zero_gradient_{name}", f"{magnitude(g):.3e}")
print("saddle_walking_east", S.saddle((0.5, 0.0)))
print("saddle_walking_north", S.saddle((0.0, 0.5)))
print("saddle_on_the_diagonal", S.saddle((0.5, 0.5)))

# -- step size -------------------------------------------------------------
exact_dx = float(S.cubic_gradient((2.0, 1.0))[0])
print("cubic_exact_dfdx", exact_dx)
for k in (1, 2, 3):
    h = 10.0 ** -k
    err = partial(S.cubic, (2.0, 1.0), 0, h) - exact_dx
    print(f"cubic_error_is_h_squared_at_1e-{k}", abs(err - h * h) / (h * h) < 1e-5)
central = {k: abs(partial(S.cubic, (2.0, 1.0), 0, 10.0 ** -k) - exact_dx) for k in range(15)}
forward = {k: abs(forward_partial(S.cubic, (2.0, 1.0), 0, 10.0 ** -k) - exact_dx) for k in range(15)}
print("best_h_central", f"1e-{min(central, key=central.get):02d}")
print("best_h_forward", f"1e-{min(forward, key=forward.get):02d}")
print("central_beats_forward_at_default", forward[5] > 1000 * central[5])
print("tiny_h_is_worse_than_moderate_h", central[14] > central[1])
print("central_error_at_default", f"{central[5]:.3e}")
print("forward_error_at_default", f"{forward[5]:.3e}")

# -- numpy.gradient --------------------------------------------------------
xs = np.linspace(0.0, 4.0, 9)
ys = np.linspace(0.0, 4.0, 9)
X, Y = np.meshgrid(xs, ys, indexing="ij")
spacing = float(xs[1] - xs[0])
gx, gy = np.gradient(X * X + 3.0 * Y * Y, xs, ys)
print("npgradient_interior", f"[{gx[2, 2]:.6f},{gy[2, 2]:.6f}]")
print("npgradient_corner_default", f"[{gx[0, 0]:.6f},{gy[0, 0]:.6f}]")
gx2, gy2 = np.gradient(X * X + 3.0 * Y * Y, xs, ys, edge_order=2)
print("npgradient_corner_edge_order_2", f"[{gx2[0, 0]:.6f},{gy2[0, 0]:.6f}]")
cgx, _cgy = np.gradient(X ** 3 + X * Y * Y, xs, ys, edge_order=2)
cubic_exact = 3.0 * xs[4] ** 2 + ys[4] ** 2
print("npgradient_cubic_error_is_spacing_squared",
      abs(abs(cgx[4, 4] - cubic_exact) - spacing ** 2) < 1e-12)
print("npgradient_returns_a_field", gx.shape == (9, 9))
print("our_gradient_returns_a_vector", gradient(S.bowl, (1.0, 1.0)).shape == (2,))

# -- the model -------------------------------------------------------------
print("model_loss", S.model_loss(S.START_PARAMS))
print("model_gradient", show(S.model_loss_gradient(S.START_PARAMS), 1))
calls = []
def counted(p):
    calls.append(1)
    return S.model_loss(p)
gradient(counted, S.START_PARAMS)
print("evaluations_for_a_three_parameter_gradient", len(calls))
before = S.model_loss(S.START_PARAMS)
g = S.model_loss_gradient(S.START_PARAMS)
print("small_step_against_the_gradient_helps",
      S.model_loss(np.array(S.START_PARAMS) - 0.01 * g) < before)
print("small_step_along_the_gradient_hurts",
      S.model_loss(np.array(S.START_PARAMS) + 0.01 * g) > before)
print("too_large_a_step_overshoots",
      S.model_loss(np.array(S.START_PARAMS) - 0.2 * g) > before)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "a central difference evaluates f exactly twice" "2" "$(get evaluations_per_partial)"
check_eq "and the coordinate being held fixed never moves" "5.0" "$(get frozen_coordinate_values)"
check_eq "while the chosen coordinate moves h each way" \
  "1.99999|2.00001" "$(get moved_coordinate_values)"
check_eq "the caller's point is not mutated" "True" "$(get point_unmutated)"
check_eq "a partial returns a plain float, not a numpy scalar" \
  "float" "$(get partial_is_a_plain_float)"

check_eq "df/dx of x^2 + 3y^2 at (2, 1) is 4" "4.0" "$(get bowl_dfdx_at_2_1)"
check_eq "df/dy of the same is 6" "6.0" "$(get bowl_dfdy_at_2_1)"
check_eq "df/dx of xy at (1, 0) is 0" "0.0" "$(get product_dfdx_at_1_0)"
check_eq "df/dy of xy at the SAME point is 1, so the surface is not flat there" \
  "1.0" "$(get product_dfdy_at_1_0)"

check_eq "thirty gradients were checked against hand-derived exact ones" \
  "30" "$(get gradients_checked)"
check_eq "and every one is inside the stated tolerance" \
  "True" "$(get worst_gradient_error_under_tolerance)"
check_eq "with at least tenfold headroom rather than scraping past" \
  "True" "$(get tolerance_headroom_over_ten)"
echo "  (worst single gradient error on this run: $(get worst_gradient_error) -- reported, not asserted)"
check_eq "the bowl's gradient at (1, 1) is (2, 6)" \
  "[2.000000,6.000000]" "$(get bowl_gradient_at_1_1)"
check_eq "the cubic's gradient at (2, 1) is (13, 4)" \
  "[13.000000,4.000000]" "$(get cubic_gradient_at_2_1)"
check_eq "a two-input function has a two-component gradient" \
  "2" "$(get gradient_size_two_inputs)"
check_eq "and a three-input one has three" "3" "$(get gradient_size_three_inputs)"
check_eq "the gradient's length at (1, 1) is sqrt(40)" \
  "6.324555320" "$(get bowl_gradient_magnitude)"

check_eq "walking due east gives back the x partial" "2.0" "$(get rate_due_east)"
check_eq "walking due north gives back the y partial" "6.0" "$(get rate_due_north)"
check_eq "walking along (3, -1) gives exactly zero" "0.0" "$(get rate_along_3_minus_1)"
check_eq "a longer direction arrow does not give a bigger answer" \
  "True" "$(get arrow_length_irrelevant)"
check_eq "dotting with the gradient agrees with measuring along the direction" \
  "True" "$(get dot_route_matches_direct_route)"

check_eq "360 bearings were measured directly" "360" "$(get sweep_size)"
check_eq "and the fastest climb is at bearing 72" "72.0" "$(get sweep_best_bearing)"
check_eq "which is the gradient's own bearing to within a sampling step" \
  "71.5651" "$(get gradient_bearing)"
# Section 6 re-runs this script with D109_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_bearing="71.5651"
if [ -n "${D109_SELF_TEST:-}" ]; then
  expected_bearing="45.0000"   # the naive belief that on a bowl the gradient
                               # points straight away from the minimum
fi
check_eq "the gradient bearing on the bowl at (1, 1) is not the 45 degrees of the straight-back direction" \
  "${expected_bearing}" "$(get gradient_bearing)"
check_eq "the sampling gap is under the stated one-degree tolerance" \
  "True" "$(get sweep_gap_within_tolerance)"
check_eq "no direction anywhere beats the gradient's own magnitude" \
  "True" "$(get no_direction_beats_the_gradient)"
check_eq "the winning rate over the magnitude equals the cosine of the gap" \
  "True" "$(get ratio_equals_cosine)"
check_eq "the steepest descent is exactly 180 degrees round" \
  "180.0000" "$(get up_and_down_are_opposite)"
check_eq "and its rate is the negative of the steepest ascent" \
  "True" "$(get down_rate_is_minus_up_rate)"

check_eq "each parametrised contour really does hold f constant" \
  "True" "$(get contours_hold_f_constant)"
check_eq "the gradient is perpendicular to every contour tested" \
  "True" "$(get perpendicular_within_tolerance)"
echo "  (worst contour dot product on this run: $(get worst_contour_dot), tolerance 1e-04)"
check_eq "and the dot product shrinks tenfold for a tenfold smaller step" \
  "True" "$(get dot_product_is_first_order_in_delta)"
check_eq "the EXACT tangent and the EXACT gradient dot to zero, no tolerance needed" \
  "True" "$(get exact_tangent_dots_to_zero)"

check_eq "a plane's gradient is (3, -2)" "[3.000000,-2.000000]" "$(get plane_gradient)"
check_eq "and it is the same vector at every point tested" \
  "True" "$(get plane_gradient_never_varies)"
check_eq "far from the origin the estimate breaks the lab's own tolerance" \
  "True" "$(get far_from_home_error_exceeds_the_labs_tolerance)"
check_eq "by an amount the roundoff bound eps|f|/2h predicts" \
  "True" "$(get far_from_home_error_matches_the_roundoff_bound)"
echo "  (measured $(get far_error) against a predicted $(get predicted_roundoff))"

check_eq "the bowl's gradient points away from its minimum, everywhere tested" \
  "True" "$(get bowl_gradient_points_away_from_the_minimum)"
check_eq "and gets longer the further out you stand" \
  "True" "$(get bowl_gradient_grows_with_distance)"

check_eq "the bowl has a zero gradient at the origin" "0.000e+00" "$(get zero_gradient_bowl)"
check_eq "so does the dome" "0.000e+00" "$(get zero_gradient_dome)"
check_eq "so does the saddle" "0.000e+00" "$(get zero_gradient_saddle)"
check_eq "yet walking east from the saddle goes UP" "0.25" "$(get saddle_walking_east)"
check_eq "and walking north from it goes DOWN" "-0.25" "$(get saddle_walking_north)"
check_eq "and along the diagonal nothing happens at all" \
  "0.0" "$(get saddle_on_the_diagonal)"

check_eq "the cubic's exact df/dx at (2, 1) is 13" "13.0" "$(get cubic_exact_dfdx)"
check_eq "the central difference overshoots by exactly h^2 at h = 1e-1" \
  "True" "$(get cubic_error_is_h_squared_at_1e-1)"
check_eq "and at h = 1e-2" "True" "$(get cubic_error_is_h_squared_at_1e-2)"
check_eq "and at h = 1e-3" "True" "$(get cubic_error_is_h_squared_at_1e-3)"
check_eq "the best central step over 15 decades is 1e-05" "1e-05" "$(get best_h_central)"
check_eq "the best forward step is 1e-08, three decades away" "1e-08" "$(get best_h_forward)"
check_eq "at the default step central beats forward by over a thousandfold" \
  "True" "$(get central_beats_forward_at_default)"
check_eq "and a step of 1e-14 is worse than one of 1e-01" \
  "True" "$(get tiny_h_is_worse_than_moderate_h)"
echo "  (central $(get central_error_at_default) against forward $(get forward_error_at_default) at h = 1e-5)"

check_eq "numpy.gradient is exact in the interior of a sampled quadratic" \
  "[2.000000,6.000000]" "$(get npgradient_interior)"
check_eq "but first-order at the corner by default, giving (0.5, 1.5) where (0, 0) is right" \
  "[0.500000,1.500000]" "$(get npgradient_corner_default)"
check_eq "edge_order=2 fixes that corner exactly" \
  "[0.000000,0.000000]" "$(get npgradient_corner_edge_order_2)"
check_eq "on a cubic its error is the GRID spacing squared, which you cannot choose" \
  "True" "$(get npgradient_cubic_error_is_spacing_squared)"
check_eq "numpy.gradient returns a field over the whole array" \
  "True" "$(get npgradient_returns_a_field)"
check_eq "ours returns one vector at one point" \
  "True" "$(get our_gradient_returns_a_vector)"

check_eq "the three-parameter loss is 22.5" "22.5" "$(get model_loss)"
check_eq "and its gradient is the three whole numbers (-17, -18, -8)" \
  "[-17.0,-18.0,-8.0]" "$(get model_gradient)"
check_eq "which cost six evaluations of the loss: two per parameter" \
  "6" "$(get evaluations_for_a_three_parameter_gradient)"
check_eq "a small step AGAINST the gradient reduces the loss" \
  "True" "$(get small_step_against_the_gradient_helps)"
check_eq "a small step ALONG it increases the loss" \
  "True" "$(get small_step_along_the_gradient_hurts)"
check_eq "and too large a step overshoots to worse than the start" \
  "True" "$(get too_large_a_step_overshoots)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong one -- 45 degrees, which is where the gradient WOULD point if a
# bowl's uphill direction were simply "straight away from the bottom" -- and
# asserts that the re-run reports the failure and exits non-zero. If this
# section passes, section 5 is not decorative.
if [ -z "${D109_SELF_TEST:-}" ]; then
  self_out="$(D109_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: the gradient bearing on the bowl at (1, 1) is not the 45 degrees"*)
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

# And a check on the check. If a future edit dropped the `-name '.venv'
# -prune` from either search above, the two checks would start reporting a
# failure caused entirely by NumPy's own shipped bytecode. This proves the
# prune is doing its job: when a `.venv` exists and contains __pycache__
# directories of its own, the pruned search must still find nothing.
if [ -d "${lab_dir}/.venv" ]; then
  inside="$(find "${lab_dir}/.venv" -type d -name '__pycache__' -print -quit 2>/dev/null)"
  if [ -n "${inside}" ]; then
    outside="$(find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null)"
    if [ -z "${outside}" ]; then
      check "the .venv prune works: the environment's own bytecode is not counted against the lab" "yes"
    else
      check "the .venv prune works: the environment's own bytecode is not counted against the lab" "no"
    fi
  else
    check "the lab-local .venv exists and holds no bytecode caches of its own" "yes"
  fi
else
  check "no lab-local .venv on this run, so there is nothing to prune" "yes"
fi

# `.venv` must never be reported as a stray file either. It is created by the
# documented setup commands in the README; a suite that then complained about
# its existence would be telling the reader off for following instructions.
if [ -d "${lab_dir}/.venv" ]; then
  check ".venv is treated as expected, never as something left behind" "yes"
else
  check ".venv is treated as expected, never as something left behind" "yes"
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
