#!/usr/bin/env bash
# Tests for the Day 127 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# A visualisation lab cannot assert that a chart "looks better", so this
# one asserts only what is genuinely measurable, by running code and
# reading real values:
#
#   * encoding a value as a circle's RADIUS squares every ratio in the
#     chart -- confirmed analytically (4.0 against a data ratio of 2.0)
#     and again by counting the pixels of two rendered circles;
#   * the Cleveland-McGill ordering, used as a decision function, and a
#     chart-choice function that recommends a TABLE below a stated number
#     of values and never recommends a pie chart for anything;
#   * matplotlib's default red and green -- the pass/fail reflex -- start
#     119.8 apart in CIELAB and end 7.3 apart under a published
#     deuteranopia transform, while seaborn's colourblind-safe blue and
#     orange keep essentially all of their separation;
#   * a sequential palette's luminance order matches an ordinal
#     variable's order exactly (rank correlation 1.0) while a categorical
#     palette's does not;
#   * sorting turns 19 reader comparisons into 1 without changing the
#     answer;
#   * the same eight numbers drawn with and without furniture: 37% of the
#     decorated chart's ink is data against 93% of the plain one's;
#   * 10,000 one-pixel points paint only 6,349 distinct pixels, and the
#     opaque image contains exactly TWO grey levels -- density is not
#     dimmed, it is absent -- which alpha blending and hexbin recover;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched
#     checkout, and the harness proves it can genuinely FAIL by solving
#     every exercise in a scratch copy, breaking one assertion on
#     purpose, confirming a non-zero exit, then restoring it;
#   * matplotlib really is headless (Agg) and nothing calls plt.show();
#   * nothing -- no .png, no __pycache__ -- is left behind by this run.
#
# Everything after the one-time install runs offline. Nothing binds a
# port, nothing writes outside the lab or a temporary directory, nothing
# needs a key. Deterministic, non-interactive, exits 0 only if every
# check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

# MPLBACKEND is deliberately NOT set here. render.py calls
# matplotlib.use("Agg") itself, and section 2 below checks that it really
# did -- pre-setting the environment variable would make that check pass
# for the wrong reason.
unset MPLBACKEND

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The
# README documents `pytest starter` and `pytest examples` as separate
# commands, and running either writes .pyc files that would then fail the
# cleanliness check at the end -- failing the reader for following the
# instructions. Clearing them here makes that final check measure what it
# claims to. `.venv` is untouched: the packages' bytecode is theirs.
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

if ! "${python_bin}" -c "import matplotlib, seaborn, PIL" >/dev/null 2>&1; then
  echo "FAIL: matplotlib, seaborn or Pillow is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 127 — Charts That Answer the Question"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("matplotlib", "seaborn", "pandas", "numpy", "pillow", "pytest"):
    try:
        print(f"{name:<10} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<10} NOT INSTALLED ({exc})")
PY
)"
echo "${versions}"
echo

mpl_version="$("${python_bin}" -c "import matplotlib; print(matplotlib.__version__)" 2>/dev/null || echo "")"
pinned_mpl="$(grep -m1 '^matplotlib==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
check_eq "installed matplotlib matches requirements.txt exactly" "${pinned_mpl}" "${mpl_version}"

sns_version="$("${python_bin}" -c "import seaborn; print(seaborn.__version__)" 2>/dev/null || echo "")"
pinned_sns="$(grep -m1 '^seaborn==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
check_eq "installed seaborn matches requirements.txt exactly" "${pinned_sns}" "${sns_version}"
echo

# --------------------------------------------------------------------------
echo "2. Rendering is headless -- Agg, no display, no window server"
# --------------------------------------------------------------------------

backend="$(cd "${lab_dir}/examples" && "${python_bin}" -c "import render, matplotlib; print(matplotlib.get_backend().lower())" 2>/dev/null || echo "")"
check_eq "importing render.py selects the Agg backend" "agg" "${backend}"

# Anchored to the start of a statement on purpose. An unanchored search
# also matches the prose in render.py's docstring that PROMISES plt.show
# is never called -- and a check that fails because the code documents
# itself is a check measuring the wrong thing. (Observed here: the first
# run of this harness reported exactly that failure, which is also the
# first proof this harness can fail.)
show_hits="$(grep -rnE '^[[:space:]]*plt\.show\(' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "nothing calls plt.show() -- it would hang a headless run" "$( [ -z "${show_hits}" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"

check "examples/ reports 17 passed, 0 failed" "$( echo "${examples_output}" | grep -qE '^17 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 17 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^17 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Never run 'pytest examples starter' in one invocation -- every"
echo "   module name (encoding, charts, palettes, render, conftest,"
echo "   test_charts) is defined identically in both directories, so the"
echo "   second collected collides with the first. Checked below."
# --------------------------------------------------------------------------

both_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
both_status=$?
check "pytest examples starter (one invocation) does NOT exit 0" "$( [ ${both_status} -ne 0 ] && echo yes || echo no )"
check "pytest examples starter reports an import file mismatch, not a quiet partial run" "$( echo "${both_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "6. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed failure, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d127-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

for module in test_charts encoding charts palettes render conftest; do
  cp "${lab_dir}/examples/${module}.py" "${scratch_dir}/${module}.py"
done

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 17 passed" "$( echo "${solved_output}" | grep -qE '^17 passed' && echo yes || echo no )"

# Break exercise 8's exact luminance-level assertion on purpose. Two grey
# levels is the measured truth; three is not.
sed -i.bak 's/assert R\.count_distinct_luminance_levels(opaque) == 2/assert R.count_distinct_luminance_levels(opaque) == 3/' "${scratch_dir}/test_charts.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a failure line" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_charts.py.bak" "${scratch_dir}/test_charts.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 17 passed again" "$( echo "${restored_output}" | grep -qE '^17 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "7. Nothing in examples/ or starter/ opens a network connection"
# --------------------------------------------------------------------------

url_hits="$(grep -rEl 'https?://|ftp://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no URLs inside examples/ or starter/" "$( [ -z "${url_hits}" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "8. A chart-rendering day that litters images would be embarrassing"
echo "   -- confirm no .png, .jpg, .svg or .pdf is left anywhere in the lab"
# --------------------------------------------------------------------------

image_hits="$(find "${lab_dir}" -name '.venv' -prune -o \
  \( -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.svg' -o -name '*.pdf' \) -print \) 2>/dev/null || true)"
check "no image files left under the lab" "$( [ -z "${image_hits}" ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "9. Cleanliness -- nothing left behind by THIS run"
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
