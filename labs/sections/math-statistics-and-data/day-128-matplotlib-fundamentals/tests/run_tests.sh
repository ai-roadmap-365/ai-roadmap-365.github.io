#!/usr/bin/env bash
# Tests for the Day 128 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# artist state, never by reading source or diffing image bytes:
#
#   * the two APIs -- plt.* called twice puts both lines on one figure;
#     fig, ax = plt.subplots() called twice produces two independent
#     figures, one line each;
#   * data round-trips exactly through ax.lines[0].get_xydata();
#   * savefig's pixel arithmetic -- a 6x4 inch figure at 100 dpi saves a
#     600x400 PNG, and doubling the dpi exactly doubles both dimensions;
#   * labels, titles and an explicit set_ylim that overrides autoscaling;
#   * plt.subplots(2, 3) returns a (2, 3) array of independent Axes;
#   * set_yscale('log') on data containing a zero silently narrows the
#     rendered range rather than raising, leaving the zero point in the
#     data but outside ax.get_ylim();
#   * a legend's text matches the labels supplied, in order;
#   * figures accumulate until closed, matplotlib's own warning fires past
#     20 open figures, and plt.close() empties the registry;
#   * an SVG carries its axis label as searchable text; the same label
#     never appears as bytes in the PNG;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside a temporary directory, nothing needs a key.
# Deterministic, non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1
export MPLBACKEND=Agg

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

if ! "${python_bin}" -c "import matplotlib" >/dev/null 2>&1; then
  echo "FAIL: matplotlib is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 128 — Matplotlib Fundamentals"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("matplotlib", "numpy", "pytest"):
    print(f"{name:<10} {version(name)}")
print(f"platform   {platform.platform()}")
print(f"exe        {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

pinned_mpl="$(grep -E '^matplotlib==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_mpl="$("${python_bin}" -c "from importlib.metadata import version; print(version('matplotlib'))")"
check_eq "installed matplotlib matches requirements.txt" "${pinned_mpl}" "${installed_mpl}"

major="$("${python_bin}" -c "import matplotlib; print(matplotlib.__version__.split('.')[0])")"
check_eq "matplotlib is version 3 or later" "3" "${major}"

backend="$("${python_bin}" -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; print(plt.get_backend())")"
check_eq "matplotlib runs on the headless Agg backend" "agg" "$(echo "${backend}" | tr '[:upper:]' '[:lower:]')"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_the_two_apis 02_data_round_trip 03_pixel_arithmetic \
              04_labels_limits_and_scales 05_subplots 06_log_scale_drops_nonpositive \
              07_legends 08_figure_leak 09_vector_versus_raster; do
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
echo "3. The reference pytest suite: real artist state, real exceptions"
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
if [ "${ref_passed:-0}" -ge 15 ]; then
  check "the reference suite ran at least 15 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 15 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain a module called `plotting`,
# and pytest imports test files by putting their directory on sys.path --
# so collecting both suites at once would otherwise let the starter tests
# import the REFERENCE solution and report unwritten exercises as passing.
# Each directory's conftest.py prevents that. This check proves it still
# does: across both suites, the skip count must be unchanged.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the reference legend test with the reference function's
# label order deliberately swapped, and asserts that the re-run reports the
# failure and exits non-zero. If this section passes, section 2 is not
# decorative.
if [ -z "${D128_SELF_TEST:-}" ]; then
  self_out="$(cd "${lab_dir}/examples" && D128_SELF_TEST=1 "${python_bin}" -c "
import plotting as P

_orig = P.plot_two_series_with_legend

def _broken(x, y1, label1, y2, label2):
    # deliberately swap the label order to break the assertion
    return _orig(x, y1, label2, y2, label1)

P.plot_two_series_with_legend = _broken
exec(open('07_legends.py').read())
" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately swapped label order makes script 07 exit non-zero (${self_status})" "yes"
  else
    check "a deliberately swapped label order makes script 07 exit non-zero" "no"
  fi
  case "${self_out}" in
    *"AssertionError"*"expected ['measured', 'predicted']"*)
      check "the failing assertion is named in the output with both values" "yes" ;;
    *) check "the failing assertion is named in the output with both values" "no" ;;
  esac
else
  echo "  (self-test run: section 5 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "6. Nothing was left behind"
# --------------------------------------------------------------------------

# `.venv` is pruned from both searches below. The virtual environment ships
# matplotlib's, NumPy's and pytest's own precompiled bytecode -- hundreds of
# __pycache__ directories that came with the packages and have nothing to do
# with whether THIS lab tidied up after itself.

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

if find "${lab_dir}" -name '.venv' -prune -o -type f \( -name '*.png' -o -name '*.svg' -o -name '*.pdf' \) -print -quit 2>/dev/null | grep -q .; then
  check "no image file (.png/.svg/.pdf) left by the lab's own code" "no"
else
  check "no image file (.png/.svg/.pdf) left by the lab's own code" "yes"
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
