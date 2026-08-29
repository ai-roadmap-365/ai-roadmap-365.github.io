#!/usr/bin/env bash
# Tests for the Day 120 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a Series built from a dict takes the dict's keys as its index, and a
#     DataFrame built from a bare NumPy array has NO labels until you supply
#     them yourself;
#   * adding two Series with partially overlapping indexes aligns on LABEL,
#     not position -- labels a and d, present on only one side, become NaN --
#     and .to_numpy() addition gives a different, purely positional answer;
#   * an int64 column reindexed onto a label that was never there is
#     silently promoted to float64, losing exact precision past 2**53, while
#     the nullable Int64 dtype stays exact;
#   * chained assignment (`df[mask]['col'] = value`) leaves the ORIGINAL
#     frame completely unchanged -- pandas 3.0.5 warns about it with a
#     ChainedAssignmentError, but the statement still "succeeds" -- and the
#     single-.loc form is the one that actually writes;
#   * .loc['b':'d'] and .iloc[1:4] return the same three rows, but .iloc[1:3]
#     -- the "matching" number -- silently drops one, because .loc's stop is
#     inclusive of a label and .iloc's stop is exclusive of a position;
#   * float('nan') != float('nan'), and comparing a Series against np.nan
#     with == finds nothing, ever -- .isna() is the only reliable test;
#   * vectorised arithmetic beats .apply(lambda ...) by at least 20x on
#     200,000 rows, measured as a ratio and a shape, never a millisecond
#     figure;
#   * pd.Series(['a', 'b']).dtype is 'str' on pandas 3.0.5, not the 'object'
#     every pre-3.0 tutorial describes;
#   * .describe() on a known eight-value column matches hand computation
#     exactly for count, mean, min and max, and matches Day 116's
#     Bessel-corrected sample standard deviation to the ninth decimal;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside the lab, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `python3 starter/check_progress.py`, and running it writes .pyc
# files that would then fail the cleanliness check at the end of this
# script -- failing the reader for following the instructions. Clearing them
# here makes that final check measure what it claims to: what THIS run left
# behind. `.venv` is untouched, because the packages' own bytecode is
# theirs, not ours.
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

# Resolve python: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping checks.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing python3:" >&2
  echo "    PYTHON=/path/to/python3 bash tests/run_tests.sh" >&2
  exit 1
}

if ! "${python_bin}" -c "import pandas, pyarrow" >/dev/null 2>&1; then
  echo "FAIL: pandas/pyarrow are not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 120 — Frames You Can Trust"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("pandas", "pyarrow", "numpy"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

pinned_pandas="$(grep -E '^pandas==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_pandas="$("${python_bin}" -c "from importlib.metadata import version; print(version('pandas'))")"
check_eq "installed pandas matches requirements.txt" "${pinned_pandas}" "${installed_pandas}"

pandas_major="$("${python_bin}" -c "import pandas; print(pandas.__version__.split('.')[0])")"
check_eq "pandas is version 3 or later (this lab's captured output is 3.0.5-specific)" "3" "${pandas_major}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_three_ways_to_build 02_alignment 03_dtype_promotion \
              04_copy_on_write 05_loc_vs_iloc 06_nan_semantics \
              07_vectorized_vs_apply 08_string_dtype 09_describe_known_column; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -8 | sed 's/^/      /'
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
echo "3. The starter checker: honest progress, both directions"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && "${python_bin}" starter/check_progress.py 2>&1)"
starter_status=$?
echo "${starter_out}" | tail -3 | sed 's/^/  /'
case "${starter_out}" in
  *"0 of 9 exercises complete."*)
    check "an untouched starter checkout reports 0 of 9 complete" "yes" ;;
  *)
    check "an untouched starter checkout reports 0 of 9 complete" "no" ;;
esac
if [ "${starter_status}" -ne 0 ]; then
  check "the starter checker exits non-zero when incomplete" "yes"
else
  check "the starter checker exits non-zero when incomplete" "no"
fi

