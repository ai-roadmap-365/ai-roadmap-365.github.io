#!/usr/bin/env bash
# Tests for the Day 121 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a country-code CSV containing "NA" for Namibia is read, by default,
#     as a MISSING value -- keep_default_na=False keeps it as the string
#     "NA" instead;
#   * an id column "00123" is inferred as the integer 123 by default, and
#     dtype={"id": "str"} preserves the leading zeros exactly;
#   * an integer above 2**53 survives read_csv()'s int64 inference exactly,
#     but a float64 round-trip silently corrupts its last digit;
#   * a date column left unparsed sorts lexicographically -- and gets the
#     chronological order WRONG the moment one row drops a leading zero --
#     while parse_dates=[...] sorts correctly;
#   * reading a latin-1 file with encoding="utf-8" raises a real
#     UnicodeDecodeError, and only the correct encoding round-trips exactly;
#   * an aggregate computed chunk-by-chunk (chunksize=1000, then again with
#     an odd chunksize=777) equals the whole-file aggregate exactly;
#   * a CSV round-trip changes at least one dtype (a nullable Int64 column
#     becomes float64), while a Parquet round-trip preserves every dtype,
#     and every value, exactly;
#   * the eight-command inspection battery (.head, .info, .dtypes,
#     .describe, .isna().sum(), .nunique(), .value_counts(),
#     memory_usage(deep=True)) reports exact, independently-known values on
#     a frame built for this test;
#   * converting a low-cardinality string column to category reduces
#     memory_usage(deep=True) by at least 5x, asserted as a ratio;
#   * JSON, SQL (sqlite3) and the stdlib csv module are also demonstrated
#     end to end;
#   * nothing is left behind on disk -- no stray .csv, .parquet or .db file,
#     no __pycache__.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside a temporary directory each script creates and
# removes itself. Deterministic, non-interactive, exits 0 only if every
# check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. `.venv` is
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

echo "Day 121 — Read It Right"
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

for script in 01_the_namibia_trap 02_leading_zeros 03_precision_loss 04_dates \
              05_encoding 06_chunking 07_csv_vs_parquet 08_inspection_battery \
              09_category_memory 10_other_formats; do
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
    ('kept_df = _FILL_THIS_IN  # pd.read_csv(path, keep_default_na=False)',
     'kept_df = pd.read_csv(path, keep_default_na=False)'),
    ('typed_df = pd.read_csv(path, dtype=_FILL_THIS_IN)  # {\'id\': \'str\'}',
     'typed_df = pd.read_csv(path, dtype={\'id\': \'str\'})'),
    ('promoted = df.astype({"order_id": _FILL_THIS_IN})  # \'float64\'',
     'promoted = df.astype({"order_id": \'float64\'})'),
    ('parsed = pd.read_csv(path, parse_dates=_FILL_THIS_IN)  # [\'date\']',
     'parsed = pd.read_csv(path, parse_dates=[\'date\'])'),
    ('pd.read_csv(path, encoding=_FILL_THIS_IN)  # \'utf-8\'',
     'pd.read_csv(path, encoding=\'utf-8\')'),
    ('for chunk in pd.read_csv(path, chunksize=_FILL_THIS_IN):  # 3',
     'for chunk in pd.read_csv(path, chunksize=3):'),
    ('parquet_dtype = str(_FILL_THIS_IN["order_id"].dtype)  # pd.read_parquet(pq_path)',
     'parquet_dtype = str(pd.read_parquet(pq_path)["order_id"].dtype)'),
    ('top_region = _FILL_THIS_IN  # df["region"].value_counts().index[0]',
     'top_region = df["region"].value_counts().index[0]'),
    ('cat_bytes = int(df["region"].astype(_FILL_THIS_IN).memory_usage(deep=True))  # "category"',
     'cat_bytes = int(df["region"].astype("category").memory_usage(deep=True))'),
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
import tempfile
from pathlib import Path

import pandas as pd

tmpdir = Path(tempfile.mkdtemp())

# Namibia trap.
p1 = tmpdir / "c.csv"
p1.write_text("code,country\nNA,Namibia\n")
default_na = pd.isna(pd.read_csv(p1).loc[0, "code"])
kept_na = pd.read_csv(p1, keep_default_na=False).loc[0, "code"]
p1.unlink()
print("default_is_missing", default_na)
print("kept_value", kept_na)

# Leading zeros.
p2 = tmpdir / "id.csv"
p2.write_text("id\n00123\n")
default_id = int(pd.read_csv(p2).loc[0, "id"])
typed_id = pd.read_csv(p2, dtype={"id": "str"}).loc[0, "id"]
p2.unlink()
print("default_id", default_id)
print("typed_id", typed_id)

