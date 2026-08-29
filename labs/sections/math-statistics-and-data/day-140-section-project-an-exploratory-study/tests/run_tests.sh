#!/usr/bin/env bash
# Tests for the Day 140 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by running code and reading real
# values, never by reading source:
#
#   * the committed dataset still matches the generator that produced it,
#     and still carries its four deliberate defects;
#   * the worked study runs the whole arc end to end and writes eleven
#     files, and the numbers it measures are the ones this lab reports;
#   * the planted effect of 6.0 ug/m3 falls inside the 95% interval the
#     study measured on its untouched confirmation half;
#   * the acceptance harness accepts that study on all eight gates;
#   * one defect at a time -- a missing question, an incomplete source
#     record, an unstated grain, a changelog masquerading as a damage
#     report, a peeked confirmation set, an estimate with no interval, an
#     unlabelled figure, an output that moved -- fails exactly the gate it
#     should, and the finding names the file, field, step or sentence;
#   * a study that peeked at its confirmation half is byte-identical to one
#     that did not, everywhere except the research log;
#   * the worked study rebuilds byte-for-byte identically, figures included;
#   * removing ONE required element from the complete worked study fails
#     exactly one gate by name -- the harness proved able to fail on a real
#     study, not only on fixtures;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one gate on purpose, confirming
#     a non-zero exit and a printed failure, then restoring it;
#   * no file is left behind anywhere, and no lab source opens a network
#     connection.
#
# Everything after the one-time install runs offline. Nothing binds a port,
# nothing needs a key. Deterministic, non-interactive, exits 0 only if
# every check passes.
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

if ! "${python_bin}" -c "import numpy, pandas, matplotlib" >/dev/null 2>&1; then
  echo "FAIL: numpy, pandas and/or matplotlib is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

scratch="$(mktemp -d "${TMPDIR:-/tmp}/day140-tests-XXXXXX")"
cleanup() { rm -rf "${scratch}"; }
trap cleanup EXIT

echo "Day 140 — Section Project: An Exploratory Study"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("numpy", "pandas", "matplotlib", "pytest"):
    print(f"{name:<10} {version(name)}")
print(f"platform   {platform.platform()}")
print(f"exe        {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

for pkg in numpy pandas matplotlib pytest; do
  pinned="$(grep -E "^${pkg}==" "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${pkg}'))")"
  check_eq "installed ${pkg} matches requirements.txt" "${pinned}" "${installed}"
done

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_question_recorded 02_provenance_complete 03_grain_asserted \
              04_damage_report 05_confirmation_untouched \
              06_uncertainty_in_the_prose 07_figures_carry_claims \
              08_reproducibility 09_whole_harness; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -5 | sed 's/^/      /'
  else
    check "${script}.py exits 0" "yes"
  fi
  case "${out}" in
    *"OK:"*) check "${script}.py reports OK" "yes" ;;
    *)       check "${script}.py reports OK" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "3. The worked study: real numbers, measured now, not quoted"
# --------------------------------------------------------------------------

measured="$(cd "${lab_dir}/examples" && "${python_bin}" - "${scratch}" <<'PY'
import sys
from pathlib import Path

import acceptance
import dataset as ds
import study

root = Path(sys.argv[1])
summary = study.build_study(root / "study")
files = sorted(
    p.relative_to(root / "study").as_posix()
    for p in (root / "study").rglob("*")
    if p.is_file()
)
verdict = acceptance.check_study(root / "study")

print(f"rows_in={summary['rows_in']}")
print(f"rows_out={summary['rows_out']}")
print(f"grain_violations={summary['grain_violations']}")
print(f"damage_steps={summary['damage_steps']}")
print(f"comparison_count={summary['comparison_count']}")
print(f"difference={summary['difference']:.2f}")
print(f"ci_low={summary['ci_low']:.2f}")
print(f"ci_high={summary['ci_high']:.2f}")
print(f"true_difference={ds.TRUE_DIFFERENCE}")
print(f"interval_covers_truth="
      f"{summary['ci_low'] < ds.TRUE_DIFFERENCE < summary['ci_high']}")
