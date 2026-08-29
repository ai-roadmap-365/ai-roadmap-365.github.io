"""A small EDA report generator that refuses to build a bad report.

This is the course-supplied tool for Day 133. It is deliberately small
enough to read in one sitting, because the point is not the code -- it is
the four rules the code refuses to bend:

* **A figure must have a stated question.** `Report.add_panel` raises
  `ReportError` on a candidate whose `question` is missing or blank.
* **A caption must carry a claim.** `carries_claim` demands a number or a
  comparative word, so "revenue by region" is rejected and "the West fell
  8.4% after the pricing change" is accepted. The heuristic is crude on
  purpose: it can tell that a claim was *made*, never whether the claim is
  *true*. Judging truth is the reader's job and yours.
* **Every figure is referenced.** `orphan_figures` compares what was
  written to disk against what the markdown links to.
* **Every reported estimate carries its uncertainty**, either as an
  interval or as an explicit note that no interval is available.
  `missing_uncertainty` lists the ones that carry neither.

Two more checks sit alongside those: `check_axes` enforces the
accessibility contract (a colourblind-safe palette and labelled axes), and
`survivors` is the "so what" filter that drops candidate figures with no
question before they ever reach the report.

The renderer writes Markdown with embedded figures. It contains no clock
reading and no random number, so two runs over the same input produce
byte-identical Markdown -- which exercise 6 asserts directly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import to_hex

__all__ = [
    "SAFE_PALETTE",
    "ReportError",
    "Estimate",
    "Finding",
    "Candidate",
    "Panel",
    "Report",
    "carries_claim",
    "claim_problem",
    "survivors",
    "orphan_figures",
    "missing_uncertainty",
    "axes_colours",
    "check_axes",
    "bootstrap_interval",
]


#: seaborn's "colorblind" palette, as hex. Read off
#: `seaborn.color_palette("colorblind")` on seaborn 0.13.2 and frozen here so
#: the accessibility check has an exact set to compare against.
SAFE_PALETTE: tuple[str, ...] = (
    "#0173b2",
    "#de8f05",
    "#029e73",
    "#d55e00",
    "#cc78bc",
    "#ca9161",
    "#fbafe4",
    "#949494",
    "#ece133",
    "#56b4e9",
)


class ReportError(ValueError):
    """Raised when a figure would break one of the report's own rules."""


# ---------------------------------------------------------------------------
# The caption rule: a caption must carry a claim
# ---------------------------------------------------------------------------

#: Words that turn a label into a comparison. Not exhaustive, and not meant
#: to be -- see `carries_claim` for what this check can and cannot do.
CLAIM_WORDS: frozenset[str] = frozenset(
    {
        "above",
        "below",
        "beyond",
        "concentrated",
        "decrease",
        "decreased",
        "double",
        "doubled",
        "drop",
        "dropped",
        "every",
        "exceeds",
        "fall",
        "fell",
        "grew",
        "growth",
        "half",
        "halved",
        "higher",
        "increase",
        "increased",
        "less",
        "lower",
        "more",
        "no",
        "none",
        "only",
        "outgrew",
        "rise",
        "rose",
        "shrank",
        "than",
        "times",
        "unchanged",
        "versus",
        "while",
    }
)


def claim_problem(caption: str) -> str | None:
    """Return why `caption` fails the claim rule, or None if it passes.

    A caption passes if it contains a digit, a percent sign, or one of
    `CLAIM_WORDS`. That is a crude test and it is meant to be: it detects
    whether a *claim was made*, and it has no way at all to judge whether
    the claim is *true*. A caption reading "revenue tripled" passes this
    check on data where revenue halved. The check buys you one thing --
    it makes the absence of a claim impossible to ship by accident.
    """
    text = caption.strip()
    if not text:
        return "the caption is empty"
    if any(character.isdigit() for character in text) or "%" in text:
        return None
    words = set(re.findall(r"[a-z]+", text.lower()))
    if words & CLAIM_WORDS:
        return None
    return (
        "the caption is a label, not a claim: it contains no number and no "
        "comparative word, so there is nothing in it a reader could disagree with"
    )


def carries_claim(caption: str) -> bool:
    """True when `caption` states something a reader could disagree with."""
    return claim_problem(caption) is None


# ---------------------------------------------------------------------------
# Estimates and their uncertainty
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Estimate:
    """One number the report asserts, with its uncertainty attached.

    Either give it an interval (`low` and `high`, from Day 118's machinery
    or `bootstrap_interval` below) or an explicit `no_interval_note` saying
    why one is not available. A bare point estimate carries neither, and
    `missing_uncertainty` will find it.
    """

    label: str
    value: float
    unit: str = ""
    low: float | None = None
    high: float | None = None
    no_interval_note: str | None = None
    decimals: int = 1

    def has_uncertainty(self) -> bool:
        interval = self.low is not None and self.high is not None
        return interval or bool(self.no_interval_note)

    def text(self) -> str:
        value = f"{self.value:.{self.decimals}f}{self.unit}"
        if self.low is not None and self.high is not None:
            low = f"{self.low:.{self.decimals}f}{self.unit}"
            high = f"{self.high:.{self.decimals}f}{self.unit}"
            return f"{self.label}: {value} (95% interval {low} to {high})"
        if self.no_interval_note:
            return f"{self.label}: {value} (no interval: {self.no_interval_note})"
        return f"{self.label}: {value}"


