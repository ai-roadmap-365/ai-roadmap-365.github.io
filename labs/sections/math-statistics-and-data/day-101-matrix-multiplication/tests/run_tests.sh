#!/usr/bin/env bash
# Tests for the Day 101 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * three from-scratch implementations of matrix multiplication — nested
#     loops, a list of dot products, and a weighted sum of columns — agree with
#     each other and with NumPy's @ on six different shapes;
#   * one output cell equals the row-times-column arithmetic a human did by
#     hand, digit for digit;
#   * A @ B and B @ A are both defined, both computed in full, and different;
#   * `*` and `@` on the same operands give different values at the same shape,
#     and different SHAPES on a matrix and a vector;
#   * a deliberate shape error raises ValueError, and each of the two transpose
#     repairs gives a different shape and a different answer;
#   * one network layer, X @ W + b, matches the hand-computed output, and a
#     wrong-length bias raises;
#   * the loop loses to NumPy by a wide margin — a margin, never a duration;
#   * nothing is left behind on disk.
#
# Everything except the one-time install runs offline. Nothing binds a port,
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

echo "Day 101 — Multiply It Yourself"
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

for script in 01_matmul_from_scratch 02_composition 03_star_versus_at \
              04_network_layer 05_cost_and_speed; do
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
echo "3. The reference pytest suite: real values, real shapes"
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
if [ "${ref_passed:-0}" -ge 60 ]; then
  check "the reference suite ran at least 60 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 60 tests (ran ${ref_passed:-0})" "no"
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

# The import guard, and the reason it exists. Both directories contain a module
# called `matmul`, and pytest imports test files by putting their directory on
# sys.path — so collecting both suites at once would otherwise let the starter
# tests import the REFERENCE solution and report unwritten exercises as
# passing. That is exactly what happened while building the Day 100 lab: eleven
# unwritten exercises passed against the reference, and it was caught only
# because the skip count changed. Each directory's conftest.py prevents it.
# This check proves it still does: across both suites the skip count must be
# unchanged.
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
import time

import numpy as np

from dataset import BIAS, FLIP_X, P, Q, ROT90, U, V, W, X
from matmul import (
    ShapeMismatch,
    add_bias,
    chain_costs,
    dot,
    identity,
    matmul_columns,
    matmul_dots,
    matmul_loops,
    matvec,
    multiplication_count,
)

npX, npW, npB = np.array(X), np.array(W), np.array(BIAS)
npP, npQ = np.array(P), np.array(Q)
npA, npF = np.array(ROT90), np.array(FLIP_X)

print("dot_pairwise", dot([3, 4], [4, 3]))
print("dot_self_is_squared_length", dot([3, 4], [3, 4]), round(float(np.linalg.norm([3, 4])) ** 2))
print("dot_perpendicular", dot([3, 4], [-4, 3]))

print("three_implementations",
      matmul_loops(X, W), matmul_dots(X, W), matmul_columns(X, W), (npX @ npW).tolist())
print("highlighted_cell", matmul_loops(X, W)[1][1], 0 * 0 + 1 * 1 + 3 * 4)
print("matvec_is_column_combination", matvec([[2, 0], [-1, 1], [0, 4]], [3, 5]))
print("columns_are_basis_images", matvec(ROT90, [1, 0]), matvec(ROT90, [0, 1]))

print("result_shape", (npX @ npW).shape)
try:
    npX @ npX
except ValueError as exc:
    print("shape_error", type(exc).__name__, "size 2 is different from 3" in str(exc))
else:
    print("shape_error", "NOTHING_RAISED", False)
try:
    matmul_loops(X, X)
except ShapeMismatch as exc:
    print("scratch_shape_error", "ShapeMismatch", "inner dimensions 3 and 2" in str(exc))
else:
    print("scratch_shape_error", "NOTHING_RAISED", False)
print("transpose_repairs", (npX @ npX.T).shape, (npX.T @ npX).shape,
      (npX @ npX.T).tolist(), (npX.T @ npX).tolist())

