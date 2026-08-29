#!/usr/bin/env bash
# Tests for the Day 132 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and measuring
# real rendered geometry, never by diffing image bytes:
#
#   * the lie factor -- 1.00 for a zero-baseline bar pair, 2.94 for the
#     same two numbers on a truncated axis, with the shown ratio read off
#     the drawn bars rather than off the inputs;
#   * truncation is fatal for bars and neutral for lines -- the bar's lie
#     factor exceeds 2.5 while the line's is exactly 1.0 on every
#     baseline tried;
#   * dual axes -- scaling CANNOT change the drawn correlation (invariant
#     to 3e-15 over 500 random scalings), inverting one axis negates it
#     exactly, and the tracking gap is a free parameter that reaches the
#     same value for r = -0.001 and for r = +0.913;
#   * a trend whose sign flips between two windows of one series;
#   * two textbook bin rules that draw one hump and two humps;
#   * radius encoding, whose shown area ratio is the square of the data
#     ratio;
#   * 3D perspective departing from the data ratio by 17% and by 110%
#     depending only on where the taller bar stands;
#   * ordering, annotation and luminance separation;
#   * a caption contract that passes an honest chart, fails a truncated
#     one, and passes a disclosed rule break;
#   * nothing left behind on disk.
#
# Everything after the one-time install runs offline. Nothing binds a
# port, nothing writes outside the lab, nothing needs a key.
# Deterministic, non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1
export MPLBACKEND=Agg

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that
# would then fail the cleanliness check at the end of this script --
# failing the reader for following the instructions. Clearing them here
# makes that final check measure what it claims to. `.venv` is untouched,
# because the packages' own bytecode is theirs, not ours.
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

for module in matplotlib seaborn pandas numpy; do
  if ! "${python_bin}" -c "import ${module}" >/dev/null 2>&1; then
    echo "FAIL: ${module} is not importable from ${python_bin}." >&2
    echo "  Install the lab's dependencies with:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    exit 1
  fi
done

echo "Day 132 — Visual Storytelling and Chart Honesty"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python      {platform.python_version()}")
for name in ("matplotlib", "seaborn", "pandas", "numpy", "pytest"):
    print(f"{name:<11} {version(name)}")
print(f"platform    {platform.platform()}")
PY
)"
echo "${versions}" | sed 's/^/  /'

for package in matplotlib seaborn pandas numpy pytest; do
  pinned="$(grep -E "^${package}==" "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${package}'))")"
  check_eq "installed ${package} matches requirements.txt" "${pinned}" "${installed}"
done

backend="$("${python_bin}" -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; print(plt.get_backend())")"
check_eq "matplotlib runs on the headless Agg backend" "agg" "$(echo "${backend}" | tr '[:upper:]' '[:lower:]')"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_lie_factor 02_bars_versus_lines 03_dual_axes \
              04_cherry_picked_window 05_binning_changes_the_conclusion \
              06_radius_versus_area 07_three_d_distortion \
              08_ordering_and_annotation 09_caption_contract; do
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
echo "3. The headline numbers, measured here and now"
# --------------------------------------------------------------------------

measured="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
import matplotlib.pyplot as plt
import honesty as H

lf_zero, _, _ = H.bar_pair_lie_factor((100.0, 102.0))
lf_trunc, shown, _ = H.bar_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
lf_line, _, _ = H.line_pair_lie_factor((100.0, 102.0), ylim=(99, 103))
print(f"lf_zero {lf_zero:.4f}")
print(f"lf_trunc {lf_trunc:.4f}")
print(f"shown_trunc {shown:.4f}")
print(f"lf_line {lf_line:.4f}")


def dual(a, b, la, lb, invert=False):
    if invert:
        lb = (lb[1], lb[0])
    fig, ax, ax2 = H.dual_axis_figure(a, b, ylim_a=la, ylim_b=lb)
    try:
        fig.canvas.draw()
        ta, tb = H.drawn_trace(ax), H.drawn_trace(ax2)
        return H.tracking_gap(ta, tb), H.pearson(ta, tb)
    finally:
        plt.close(fig)