print(f"file_count={len(files)}")
print(f"gate_count={len(verdict.gates)}")
print(f"verdict_ok={verdict.ok}")
print(f"failed_gates={','.join(verdict.failed_gates) or 'none'}")

# Two builds, byte for byte.
study.build_study(root / "again")
same_md = all(
    (root / "study" / n).read_bytes() == (root / "again" / n).read_bytes()
    for n in ("REPORT.md", "CLEANING.md", "QUESTION.md", "RESEARCH_LOG.md")
)
same_all = all(
    (root / "study" / rel).read_bytes() == (root / "again" / rel).read_bytes()
    for rel in study.manifest_targets(root / "study") + [study.MANIFEST_NAME]
)
print(f"markdown_identical={same_md}")
print(f"everything_identical={same_all}")
PY
)"
mstatus=$?
echo "${measured}" | sed 's/^/  /'
if [ "${mstatus}" -ne 0 ]; then
  check "the worked study builds and is graded" "no"
else
  check "the worked study builds and is graded" "yes"
fi

value_of() { printf '%s\n' "${measured}" | grep "^$1=" | cut -d= -f2-; }

check_eq "the delivery carries 264 rows"            "264"  "$(value_of rows_in)"
check_eq "245 rows survive cleaning"                "245"  "$(value_of rows_out)"
check_eq "8 rows violate the grain on arrival"      "8"    "$(value_of grain_violations)"
check_eq "the damage report has four measured steps" "4"   "$(value_of damage_steps)"
check_eq "the research log records 4 comparisons"   "4"    "$(value_of comparison_count)"
check_eq "the study writes 11 files"                "11"   "$(value_of file_count)"
check_eq "the harness runs 8 gates"                 "8"    "$(value_of gate_count)"
check_eq "the worked study is ACCEPTED"             "True" "$(value_of verdict_ok)"
check_eq "no gate fails on the worked study"        "none" "$(value_of failed_gates)"
check_eq "the planted 6.0 difference falls inside the measured interval" \
  "True" "$(value_of interval_covers_truth)"
check_eq "two builds produce identical Markdown"    "True" "$(value_of markdown_identical)"
check_eq "two builds produce identical everything, figures included" \
  "True" "$(value_of everything_identical)"

# --------------------------------------------------------------------------
echo
echo "4. One defect at a time fails exactly the gate it should"
# --------------------------------------------------------------------------

defects="$(cd "${lab_dir}/examples" && "${python_bin}" - "${scratch}" <<'PY'
import sys
from pathlib import Path

import acceptance
import fixtures as fx

root = Path(sys.argv[1])
good = root / "study"

cases = [
    ("missing-question", fx.break_missing_question, "question_recorded", True),
    ("incomplete-source", fx.break_provenance, "provenance_complete", True),
    ("stale-checksum", fx.break_provenance_checksum, "provenance_complete", True),
    ("no-grain", fx.break_grain, "grain_asserted", True),
    ("unverified-grain", fx.break_grain_unverified, "grain_asserted", True),
    ("changelog-not-damage", fx.break_damage_report, "damage_report_quantified", True),
    ("peeked-confirmation", fx.break_confirmation_peeked, "confirmation_untouched", True),
    ("no-interval", fx.break_uncertainty, "uncertainty_reported", True),
    ("unlabelled-figure", fx.break_figure_label, "figures_documented", True),
    ("stray-figure", fx.break_figure_undocumented, "figures_documented", True),
    ("output-moved", fx.break_reproducibility, "outputs_reproducible", False),
]

for label, mutator, gate_name, rewrite in cases:
    broken = fx.variant(good, root / f"broken-{label}", mutator,
                        rewrite_manifest=rewrite)
    verdict = acceptance.check_study(broken)
    only = ",".join(verdict.failed_gates)
    named = verdict.gate(gate_name).findings[0] if not verdict.gate(gate_name).ok else ""
    print(f"{label}|{only}|{gate_name}|{named}")
PY
)"

