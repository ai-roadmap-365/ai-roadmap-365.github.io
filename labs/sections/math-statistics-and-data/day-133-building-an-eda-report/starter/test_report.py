"""Your exercises for Day 133 -- "A Report That Argues".

Nine exercises. Every test below currently calls `pytest.skip(...)` --
replace the skip with real assertions and delete the skip line. Read
`00_brief.md` for the exercise-by-exercise explanation, `report.py` for
the generator you are testing, and `analysis.py` for the twelve candidate
figures it is fed.

Check yourself at any point:

    pytest starter -v

The reference answer key lives in `examples/test_report.py` -- read it
AFTER you have tried, never before.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from analysis import (
    analyse_missing,
    bare_point_estimate_candidate,
    build_report,
    candidate_figures,
    draw_inaccessible,
    draw_missing_by_column,
)
from report import (
    Candidate,
    Finding,
    Report,
    ReportError,
    accessibility_problems,
    carries_claim,
    claim_problem,
    discarded,
    missing_uncertainty,
    orphan_figures,
    survivors,
)


def line_containing(markdown: str, needle: str) -> str:
    """The one line of `markdown` that contains `needle`."""
    hits = [line for line in markdown.splitlines() if needle in line]
    assert len(hits) >= 1, f"no line contains {needle!r}"
    return hits[0]


def percentage_in(text: str) -> float:
    """The first signed percentage in `text`, as a float."""
    match = re.search(r"(-?\d+(?:\.\d+)?)%", text)
    assert match is not None, f"no percentage in {text!r}"
    return float(match.group(1))


def blank_report() -> Report:
    return Report(
        title="A scratch report",
        question="Does the generator hold its own line?",
        decision="Whether to trust anything this generator produces.",
        provenance="the same synthetic frame the real report uses",
    )


# --------------------------------------------------------------------------
# Exercise 1 -- a figure must have a question.
# --------------------------------------------------------------------------


def test_01_a_figure_must_have_a_question(frame):
    pytest.skip(
        "Build a Candidate with no question (and one with a blank '   ' question) "
        "and assert blank_report().add_panel(...) raises ReportError mentioning "
        "'no stated question' and leaves report.panels empty; then add the same "
        "candidate WITH a question and assert the panel is admitted, numbered 1, "
        "with image 'figures/01-pretty-chart.png'"
    )


# --------------------------------------------------------------------------
# Exercise 2 -- the caption carries the claim.
# --------------------------------------------------------------------------


def test_02_caption_carries_a_claim(frame):
    pytest.skip(
        "Assert carries_claim('revenue by region') is False and that "
        "claim_problem() explains it is a label rather than a claim; assert a "
        "caption with a number in it passes; assert add_panel refuses a Finding "
        "whose caption is only a label; then assert BOTH honest limits of the "
        "heuristic -- 'revenue doubled in every region' passes even though the "
        "check cannot know it is false, and 'revenue tripled in all four regions' "
        "is refused even though it is a real claim"
    )


# --------------------------------------------------------------------------
# Exercise 3 -- numbers in the prose come from the data.
# --------------------------------------------------------------------------


def test_03_numbers_come_from_the_data(frame, perturbed_frame, report_dir, second_report_dir):
    pytest.skip(
        "Render build_report(frame) and build_report(perturbed_frame) into the two "
        "temporary directories, pull the line containing 'West change across the "
        "pricing change' out of each with line_containing, and assert the two lines "
        "differ, that the original percentage is negative, and that the perturbed "
        "one is more than 20 points lower; assert the 'Data fingerprint' lines "
        "differ too"
    )


# --------------------------------------------------------------------------
# Exercise 4 -- every figure is referenced.
# --------------------------------------------------------------------------


def test_04_no_orphan_figures(frame, report_dir):
    pytest.skip(
        "Render the report, assert five PNG files were written and that "
        "orphan_figures(markdown, report_dir / 'figures') is empty and every "
        "written name appears in the markdown; then shutil.copy one figure to "
        "'99-left-over.png' and assert orphan_figures now returns exactly that name"
    )


# --------------------------------------------------------------------------
# Exercise 5 -- uncertainty is stated, not implied.
# --------------------------------------------------------------------------


def test_05_uncertainty_is_present(frame):
    pytest.skip(
        "Assert missing_uncertainty(build_report(frame)) is empty, that all five "
        "panels carry an Estimate, that four of them carry a 95% interval "
        "(low < value < high) and one carries an explicit no_interval_note; then "
        "add bare_point_estimate_candidate() and assert missing_uncertainty now "
        "returns ['bare-total']"
    )


# --------------------------------------------------------------------------
# Exercise 6 -- reproducibility.
# --------------------------------------------------------------------------


def test_06_two_runs_are_byte_identical(
    frame, perturbed_frame, report_dir, second_report_dir, third_report_dir
):
    pytest.skip(
        "Render the same frame twice into two directories and assert the returned "
        "markdown strings are equal, the two report.md files are byte-identical, "
        "and each figures/*.png pair is byte-identical; then render the perturbed "
        "frame and assert it differs; finally assert no ISO date appears anywhere "
        "in the output (re.search(r'\\b20\\d\\d-\\d\\d-\\d\\d\\b', markdown) is None)"
    )


# --------------------------------------------------------------------------
# Exercise 7 -- ordering for the reader.
# --------------------------------------------------------------------------


def test_07_conclusion_comes_before_the_evidence(frame, report_dir):
    pytest.skip(
        "Render the report and assert markdown.index() puts '## Conclusion' before "
        "'## What we looked at and found nothing in', before '## Evidence', before "
        "'## Caveats', before '## Provenance', and before '### Figure 1'; then "
        "assert each panel's numbered caption line appears verbatim in the "
        "conclusion, so the claim and the finding cannot drift apart"
    )


# --------------------------------------------------------------------------
# Exercise 8 -- the "so what" filter.
# --------------------------------------------------------------------------


def test_08_the_so_what_filter(frame, candidates, report_dir):
    pytest.skip(
        "Assert there are 12 candidates, that survivors() keeps 5 and discarded() "
        "drops 7, and that fewer than half survive; render the report and assert "
        "no dropped slug appears in the markdown and no figure file was written "
        "for one, while every dropped candidate's dropped_because line IS in the "
        "markdown, and every surviving slug has a figure file"
    )


# --------------------------------------------------------------------------
# Exercise 9 -- the accessibility contract, as a build check.
# --------------------------------------------------------------------------


def test_09_accessibility_contract(frame, candidates):
    pytest.skip(
        "Assert accessibility_problems(candidate.draw, frame) is empty for every "
        "surviving candidate; then assert accessibility_problems(draw_inaccessible, "
        "frame) reports exactly four problems -- an unlabelled x axis, an "
        "unlabelled y axis, and the two off-palette colours #ff0000 and #008000"
    )
