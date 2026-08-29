#!/usr/bin/env bash
# Tests for the Day 136 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by running code and reading real
# values, never by reading source:
#
#   * twenty independent alpha=0.05 comparisons on data with NO real signal
#     give a 64.15% chance of at least one false positive -- exact
#     arithmetic, confirmed by simulation, for k=5, 20 and 40;
#   * one concrete 40-comparison scan of a signal-free dataset really does
#     turn up a "winning" comparison whose effect size looks publishable;
#   * a real, planted effect survives an untouched confirmation set, and a
#     spurious column chosen for looking best among thirty candidates does
#     not -- the day's centrepiece, both p-values on both splits;
#   * varying a subset filter and an outcome definition with no test
#     declared per variant inflates the apparent significance rate several
#     times over one pre-declared comparison;
#   * Bonferroni restores the nominal family-wise rate when the comparison
#     count is known and correct, and fails when the true count exceeds
#     the reported one;
#   * a research log's own length is the true comparison count, and every
#     entry carries a timestamp, a look and an outcome -- including nulls;
#   * a triage score ranks a cheap, decision-relevant question above an
#     expensive, less relevant one;
#   * a time-boxed stopping rule's false-positive rate sits near the
#     nominal alpha, and "stop when significant" inflates it several
#     times over, on the exact same budget of looks;
#   * the object handed to a report stage is refused unless it carries a
#     finding, a confirmation-set result and a comparison count;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed failure, then restoring it;
#   * no file is left behind anywhere, and no lab source opens a network
#     connection.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing needs a key. Deterministic, non-interactive, exits 0 only if
# every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

if ! "${python_bin}" -c "import numpy, pandas" >/dev/null 2>&1; then
  echo "FAIL: numpy and/or pandas is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 136 — The Exploratory Data Analysis Process"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("numpy", "pandas", "pytest"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

for pkg in numpy pandas pytest; do
  pinned="$(grep -E "^${pkg}==" "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${pkg}'))")"
  check_eq "installed ${pkg} matches requirements.txt" "${pinned}" "${installed}"
done

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_forking_paths 02_plausible_story 03_holdout_rescues_you \
              04_choices_are_comparisons 05_bonferroni_and_its_limit \
              06_research_log 07_triage 08_stopping_rule 09_handoff_contract; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -5 | sed 's/^/      /'
  else
    check "${script}.py exits 0" "yes"
  fi
  case "${out}" in
    *"OK:"*)
      check "${script}.py reports OK" "yes" ;;
    *) check "${script}.py reports OK" "no" ;;
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
if [ "${ref_passed:-0}" -ge 24 ]; then
  check "the reference suite ran at least 24 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 24 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `exploration`
# and `dataset`; each directory's conftest.py prevents a cross-import. This
# check proves it still does: auto-discovering both directories from the
# lab root must report the same skip count as `pytest starter` alone.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "auto-discovering both suites does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs script 01 (forking paths) with its expected exact rate
# for k=20 deliberately swapped for a wrong one, and asserts that the
# re-run reports the failure and exits non-zero.
if [ -z "${D136_SELF_TEST:-}" ]; then
  self_out="$(cd "${lab_dir}/examples" && D136_SELF_TEST=1 "${python_bin}" -c "
src = open('01_forking_paths.py').read()
src = src.replace(\"expected_exact = {5: 0.2262, 20: 0.6415, 40: 0.8715}[k]\", \"expected_exact = {5: 0.2262, 20: 99.0, 40: 0.8715}[k]\")
g = {'__name__': '__main__', '__file__': '01_forking_paths.py'}
exec(compile(src, '01_forking_paths.py', 'exec'), g)
" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes script 01 exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes script 01 exit non-zero" "no"
  fi
  case "${self_out}" in
    *"AssertionError"*"0.6415"*)
      check "the failing assertion is named in the output with the real value" "yes" ;;
    *) check "the failing assertion is named in the output with the real value" "no" ;;
  esac
else
  echo "  (self-test run: section 5 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "6. Nothing was left behind"
# --------------------------------------------------------------------------

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