while IFS='|' read -r label only expected finding; do
  [ -z "${label}" ] && continue
  check_eq "${label} fails only ${expected}" "${expected}" "${only}"
  case "${finding}" in
    *.md*|*.json*|*fig-*)
      check "${label}: the finding names a file, field, step or sentence" "yes" ;;
    *) check "${label}: the finding names a file, field, step or sentence (got '${finding}')" "no" ;;
  esac
done <<< "${defects}"

# --------------------------------------------------------------------------
echo
echo "5. A peeked confirmation set is invisible outside the research log"
# --------------------------------------------------------------------------

peek="$(cd "${lab_dir}/examples" && "${python_bin}" - "${scratch}" <<'PY'
import sys
from pathlib import Path

import acceptance
import fixtures as fx

root = Path(sys.argv[1])
good = root / "study"
peeked = fx.variant(good, root / "peeked", fx.break_confirmation_peeked)

identical = [
    n for n in ("REPORT.md", "FIGURES.json", "CLEANING.md", "SOURCE.json",
                "INGEST.json", "QUESTION.md")
    if (good / n).read_bytes() == (peeked / n).read_bytes()
]
log_differs = (good / "RESEARCH_LOG.md").read_bytes() != (
    peeked / "RESEARCH_LOG.md"
).read_bytes()
print(f"identical_files={len(identical)}")
print(f"log_differs={log_differs}")
print(f"caught={acceptance.check_study(peeked).failed_gates == ('confirmation_untouched',)}")
PY
)"
echo "${peek}" | sed 's/^/  /'
peek_of() { printf '%s\n' "${peek}" | grep "^$1=" | cut -d= -f2-; }
check_eq "six study files are byte-identical between the honest and peeked study" \
  "6" "$(peek_of identical_files)"
check_eq "only the research log differs" "True" "$(peek_of log_differs)"
check_eq "and the harness still catches the peek" "True" "$(peek_of caught)"

# --------------------------------------------------------------------------
echo
echo "6. Removing ONE required element from the real study fails one gate"
# --------------------------------------------------------------------------

# This is the proof that matters. A harness only ever exercised against
# purpose-built fixtures has not been shown to work on a real study. Here a
# single line -- the checksum field -- is deleted from the complete, passing
# worked study, and the verdict must name exactly that.
one="$(cd "${lab_dir}/examples" && "${python_bin}" - "${scratch}" <<'PY'
import json
import sys
from pathlib import Path

import acceptance
import fixtures as fx

root = Path(sys.argv[1])


def remove_checksum(study_dir: Path) -> None:
    path = study_dir / "SOURCE.json"
    payload = json.loads(path.read_text())
    del payload["checksum_sha256"]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


broken = fx.variant(root / "study", root / "one-element", remove_checksum)
verdict = acceptance.check_study(broken)
print(f"ok={verdict.ok}")
print(f"failed={','.join(verdict.failed_gates)}")
print(f"findings={len(verdict.findings)}")
print(f"finding={verdict.findings[0]}")
PY
)"
echo "${one}" | sed 's/^/  /'
one_of() { printf '%s\n' "${one}" | grep "^$1=" | cut -d= -f2-; }
check_eq "the study is no longer accepted"      "False" "$(one_of ok)"
check_eq "exactly one gate fails"               "provenance_complete" "$(one_of failed)"
check_eq "exactly one finding is reported"      "1" "$(one_of findings)"
check_eq "and it names the deleted field"       "SOURCE.json is missing: checksum_sha256" \
  "$(one_of finding)"

# --------------------------------------------------------------------------
echo
echo "7. The reference pytest suite: real values, real exceptions"
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
if [ "${ref_passed:-0}" -ge 50 ]; then
  check "the reference suite ran at least 50 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 50 tests (ran ${ref_passed:-0})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "8. The starter suite skips unattempted work instead of failing it"
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
  *)         check "unwritten exercises are reported as skipped, not passed" "no" ;;
esac