print("not_commutative", (npA @ npF).tolist(), (npF @ npA).tolist())
print("not_commutative_untidy", (npP @ npQ).tolist(), (npQ @ npP).tolist())
print("composition_two_steps", matvec(ROT90, matvec(FLIP_X, V)))
print("composition_one_step", matvec(matmul_loops(ROT90, FLIP_X), V))
C = [[1, 1], [0, 2]]
print("associative", matmul_loops(matmul_loops(ROT90, FLIP_X), C) ==
      matmul_loops(ROT90, matmul_loops(FLIP_X, C)))

print("star_vs_at_same_shape", (npP * npQ).tolist(), (npP @ npQ).tolist())
print("star_vs_at_elementwise_zeros", (npA * npF).tolist(), (npA @ npF).tolist())
print("star_shape", (npX * np.array(U)).shape, "at_shape", (npX @ np.array(U)).shape)
print("star_values", (npX * np.array(U)).tolist(), "at_values", (npX @ np.array(U)).tolist())
print("at_is_star_then_sum", np.array_equal((npX * np.array(U)).sum(axis=1), npX @ np.array(U)))

print("identity_noop", matmul_loops(identity(2), X) == X, matmul_loops(X, identity(3)) == X)

print("layer_out", (npX @ npW + npB).tolist())
print("layer_out_scratch", add_bias(matmul_loops(X, W), BIAS))
try:
    (npX @ npW) + np.array([5, -2, 7])
except ValueError as exc:
    print("bad_bias", type(exc).__name__, "could not be broadcast" in str(exc))
else:
    print("bad_bias", "NOTHING_RAISED", False)

W2 = np.array([[1, 0, 2], [3, 1, 0]])
b2 = np.array([0, 1, -1])
print("layers_collapse", bool(np.array_equal(
    (npX @ npW + npB) @ W2 + b2, npX @ (npW @ W2) + (npB @ W2 + b2))))