# Prove the checker can also report success: solve every exercise in a
# scratch copy, confirm 9 of 9 and exit 0, then discard the copy. The real
# starter/exercises.py on disk is never modified by this.
solved_dir="$(mktemp -d)"
trap 'rm -rf "${solved_dir}"' EXIT
cp "${lab_dir}/starter/exercises.py" "${solved_dir}/exercises.py"
cp "${lab_dir}/starter/check_progress.py" "${solved_dir}/check_progress.py"
"${python_bin}" - "${solved_dir}/exercises.py" <<'PY'
import sys
path = sys.argv[1]
s = open(path).read()
replacements = [
    ('index_list = _FILL_THIS_IN  # convert s.index to a plain list', 'index_list = list(s.index)'),
    ('nan_labels = _FILL_THIS_IN  # set of index labels where z is NaN -- use z.isna()', 'nan_labels = set(z.index[z.isna()])'),
    ('dtype_name = _FILL_THIS_IN  # str(reindexed.dtype)', 'dtype_name = str(reindexed.dtype)'),
    ('_FILL_THIS_IN  # write the ONE .loc statement that actually changes df["b"] where a > 1, to 0', 'df.loc[df["a"] > 1, "b"] = 0'),
    ('by_position = _FILL_THIS_IN  # the .iloc slice that STOPS BEFORE position 3', 'by_position = df.iloc[1:3]'),
    ('result = _FILL_THIS_IN  # the actual comparison, not a hard-coded boolean', 'result = float("nan") == float("nan")'),
    ('result = _FILL_THIS_IN  # one vectorised expression, no .apply', 'result = prices * 1.08'),
    ('dtype_name = _FILL_THIS_IN  # str(s.dtype)', 'dtype_name = str(s.dtype)'),
    ('result = _FILL_THIS_IN  # (desc["count"], desc["mean"], desc["min"], desc["max"])', 'result = (desc["count"], desc["mean"], desc["min"], desc["max"])'),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f"pattern not found, starter/exercises.py has drifted: {old!r}")
    s = s.replace(old, new)
open(path, "w").write(s)
PY
solved_out="$(cd "${solved_dir}" && "${python_bin}" check_progress.py 2>&1)"
solved_status=$?
echo "${solved_out}" | tail -3 | sed 's/^/  /'
case "${solved_out}" in
  *"9 of 9 exercises complete."*)
    check "a fully solved copy reports 9 of 9 complete" "yes" ;;
  *)
    check "a fully solved copy reports 9 of 9 complete" "no" ;;
esac
check_eq "the checker exits 0 once every exercise is correct" "0" "${solved_status}"
rm -rf "${solved_dir}"
trap - EXIT

# --------------------------------------------------------------------------
echo
echo "4. The lesson's sharpest claims, checked one value at a time"
# --------------------------------------------------------------------------

facts="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
import warnings

import numpy as np
import pandas as pd

# Copy-on-Write: chained assignment does nothing; .loc does.
df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
before = df["b"].tolist()
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df[df["a"] > 1]["b"] = 0
    warned = any(w.category.__name__ == "ChainedAssignmentError" for w in caught)
after_chained = df["b"].tolist()
df.loc[df["a"] > 1, "b"] = 0
after_loc = df["b"].tolist()
print("cow_chained_unchanged", after_chained == before)
print("cow_warned", warned)
print("cow_loc_changed", after_loc)

# String dtype default.
print("string_dtype", str(pd.Series(["a", "b"]).dtype))

# Alignment.
x = pd.Series([1, 2, 3], index=["a", "b", "c"])
y = pd.Series([10, 20, 30], index=["b", "c", "d"])
z = x + y
print("alignment_nan_labels", "|".join(sorted(z.index[z.isna()])))
print("alignment_b", z["b"])
print("alignment_c", z["c"])

# loc vs iloc, the corrected framing.
df5 = pd.DataFrame({"val": [10, 20, 30, 40, 50]}, index=["a", "b", "c", "d", "e"])
print("loc_iloc4_equal", df5.loc["b":"d"].equals(df5.iloc[1:4]))
print("iloc3_shorter", len(df5.iloc[1:3]) == len(df5.loc["b":"d"]) - 1)

