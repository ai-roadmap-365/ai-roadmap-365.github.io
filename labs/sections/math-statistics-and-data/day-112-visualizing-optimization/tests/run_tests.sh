#!/usr/bin/env bash
# Tests for the Day 112 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * evaluate_grid puts the analytic minimum at the true grid cell, for a
#     bowl and for an anisotropic one;
#   * the ASCII contour renderer produces the exact character at the exact
#     cell a symmetric bowl predicts -- a transposed grid fails this loudly;
#   * a Pillow heatmap's pixel at the minimum is the colour ramp's own
#     lowest-value stop, read back from the saved PNG;
#   * world_to_pixel places the four corners and the centre of a symmetric
#     window exactly, and a descent path drawn with it starts at the start
#     point's pixel and ends within two pixels of the minimum's;
#   * a well-conditioned run's loss on a log10 axis is provably collinear --
#     fit to a line, the residual is measured in pixels, not asserted in
#     prose;
#   * an animated GIF has exactly as many frames as the descent had steps;
#   * a learning-rate sweep finds an interior optimum, a basin of several
#     good rates either side of it, and genuine divergence past eta = 1,
#     caught as float('inf') rather than raised as an exception;
#   * two runs on differently conditioned bowls, same start, same learning
#     rate, same step count, land within 5% of the same final loss while
#     their path lengths differ by more than 5x -- the day's opening claim,
#     made into an assertion;
#   * nothing is left behind on disk, including no PNG or GIF file.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing writes outside the lab (or a temporary directory it removes
# itself), nothing needs a key. Deterministic, non-interactive, exits 0 only
# if every check passes.
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
  if [ "$2" = "$3" ]; then
    check "$1" "yes"
  else
    check "$1 (expected [$2], got [$3])" "no"
  fi
}

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

if ! "${python_bin}" -c "import numpy, PIL" >/dev/null 2>&1; then
  echo "FAIL: numpy and/or Pillow are not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 112 — Visualizing Optimization"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("numpy", "Pillow", "pytest"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

pinned_numpy="$(grep -E '^numpy==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_numpy="$("${python_bin}" -c "from importlib.metadata import version; print(version('numpy'))")"
check_eq "installed numpy matches requirements.txt" "${pinned_numpy}" "${installed_numpy}"

pinned_pillow="$(grep -E '^Pillow==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed_pillow="$("${python_bin}" -c "from importlib.metadata import version; print(version('Pillow'))")"
check_eq "installed Pillow matches requirements.txt" "${pinned_pillow}" "${installed_pillow}"

no_matplotlib="$("${python_bin}" -c "
try:
    import matplotlib  # noqa: F401
    print('present')
except ImportError:
    print('absent')
")"
check_eq "matplotlib is genuinely absent from this environment" "absent" "${no_matplotlib}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_grid_and_ascii 02_heatmap_and_path 03_loss_curves \
              04_animated_gif 05_learning_rate_sweep 06_two_runs_same_loss; do
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
if [ "${ref_passed:-0}" -ge 10 ]; then
  check "the reference suite ran at least 10 tests (ran ${ref_passed:-0})" "yes"
else
  check "the reference suite ran at least 10 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain modules called `dataset`,
# `gridviz`, `descent` and `imaging`, and collecting both suites at once
# would otherwise let the starter tests import the REFERENCE solution. Each
# directory's conftest.py prevents that; this check proves it still does.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The day's opening claim, checked one value at a time"
# --------------------------------------------------------------------------

# Section 6 re-runs this whole script with D112_SELF_TEST set, which asks
# for a threshold ten times tighter than the two runs actually achieve --
# proving the harness can fail rather than merely claiming it could.
threshold="${D112_SELF_TEST_THRESHOLD:-0.05}"

facts="$(cd "${lab_dir}/examples" && "${python_bin}" - <<PY
import dataset as D
import descent as DS

well_path = DS.gradient_descent(D.WELL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
ill_path = DS.gradient_descent(D.ILL_GRAD, D.START, D.LEARNING_RATE, D.STEPS)
well_loss = DS.losses_along(D.WELL_F, well_path)[-1]
ill_loss = DS.losses_along(D.ILL_F, ill_path)[-1]
relative_gap = abs(well_loss - ill_loss) / max(well_loss, ill_loss)
well_len = DS.path_length(well_path)
ill_len = DS.path_length(ill_path)

print("well_loss", f"{well_loss:.6e}")
print("ill_loss", f"{ill_loss:.6e}")
print("relative_gap", f"{relative_gap:.6f}")
print("relative_gap_within_threshold", relative_gap < ${threshold})
print("well_len", f"{well_len:.4f}")
print("ill_len", f"{ill_len:.4f}")
print("length_ratio", f"{ill_len / well_len:.4f}")
print("length_ratio_over_5x", (ill_len / well_len) > 5.0)
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

echo "  (measured on this run: well-conditioned final loss $(get well_loss), ill-conditioned $(get ill_loss), relative gap $(get relative_gap) -- reported, not asserted to a value)"
check_eq "the two final losses land within the stated threshold of each other" \
  "True" "$(get relative_gap_within_threshold)"
echo "  (measured on this run: well-conditioned path length $(get well_len), ill-conditioned $(get ill_len), ratio $(get length_ratio)x)"
check_eq "the ill-conditioned path is over 5x longer than the well-conditioned one" \
  "True" "$(get length_ratio_over_5x)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with the threshold in section 5 replaced
# by one the measured runs cannot meet, and asserts that the re-run reports
# the failure and exits non-zero. If this section passes, section 5 is not
# decorative.
if [ -z "${D112_SELF_TEST:-}" ]; then
  self_out="$(D112_SELF_TEST=1 D112_SELF_TEST_THRESHOLD=0.001 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "an unmeetable threshold makes the harness exit non-zero (${self_status})" "yes"
  else
    check "an unmeetable threshold makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: the two final losses land within the stated threshold of each other"*)
      check "the failing check is named in the output" "yes" ;;
    *) check "the failing check is named in the output" "no" ;;
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

if find "${lab_dir}" -name '.venv' -prune -o -type f \( -name '*.png' -o -name '*.gif' \) -print -quit 2>/dev/null | grep -q .; then
  check "no PNG or GIF file left anywhere in the lab (exercise 9)" "no"
else
  check "no PNG or GIF file left anywhere in the lab (exercise 9)" "yes"
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
