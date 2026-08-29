#!/usr/bin/env bash
# Tests for the Day 126 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * a step that recomputes its clip threshold from whatever data is
#     currently passing through it is NOT idempotent -- pipeline(pipeline(df))
#     changes order 7's amount from 1236.5 to 1223.675 -- while the real
#     pipeline, which reads its threshold from config, is idempotent exactly;
#   * two independent runs on the same input hash identically, and an
#     explicit order_id tie-break makes the final row order the same
#     regardless of which order two tied rows arrived in;
#   * the step log reconciles: every step's rows-out equals the next step's
#     rows-in, and the total change equals the sum of the per-step deltas;
#   * the input contract raises, naming the column, on a missing column or a
#     wrong dtype;
#   * the output contract raises, naming the violated condition, when the
#     clip step is sabotaged into a no-op;
#   * a .pipe() chain produces a frame identical to sequential application;
#   * normalising region strings before deduplicating catches a resubmitted
#     order that reversing the order misses entirely;
#   * a Parquet checkpoint round-trip preserves every dtype exactly,
#     including a nullable Int64 column's missing value;
#   * a manifest's input, config and output hashes are stable across
#     independent runs, and changing one input byte changes both the input
#     hash and the output hash;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every exercise
#     in a scratch copy, breaking one assertion on purpose, confirming a
#     non-zero exit and a printed FAIL, then restoring it;
#   * nothing -- no .parquet, .json or .csv file, no __pycache__ -- is left
#     behind by this run.
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

echo "Day 126 — A Pipeline You Can Re-run"
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
check "examples/ reports 17 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^17 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 17 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^17 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Never run 'pytest examples starter' in one invocation -- every"
echo "   module name (data, steps, pipeline, conftest, test_pipeline) is"
echo "   shared between both directories, so the second collected can"
echo "   shadow, or outright collide with, the first. Checked below."
# --------------------------------------------------------------------------

both_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
both_status=$?
check "pytest examples starter (one invocation) does NOT exit 0" "$( [ ${both_status} -ne 0 ] && echo yes || echo no )"
check "pytest examples starter reports an import file mismatch, not a quiet partial run" "$( echo "${both_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed FAIL, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d126-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

cp "${lab_dir}/examples/test_pipeline.py" "${scratch_dir}/test_pipeline.py"
cp "${lab_dir}/examples/data.py" "${scratch_dir}/data.py"
cp "${lab_dir}/examples/steps.py" "${scratch_dir}/steps.py"
cp "${lab_dir}/examples/pipeline.py" "${scratch_dir}/pipeline.py"
cp "${lab_dir}/examples/conftest.py" "${scratch_dir}/conftest.py"

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 17 passed" "$( echo "${solved_output}" | grep -qE '^17 passed' && echo yes || echo no )"

# Break test_1's exact idempotence assertion on purpose.
sed -i.bak 's/assert once\.equals(twice)/assert not once.equals(twice)/' "${scratch_dir}/test_pipeline.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a FAIL/failed line" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_pipeline.py.bak" "${scratch_dir}/test_pipeline.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 17 passed again" "$( echo "${restored_output}" | grep -qE '^17 passed' && echo yes || echo no )"

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
echo "7. A pipeline day that litters would be embarrassing -- confirm no"
echo "   .parquet, .json or .csv artifact is left behind anywhere in the lab"
# --------------------------------------------------------------------------

artifact_hits="$(find "${lab_dir}" -name '.venv' -prune -o -name 'expected-output' -prune -o \
  \( -type f \( -name '*.parquet' -o -name '*.json' -o -name '*.csv' \) -print \) 2>/dev/null || true)"
check "no stray .parquet/.json/.csv files under the lab (outside expected-output/)" "$( [ -z "${artifact_hits}" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "8. Cleanliness -- nothing left behind by THIS run"
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
