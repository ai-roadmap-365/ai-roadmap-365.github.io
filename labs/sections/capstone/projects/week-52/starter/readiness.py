"""STARTER -- implement the seven tasks below, then run the tests.

Decide whether a capstone is actually deliverable, or only feels finished.

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
        raise NotImplementedError(
            "TASK 1: a checkable KIND is not enough -- a command with no detail "
            "is nobody's evidence."
        )

    def age_days(self, today: date) -> int:
        raise NotImplementedError(
            "TASK 2: undated evidence must behave as ancient, not as fresh. "
            "Returning 0 here is the single most dangerous bug in this file."
        )

    def is_stale(self, today: date, *, after: int = STALE_AFTER_DAYS) -> bool:
        raise NotImplementedError("TASK 3: older than the window is stale")


@dataclass
class ReadinessReport:
    missing: list[Requirement] = field(default_factory=list)
    weak: list[Requirement] = field(default_factory=list)
    stale: list[Requirement] = field(default_factory=list)
    solid: list[Requirement] = field(default_factory=list)

    @property
    def blockers(self) -> list[Requirement]:
        """Everything blocking, in the order it should be fixed."""
        raise NotImplementedError(
            "TASK 4: blocking requirements only, missing first, then weak, then "
            "stale -- the order the work should be done in."
        )

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
    raise NotImplementedError(
        "TASK 5: the BEST evidence, not the first listed. An explicit NONE is "
        "the same as offering nothing. Kind is declared in ascending order of "
        "worth, so list(Kind) gives you the ranking."
    )


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
    raise NotImplementedError(
        "TASK 6: sort every requirement into exactly ONE of missing, weak, "
        "stale, solid -- in that order, because the advice differs."
    )


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
    raise NotImplementedError(
        "TASK 7: lead with the verdict, then one line per problem. Mark each "
        "BLOCKING or optional, name the requirement and the day it came from, "
        "say which kind of evidence was too weak, and say how many days old "
        "stale evidence is. A ready delivery gets one line and no list."
    )
