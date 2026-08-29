#!/usr/bin/env bash
# Tests for the Day 104 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a list of a million integers costs 36,000,056 bytes and the equivalent
#     int64 array costs 8,000,000 -- and sys.getsizeof on its own says they are
#     the same size, which is why the lab does not use it as the measurement;
#   * an int8 wraps from 127 to -128 with no exception and no warning, and the
#     absence of the warning is asserted rather than assumed;
#   * three operations written as a loop and as a NumPy expression agree over a
#     million elements with ==, not with a tolerance;
#   * the vectorised versions are at least 20 times faster -- the SHAPE of the
#     gap, never a millisecond figure, because a timing assertion is flaky on
#     someone else's machine;
#   * `and` on two arrays raises ValueError with the ambiguous-truth-value
#     message, and `&` does the thing that was meant;
#   * argsort returns [3, 2, 0] for Day 103's query, which is
#     race-day-nutrition, marathon-plan, roast-chicken;
#   * a slice is a view, so writing through it writes through to the original,
#     and .copy() breaks the link;
#   * np.nan != np.nan, np.isnan finds it, and np.nanmean gives 7/3;
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

echo "Day 104 — Stop Writing the Loop"
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

for script in 01_list_versus_array 02_dtypes_and_overflow 03_same_answer_faster \
              04_creating_and_ufuncs 05_masks_and_selection \
              06_axes_views_and_ranking 07_nan_and_when_not_to_vectorise; do
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
if [ "${ref_passed:-0}" -ge 100 ]; then
  check "the reference suite ran at least 100 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 100 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `vectorize` and
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
import sys
import warnings

import numpy as np

import dataset
from vectorize import (
    array_bytes,
    clip_loop,
    clip_vec,
    cosine_similarities,
    count_above,
    list_bytes,
    mask_between,
    nan_aware_mean,
    roots_loop,
    roots_vec,
    scale_and_offset_loop,
    scale_and_offset_vec,
    select,
    speedup,
    time_call,
    top_k_indices,
    wrap_int8,
)

# -- memory ---------------------------------------------------------------
values = list(range(dataset.N_BIG))
array = np.arange(dataset.N_BIG, dtype=np.int64)
print("naive_ratio_is_about_one", round(sys.getsizeof(values) / array.nbytes, 2))
print("honest_list_bytes", list_bytes(values))
print("array_bytes", array_bytes(array))
print("honest_ratio", round(list_bytes(values) / array_bytes(array), 2))
print("python_int_bytes", sys.getsizeof(1_000_000))
print("int64_element_bytes", array.itemsize)
del values

grid = np.arange(12).reshape(3, 4)
print("strides", grid.strides)
print("transpose_is_a_view", bool(np.shares_memory(grid, grid.T)))

# -- dtypes ---------------------------------------------------------------
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    wrapped = wrap_int8(127, 1)
    names = [w.category.__name__ for w in caught]
print("int8_wrap", wrapped)
print("int8_wrap_warnings", ",".join(names) if names else "none")
print("int8_doubled", (np.array(dataset.INT8_DOUBLING_INPUT, dtype=np.int8) * np.int8(2)).tolist())
print("int8_plus_python_int", (np.array([127], dtype=np.int8) + 1).tolist(),
      (np.array([127], dtype=np.int8) + 1).dtype)
print("astype_int16", (np.array([127], dtype=np.int8).astype(np.int16) + 1).tolist())
blind = np.float32(dataset.FLOAT32_BLIND_SPOT)
print("float32_blind", bool(blind + np.float32(1.0) == blind))
print("float64_not_blind", float(np.float64(dataset.FLOAT32_BLIND_SPOT) + 1.0))

# -- the three operations, twice each --------------------------------------
big = dataset.big_values()
as_list = big.tolist()
print("scale_exact", bool(np.array_equal(
    np.array(scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C)),
    scale_and_offset_vec(big, dataset.SCALE_M, dataset.SCALE_C))))
print("roots_exact", bool(np.array_equal(
    np.array(roots_loop(as_list)), roots_vec(big))))
print("clip_exact", bool(np.array_equal(
    np.array(clip_loop(as_list, dataset.CLIP_LO, dataset.CLIP_HI)),
    clip_vec(big, dataset.CLIP_LO, dataset.CLIP_HI))))
factor = speedup(
    time_call(lambda: scale_and_offset_loop(as_list, dataset.SCALE_M, dataset.SCALE_C), 3),
    time_call(lambda: scale_and_offset_vec(big, dataset.SCALE_M, dataset.SCALE_C), 3),
)
print("speedup_over_20", factor > 20.0)
print("speedup_measured", round(factor, 1))
pow_differs = int(np.count_nonzero(np.array([x ** 0.5 for x in as_list]) != roots_vec(big)))
math_differs = int(np.count_nonzero(np.array([math.sqrt(x) for x in as_list]) != roots_vec(big)))
print("pow_disagrees", pow_differs > 0)
print("math_agrees", math_differs == 0)