# The import guard. Both directories contain modules called `acceptance`,
# `study`, `dataset` and `fixtures`; each directory's conftest.py prevents a
# cross-import. Auto-discovering both from the lab root must report the same
# skip count as `pytest starter` alone.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "auto-discovering both suites does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "9. The starter suite can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section solves every exercise in a SCRATCH copy of starter/ by dropping in
# the reference harness, breaks one gate on purpose, and asserts the suite
# reports the failure and exits non-zero. Nothing under the lab is modified.
solved="${scratch}/solved"
mkdir -p "${solved}"
cp "${lab_dir}/starter/"*.py "${solved}/"
cp "${lab_dir}/starter/00_brief.md" "${solved}/"
mkdir -p "${solved}/data"
cp "${lab_dir}/starter/data/observations.csv" "${solved}/data/"
cp "${lab_dir}/examples/acceptance.py" "${solved}/acceptance.py"

solved_out="$(cd "${scratch}" && "${pytest_bin}" solved -q -p no:cacheprovider 2>&1)"
solved_status=$?
echo "${solved_out}" | tail -2 | sed 's/^/  /'
if [ "${solved_status}" -eq 0 ]; then
  check "a fully solved starter passes every exercise" "yes"
else
  check "a fully solved starter passes every exercise" "no"
fi
solved_passed="$(printf '%s\n' "${solved_out}" | grep -o '[0-9][0-9]* passed' | head -1 | cut -d' ' -f1)"
check_eq "the solved starter runs all 33 exercises" "33" "${solved_passed:-0}"

# Now break exactly one thing: make the provenance gate stop verifying the
# checksum it was handed. The suite must notice.
"${python_bin}" - "${solved}/acceptance.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
src = path.read_text()
needle = "    recorded = payload.get(\"checksum_sha256\")\n    local = payload.get(\"path\")"
assert needle in src, "the self-test needs the provenance checksum block"
path.write_text(src.replace(needle, "    recorded = None\n    local = None"))
PY

broken_out="$(cd "${scratch}" && "${pytest_bin}" solved -q -p no:cacheprovider 2>&1)"
broken_status=$?
echo "${broken_out}" | tail -3 | sed 's/^/  /'
if [ "${broken_status}" -ne 0 ]; then
  check "breaking one gate makes the starter suite exit non-zero (${broken_status})" "yes"
else
  check "breaking one gate makes the starter suite exit non-zero" "no"
fi
case "${broken_out}" in
  *"test_provenance_gate_verifies_the_checksum"*)
    check "the failing test is named in the output" "yes" ;;
  *) check "the failing test is named in the output" "no" ;;
esac
case "${broken_out}" in
  *"the gate must recompute it"*)
    check "the failure message explains what went wrong" "yes" ;;
  *) check "the failure message explains what went wrong" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "10. Nothing was left behind"
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

# The scripts and the study builder write only into temporary directories.
# Nothing may have appeared under examples/ or starter/ beyond what ships.
expected_files="examples/01_question_recorded.py
examples/02_provenance_complete.py
examples/03_grain_asserted.py
examples/04_damage_report.py
examples/05_confirmation_untouched.py
examples/06_uncertainty_in_the_prose.py
examples/07_figures_carry_claims.py
examples/08_reproducibility.py
examples/09_whole_harness.py
examples/acceptance.py
examples/conftest.py
examples/data/observations.csv
examples/dataset.py
examples/fixtures.py
examples/study.py
examples/test_reference.py
starter/00_brief.md
starter/acceptance.py
starter/conftest.py
starter/data/observations.csv
starter/dataset.py
starter/fixtures.py
starter/study.py
starter/test_starter.py"
actual_files="$(cd "${lab_dir}" && find examples starter -type f | sed 's|^\./||' | LC_ALL=C sort)"
check_eq "the lab's own directories contain exactly the files that ship" \
  "$(printf '%s\n' "${expected_files}" | LC_ALL=C sort | tr '\n' ' ')" \
  "$(printf '%s\n' "${actual_files}" | LC_ALL=C sort | tr '\n' ' ')"

if [ -d "${lab_dir}/study" ] || [ -d "${lab_dir}/examples/study" ]; then
  check "no study directory was written inside the lab" "no"
else
  check "no study directory was written inside the lab" "yes"
fi

if grep -rqE 'urlopen|requests\.|socket\.|http://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