print("count_small", multiplication_count(2, 3, 2))
print("count_200", multiplication_count(200, 200, 200))
print("chain_small", chain_costs(10, 100, 5, 50))
print("chain_big", chain_costs(1024, 4096, 8, 4096))
print("chain_big_ratio", 17314086912 // 67108864)

# The timing. A RATIO is asserted, never a duration. The threshold is far
# below what this machine measured, so a slow or busy machine still passes.
size = 120
rng = np.random.default_rng(2026)
left = rng.integers(0, 10, size=(size, size)).astype(np.float64)
right = rng.integers(0, 10, size=(size, size)).astype(np.float64)
start = time.perf_counter()
loop_answer = matmul_loops(left.tolist(), right.tolist())
loop_seconds = time.perf_counter() - start
best = float("inf")
for _ in range(5):
    start = time.perf_counter()
    numpy_answer = left @ right
    best = min(best, time.perf_counter() - start)
print("timing_answers_agree", bool(np.allclose(np.array(loop_answer), numpy_answer, atol=1e-9)))
print("timing_ratio_over_50", bool(loop_seconds / best > 50))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the dot product multiplies pairwise and adds" "24" "$(get dot_pairwise)"
check_eq "a vector dotted with itself is its squared length" "25 25" \
  "$(get dot_self_is_squared_length)"
check_eq "perpendicular vectors have a dot product of zero" "0" "$(get dot_perpendicular)"
check_eq "loops, dot products, columns and NumPy all agree" \
  "[[0, 2], [-1, 13]] [[0, 2], [-1, 13]] [[0, 2], [-1, 13]] [[0, 2], [-1, 13]]" \
  "$(get three_implementations)"
check_eq "the highlighted cell equals the hand arithmetic 0*0 + 1*1 + 3*4" "13 13" \
  "$(get highlighted_cell)"
check_eq "matrix times vector is a weighted sum of the columns" "[6, 2, 20]" \
  "$(get matvec_is_column_combination)"
check_eq "the columns of a matrix are where the basis vectors land" "[0, 1] [-1, 0]" \
  "$(get columns_are_basis_images)"
check_eq "(2, 3) @ (3, 2) gives (2, 2)" "(2, 2)" "$(get result_shape)"
check_eq "(2, 3) @ (2, 3) raises ValueError naming the mismatch" "ValueError True" \
  "$(get shape_error)"
check_eq "the from-scratch version raises ShapeMismatch naming both inner dimensions" \
  "ShapeMismatch True" "$(get scratch_shape_error)"
check_eq "the two transpose repairs give different shapes and different answers" \
  "(2, 2) (3, 3) [[5, 2], [2, 10]] [[1, 2, 0], [2, 5, 3], [0, 3, 9]]" \
  "$(get transpose_repairs)"
check_eq "A @ B and B @ A are both defined and genuinely different" \
  "[[0, 1], [1, 0]] [[0, -1], [-1, 0]]" "$(get not_commutative)"
check_eq "the same holds on a second, untidier pair" \
  "[[19, 22], [43, 50]] [[23, 34], [31, 46]]" "$(get not_commutative_untidy)"
check_eq "flip then rotate, one step at a time, lands at [1, 3]" "[1, 3]" \
  "$(get composition_two_steps)"
check_eq "the single product matrix lands at the same point" "[1, 3]" \
  "$(get composition_one_step)"
check_eq "multiplication is associative" "True" "$(get associative)"
check_eq "* and @ give different values at the SAME shape" \
  "[[5, 12], [21, 32]] [[19, 22], [43, 50]]" "$(get star_vs_at_same_shape)"
check_eq "the elementwise product of the two transformations is all zeros" \
  "[[0, 0], [0, 0]] [[0, 1], [1, 0]]" "$(get star_vs_at_elementwise_zeros)"
check_eq "* and @ give different SHAPES on a matrix and a vector" \
  "(2, 3) at_shape (2,)" "$(get star_shape)"
check_eq "* and @ give different values there too, not only different shapes" \
  "[[10, 4, 0], [0, 2, 15]] at_values [14, 17]" "$(get star_values)"
check_eq "@ is * followed by a sum along the last axis" "True" "$(get at_is_star_then_sum)"
check_eq "the identity matrix leaves a matrix alone from either side" "True True" \
  "$(get identity_noop)"
# Section 6 re-runs this script with D101_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_layer="[[5, 0], [4, 11]]"
if [ -n "${D101_SELF_TEST:-}" ]; then
  expected_layer="[[5, 0], [4, 10]]"   # off by one in the last cell, deliberately
fi
check_eq "one network layer, X @ W + b, matches the hand-computed output" \
  "${expected_layer}" "$(get layer_out)"
check_eq "the from-scratch layer matches it too" "[[5, 0], [4, 11]]" \
  "$(get layer_out_scratch)"
check_eq "a bias of the wrong length raises ValueError" "ValueError True" "$(get bad_bias)"
check_eq "two layers with no activation between them collapse into one" "True" \
  "$(get layers_collapse)"
check_eq "an (m, n) @ (n, p) costs m*n*p multiplications" "12" "$(get count_small)"
check_eq "two 200 by 200 matrices cost eight million" "8000000" "$(get count_200)"
check_eq "the small chain costs 7500 one way and 75000 the other" "(7500, 75000)" \
  "$(get chain_small)"
check_eq "the adapter chain costs 67108864 one way and 17314086912 the other" \
  "(67108864, 17314086912)" "$(get chain_big)"
check_eq "which is a factor of 258" "258" "$(get chain_big_ratio)"
check_eq "the loop and NumPy return the same answer" "True" "$(get timing_answers_agree)"
check_eq "NumPy beats the loop by a wide margin (a ratio, never a duration)" "True" \
  "$(get timing_ratio_over_50)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong layer output, and asserts that the re-run reports the failure and
# exits non-zero. If this section passes, section 5 is not decorative.
if [ -z "${D101_SELF_TEST:-}" ]; then
  self_out="$(D101_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: one network layer, X @ W + b"*)
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