# -- masking ---------------------------------------------------------------
readings = dataset.small_readings()
print("readings_match_documented", readings.tolist() == dataset.SMALL_READINGS_EXPECTED)
print("count_above_50", count_above(readings, 50))
print("values_above_50", select(readings, readings > 50).tolist())
print("mask_dtype", (readings > 50).dtype)
print("between_count", int(mask_between(readings, 30, 70).sum()))
print("between_values", readings[mask_between(readings, 30, 70)].tolist())
print("mask_mean", float((readings > 50).mean()))
print("fancy", readings[np.array([0, 5, 19, 5])].tolist())
try:
    (readings > 30) and (readings < 70)
except Exception as exc:  # deliberately broad: the TYPE is what is asserted
    print("keyword_and_raises", type(exc).__name__)
else:
    print("keyword_and_raises", "NOTHING_RAISED")
try:
    readings > 30 & readings < 70
except Exception as exc:  # deliberately broad: the TYPE is what is asserted
    print("missing_brackets_raise", type(exc).__name__)
else:
    print("missing_brackets_raise", "NOTHING_RAISED")

# -- axes, views, ranking ---------------------------------------------------
print("sum_axis0_shape", grid.sum(axis=0).shape)
print("sum_axis1_shape", grid.sum(axis=1).shape)
print("sum_axis1_values", grid.sum(axis=1).tolist())
v = np.array([1.0, 2.0, 3.0])
print("newaxis_column_shape", v[:, np.newaxis].shape)
fresh = np.arange(12).reshape(3, 4)
row = fresh[1]
row[0] = 999
print("view_wrote_through", int(fresh[1, 0]))
fresh2 = np.arange(12).reshape(3, 4)
copied = fresh2[2].copy()
copied[0] = -1
print("copy_did_not", int(fresh2[2, 0]))
print("mask_is_a_copy", bool(np.shares_memory(fresh2, fresh2[fresh2 > 5])))
print("ravel_is_a_view", bool(np.shares_memory(fresh2, fresh2.ravel())))
print("flatten_is_a_copy", bool(np.shares_memory(fresh2, fresh2.flatten())))
scores = np.array([5.0, 1.0, 9.0, 3.0])
print("argsort", np.argsort(scores).tolist())
sims = cosine_similarities(dataset.CATALOGUE, dataset.QUERY)
print("sims_shape", sims.shape)
top = top_k_indices(sims, dataset.TOP_K)
print("top3_indices", top.tolist())
print("top3_names", "|".join(dataset.ARTICLE_NAMES[i] for i in top))
print("margin_is_small", 0.0 < float(sims[top[0]] - sims[top[1]]) < 0.01)

# -- nan --------------------------------------------------------------------
holed = dataset.WITH_A_HOLE
print("nan_ne_nan", np.nan != np.nan)
print("eq_nan_finds_nothing", int((holed == np.nan).sum()))
print("isnan_finds_it", int(np.isnan(holed).sum()))
print("mean_is_nan", math.isnan(float(holed.mean())))
print("nanmean", nan_aware_mean(holed))
print("nansum", float(np.nansum(holed)))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "sys.getsizeof alone makes the list look the same size as the array" \
  "1.0" "$(get naive_ratio_is_about_one)"
check_eq "the honest list total is 36,000,056 bytes" \
  "36000056" "$(get honest_list_bytes)"
check_eq "the equivalent int64 array is 8,000,000 bytes" \
  "8000000" "$(get array_bytes)"
check_eq "so the array is 4.5 times smaller" "4.5" "$(get honest_ratio)"
check_eq "one Python int is 28 bytes here" "28" "$(get python_int_bytes)"
check_eq "one int64 array element is 8 bytes" "8" "$(get int64_element_bytes)"
check_eq "a 3 by 4 int64 array has strides (32, 8)" "(32, 8)" "$(get strides)"
check_eq "a transpose copies nothing" "True" "$(get transpose_is_a_view)"

check_eq "int8 127 + 1 wraps to -128" "-128" "$(get int8_wrap)"
check_eq "and does so with no warning at all on this numpy" \
  "none" "$(get int8_wrap_warnings)"
check_eq "doubling [120, 125, 127] as int8 wraps two of the three" \
  "[-16, -6, -2]" "$(get int8_doubled)"
check_eq "a plain Python 1 does not widen the array" \
  "[-128] int8" "$(get int8_plus_python_int)"
check_eq "asking for int16 first gives the right answer" \
  "[128]" "$(get astype_int16)"
