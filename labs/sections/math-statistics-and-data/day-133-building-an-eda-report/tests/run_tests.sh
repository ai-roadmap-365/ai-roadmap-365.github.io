#!/usr/bin/env bash
# Tests for the Day 133 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the day's claims by running the real report generator
# over the real frame and reading the document it produces -- never by
# reading source and never by comparing image bytes across machines:
#
#   * the generator REFUSES a figure with no stated question, and accepts
#     the identical figure once a question is attached;
#   * it REFUSES a caption that is a label ("revenue by region") and
#     accepts one carrying a number;
#   * the numbers printed in the prose move when one input value moves,
#     so the text cannot drift away from the figures;
#   * the rendered report has no orphan figure, and a deliberately
#     orphaned file is detected;
#   * every reported estimate carries a 95% interval or an explicit note
#     saying why none is available, and a bare point estimate is caught;
#   * two runs over the same input produce byte-identical Markdown, and
#     changing one input value changes it;
#   * the conclusion is rendered before the detailed evidence;
#   * 12 candidate figures go in and 5 come out -- the "so what" filter,
#     with the 7 discarded ones surviving only as one-line null results;
#   * every figure passes the accessibility contract, and a red-against-
#     green chart with unlabelled axes fails it with four named problems;
#   * the reference suite (`examples/`) passes in full;
#   * the exercise suite (`starter/`) is all-skip on an untouched checkout,
#     and the harness proves it can genuinely FAIL by solving every
#     exercise in a scratch copy, breaking one assertion on purpose,
#     confirming a non-zero exit and a printed failure, then restoring it;
#   * no image and no generated Markdown is left behind anywhere.
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

if ! "${python_bin}" -c "import matplotlib, pandas, numpy" >/dev/null 2>&1; then
  echo "FAIL: matplotlib, pandas or numpy is not importable from ${python_bin}." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

echo "Day 133 — A Report That Argues"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
from importlib.metadata import version

print(f"python     {platform.python_version()}")
for name in ("matplotlib", "seaborn", "pandas", "numpy", "pytest"):
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
echo "2. The generator's own rules, exercised directly"
# --------------------------------------------------------------------------

behaviour="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
"""Drive the report generator and print one machine-readable line per claim."""
import re
import shutil
import tempfile
from pathlib import Path

import data
import analysis
import report as R

frame = data.monthly_sales()
results = {}


def record(key, value):
    results[key] = value


# -- a figure must have a question -----------------------------------------
blank = R.Report(title="t", question="q", decision="d", provenance="p")
nameless = R.Candidate(
    slug="pretty", draw=analysis.draw_missing_by_column, analyse=analysis.analyse_missing
)
try:
    blank.add_panel(nameless, frame)
    record("refuses_questionless", "no")
except R.ReportError as exc:
    record("refuses_questionless", "yes" if "no stated question" in str(exc) else "no")
record("questionless_left_no_panel", "yes" if not blank.panels else "no")

asked = R.Candidate(
    slug="pretty",
    question="Which rows have no revenue?",
    draw=analysis.draw_missing_by_column,
    analyse=analysis.analyse_missing,
)
blank.add_panel(asked, frame)
record("accepts_with_question", "yes" if len(blank.panels) == 1 else "no")

# -- the caption must carry a claim ----------------------------------------
record("rejects_label_caption", "no" if R.carries_claim("revenue by region") else "yes")
record(
    "accepts_claim_caption",
    "yes"
    if R.carries_claim("three regions grew, and the fourth fell by 12% after the March change")
    else "no",
)

# -- the so-what filter ----------------------------------------------------
candidates = analysis.candidate_figures()
kept = R.survivors(candidates)
dropped = R.discarded(candidates)
record("candidates_total", str(len(candidates)))
record("candidates_kept", str(len(kept)))
record("candidates_dropped", str(len(dropped)))