def bootstrap_interval(
    values: Sequence[float] | np.ndarray,
    *,
    statistic: Callable[[np.ndarray], float] = np.mean,
    resamples: int = 2000,
    level: float = 0.95,
    seed: int = 133,
) -> tuple[float, float]:
    """A percentile bootstrap interval, seeded so the report stays reproducible.

    Day 118's interval, computed by resampling rather than by formula, which
    is what you reach for when the statistic has no tidy standard error.
    """
    sample = np.asarray(values, dtype=float)
    sample = sample[~np.isnan(sample)]
    if sample.size < 2:
        raise ReportError("a bootstrap interval needs at least two observations")
    rng = np.random.default_rng(seed)
    draws = rng.choice(sample, size=(resamples, sample.size), replace=True)
    stats = np.array([float(statistic(row)) for row in draws])
    tail = (1.0 - level) / 2.0
    return float(np.quantile(stats, tail)), float(np.quantile(stats, 1.0 - tail))


# ---------------------------------------------------------------------------
# Candidates, findings and panels
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """What one figure turned out to say, computed from the data."""

    caption: str
    prose: str
    estimate: Estimate | None = None


@dataclass(frozen=True)
class Candidate:
    """A figure someone made during exploration. Most do not survive.

    `question` is the whole filter. A candidate with no question answers no
    question, and `survivors` drops it before it can reach the report --
    but `dropped_because` is kept, because "we looked and found nothing"
    is worth one line to the next reader.
    """

    slug: str
    question: str | None = None
    draw: Callable[[Axes, pd.DataFrame], None] | None = None
    analyse: Callable[[pd.DataFrame], Finding] | None = None
    dropped_because: str = ""


@dataclass
class Panel:
    """A candidate that survived, with its finding resolved against the data."""

    slug: str
    question: str
    finding: Finding
    draw: Callable[[Axes, pd.DataFrame], None]
    number: int = 0
    image: str = ""


def survivors(candidates: Iterable[Candidate]) -> list[Candidate]:
    """The "so what" filter: keep only candidates that answer a stated question."""
    return [c for c in candidates if c.question and c.question.strip()]


def discarded(candidates: Iterable[Candidate]) -> list[Candidate]:
    """The complement of `survivors` -- what the report will not show."""
    return [c for c in candidates if not (c.question and c.question.strip())]


# ---------------------------------------------------------------------------
# Accessibility contract
# ---------------------------------------------------------------------------


def axes_colours(ax: Axes) -> list[str]:
    """Every colour actually painted on `ax`, as lowercase hex, alpha dropped."""
    found: list[str] = []
    for patch in ax.patches:
        found.append(to_hex(patch.get_facecolor()))
    for line in ax.get_lines():
        found.append(to_hex(line.get_color()))
    for collection in ax.collections:
        for rgba in np.atleast_2d(collection.get_facecolor()):
            found.append(to_hex(rgba))
    return [colour.lower() for colour in found]


def check_axes(ax: Axes) -> list[str]:
    """Problems with `ax` against the report's accessibility contract.

    Days 127 and 132, turned into a build check: every mark must be drawn in
    a colourblind-safe colour, and both axes must be labelled. Returns an
    empty list when the axes pass.
    """
    problems: list[str] = []
    if not ax.get_xlabel().strip():
        problems.append("the x axis has no label")
    if not ax.get_ylabel().strip():
        problems.append("the y axis has no label")
    safe = {colour.lower() for colour in SAFE_PALETTE}
    for colour in sorted(set(axes_colours(ax))):
        if colour not in safe:
            problems.append(f"colour {colour} is not in the colourblind-safe palette")
    return problems


def accessibility_problems(
    draw: Callable[[Axes, pd.DataFrame], None], frame: pd.DataFrame
) -> list[str]:
    """Draw into a throwaway figure and run `check_axes` on the result."""
    figure, ax = plt.subplots(figsize=(6.0, 3.5), dpi=100)
    try:
        draw(ax, frame)
        return check_axes(ax)
    finally:
        plt.close(figure)


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

_IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def orphan_figures(markdown: str, figure_dir: Path | str) -> list[str]:
    """Image files on disk that the markdown never links to.

    An orphan is not a cosmetic problem. It is either a figure you meant to
    discuss and forgot, or a leftover from a previous run that will confuse
    whoever opens the directory next.
    """
    referenced = {Path(target).name for target in _IMAGE_LINK.findall(markdown)}
    directory = Path(figure_dir)
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.glob("*.png") if p.name not in referenced)