a, b = H.uncorrelated_pair()
c, d = H.correlated_pair()
gap_apart, r_apart = dual(a, b, H.banded_limits(a, .55, .95), H.banded_limits(b, .05, .45))
gap_wide, r_wide = dual(a, b, H.widened_limits(a), H.widened_limits(b))
gap_strong, _ = dual(c, d, H.widened_limits(c), H.widened_limits(d))
_, r_inv = dual(c, d, H.matched_limits(c), H.matched_limits(d), invert=True)
print(f"data_r {H.pearson(a, b):.6f}")
print(f"drawn_r_apart {r_apart:.6f}")
print(f"drawn_r_wide {r_wide:.6f}")
print(f"gap_apart {gap_apart:.4f}")
print(f"gap_wide {gap_wide:.4f}")
print(f"gap_strong {gap_strong:.4f}")
print(f"strong_r {H.pearson(c, d):.6f}")
print(f"strong_r_inverted {r_inv:.6f}")

values = H.dipping_series()
half = len(values) // 2
print(f"slope_first {H.trend_slope(values[:half]):.4f}")
print(f"slope_second {H.trend_slope(values[half:]):.4f}")

sample = H.bimodal_sample()
print(f"modes_sturges {H.count_modes(H.histogram_counts(sample, bins='sturges'))}")
print(f"modes_fd {H.count_modes(H.histogram_counts(sample, bins='fd'))}")

fig, ax = H.bubble_pair((25.0, 100.0), encode="radius")
fig.canvas.draw()
print(f"bubble_area_ratio {H.drawn_area_ratio(ax):.2f}")
plt.close(fig)

far = H.bar3d_projected_areas([1.0, 2.0], [0.0, 3.0])
near = H.bar3d_projected_areas([1.0, 2.0], [3.0, 0.0])
print(f"ratio_3d_far {far[1] / far[0]:.3f}")
print(f"ratio_3d_near {near[1] / near[0]:.3f}")
print(f"lum_red_green {H.luminance_separation(H.CLASSIC_RED, H.CLASSIC_GREEN):.4f}")
print(f"lum_emphasis {H.luminance_separation(H.HIGHLIGHT, H.MUTED):.4f}")
PY
)"
echo "${measured}" | sed 's/^/  /'

value_of() { printf '%s\n' "${measured}" | grep "^$1 " | cut -d' ' -f2; }

check_eq "a zero-baseline bar pair has lie factor 1.0000" "1.0000" "$(value_of lf_zero)"
check_eq "the truncated bar pair draws a 3.0000 height ratio" "3.0000" "$(value_of shown_trunc)"
check_eq "the truncated bar pair has lie factor 2.9412" "2.9412" "$(value_of lf_trunc)"
check_eq "the same numbers as a line have lie factor 1.0000" "1.0000" "$(value_of lf_line)"
check_eq "the demonstration pair's data correlation" "-0.001034" "$(value_of data_r)"
check_eq "scaling apart leaves the drawn correlation unchanged" "-0.001034" "$(value_of drawn_r_apart)"
check_eq "scaling together leaves the drawn correlation unchanged" "-0.001034" "$(value_of drawn_r_wide)"
check_eq "inverting one axis negates a strong correlation exactly" "-0.913234" "$(value_of strong_r_inverted)"
check_eq "the separated scaling draws a 0.4938 tracking gap" "0.4938" "$(value_of gap_apart)"
check_eq "the widened scaling draws a 0.0147 tracking gap" "0.0147" "$(value_of gap_wide)"
check_eq "a strongly correlated pair draws the same small gap" "0.0046" "$(value_of gap_strong)"
check_eq "the first window's trend slope is negative" "-0.7305" "$(value_of slope_first)"
check_eq "the second window's trend slope is positive" "0.7045" "$(value_of slope_second)"
check_eq "Sturges' rule draws one hump" "1" "$(value_of modes_sturges)"
check_eq "Freedman-Diaconis draws two humps" "2" "$(value_of modes_fd)"
check_eq "radius encoding squares a data ratio of 4 into 16" "16.00" "$(value_of bubble_area_ratio)"
check_eq "3D, taller bar far, draws a 2.341 ratio (data ratio 2)" "2.341" "$(value_of ratio_3d_far)"
check_eq "3D, taller bar near, draws a 4.204 ratio (data ratio 2)" "4.204" "$(value_of ratio_3d_near)"
check_eq "red and green differ by only 0.0996 in luminance" "0.0996" "$(value_of lum_red_green)"
check_eq "deliberate emphasis reaches 0.5505 in luminance" "0.5505" "$(value_of lum_emphasis)"