# -- render twice, and once from a perturbed frame -------------------------
first_dir = Path(tempfile.mkdtemp(prefix="d133-a-"))
second_dir = Path(tempfile.mkdtemp(prefix="d133-b-"))
third_dir = Path(tempfile.mkdtemp(prefix="d133-c-"))
try:
    first = analysis.build_report(frame).render(first_dir, frame)
    second = analysis.build_report(frame).render(second_dir, frame)
    changed_frame = data.perturbed()
    third = analysis.build_report(changed_frame).render(third_dir, changed_frame)

    record(
        "markdown_byte_identical",
        "yes"
        if (first_dir / "report.md").read_bytes() == (second_dir / "report.md").read_bytes()
        else "no",
    )
    png_same = all(
        p.read_bytes() == (second_dir / "figures" / p.name).read_bytes()
        for p in sorted((first_dir / "figures").glob("*.png"))
    )
    record("figure_bytes_identical_same_machine", "yes" if png_same else "no")
    record("changed_input_changes_document", "yes" if third != first else "no")
    record("no_clock_reading_in_output", "no" if re.search(r"\b20\d\d-\d\d-\d\d\b", first) else "yes")

    def west(text):
        line = [ln for ln in text.splitlines() if "West change across the pricing change" in ln][0]
        return float(re.search(r"(-?\d+(?:\.\d+)?)%", line).group(1))

    record("west_change_original", f"{west(first):.1f}")
    record("west_change_perturbed", f"{west(third):.1f}")

    # -- ordering ----------------------------------------------------------
    order = [
        first.index("## Conclusion"),
        first.index("## What we looked at and found nothing in"),
        first.index("## Evidence"),
        first.index("## Caveats"),
        first.index("## Provenance"),
    ]
    record("sections_in_reader_order", "yes" if order == sorted(order) else "no")
    record(
        "conclusion_before_first_figure",
        "yes" if first.index("## Conclusion") < first.index("### Figure 1") else "no",
    )

    # -- orphans -----------------------------------------------------------
    figure_dir = first_dir / "figures"
    record("figures_written", str(len(list(figure_dir.glob("*.png")))))
    record("no_orphans_in_report", "yes" if R.orphan_figures(first, figure_dir) == [] else "no")
    shutil.copy(sorted(figure_dir.glob("*.png"))[0], figure_dir / "99-left-over.png")
    record(
        "orphan_is_detected",
        "yes" if R.orphan_figures(first, figure_dir) == ["99-left-over.png"] else "no",
    )

    # -- dropped candidates never reach the document -----------------------
    record(
        "dropped_slugs_absent_from_report",
        "yes" if all(c.slug not in first for c in dropped) else "no",
    )
    record(
        "null_results_kept_as_one_line_each",
        "yes" if all(c.dropped_because in first for c in dropped) else "no",
    )
finally:
    for directory in (first_dir, second_dir, third_dir):
        shutil.rmtree(directory, ignore_errors=True)

# -- uncertainty -----------------------------------------------------------
built = analysis.build_report(frame)
record("every_estimate_has_uncertainty", "yes" if R.missing_uncertainty(built) == [] else "no")
estimates = [p.finding.estimate for p in built.panels]
record("estimates_with_interval", str(sum(1 for e in estimates if e.low is not None)))
record("estimates_with_explicit_note", str(sum(1 for e in estimates if e.no_interval_note)))
built.add_panel(analysis.bare_point_estimate_candidate(), frame)
record(
    "bare_point_estimate_is_caught",
    "yes" if R.missing_uncertainty(built) == ["bare-total"] else "no",
)

# -- accessibility ---------------------------------------------------------
clean = all(R.accessibility_problems(c.draw, frame) == [] for c in kept)
record("every_figure_passes_accessibility", "yes" if clean else "no")
bad = R.accessibility_problems(analysis.draw_inaccessible, frame)
record("inaccessible_chart_problem_count", str(len(bad)))
record(
    "inaccessible_chart_names_both_colours",
    "yes" if any("#ff0000" in p for p in bad) and any("#008000" in p for p in bad) else "no",
)

for key, value in results.items():
    print(f"{key}={value}")
PY
)"
behaviour_status=$?
echo "${behaviour}"
echo

value_of() { echo "${behaviour}" | grep "^$1=" | cut -d= -f2-; }

