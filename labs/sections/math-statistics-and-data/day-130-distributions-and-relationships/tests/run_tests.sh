#!/usr/bin/env bash
# Tests for the Day 130 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running real NumPy / seaborn /
# matplotlib / pandas code and reading real computed values -- never by
# reading source or comparing image bytes:
#
#   * the same 500-point bimodal sample shows 1 mode at 5 bins, 2 modes
#     under Freedman-Diaconis, and more than 10 spurious modes at 100 bins;
#   * on a skewed sample, 'sturges', 'scott' and 'fd' choose three
#     different bin counts;
#   * a KDE bandwidth (bw_adjust) of 1.0 finds 2 modes on the bimodal
#     sample and 3.0 (over-smoothed) finds 1;
#   * a KDE of strictly positive data assigns a real, non-trivial fraction
#     of its density below zero;
#   * two samples engineered to share a five-number summary within 0.3
#     units nonetheless show 2 modes and 1 mode respectively at 15 bins --
#     the boxplot's blind spot, demonstrated directly;
#   * an ECDF passes through every observation, and reading its median off
#     the curve matches numpy.median to 1e-9;
#   * a small, dense scatter of 20,000 points paints under half as many
#     distinct screen pixels as there are points, and a hexbin of the same
#     data recovers a real density peak;
#   * a strong quadratic relationship has near-zero Pearson AND Spearman
#     correlation, while a fitted quadratic's R^2 exceeds 0.95;
#   * jittered positions never move more than the stated jitter width, and
#     the source data is provably untouched;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed FAIL, then restoring it;
#   * nothing is left behind on disk.
#
# Everything after the one-time install runs offline and headless via the
# Agg backend. Nothing binds a port, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1
export MPLBACKEND=Agg

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

if ! "${python_bin}" -c "import seaborn" >/dev/null 2>&1; then
  echo "FAIL: seaborn is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 130 — Pictures of a Distribution"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("seaborn", "matplotlib", "pandas", "numpy", "pytest"):
    try:
        print(f"{name:<10} {version(name)}")
    except Exception as exc:  # pragma: no cover
        print(f"{name:<10} NOT INSTALLED ({exc})")
PY
)"
echo "${versions}"
echo

mismatch=0
while IFS= read -r line; do
  [ -z "${line}" ] && continue
  pkg="${line%%==*}"
  pinned="${line#*==}"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${pkg}'))" 2>/dev/null || echo "MISSING")"
  if [ "${installed}" != "${pinned}" ]; then
    mismatch=1
    echo "  version mismatch: ${pkg} pinned ${pinned}, installed ${installed}"
  fi
done < "${lab_dir}/requirements/requirements.txt"
check "installed packages match requirements.txt exactly" "$( [ ${mismatch} -eq 0 ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "2. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"

examples_passed_line="$(echo "${examples_output}" | grep -E '^[0-9]+ passed' || true)"
check "examples/ reports 9 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^9 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 9 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^9 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Never run 'pytest examples starter' in one invocation -- same"
echo "   module name (test_distributions.py) in both directories means"
echo "   pytest collects them by dotted module name and the second can"
echo "   collide with the first. Documented, and run only as two commands."
# --------------------------------------------------------------------------

combined_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
combined_status=$?
check "'pytest examples starter' aborts collection rather than silently passing" "$( [ ${combined_status} -ne 0 ] && echo yes || echo no )"
check "the collision is reported as an import file mismatch" "$( echo "${combined_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed FAIL, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d130-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

cp "${lab_dir}/examples/test_distributions.py" "${scratch_dir}/test_distributions.py"
cp "${lab_dir}/examples/data.py" "${scratch_dir}/data.py"
cp "${lab_dir}/examples/conftest.py" "${scratch_dir}/conftest.py"

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 9 passed" "$( echo "${solved_output}" | grep -qE '^9 passed' && echo yes || echo no )"

# Break exercise 5's exact mode-count assertion on purpose.
sed -i.bak 's/assert bimodal_modes == 2/assert bimodal_modes == 99/' "${scratch_dir}/test_distributions.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a FAIL/failed line" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_distributions.py.bak" "${scratch_dir}/test_distributions.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 9 passed again" "$( echo "${restored_output}" | grep -qE '^9 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "6. Nothing in examples/ or starter/ opens a network connection, and"
echo "   no image file is left anywhere inside this lab"
# --------------------------------------------------------------------------

url_hits="$(grep -rEl 'https?://|ftp://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no URLs inside examples/ or starter/" "$( [ -z "${url_hits}" ] && echo yes || echo no )"

image_hits="$(find "${lab_dir}" -name '.venv' -prune -o -type f \( -iname '*.png' -o -iname '*.svg' -o -iname '*.jpg' -o -iname '*.pdf' \) -print 2>/dev/null || true)"
check "no image files left anywhere inside the lab" "$( [ -z "${image_hits}" ] && echo yes || echo no )"
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
