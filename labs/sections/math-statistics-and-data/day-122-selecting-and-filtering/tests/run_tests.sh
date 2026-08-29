#!/usr/bin/env bash
# Tests for the Day 122 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a naive two-way split of a column with missing values (score > 50,
#     score <= 50) does NOT add up to the total row count -- the shortfall
#     is exactly the count of missing rows, and a three-way partition
#     (high, low, missing) restores the invariant exactly;
#   * `mask1 and mask2` raises ValueError (ambiguous truth value of a
#     Series), while `mask1 & mask2` computes the elementwise AND with no
#     error;
#   * `df.a > 1 & df.b < 2` does not group the way it reads -- `&` binds
#     tighter than the comparisons -- and raises the same ValueError;
#     `~df.a == 2` silently computes the WRONG (not erroring) result for
#     the same reason;
#   * a boolean mask built from a reordered copy of a frame, applied to the
#     original, aligns by LABEL and returns the correct rows in the
#     original's own order; the same booleans applied positionally (via
#     .to_numpy()) return a different, wrong set of rows;
#   * .str.contains() on a missing value returns None on object dtype
#     (raising ValueError when used to filter) but a clean False on
#     pandas 3.0's default str dtype -- na=False fixes both;
#   * .query() with an @variable selects the identical rows to the
#     equivalent mask, for both a single and a compound condition;
#   * .isin() matches a chain of == / | exactly, and .isin([]) returns
#     zero rows rather than the whole frame;
#   * .nlargest()/.nsmallest() match .sort_values().head() exactly when
#     there is no tie at the cutoff, and keep='all' returns MORE than n
#     rows when there is;
#   * .drop_duplicates() with different `subset` values gives different,
#     all-correct answers to "how many duplicates", and .filter() selects
#     labels, never rows, silently matching nothing if given row-shaped
#     arguments;
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

echo "Day 122 — Filters That Add Up"
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

for script in 01_partition_invariant 02_and_or_raise 03_precedence \
              04_mask_alignment 05_str_contains_na 06_query_equivalence \
              07_isin_vs_chained 08_nlargest_vs_sort_head 09_drop_duplicates_and_filter; do
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
    ('missing_count = _FILL_THIS_IN  # count of rows where score is NaN -- use .isna().sum()', 'missing_count = int(scores.score.isna().sum())'),
    ('and_mask = _FILL_THIS_IN  # the elementwise-AND version, using & not `and`', 'and_mask = mask1 & mask2'),
    ('correct_mask = _FILL_THIS_IN  # (table.a > 1) & (table.b < 2), correctly parenthesised', 'correct_mask = (table.a > 1) & (table.b < 2)'),
    ('result = _FILL_THIS_IN  # apply `mask` to the ORIGINAL `scores`, not `reordered`', 'result = scores[mask]'),
    ('mask = _FILL_THIS_IN  # names.str.contains("a", case=False, na=False)', 'mask = names.str.contains("a", case=False, na=False)'),
    ('result = _FILL_THIS_IN  # orders.query("amount > @threshold")', 'result = orders.query("amount > @threshold")'),
    ('result = _FILL_THIS_IN  # staff[staff.dept.isin(empty_wanted)]', 'result = staff[staff.dept.isin(empty_wanted)]'),
    ('result = _FILL_THIS_IN  # tied.nlargest(2, "score", keep="all")', 'result = tied.nlargest(2, "score", keep="all")'),
    ('result = _FILL_THIS_IN  # orders.drop_duplicates(subset=["customer"], keep="first")', 'result = orders.drop_duplicates(subset=["customer"], keep="first")'),
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
import numpy as np
import pandas as pd

# The partition invariant.
scores = pd.DataFrame({"score": [72, 45, np.nan, 91, 50, np.nan, 88, 33]})
high = scores[scores.score > 50]
low = scores[scores.score <= 50]
missing = int(scores.score.isna().sum())
print("partition_naive_sum", len(high) + len(low))
print("partition_total", len(scores))
print("partition_missing", missing)
print("partition_three_way_sum", len(high) + len(low) + missing)

# and/or raise.
try:
    (scores.score > 50) and (scores.score < 90)
    and_raised = False
except ValueError:
    and_raised = True
print("and_raised", and_raised)