# --------------------------------------------------------------------------
echo
echo "4. The reference pytest suite: real geometry, real exceptions"
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
if [ "${ref_passed:-0}" -ge 40 ]; then
  check "the reference suite ran at least 40 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 40 tests (ran ${ref_passed:-0})" "no"
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

# The import guard. Both directories contain a module called `honesty`,
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
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green suite proves nothing until you have watched it go red. This
# section re-runs the caption contract with the zero-baseline rule
# deliberately removed, and asserts the re-run reports the failure and
# exits non-zero. Nothing on disk is modified: the reference function is
# replaced in memory for the duration of one subprocess.
if [ -z "${D132_SELF_TEST:-}" ]; then
  self_out="$(cd "${lab_dir}/examples" && D132_SELF_TEST=1 "${python_bin}" -c "
import honesty as H

def _toothless(ax, caption):
    # a review tool that approves of everything -- the exact failure mode
    # a checklist is supposed to prevent
    return True, []

H.review_chart = _toothless
exec(open('09_caption_contract.py').read())
" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a review function that approves everything makes script 09 exit non-zero (${self_status})" "yes"
  else
    check "a review function that approves everything makes script 09 exit non-zero" "no"
  fi
  case "${self_out}" in
    *"AssertionError"*"the truncated chart must fail the contract"*)
      check "the failing assertion is named in the output" "yes" ;;
    *) check "the failing assertion is named in the output" "no" ;;
  esac

  # And the same for a measurement, not just a check: a lie_factor that
  # ignores the drawn geometry and reports 1.0 for everything must be
  # caught by script 01.
  self2_out="$(cd "${lab_dir}/examples" && D132_SELF_TEST=1 "${python_bin}" -c "
import honesty as H
H.lie_factor = lambda shown, data: 1.0
exec(open('01_lie_factor.py').read())
" 2>&1)"
  self2_status=$?
  if [ "${self2_status}" -ne 0 ]; then
    check "a lie_factor stuck at 1.0 makes script 01 exit non-zero (${self2_status})" "yes"
  else
    check "a lie_factor stuck at 1.0 makes script 01 exit non-zero" "no"
  fi
else
  echo "  (self-test run: section 6 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "7. Nothing was left behind"
# --------------------------------------------------------------------------

# `.venv` is pruned from every search below. The virtual environment ships
# matplotlib's, pandas' and pytest's own precompiled bytecode -- hundreds
# of __pycache__ directories that came with the packages and have nothing
# to do with whether THIS lab tidied up after itself.

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

# This lab draws around fifty figures. Not one of them may reach the disk.
if find "${lab_dir}" -name '.venv' -prune -o -type f \( -name '*.png' -o -name '*.svg' -o -name '*.pdf' \) -print -quit 2>/dev/null | grep -q .; then
  check "no image file (.png/.svg/.pdf) left by the lab's own code" "no"
  find "${lab_dir}" -name '.venv' -prune -o -type f \( -name '*.png' -o -name '*.svg' -o -name '*.pdf' \) -print 2>/dev/null | sed 's/^/      /'
else
  check "no image file (.png/.svg/.pdf) left by the lab's own code" "yes"
fi

# Match a real CALL at the start of a statement, not the "never call
# plt.show()" warnings the lab's own docstrings carry -- an earlier
# version of this check matched those and failed the lab for documenting
# the rule it follows.
if grep -rnE '^[[:space:]]*plt\.show\(' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source calls plt.show()" "no"
else
  check "no lab source calls plt.show()" "yes"
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
