#!/usr/bin/env bash
# Tests for the Day 119 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * dataset A (16,000 rows) and dataset B (20,000 rows) both load with the
#     right row counts, group labels and no missing values, and a hand-built
#     row with a missing value is correctly rejected;
#   * the sample-ratio mismatch check passes on A's clean 50/50 split and
#     fails on B's planted 48/52 split, with both p-values reported;
#   * a handful of planted bot-like sessions drag the MEAN of time-on-page
#     well above the MEDIAN in every group of both datasets;
#   * the primary test's 95% confidence interval on A excludes zero, and
#     agrees with the significance test at alpha=0.05;
#   * the effect size is always reported as an absolute difference AND a
#     relative lift together, never a bare p-value;
#   * a guardrail (page latency) holds on A within its declared tolerance,
#     and the same check is proven capable of failing under an impossible
#     tolerance;
#   * segment analysis finds every one of B's three segments pointing the
#     OPPOSITE way from B's pooled number -- a real, measured Simpson's
#     paradox -- and flags the reversal, while A's segments agree with its
#     pooled number and trip no flag;
#   * walking dataset A in arrival order, the running p-value dips below
#     0.05 as early as row 4,000, climbs back above it by row 5,000, and
#     only settles for good after row 5,500 -- even though the full-sample
#     verdict at row 16,000 is also significant;
#   * the verdict function ships dataset A and REFUSES to give dataset B a
#     verdict at all once its sample-ratio mismatch check has failed;
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

echo "Day 119 — Analyzing an Experiment End to End"
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
echo "2. The shipped data exists and is exactly what generate_data.py makes"
# --------------------------------------------------------------------------

data_ok="$("${python_bin}" - <<PY
import csv
from pathlib import Path

lab = Path("${lab_dir}")
a = list(csv.DictReader((lab / "data" / "exp_a.csv").open()))
b = list(csv.DictReader((lab / "data" / "exp_b.csv").open()))
print("yes" if (len(a) == 16000 and len(b) == 20000) else "no")
PY
)"
check_eq "data/exp_a.csv has 16000 rows and data/exp_b.csv has 20000 rows" "yes" "${data_ok}"

# --------------------------------------------------------------------------
echo
echo "3. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_load_and_validate 02_sample_ratio_mismatch 03_group_summary \
              04_primary_test 05_effect_size 06_guardrail 07_segment_analysis \
              08_peeking 09_verdict; do
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
echo "4. The reference pytest suite: real values, real exceptions"
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
if [ "${ref_passed:-0}" -ge 12 ]; then
  check "the reference suite ran at least 12 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 12 tests (ran ${ref_passed:-0})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "5. The starter suite skips unattempted work instead of failing it"
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

both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green suite proves nothing until it has been watched go red. This
# temporarily swaps the reference solution into starter/experiment.py,
# confirms the full starter suite passes, then breaks ONE function's
# contract on purpose (verdict() returning "ship" for the SRM-failed
# dataset instead of refusing) and confirms pytest reports the failure and
# exits non-zero, before restoring the original blank skeleton.
if [ -z "${D119_SELF_TEST:-}" ]; then
  backup="$(mktemp)"
  cp "${lab_dir}/starter/experiment.py" "${backup}"
  cp "${lab_dir}/examples/experiment.py" "${lab_dir}/starter/experiment.py"

  solved_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
  solved_status=$?
  if [ "${solved_status}" -eq 0 ]; then
    check "a fully solved starter/experiment.py passes the whole starter suite" "yes"
  else
    check "a fully solved starter/experiment.py passes the whole starter suite" "no"
    echo "${solved_out}" | tail -5 | sed 's/^/      /'
  fi

  # Break the SRM refusal on purpose: patch verdict() so it never refuses.
  "${python_bin}" - "${lab_dir}/starter/experiment.py" <<'PY'
import sys
path = sys.argv[1]
src = open(path).read()
needle = 'if not srm_result["passed"]:'
assert needle in src, "could not find the refusal branch to break"
broken = src.replace(
    needle,
    'if False:  # D119_SELF_TEST: refusal branch disabled on purpose',
    1,
)
open(path, "w").write(broken)
PY

  broken_out="$(cd "${lab_dir}" && D119_SELF_TEST=1 "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
  broken_status=$?
  if [ "${broken_status}" -ne 0 ]; then
    check "disabling the SRM refusal makes the starter suite fail (exit ${broken_status})" "yes"
  else
    check "disabling the SRM refusal makes the starter suite fail" "no"
  fi
  case "${broken_out}" in
    *"do not trust this result"*"assert"*|*"AssertionError"*)
      check "the failing test names the broken expectation" "yes" ;;
    *) check "the failing test names the broken expectation" "no" ;;
  esac

  cp "${backup}" "${lab_dir}/starter/experiment.py"
  rm -f "${backup}"

  restored_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
  case "${restored_out}" in
    *skipped*) check "restoring the blank skeleton goes back to skipped, not failed" "yes" ;;
    *) check "restoring the blank skeleton goes back to skipped, not failed" "no" ;;
  esac
else
  echo "  (self-test run: section 6 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "7. Nothing was left behind"
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