# Precision.
big_id = 2**53 + 1
p3 = tmpdir / "big.csv"
p3.write_text(f"order_id\n{big_id}\n")
df3 = pd.read_csv(p3)
exact = int(df3.loc[0, "order_id"])
corrupted = int(df3.astype({"order_id": "float64"}).loc[0, "order_id"])
p3.unlink()
print("precision_exact", exact == big_id)
print("precision_corrupted_by_one", big_id - corrupted)

# CSV vs Parquet.
df4 = pd.DataFrame({"order_id": pd.array([1001, 1002, pd.NA], dtype="Int64")})
csv_path = tmpdir / "o.csv"
pq_path = tmpdir / "o.parquet"
df4.to_csv(csv_path, index=False)
df4.to_parquet(pq_path)
csv_dtype = str(pd.read_csv(csv_path)["order_id"].dtype)
parquet_dtype = str(pd.read_parquet(pq_path)["order_id"].dtype)
csv_path.unlink()
pq_path.unlink()
print("csv_dtype", csv_dtype)
print("parquet_dtype", parquet_dtype)

# Chunking.
p5 = tmpdir / "chunks.csv"
p5.write_text("value\n" + "\n".join(str(i) for i in range(1, 1001)) + "\n")
whole = int(pd.read_csv(p5)["value"].sum())
chunked = sum(int(c["value"].sum()) for c in pd.read_csv(p5, chunksize=97))
p5.unlink()
print("chunking_matches", whole == chunked)

tmpdir.rmdir()
PY
)"
echo "${facts}" | sed 's/^/  /'

get_fact() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the default read turns Namibia's NA into a real missing value" "True" "$(get_fact default_is_missing)"
check_eq "keep_default_na=False keeps the literal string 'NA'" "NA" "$(get_fact kept_value)"
check_eq "the default read silently drops the leading zeros: '00123' becomes 123" "123" "$(get_fact default_id)"
check_eq "dtype={'id': 'str'} preserves the leading zeros exactly" "00123" "$(get_fact typed_id)"
check_eq "int64 preserves an ID past 2**53 exactly" "True" "$(get_fact precision_exact)"
check_eq "a float64 round-trip corrupts that ID by exactly 1" "1" "$(get_fact precision_corrupted_by_one)"
check_eq "a nullable Int64 column survives a CSV round-trip as float64, not Int64" "float64" "$(get_fact csv_dtype)"
check_eq "the same column survives a Parquet round-trip as Int64, unchanged" "Int64" "$(get_fact parquet_dtype)"
check_eq "an aggregate computed chunk-by-chunk (chunksize=97) equals the whole-file aggregate" "True" "$(get_fact chunking_matches)"

# --------------------------------------------------------------------------
echo
echo "5. Prove the harness can fail, then restore it"
# --------------------------------------------------------------------------

broken_script="${lab_dir}/examples/03_precision_loss.py"
cp "${broken_script}" "${broken_script}.bak"
sed -i.tmp 's/read_value == BIG_ID/read_value != BIG_ID/' "${broken_script}"
rm -f "${broken_script}.tmp"
broken_out="$(cd "${lab_dir}/examples" && "${python_bin}" 03_precision_loss.py 2>&1)"
broken_status=$?
mv "${broken_script}.bak" "${broken_script}"
if [ "${broken_status}" -ne 0 ]; then
  check "a deliberately wrong assertion makes 03_precision_loss.py exit non-zero" "yes"
else
  check "a deliberately wrong assertion makes 03_precision_loss.py exit non-zero" "no"
fi
case "${broken_out}" in
  *FAIL:*) check "the broken run reports a FAIL line" "yes" ;;
  *) check "the broken run reports a FAIL line" "no" ;;
esac
restored_out="$(cd "${lab_dir}/examples" && "${python_bin}" 03_precision_loss.py 2>&1)"
restored_status=$?
check_eq "the script is restored and exits 0 again" "0" "${restored_status}"
case "${restored_out}" in
  *"03_precision_loss.py: every assertion held."*)
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

stray_data="$(find "${lab_dir}" -name '.venv' -prune -o -type f \( -name '*.csv' -o -name '*.parquet' -o -name '*.db' \) -print 2>/dev/null)"
if [ -z "${stray_data}" ]; then
  check "no .csv, .parquet or .db file was left behind anywhere in the lab" "yes"
else
  check "no .csv, .parquet or .db file was left behind anywhere in the lab" "no"
  echo "${stray_data}" | sed 's/^/      /'
fi

echo
echo "${checks} checks, ${failures} failure(s)."
if [ "${failures}" -ne 0 ]; then
  exit 1
fi
exit 0
