#!/usr/bin/env bash
# Tests for the Day 102 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a matrix's COLUMNS are where the basis vectors land, and the two landings
#     alone determine where every other vector goes;
#   * scaling, reflection, shear and rotation each come out of that one
#     question, and each agrees with NumPy;
#   * a matrix preserves addition and scalar multiplication, and "matrix plus a
#     constant" fails BOTH -- by exactly the constant, and by exactly (s - 1)
#     times the constant, which is asserted rather than described;
#   * a quarter turn's cosine is 6.123233995736766e-17 and not 0.0, so every
#     float check here states a tolerance and the harness asserts the
#     inexactness itself;
#   * composing two transformations is one matrix product, BA means A first,
#     and AB is a different transformation;
#   * the determinant IS the signed area of the transformed unit square --
#     positive, negative and zero cases all measured;
#   * a singular matrix's inverse raises numpy.linalg.LinAlgError with the
#     message "Singular matrix", and the exact class is asserted;
#   * twenty stacked linear layers collapse to one 2 by 2 matrix;
#   * nothing is left behind on disk.
#
# Everything runs offline. Nothing binds a port, nothing writes outside the
# lab, nothing needs a key. Deterministic, non-interactive, exits 0 only if
# every check passes.
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

echo "Day 102 — Where Do the Basis Vectors Land?"
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

for script in 01_columns_are_landings 02_building_the_transformations \
              03_linear_or_not 04_composition_and_order \
              05_determinant_inverse_rank 06_the_limit_of_linear; do
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
if [ "${ref_passed:-0}" -ge 75 ]; then
  check "the reference suite ran at least 75 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 75 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `transforms` and
# `shapes`, and pytest imports test files by putting their directory on
# sys.path — so collecting both suites at once would otherwise let the starter
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
import random

import numpy as np

import shapes
from transforms import (
    apply,
    columns_of,
    compose,
    determinant,
    inverse,
    is_linear,
    preserves_addition,
    preserves_scaling,
    rank,
    reflection_in_x_axis,
    rotation,
    scaling,
    shear_x,
    signed_area,
    transform_polygon,
    SingularMatrix,
)

TOL = shapes.TOL

M = shapes.PICTURE_MATRIX
print("columns", columns_of(M))
print("row0_is_not_a_landing", tuple(M[0]) != columns_of(M)[0])
print("sends_2_1", apply(M, (2.0, 1.0)))
print("det_picture_scratch", determinant(M))
print("det_picture_numpy_exact", float(np.linalg.det(np.array(M))) == 7.0)
print("det_picture_numpy_close", abs(float(np.linalg.det(np.array(M))) - 7.0) < 1e-14)

print("scale", scaling(2.0, 3.0))
print("flip", reflection_in_x_axis())
print("shear", shear_x(2.0))
print("shear_on_axis", apply(shear_x(2.0), (5.0, 0.0)))

Q = rotation(math.pi / 2)
print("cos_quarter_exact_zero", math.cos(math.pi / 2) == 0.0)
print("quarter_within_tol", all(
    abs(a - b) <= TOL for a, b in zip(apply(Q, shapes.E1), (0.0, 1.0))
))
print("sin_thirty_exact_half", math.sin(math.radians(30)) == 0.5)

S = shapes.SCALE_MATRIX
b = (1.0, 1.0)
u, v, s = (1.0, 2.0), (3.0, -1.0), 5.0
linear = lambda p: apply(S, p)
affine = lambda p: tuple(c + o for c, o in zip(apply(S, p), b))
print("linear_is_linear", is_linear(linear, u, v, s, TOL))
print("affine_is_linear", is_linear(affine, u, v, s, TOL))
ok, together, separately = preserves_addition(affine, u, v, TOL)
print("affine_add_gap", tuple(round(x - y, 12) for x, y in zip(separately, together)))
ok, first, after = preserves_scaling(affine, u, s, TOL)
print("affine_scale_gap", tuple(round(x - y, 12) for x, y in zip(after, first)))
print("linear_fixes_origin", linear((0.0, 0.0)) == (0.0, 0.0))
print("affine_moves_origin", affine((0.0, 0.0)) == b)