check "the generator ran without error" "$( [ ${behaviour_status} -eq 0 ] && echo yes || echo no )"
check "refuses a figure with no stated question" "$( [ "$(value_of refuses_questionless)" = yes ] && echo yes || echo no )"
check "a refused figure leaves no half-added panel" "$( [ "$(value_of questionless_left_no_panel)" = yes ] && echo yes || echo no )"
check "accepts the identical figure once it has a question" "$( [ "$(value_of accepts_with_question)" = yes ] && echo yes || echo no )"
check "rejects the caption 'revenue by region' as a label" "$( [ "$(value_of rejects_label_caption)" = yes ] && echo yes || echo no )"
check "accepts a caption carrying a number" "$( [ "$(value_of accepts_claim_caption)" = yes ] && echo yes || echo no )"
check "12 candidate figures go in" "$( [ "$(value_of candidates_total)" = 12 ] && echo yes || echo no )"
check "5 survive the 'so what' filter and 7 do not" "$( [ "$(value_of candidates_kept)" = 5 ] && [ "$(value_of candidates_dropped)" = 7 ] && echo yes || echo no )"
check "two runs over the same input produce byte-identical Markdown" "$( [ "$(value_of markdown_byte_identical)" = yes ] && echo yes || echo no )"
check "figure PNG bytes match across two runs on this machine" "$( [ "$(value_of figure_bytes_identical_same_machine)" = yes ] && echo yes || echo no )"
check "changing one input value changes the document" "$( [ "$(value_of changed_input_changes_document)" = yes ] && echo yes || echo no )"
check "nothing in the output is a clock reading" "$( [ "$(value_of no_clock_reading_in_output)" = yes ] && echo yes || echo no )"
check "the West figure in the prose moved with the data" "$( [ "$(value_of west_change_original)" != "$(value_of west_change_perturbed)" ] && echo yes || echo no )"
check "conclusion, omissions, evidence, caveats, provenance are in reader order" "$( [ "$(value_of sections_in_reader_order)" = yes ] && echo yes || echo no )"
check "the conclusion is rendered before Figure 1" "$( [ "$(value_of conclusion_before_first_figure)" = yes ] && echo yes || echo no )"
check "five figures written, none of them orphaned" "$( [ "$(value_of figures_written)" = 5 ] && [ "$(value_of no_orphans_in_report)" = yes ] && echo yes || echo no )"
check "a deliberately orphaned figure is detected" "$( [ "$(value_of orphan_is_detected)" = yes ] && echo yes || echo no )"
check "no discarded slug reaches the rendered report" "$( [ "$(value_of dropped_slugs_absent_from_report)" = yes ] && echo yes || echo no )"
check "every discarded candidate survives as a one-line null result" "$( [ "$(value_of null_results_kept_as_one_line_each)" = yes ] && echo yes || echo no )"
check "every reported estimate carries an interval or an explicit note" "$( [ "$(value_of every_estimate_has_uncertainty)" = yes ] && echo yes || echo no )"
check "four estimates carry an interval and one carries an explicit note" "$( [ "$(value_of estimates_with_interval)" = 4 ] && [ "$(value_of estimates_with_explicit_note)" = 1 ] && echo yes || echo no )"
check "a bare point estimate is caught" "$( [ "$(value_of bare_point_estimate_is_caught)" = yes ] && echo yes || echo no )"
check "every figure passes the accessibility contract" "$( [ "$(value_of every_figure_passes_accessibility)" = yes ] && echo yes || echo no )"
check "the red-against-green chart fails with four named problems" "$( [ "$(value_of inaccessible_chart_problem_count)" = 4 ] && [ "$(value_of inaccessible_chart_names_both_colours)" = yes ] && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "3. Reference suite -- examples/ must pass in full"
# --------------------------------------------------------------------------

examples_output="$(cd "${lab_dir}" && "${pytest_bin}" examples -q 2>&1)"
examples_status=$?
echo "${examples_output}" | tail -5
check "examples/ exits 0" "$( [ ${examples_status} -eq 0 ] && echo yes || echo no )"
examples_passed_line="$(echo "${examples_output}" | grep -E '^[0-9]+ passed' || true)"
check "examples/ reports 9 passed, 0 failed" "$( echo "${examples_passed_line}" | grep -qE '^9 passed' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "4. Exercise suite -- starter/ is all-skip on an untouched checkout"
# --------------------------------------------------------------------------

