"""Decide whether a capstone is actually deliverable, or only feels finished.

Offline and standard-library only. The input is a declared delivery -- a list
of requirements and the evidence offered for each -- so nothing is fetched and
nothing is executed.

Week 52 asked for a capstone that is deployed, monitored, security-reviewed,
documented and demonstrated. By the end of it every one of those will feel
done, and the gap between feeling done and being deliverable is made of three
specific things:

  missing      a requirement with no evidence at all
  weak         evidence that is an assertion rather than something checkable
  stale        evidence that was true once and has not been re-checked since

The one that catches people is WEAK. "Monitoring is set up" is not evidence of
monitoring; it is a claim that monitoring exists, offered by the person with
the strongest reason to believe it. A command someone else can run, a URL they
can open, or a number you measured is evidence. The distinction is the same one
day 363 applied to a portfolio, turned on your own project.

Nothing here checks whether your capstone is GOOD. It checks whether the claim
that it is finished can survive somebody else looking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Kind(str, Enum):
    """What sort of evidence was offered, ordered by how much it is worth."""

    NONE = "none"  # nothing offered
    ASSERTION = "assertion"  # "it is set up"
    FILE = "file"  # a document exists
    URL = "url"  # something a reader can open
    COMMAND = "command"  # something anyone can run and see fail
    MEASUREMENT = "measurement"  # a number you took


# Assertions and bare files are claims about the project. Everything from a URL
# upwards can be checked by somebody who does not trust you, which is the whole
# point of a delivery gate.
CHECKABLE = (Kind.URL, Kind.COMMAND, Kind.MEASUREMENT)

# How long a piece of evidence stays meaningful. A deployment verified three
# months ago says nothing about the deployment today.
STALE_AFTER_DAYS = 30


@dataclass(frozen=True)
class Requirement:
    id: str
    day: int
    title: str
    blocking: bool = True  # can the capstone ship without it?


@dataclass(frozen=True)
class Evidence:
    requirement_id: str
    kind: Kind
    detail: str = ""
    verified_on: date | None = None

    @property
    def is_checkable(self) -> bool:
        return self.kind in CHECKABLE and bool(self.detail.strip())

    def age_days(self, today: date) -> int:
        return (today - self.verified_on).days if self.verified_on else 10**6

    def is_stale(self, today: date, *, after: int = STALE_AFTER_DAYS) -> bool:
        return self.age_days(today) > after


@dataclass
class ReadinessReport:
    missing: list[Requirement] = field(default_factory=list)
    weak: list[Requirement] = field(default_factory=list)
    stale: list[Requirement] = field(default_factory=list)
    solid: list[Requirement] = field(default_factory=list)

    @property
    def blockers(self) -> list[Requirement]:
        """Everything blocking, in the order it should be fixed."""
        seen: set[str] = set()
        out: list[Requirement] = []
        for group in (self.missing, self.weak, self.stale):
            for req in group:
                if req.blocking and req.id not in seen:
                    seen.add(req.id)
                    out.append(req)
        return out

    @property
    def ready(self) -> bool:
        return not self.blockers

    def summary(self) -> str:
        return (
            f"solid={len(self.solid)} weak={len(self.weak)} stale={len(self.stale)} "
            f"missing={len(self.missing)}  "
            f"{'READY' if self.ready else f'NOT READY ({len(self.blockers)} blocking)'}"
        )


def evidence_for(requirement: Requirement, evidence: list[Evidence]) -> Evidence | None:
    """The best evidence offered for a requirement.

    Best rather than first: a requirement backed by both an assertion and a
    measurement is backed by the measurement, and the order somebody happened
    to list them in should not change the verdict.
    """
    offered = [e for e in evidence if e.requirement_id == requirement.id and e.kind is not Kind.NONE]
    if not offered:
        return None
    order = list(Kind)
    return max(offered, key=lambda e: order.index(e.kind))


def assess(
    requirements: list[Requirement],
    evidence: list[Evidence],
    today: date,
    *,
    stale_after: int = STALE_AFTER_DAYS,
) -> ReadinessReport:
    """Sort every requirement into missing, weak, stale or solid.

    The categories are exclusive and checked in that order, because the advice
    differs. Missing needs the work done. Weak needs the claim replaced with
    something checkable. Stale needs one command re-run.
    """
    report = ReadinessReport()
    for req in requirements:
        found = evidence_for(req, evidence)
        if found is None:
            report.missing.append(req)
        elif not found.is_checkable:
            report.weak.append(req)
        elif found.is_stale(today, after=stale_after):
            report.stale.append(req)
        else:
            report.solid.append(req)
    return report


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def findings(
    requirements: list[Requirement],
    evidence: list[Evidence],
    today: date,
    *,
    stale_after: int = STALE_AFTER_DAYS,
) -> list[str]:
    """The gate, as sentences somebody could act on this afternoon."""
    out: list[str] = []
    report = assess(requirements, evidence, today, stale_after=stale_after)

    if report.ready:
        out.append(
            f"Deliverable. All {len(report.solid)} requirements are backed by evidence "
            "somebody else could check."
        )
    else:
        out.append(
            f"NOT deliverable: {len(report.blockers)} blocking requirement(s) of "
            f"{len(requirements)}."
        )

    for req in report.missing:
        mark = "BLOCKING" if req.blocking else "optional"
        out.append(f"{mark}: '{req.title}' (day {req.day}) has no evidence at all.")

    for req in report.weak:
        found = evidence_for(req, evidence)
        kind = found.kind.value if found else "none"
        mark = "BLOCKING" if req.blocking else "optional"
        out.append(
            f"{mark}: '{req.title}' (day {req.day}) rests on {_article(kind)} {kind}. "
            "Replace it with a command, a URL or a measurement."
        )

    for req in report.stale:
        found = evidence_for(req, evidence)
        age = found.age_days(today) if found else 0
        mark = "BLOCKING" if req.blocking else "optional"
        out.append(
            f"{mark}: '{req.title}' (day {req.day}) was last verified {age} days ago. Re-run it."
        )

    return out
