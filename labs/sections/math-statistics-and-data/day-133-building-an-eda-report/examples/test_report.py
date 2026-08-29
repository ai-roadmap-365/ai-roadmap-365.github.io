"""Reference solutions -- Day 133, A Report That Argues.

Nine exercises. Each one asserts on real behaviour of the report generator
in `report.py` running over the real frame in `data.py` -- never on image
bytes, and never on the presence of a file alone.

Run with: pytest examples -q
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
    report = blank_report()

    nameless = Candidate(
        slug="pretty-chart",
        draw=draw_missing_by_column,
        analyse=analyse_missing,
    )
    with pytest.raises(ReportError) as raised:
        report.add_panel(nameless, frame)
    assert "no stated question" in str(raised.value)
    assert report.panels == [], "a refused figure must not be half-admitted"

    blank = Candidate(
        slug="pretty-chart",
        question="   ",
        draw=draw_missing_by_column,
        analyse=analyse_missing,
    )
    with pytest.raises(ReportError):
        report.add_panel(blank, frame)

    asked = Candidate(
        slug="pretty-chart",
        question="Which rows have no revenue?",
        draw=draw_missing_by_column,
        analyse=analyse_missing,
    )
    panel = report.add_panel(asked, frame)
    assert panel.question == "Which rows have no revenue?"
    assert len(report.panels) == 1
    assert panel.number == 1
    assert panel.image == "figures/01-pretty-chart.png"


# --------------------------------------------------------------------------
# Exercise 2 -- the caption carries the claim.
# --------------------------------------------------------------------------


def test_02_caption_carries_a_claim(frame):
    # A label. Nothing in it a reader could disagree with.
    assert carries_claim("revenue by region") is False
    assert "label, not a claim" in claim_problem("revenue by region")
    assert carries_claim("monthly revenue, all regions") is False
    assert carries_claim("") is False

    # A claim: it has a number in it.
    assert carries_claim(
        "three regions grew, and the fourth fell by 12% after the March pricing change"
    )
    # A claim: no number, but a comparison.
    assert carries_claim("partner revenue is lower than direct revenue in every region")

    # The generator refuses a panel whose caption is only a label.
    report = blank_report()
    labelled = Candidate(
        slug="labelled",
        question="What does revenue look like by region?",
        draw=draw_missing_by_column,
        analyse=lambda _frame: Finding(caption="revenue by region", prose="No claim here."),
    )
    with pytest.raises(ReportError) as raised:
        report.add_panel(labelled, frame)
    assert "label, not a claim" in str(raised.value)

    # The honest limits of the check, in both directions. It passes a caption
    # that is flatly false, because it cannot read the data ...
    assert carries_claim("revenue doubled in every region")
    # ... and it refuses a genuine claim written without a number and without
    # one of its comparative words. "tripled" is simply not on the list. The
    # check makes the ABSENCE of a claim impossible to ship by accident; it is
    # not, and cannot be, a judge of whether the claim is right.
    assert carries_claim("revenue tripled in all four regions") is False


# --------------------------------------------------------------------------
# Exercise 3 -- numbers in the prose come from the data.
# --------------------------------------------------------------------------


def test_03_numbers_come_from_the_data(frame, perturbed_frame, report_dir, second_report_dir):
    original = build_report(frame).render(report_dir, frame)
    changed = build_report(perturbed_frame).render(second_report_dir, perturbed_frame)

    needle = "West change across the pricing change"
    original_line = line_containing(original, needle)
    changed_line = line_containing(changed, needle)
    assert original_line != changed_line

    original_pct = percentage_in(original_line)
    changed_pct = percentage_in(changed_line)
    assert original_pct < 0.0
    # One input value moved; the sentence moved with it by a wide margin.
    assert changed_pct < original_pct - 20.0

    # The fingerprint in the provenance section moved too, because it is a
    # hash of the input rather than a note about the run.
    assert line_containing(original, "Data fingerprint") != line_containing(
        changed, "Data fingerprint"
    )


# --------------------------------------------------------------------------
# Exercise 4 -- every figure is referenced.
# --------------------------------------------------------------------------


def test_04_no_orphan_figures(frame, report_dir):
    markdown = build_report(frame).render(report_dir, frame)
    figure_dir = report_dir / "figures"

    written = sorted(p.name for p in figure_dir.glob("*.png"))
    assert len(written) == 5
    assert orphan_figures(markdown, figure_dir) == []
    for name in written:
        assert f"figures/{name}" in markdown

    # A leftover from an earlier run is exactly what this check is for.
    shutil.copy(figure_dir / written[0], figure_dir / "99-left-over.png")
    assert orphan_figures(markdown, figure_dir) == ["99-left-over.png"]


# --------------------------------------------------------------------------
# Exercise 5 -- uncertainty is stated, not implied.
# --------------------------------------------------------------------------


def test_05_uncertainty_is_present(frame):
    report = build_report(frame)
    assert missing_uncertainty(report) == []

    estimates = [panel.finding.estimate for panel in report.panels]
    assert all(estimate is not None for estimate in estimates)

    with_interval = [e for e in estimates if e.low is not None and e.high is not None]
    with_note = [e for e in estimates if e.no_interval_note]
    assert len(with_interval) == 4
    assert len(with_note) == 1
    assert "single observation" in with_note[0].no_interval_note
    for estimate in with_interval:
        assert estimate.low < estimate.value < estimate.high
        assert "95% interval" in estimate.text()

    # A bare point estimate carries neither, and the check finds it.
    report.add_panel(bare_point_estimate_candidate(), frame)
    assert missing_uncertainty(report) == ["bare-total"]


# --------------------------------------------------------------------------
# Exercise 6 -- reproducibility.
# --------------------------------------------------------------------------


def test_06_two_runs_are_byte_identical(
    frame, perturbed_frame, report_dir, second_report_dir, third_report_dir
):
    first = build_report(frame).render(report_dir, frame)
    second = build_report(frame).render(second_report_dir, frame)

    assert first == second
    assert (report_dir / "report.md").read_bytes() == (
        second_report_dir / "report.md"
    ).read_bytes()

    # Figure bytes too, on this machine: same backend, same fonts, same run.
    for path in sorted((report_dir / "figures").glob("*.png")):
        twin = second_report_dir / "figures" / path.name
        assert path.read_bytes() == twin.read_bytes()

    # Change one input value and the document changes.
    third = build_report(perturbed_frame).render(third_report_dir, perturbed_frame)
    assert third != first

    # Nothing in the output is a clock reading.
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", first)


# --------------------------------------------------------------------------
# Exercise 7 -- ordering for the reader.
# --------------------------------------------------------------------------


def test_07_conclusion_comes_before_the_evidence(frame, report_dir):
    markdown = build_report(frame).render(report_dir, frame)

    conclusion = markdown.index("## Conclusion")
    omissions = markdown.index("## What we looked at and found nothing in")
    evidence = markdown.index("## Evidence")
    caveats = markdown.index("## Caveats")
    provenance = markdown.index("## Provenance")

    assert conclusion < omissions < evidence < caveats < provenance
    assert conclusion < markdown.index("### Figure 1")
    # The conclusion is literally the list of captions: the claim the caption
    # carries is the finding, so the two can never drift apart.
    for panel in build_report(frame).panels:
        assert f"{panel.number}. {panel.finding.caption} (Figure {panel.number})" in markdown


# --------------------------------------------------------------------------
# Exercise 8 -- the "so what" filter.
# --------------------------------------------------------------------------


def test_08_the_so_what_filter(frame, candidates, report_dir):
    kept = survivors(candidates)
    dropped = discarded(candidates)

    assert len(candidates) == 12
    assert len(kept) == 5
    assert len(dropped) == 7
    assert len(kept) + len(dropped) == len(candidates)
    # Most of what exploration produced does not survive. That is the ratio.
    assert len(kept) / len(candidates) < 0.5

    markdown = build_report(frame).render(report_dir, frame)
    figure_dir = report_dir / "figures"

    for candidate in dropped:
        assert candidate.slug not in markdown
        assert list(figure_dir.glob(f"*{candidate.slug}*")) == []
        # But the null result survives as one line, so nobody repeats it.
        assert candidate.dropped_because in markdown

    for candidate in kept:
        assert any(candidate.slug in p.name for p in figure_dir.glob("*.png"))


# --------------------------------------------------------------------------
# Exercise 9 -- the accessibility contract, as a build check.
# --------------------------------------------------------------------------


def test_09_accessibility_contract(frame, candidates):
    for candidate in survivors(candidates):
        assert accessibility_problems(candidate.draw, frame) == [], candidate.slug

    problems = accessibility_problems(draw_inaccessible, frame)
    assert "the x axis has no label" in problems
    assert "the y axis has no label" in problems
    assert any("#ff0000" in problem for problem in problems)
    assert any("#008000" in problem for problem in problems)
    assert len(problems) == 4