starter_output="$(cd "${lab_dir}" && "${pytest_bin}" starter -q 2>&1)"
starter_status=$?
echo "${starter_output}" | tail -5
check "starter/ (untouched) exits 0" "$( [ ${starter_status} -eq 0 ] && echo yes || echo no )"
check "starter/ (untouched) reports 9 skipped, 0 failed" "$( echo "${starter_output}" | grep -qE '^9 skipped' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "5. Never run 'pytest examples starter' in one invocation -- both"
echo "   directories define a module named test_report.py, and pytest"
echo "   collects by dotted module name. Documented, and run as two commands."
# --------------------------------------------------------------------------

combined_output="$(cd "${lab_dir}" && "${pytest_bin}" examples starter -q 2>&1)"
combined_status=$?
check "'pytest examples starter' aborts rather than silently passing" "$( [ ${combined_status} -ne 0 ] && echo yes || echo no )"
check "the collision is reported as an import file mismatch" "$( echo "${combined_output}" | grep -qi 'import file mismatch' && echo yes || echo no )"
echo

# --------------------------------------------------------------------------
echo "6. Prove the suite can genuinely FAIL: solve every exercise in a"
echo "   scratch copy, confirm green, break one assertion on purpose,"
echo "   confirm a non-zero exit and a printed failure, then restore."
# --------------------------------------------------------------------------

scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/d133-scratch.XXXXXX")"
cleanup_scratch() { rm -rf "${scratch_dir}"; }
trap cleanup_scratch EXIT

for module in test_report.py analysis.py report.py data.py conftest.py; do
  cp "${lab_dir}/examples/${module}" "${scratch_dir}/${module}"
done

solved_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
solved_status=$?
check "scratch copy of the solved suite exits 0" "$( [ ${solved_status} -eq 0 ] && echo yes || echo no )"
check "scratch copy reports 9 passed" "$( echo "${solved_output}" | grep -qE '^9 passed' && echo yes || echo no )"

# Break exercise 8's exact survivor count on purpose.
sed -i.bak 's/assert len(kept) == 5/assert len(kept) == 99/' "${scratch_dir}/test_report.py"

broken_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
broken_status=$?
check "broken scratch copy exits non-zero" "$( [ ${broken_status} -ne 0 ] && echo yes || echo no )"
check "broken scratch copy prints a failure" "$( echo "${broken_output}" | grep -qiE 'failed|assert' && echo yes || echo no )"

mv "${scratch_dir}/test_report.py.bak" "${scratch_dir}/test_report.py"
restored_output="$("${pytest_bin}" "${scratch_dir}" -q 2>&1)"
restored_status=$?
check "restored scratch copy exits 0 again" "$( [ ${restored_status} -eq 0 ] && echo yes || echo no )"
check "restored scratch copy reports 9 passed again" "$( echo "${restored_output}" | grep -qE '^9 passed' && echo yes || echo no )"

cleanup_scratch
trap - EXIT
echo

# --------------------------------------------------------------------------
echo "7. Offline, and nothing left behind"
# --------------------------------------------------------------------------

url_hits="$(grep -rEl 'https?://|ftp://' "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null || true)"
check "no URLs inside examples/ or starter/" "$( [ -z "${url_hits}" ] && echo yes || echo no )"

image_hits="$(find "${lab_dir}" -name '.venv' -prune -o -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.svg' -o -iname '*.pdf' \) -print 2>/dev/null || true)"
check "no image files anywhere inside the lab" "$( [ -z "${image_hits}" ] && echo yes || echo no )"

report_hits="$(find "${lab_dir}" -name '.venv' -prune -o -type f -name 'report.md' -print 2>/dev/null || true)"
check "no generated report.md left inside the lab" "$( [ -z "${report_hits}" ] && echo yes || echo no )"

find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

stray="$(find "${lab_dir}" -name '.venv' -prune -o \( -type d -name '__pycache__' -print -o -type d -name '.pytest_cache' -print \) 2>/dev/null || true)"
check "no __pycache__ or .pytest_cache left behind" "$( [ -z "${stray}" ] && echo yes || echo no )"

leftover_tmp="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'd133-*' -print 2>/dev/null || true)"
check "no d133 temporary directory left in the system temp directory" "$( [ -z "${leftover_tmp}" ] && echo yes || echo no )"
echo

echo "-------------------------------------------------------------"
echo "${checks} checks, ${failures} failure(s)"
if [ "${failures}" -gt 0 ]; then
  exit 1
fi
exit 0