check_eq "float32 cannot tell 16777216 from 16777217" "True" "$(get float32_blind)"
check_eq "float64 can" "16777217.0" "$(get float64_not_blind)"

check_eq "loop and vectorised scale-and-offset agree EXACTLY on a million values" \
  "True" "$(get scale_exact)"
check_eq "loop and vectorised square roots agree EXACTLY" "True" "$(get roots_exact)"
check_eq "loop and vectorised clip agree EXACTLY" "True" "$(get clip_exact)"
check_eq "the vectorised version is at least 20 times faster" \
  "True" "$(get speedup_over_20)"
check_eq "x ** 0.5 is NOT the same operation as np.sqrt" "True" "$(get pow_disagrees)"
check_eq "math.sqrt IS the same operation as np.sqrt" "True" "$(get math_agrees)"
echo "  (measured speedup on this run: $(get speedup_measured)x -- reported, not asserted)"

check_eq "the seeded readings are the twenty documented values" \
  "True" "$(get readings_match_documented)"
check_eq "nine readings are above 50" "9" "$(get count_above_50)"
check_eq "and they are the nine documented values" \
  "[70, 83, 69, 65, 75, 73, 97, 64, 82]" "$(get values_above_50)"
check_eq "a comparison produces a boolean array" "bool" "$(get mask_dtype)"
check_eq "seven readings are strictly between 30 and 70" "7" "$(get between_count)"
check_eq "and they are the seven documented values" \
  "[34, 69, 65, 37, 37, 41, 64]" "$(get between_values)"
check_eq "the mask's mean is the fraction above 50" "0.45" "$(get mask_mean)"
check_eq "fancy indexing keeps the order asked for and allows a repeat" \
  "[70, 21, 82, 21]" "$(get fancy)"
check_eq "the keyword 'and' raises ValueError on two arrays" \
  "ValueError" "$(get keyword_and_raises)"
check_eq "and so does the same expression with the brackets left off" \
  "ValueError" "$(get missing_brackets_raise)"

check_eq "summing a (3, 4) along axis 0 leaves shape (4,)" \
  "(4,)" "$(get sum_axis0_shape)"
check_eq "summing it along axis 1 leaves shape (3,)" "(3,)" "$(get sum_axis1_shape)"
check_eq "and the three row totals are 6, 22, 38" "[6, 22, 38]" "$(get sum_axis1_values)"
check_eq "np.newaxis turns a length-3 row into a 3 by 1 column" \
  "(3, 1)" "$(get newaxis_column_shape)"
check_eq "writing through a row slice writes through to the original" \
  "999" "$(get view_wrote_through)"
check_eq "writing through a .copy() does not" "8" "$(get copy_did_not)"
check_eq "a boolean mask returns a copy, never a view" "False" "$(get mask_is_a_copy)"
check_eq "ravel returns a view when it can" "True" "$(get ravel_is_a_view)"
check_eq "flatten always returns a copy" "False" "$(get flatten_is_a_copy)"
check_eq "argsort returns positions, not values" "[1, 3, 0, 2]" "$(get argsort)"
check_eq "one cosine similarity per catalogue row" "(6,)" "$(get sims_shape)"
check_eq "the top 3 by argsort are indices 3, 2 and 0" "[3, 2, 0]" "$(get top3_indices)"
check_eq "which are the three documented articles, best first" \
  "race-day-nutrition|marathon-plan|roast-chicken" "$(get top3_names)"
check_eq "the winner's margin is small enough to report rather than trumpet" \
  "True" "$(get margin_is_small)"

check_eq "nan is not equal to itself" "True" "$(get nan_ne_nan)"
check_eq "comparing an array to nan finds nothing at all" \
  "0" "$(get eq_nan_finds_nothing)"
check_eq "np.isnan finds the one that is missing" "1" "$(get isnan_finds_it)"
check_eq "the plain mean is nan, loudly" "True" "$(get mean_is_nan)"
# Section 6 re-runs this script with D104_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_nanmean="2.3333333333333335"
if [ -n "${D104_SELF_TEST:-}" ]; then
  expected_nanmean="2.5"   # the naive belief that a missing value is a zero-cost skip
fi
check_eq "np.nanmean divides by the three readings that exist, not the four wanted" \
  "${expected_nanmean}" "$(get nanmean)"
check_eq "np.nansum is 7.0" "7.0" "$(get nansum)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for a wrong one -- 2.5, which is what you would get if a nan simply did not
# count and the divisor stayed at four -- and asserts that the re-run reports
# the failure and exits non-zero. If this section passes, section 5 is not
# decorative.
if [ -z "${D104_SELF_TEST:-}" ]; then
  self_out="$(D104_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: np.nanmean divides by the three readings"*)
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