# str.contains trap, by dtype.
names_str = pd.Series(["Alice", None, "dave"], dtype="str")
mask_str = names_str.str.contains("a", case=False)
print("str_dtype_mask_has_nan", bool(mask_str.isna().any()))

names_obj = pd.Series(["Alice", None, "dave"], dtype="object")
mask_obj = names_obj.str.contains("a", case=False)
try:
    names_obj[mask_obj]
    obj_filter_raised = False
except ValueError:
    obj_filter_raised = True
print("object_dtype_filter_raises", obj_filter_raised)

mask_obj_fixed = names_obj.str.contains("a", case=False, na=False)
print("na_false_fixed_count", int(mask_obj_fixed.sum()))

# isin([]) versus the whole frame.
staff = pd.DataFrame({"dept": ["eng", "sales", "hr"]})
print("isin_empty_rows", len(staff[staff.dept.isin([])]))
print("isin_empty_negated_rows", len(staff[~staff.dept.isin([])]))

# nlargest keep='all' beyond n.
tied = pd.DataFrame({"score": [80, 80, 80, 60]})
print("nlargest_keep_all_rows", len(tied.nlargest(2, "score", keep="all")))
print("sort_head_rows", len(tied.sort_values("score", ascending=False).head(2)))
PY
)"
echo "${facts}" | sed 's/^/  /'

get_fact() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

if [ "$(get_fact partition_naive_sum)" != "$(get_fact partition_total)" ]; then
  check "the naive high+low split does NOT equal the total (6 != 8)" "yes"
else
  check "the naive high+low split does NOT equal the total (6 != 8)" "no"
fi
check_eq "the missing count exactly accounts for the shortfall" "2" "$(get_fact partition_missing)"
check_eq "the three-way partition (high+low+missing) equals the total" "$(get_fact partition_total)" "$(get_fact partition_three_way_sum)"
check_eq "\`and\` between two masks raises ValueError" "True" "$(get_fact and_raised)"
check_eq "on pandas 3.0's str dtype, .str.contains() on a missing entry is NOT NaN" "False" "$(get_fact str_dtype_mask_has_nan)"
check_eq "on object dtype, filtering with the unfixed .str.contains() mask raises ValueError" "True" "$(get_fact object_dtype_filter_raises)"
check_eq "na=False on object dtype recovers the correct 2 matches" "2" "$(get_fact na_false_fixed_count)"
check_eq "isin([]) returns zero rows, not the whole frame" "0" "$(get_fact isin_empty_rows)"
check_eq "~isin([]) (negated) returns every row instead" "3" "$(get_fact isin_empty_negated_rows)"
check_eq "nlargest(2, keep='all') returns all 3 rows tied at the cutoff, more than n" "3" "$(get_fact nlargest_keep_all_rows)"
check_eq "sort_values().head(2) is forced to exactly n=2 rows even with the same tie" "2" "$(get_fact sort_head_rows)"

# --------------------------------------------------------------------------
echo
echo "5. Prove the harness can fail, then restore it"
# --------------------------------------------------------------------------

broken_script="${lab_dir}/examples/07_isin_vs_chained.py"
cp "${broken_script}" "${broken_script}.bak"
sed -i.tmp "s/len(via_isin) == 5/len(via_isin) == 999/" "${broken_script}"
rm -f "${broken_script}.tmp"
broken_out="$(cd "${lab_dir}/examples" && "${python_bin}" 07_isin_vs_chained.py 2>&1)"
broken_status=$?
mv "${broken_script}.bak" "${broken_script}"
if [ "${broken_status}" -ne 0 ]; then
  check "a deliberately wrong assertion makes 07_isin_vs_chained.py exit non-zero" "yes"
else
  check "a deliberately wrong assertion makes 07_isin_vs_chained.py exit non-zero" "no"
fi
case "${broken_out}" in
  *FAIL:*) check "the broken run reports a FAIL line" "yes" ;;
  *) check "the broken run reports a FAIL line" "no" ;;
esac
restored_out="$(cd "${lab_dir}/examples" && "${python_bin}" 07_isin_vs_chained.py 2>&1)"
restored_status=$?
check_eq "the script is restored and exits 0 again" "0" "${restored_status}"
case "${restored_out}" in
  *"07_isin_vs_chained.py: every assertion held."*)
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