A, B = shear_x(2.0), Q
BA, AB = compose(B, A), compose(A, B)
print("BA_matches_hand", all(
    abs(x - y) <= TOL
    for r1, r2 in zip(BA, shapes.SHEAR_THEN_ROTATE) for x, y in zip(r1, r2)
))
print("AB_matches_hand", all(
    abs(x - y) <= TOL
    for r1, r2 in zip(AB, shapes.ROTATE_THEN_SHEAR) for x, y in zip(r1, r2)
))
print("orders_differ", any(
    abs(x - y) > TOL for r1, r2 in zip(BA, AB) for x, y in zip(r1, r2)
))
two_steps = transform_polygon(B, transform_polygon(A, shapes.FLAG))
at_once = transform_polygon(BA, shapes.FLAG)
print("one_matrix_equals_two_steps", all(
    abs(x - y) <= TOL for p, q in zip(two_steps, at_once) for x, y in zip(p, q)
))

for name, matrix, expected in (
    ("area_scale", scaling(2.0, 3.0), 6.0),
    ("area_shear", shear_x(2.0), 1.0),
    ("area_flip", reflection_in_x_axis(), -1.0),
    ("area_collapse", shapes.COLLAPSE_MATRIX, 0.0),
):
    area = signed_area(transform_polygon(matrix, shapes.UNIT_SQUARE))
    print(name, round(area, 12), round(determinant(matrix), 12), expected)

G = shapes.COLLAPSE_MATRIX
print("collapse_on_one_line", all(
    abs(apply(G, p)[1] - 2.0 * apply(G, p)[0]) <= TOL
    for p in [(1.0, 0.0), (0.0, 1.0), (3.0, -1.0)]
))
print("collapse_two_points_one_landing", apply(G, (2.0, 0.0)) == apply(G, (0.0, 1.0)))
print("rank_collapse", rank(G), int(np.linalg.matrix_rank(np.array(G))))
print("rank_zero_matrix", rank([[0.0, 0.0], [0.0, 0.0]]))

print("inverse_of_shear", inverse(shear_x(2.0)) == shear_x(-2.0))
try:
    inverse(G)
except SingularMatrix:
    print("scratch_inverse_refuses", "SingularMatrix")
else:
    print("scratch_inverse_refuses", "NOTHING_RAISED")
try:
    np.linalg.inv(np.array(G))
except Exception as exc:  # deliberately broad: the TYPE is what is asserted
    print("numpy_inverse_refuses", type(exc).__name__, str(exc))
else:
    print("numpy_inverse_refuses", "NOTHING_RAISED", "")
print("linalgerror_is_valueerror", issubclass(np.linalg.LinAlgError, ValueError))

random.seed(102)
stack = [
    [[random.uniform(-2, 2) for _ in range(2)] for _ in range(2)] for _ in range(20)
]
point = (0.7, -0.4)
stepwise = point
for layer in stack:
    stepwise = apply(layer, stepwise)
combined = stack[0]
for layer in stack[1:]:
    combined = compose(layer, combined)
at_once_pt = apply(combined, point)
print("stack_collapses", all(
    abs(a - c) <= 1e-9 * max(1.0, abs(a)) for a, c in zip(stepwise, at_once_pt)
))
print("stack_still_fixes_origin", all(
    abs(c) <= TOL for c in apply(combined, (0.0, 0.0))
))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the columns are the two landing places" \
  "((3.0, 1.0), (-1.0, 2.0))" "$(get columns)"
check_eq "row 0 is NOT a landing place" "True" "$(get row0_is_not_a_landing)"
check_eq "the matrix sends (2, 1) to the hand-worked (5, 4)" \
  "(5.0, 4.0)" "$(get sends_2_1)"
check_eq "the from-scratch determinant of the picture matrix is exactly 7" \
  "7.0" "$(get det_picture_scratch)"
check_eq "numpy.linalg.det is NOT exactly 7 on the same matrix" \
  "False" "$(get det_picture_numpy_exact)"
check_eq "numpy.linalg.det is within 1e-14 of 7" \
  "True" "$(get det_picture_numpy_close)"

check_eq "scaling(2, 3) is derived correctly" \
  "[[2.0, 0.0], [0.0, 3.0]]" "$(get scale)"
check_eq "reflection in the x axis is derived correctly" \
  "[[1.0, 0.0], [0.0, -1.0]]" "$(get flip)"
check_eq "shear_x(2) is derived correctly" \
  "[[1.0, 2.0], [0.0, 1.0]]" "$(get shear)"