def missing_uncertainty(report: "Report") -> list[str]:
    """Slugs of panels whose estimate carries neither an interval nor a note."""
    return [
        panel.slug
        for panel in report.panels
        if panel.finding.estimate is not None
        and not panel.finding.estimate.has_uncertainty()
    ]


@dataclass
class Report:
    """An ordered argument with evidence attached."""

    title: str
    question: str
    decision: str
    provenance: str
    caveats: list[str] = field(default_factory=list)
    null_results: list[str] = field(default_factory=list)
    panels: list[Panel] = field(default_factory=list)
    data_fingerprint: str = ""

    def add_panel(self, candidate: Candidate, frame: pd.DataFrame) -> Panel:
        """Resolve one candidate against the data and admit it to the report.

        Raises `ReportError` when the candidate has no stated question, when
        its caption is a label rather than a claim, or when it has no way to
        draw itself or to compute its finding.
        """
        if not candidate.question or not candidate.question.strip():
            raise ReportError(
                f"figure {candidate.slug!r} has no stated question; a figure whose "
                "question you cannot state is a figure that does not belong in the report"
            )
        if candidate.draw is None or candidate.analyse is None:
            raise ReportError(
                f"figure {candidate.slug!r} has a question but no way to answer it"
            )

        finding = candidate.analyse(frame)
        problem = claim_problem(finding.caption)
        if problem is not None:
            raise ReportError(f"figure {candidate.slug!r}: {problem}")

        panel = Panel(
            slug=candidate.slug,
            question=candidate.question.strip(),
            finding=finding,
            draw=candidate.draw,
            number=len(self.panels) + 1,
        )
        panel.image = f"figures/{panel.number:02d}-{panel.slug}.png"
        self.panels.append(panel)
        return panel

    # -- rendering ---------------------------------------------------------

    def render(self, outdir: Path | str, frame: pd.DataFrame) -> str:
        """Write the figures and `report.md` into `outdir`, and return the markdown.

        The output contains no clock reading and no unseeded random number,
        so two runs over the same input are byte-identical. Provenance is a
        fingerprint of the data, not a timestamp of the run.
        """
        directory = Path(outdir)
        figure_dir = directory / "figures"
        figure_dir.mkdir(parents=True, exist_ok=True)

        for panel in self.panels:
            figure, ax = plt.subplots(figsize=(6.0, 3.5), dpi=100)
            try:
                panel.draw(ax, frame)
                figure.tight_layout()
                figure.savefig(directory / panel.image)
            finally:
                plt.close(figure)

        markdown = self._markdown(frame)
        (directory / "report.md").write_text(markdown, encoding="utf-8")
        return markdown

    def fingerprint(self, frame: pd.DataFrame) -> str:
        """A short content hash of the input, so provenance names the data."""
        payload = frame.to_csv(index=False).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:12]

    def _markdown(self, frame: pd.DataFrame) -> str:
        lines: list[str] = []
        add = lines.append

        add(f"# {self.title}")
        add("")
        add(f"**Question.** {self.question}")
        add("")
        add(f"**Decision this feeds.** {self.decision}")
        add("")

        add("## Conclusion")
        add("")
        if not self.panels:
            add("No figure in this analysis answered a stated question.")
        for panel in self.panels:
            add(f"{panel.number}. {panel.finding.caption} (Figure {panel.number})")
        add("")
        for panel in self.panels:
            if panel.finding.estimate is not None:
                add(f"- {panel.finding.estimate.text()}")
        add("")

        add("## What we looked at and found nothing in")
        add("")
        if self.null_results:
            for note in self.null_results:
                add(f"- {note}")
        else:
            add("- Nothing was set aside; every candidate figure answered a question.")
        add("")

        add("## Evidence")
        add("")
        for panel in self.panels:
            add(f"### Figure {panel.number} — {panel.question}")
            add("")
            add(f"![{panel.question}]({panel.image})")
            add("")
            add(f"**Figure {panel.number}.** {panel.finding.caption}")
            add("")
            add(panel.finding.prose)
            add("")
            if panel.finding.estimate is not None:
                add(f"*{panel.finding.estimate.text()}*")
                add("")

        add("## Caveats")
        add("")
        for caveat in self.caveats:
            add(f"- {caveat}")
        add("")

        add("## Provenance")
        add("")
        add(f"- Source: {self.provenance}")
        add(f"- Shape: {len(frame)} rows, {len(frame.columns)} columns")
        add(f"- Data fingerprint (sha256, first 12): `{self.fingerprint(frame)}`")
        add(
            "- This document was generated by code from the input above. Nothing in "
            "it was typed by hand, so re-running it on new data cannot leave the "
            "prose disagreeing with the figures."
        )
        add("")

        return "\n".join(lines)