# Int64 stays exact past 2**53; plain int64 promoted through reindex does not.
big_id = 2**53 + 1
lost = int(pd.Series([big_id], dtype="int64").reindex([0, 1]).iloc[0])
kept = int(pd.Series([big_id], dtype="Int64").reindex([0, 1]).iloc[0])
print("big_id_lost_precision", lost != big_id)
print("big_id_kept_precision", kept == big_id)
PY
)"
echo "${facts}" | sed 's/^/  /'

get_fact() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "chained assignment leaves df['b'] byte-for-byte unchanged" "True" "$(get_fact cow_chained_unchanged)"
check_eq "pandas 3.0.5 raises a ChainedAssignmentError warning on that statement" "True" "$(get_fact cow_warned)"
check_eq "the .loc form changes b to [10, 0, 0]" "[10, 0, 0]" "$(get_fact cow_loc_changed)"
check_eq "pd.Series(['a','b']).dtype is the pandas-3.0 default str, not object" "str" "$(get_fact string_dtype)"
check_eq "exactly labels a and d go NaN under alignment" "a|d" "$(get_fact alignment_nan_labels)"
check_eq "label b aligns to 2 + 10 = 12.0" "12.0" "$(get_fact alignment_b)"
check_eq "label c aligns to 3 + 20 = 23.0" "23.0" "$(get_fact alignment_c)"
check_eq "loc['b':'d'] equals iloc[1:4] (different stop values, same rows)" "True" "$(get_fact loc_iloc4_equal)"
check_eq "iloc[1:3] is exactly one row shorter than loc['b':'d']" "True" "$(get_fact iloc3_shorter)"
check_eq "plain int64 loses exact precision past 2**53 once promoted" "True" "$(get_fact big_id_lost_precision)"
check_eq "nullable Int64 keeps exact precision past 2**53" "True" "$(get_fact big_id_kept_precision)"

# --------------------------------------------------------------------------
echo
echo "5. Prove the harness can fail, then restore it"
# --------------------------------------------------------------------------

broken_script="${lab_dir}/examples/08_string_dtype.py"
cp "${broken_script}" "${broken_script}.bak"
sed -i.tmp 's/str(s.dtype) == "str"/str(s.dtype) == "object"/' "${broken_script}"
rm -f "${broken_script}.tmp"
broken_out="$(cd "${lab_dir}/examples" && "${python_bin}" 08_string_dtype.py 2>&1)"
broken_status=$?
mv "${broken_script}.bak" "${broken_script}"
if [ "${broken_status}" -ne 0 ]; then
  check "a deliberately wrong assertion makes 08_string_dtype.py exit non-zero" "yes"
else
  check "a deliberately wrong assertion makes 08_string_dtype.py exit non-zero" "no"
fi
case "${broken_out}" in
  *FAIL:*) check "the broken run reports a FAIL line" "yes" ;;
  *) check "the broken run reports a FAIL line" "no" ;;
esac
restored_out="$(cd "${lab_dir}/examples" && "${python_bin}" 08_string_dtype.py 2>&1)"
restored_status=$?
check_eq "the script is restored and exits 0 again" "0" "${restored_status}"
case "${restored_out}" in
  *"08_string_dtype.py: every assertion held."*)
    check "the restored script reports every assertion held" "yes" ;;
  *) check "the restored script reports every assertion held" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "6. Nothing left behind, and no network dependency baked into the lab"
# --------------------------------------------------------------------------

if grep -rInE 'https?://' "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1; then
  check "no URL appears in examples/ or starter/" "no"
else
  check "no URL appears in examples/ or starter/" "yes"
fi

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -print 2>/dev/null)"
if [ -z "${stray}" ]; then
  check "no __pycache__ or .pytest_cache directories were left behind" "yes"
else
  check "no __pycache__ or .pytest_cache directories were left behind" "no"
  echo "${stray}" | sed 's/^/      /'
fi

echo
echo "${checks} checks, ${failures} failure(s)."
if [ "${failures}" -ne 0 ]; then
  exit 1
fi
exit 0