check_eq "a shear leaves a point at height 0 exactly where it was" \
  "(5.0, 0.0)" "$(get shear_on_axis)"

# Section 6 re-runs this script with D102_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_cos_exact="False"
if [ -n "${D102_SELF_TEST:-}" ]; then
  expected_cos_exact="True"   # the naive belief, deliberately wrong here
fi
check_eq "cos(pi / 2) is not exactly 0.0, which is why a tolerance is required" \
  "${expected_cos_exact}" "$(get cos_quarter_exact_zero)"
check_eq "the quarter turn still lands on (0, 1) within the stated tolerance" \
  "True" "$(get quarter_within_tol)"
check_eq "sin(30 degrees) is not exactly 0.5 either" \
  "False" "$(get sin_thirty_exact_half)"

check_eq "a matrix is linear on the tested pair" "True" "$(get linear_is_linear)"
check_eq "matrix-plus-a-constant is not linear" "False" "$(get affine_is_linear)"
check_eq "the addition failure is exactly b" "(1.0, 1.0)" "$(get affine_add_gap)"
check_eq "the scaling failure is exactly (s - 1) times b" \
  "(4.0, 4.0)" "$(get affine_scale_gap)"
check_eq "a linear map fixes the origin" "True" "$(get linear_fixes_origin)"
check_eq "an affine map moves it" "True" "$(get affine_moves_origin)"

check_eq "compose(B, A) matches the hand-worked shear-then-rotate" \
  "True" "$(get BA_matches_hand)"
check_eq "compose(A, B) matches the hand-worked rotate-then-shear" \
  "True" "$(get AB_matches_hand)"
check_eq "the two orders are different transformations" "True" "$(get orders_differ)"
check_eq "one composed matrix reproduces the two-step sequence on every corner" \
  "True" "$(get one_matrix_equals_two_steps)"

check_eq "scaling(2, 3) multiplies the unit square's area by 6" \
  "6.0 6.0 6.0" "$(get area_scale)"
check_eq "a shear preserves area exactly" "1.0 1.0 1.0" "$(get area_shear)"
check_eq "a reflection gives a NEGATIVE area of the same size" \
  "-1.0 -1.0 -1.0" "$(get area_flip)"
check_eq "a collapse gives area 0" "0.0 0.0 0.0" "$(get area_collapse)"

check_eq "the collapse puts every vector on the line y = 2x" \
  "True" "$(get collapse_on_one_line)"
check_eq "two different points land on the same place, so nothing can undo it" \
  "True" "$(get collapse_two_points_one_landing)"
check_eq "the collapse has rank 1, and numpy agrees" "1 1" "$(get rank_collapse)"
check_eq "the all-zero matrix has rank 0" "0" "$(get rank_zero_matrix)"

check_eq "the inverse of shear_x(2) is shear_x(-2)" "True" "$(get inverse_of_shear)"
check_eq "the from-scratch inverse refuses a singular matrix" \
  "SingularMatrix" "$(get scratch_inverse_refuses)"
check_eq "numpy.linalg.inv raises LinAlgError with the message 'Singular matrix'" \
  "LinAlgError Singular matrix" "$(get numpy_inverse_refuses)"
check_eq "numpy.linalg.LinAlgError is catchable as a ValueError" \
  "True" "$(get linalgerror_is_valueerror)"

check_eq "twenty stacked linear layers collapse to one 2 by 2 matrix" \
  "True" "$(get stack_collapses)"
check_eq "and the stack still cannot move the origin" \
  "True" "$(get stack_still_fixes_origin)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for the naive belief that cos(pi / 2) is exactly 0.0, and asserts that the
# re-run reports the failure and exits non-zero. If this section passes,
# section 5 is not decorative.
if [ -z "${D102_SELF_TEST:-}" ]; then
  self_out="$(D102_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: cos(pi / 2) is not exactly 0.0"*)
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

# `.venv` is pruned from the searches below. A virtual environment ships the
# installed packages' own precompiled bytecode -- hundreds of __pycache__
# directories that came with NumPy or pytest and have nothing to do with
# whether THIS lab tidied up after itself. Without the prune, following the
# README's own setup instructions makes this check fail, which reports a
# problem the reader cannot fix and did not cause.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory anywhere under the lab after a full run" "no"
else
  check "no __pycache__ directory anywhere under the lab after a full run" "yes"
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
