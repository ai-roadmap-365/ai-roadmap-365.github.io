#!/usr/bin/env bash
# Tests for the Day 124 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a many-to-many merge on duplicated keys produces exactly the product
#     of the per-key group sizes on each side, summed across keys;
#   * validate='one_to_one' raises MergeError the moment that assumption
#     is violated, and passes silently when the assumption genuinely holds;
#   * indicator=True's left_only/right_only/both counts reconcile exactly
#     with the two input row counts;
#   * an int64 key merged against a categorical key of the same digits
#     matches nothing and returns zero rows, silently; casting fixes it;
#     and a plain str key against int64 now RAISES instead, in this
#     pandas version -- an honest correction, checked directly;
#   * inner/left/right/outer row counts on one pair of frames;
#   * default _x/_y suffixes on overlapping columns, and that explicit
#     suffixes rename them as asked; on= vs left_on/right_on agree; join()
#     on the index matches merge() on the column;
#   * concat's axis-0 and axis-1 alignment fills unmatched columns/labels
#     with NaN in exactly the cells that should be NaN, never elsewhere;
#   * melt -> pivot round-trips back to the original frame exactly;
#   * pivot raises on duplicate index/column pairs; pivot_table aggregates
#     them instead, reporting the correct mean;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed FAIL, then restoring it;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside the lab, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q` and `pytest examples -q` separately, and
# running either writes .pyc files that would then fail the cleanliness
# check at the end of this script -- failing the reader for following the
# instructions. Clearing them here makes that final check measure what it
# claims to: what THIS run left behind. `.venv` is untouched, because the
# packages' own bytecode is theirs, not ours.
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

python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

if ! "${python_bin}" -c "import pandas" >/dev/null 2>&1; then
  echo "FAIL: pandas is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 124 — Joins That Keep Their Shape"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("pandas", "pyarrow", "numpy", "pytest"):
    try:
        print(f"{name:<8} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<8} NOT INSTALLED ({exc})")
PY
)"
echo "${versions}"
echo

pandas_version="$("${python_bin}" -c "import pandas; print(pandas.__version__)" 2>/dev/null || echo "")"
pinned_pandas="$(grep -m1 '^pandas==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
check_eq "installed pandas matches requirements.txt exactly" "${pinned_pandas}" "${pandas_version}"
echo

# --------------------------------------------------------------------------
echo "2. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"

examples_passed_line="$(echo "${examples_output}" | grep -E '^[0-9]+ passed' || true)"
check "examples/ reports 22 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^22 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 22 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^22 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Never run 'pytest examples starter' in one invocation -- same"
echo "   module name in both directories means the second collected can"
echo "   shadow the first. Documented and checked separately, above."
# --------------------------------------------------------------------------
echo

# --------------------------------------------------------------------------
echo "5. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed FAIL, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d124-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

cp "${lab_dir}/examples/test_merge.py" "${scratch_dir}/test_merge.py"
cp "${lab_dir}/examples/data.py" "${scratch_dir}/data.py"
cp "${lab_dir}/examples/conftest.py" "${scratch_dir}/conftest.py"

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 22 passed" "$( echo "${solved_output}" | grep -qE '^22 passed' && echo yes || echo no )"

# Break test_1's exact row-count assertion on purpose: 14 -> 999.
sed -i.bak 's/assert expected_rows == 14/assert expected_rows == 999/' "${scratch_dir}/test_merge.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a FAIL/failed line" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_merge.py.bak" "${scratch_dir}/test_merge.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 22 passed again" "$( echo "${restored_output}" | grep -qE '^22 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "6. Nothing in examples/ or starter/ opens a network connection"
# --------------------------------------------------------------------------

url_hits="$(grep -rEl 'https?://|ftp://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no URLs inside examples/ or starter/" "$( [ -z "${url_hits}" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "7. Cleanliness -- nothing left behind by THIS run"
# --------------------------------------------------------------------------

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o \( -type d -name '__pycache__' -print -o -type d -name '.pytest_cache' -print \) 2>/dev/null || true)"
check "no __pycache__ or .pytest_cache left behind" "$( [ -z "${stray}" ] && echo yes || echo no )"
echo

echo "-------------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)"
if [ "${failures}" -gt 0 ]; then
  exit 1
fi
exit 0
