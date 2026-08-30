"""Check that the claims in a portfolio are specific, attributed and evidenced.

Offline and standard-library only. The subject is a list of written claims, so
nothing is fetched and nothing is executed.

A portfolio is a set of claims about what you did. A reader -- a hiring
manager, a collaborator, a reviewer -- is deciding how much to believe, and
they do that on four properties that are visible in the sentence itself:

  specific     a number with a unit beats an adjective
  baseline     "reduced to 840ms" is meaningless without "from 4.2s"
  attributed   what YOU did, distinct from what the team did
  evidenced    a link to something a reader can actually open

The uncomfortable one is attribution. Writing "I" where the work was shared is
dishonest; writing "we" for work that was yours undersells it. Both are common,
and the fix is the same -- say who did what, precisely.

Nothing here judges whether a claim is TRUE. It checks whether a claim is
CHECKABLE, which is the property a reader can assess without knowing you.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Grade(str, Enum):
    STRONG = "strong"
    WEAK = "weak"
    VAGUE = "vague"


# Adjectives that sound like measurements and are not.
VAGUE_WORDS = (
    "significantly",
    "greatly",
    "massively",
    "dramatically",
    "substantially",
    "much faster",
    "much better",
    "world-class",
    "cutting-edge",
    "state of the art",
    "state-of-the-art",
    "robust",
    "seamless",
    "blazing",
)

# What counts as a measurement. Three shapes, because real claims use all
# three and a checker that only accepts one pushes people toward padding their
# sentences with units that do not belong.
MEASUREMENT = re.compile(
    # a number with a unit, a percentage, a multiplier, or a currency amount
    r"\b\d+(?:\.\d+)?\s?(?:%|x\b|ms|s\b|kb|mb|gb|k\b|m\b|hours?|days?|weeks?|months?"
    r"|people|users|requests|documents|questions|queries)"
    r"|[$£€]\s?\d+(?:[.,]\d+)?"
    # a stated change between two figures -- "from 0.71 to 0.94" is a
    # measurement even though a ratio has no unit
    r"|\bfrom\s+\d+(?:\.\d+)?\s*\w*\s+to\s+\d+(?:\.\d+)?",
    re.I,
)

# Wording that names a starting point, so a change can be judged.
BASELINE = re.compile(r"\bfrom\b|\bbaseline\b|\bpreviously\b|\bwas\b|\bcompared (?:to|with)\b", re.I)

# First-person singular, and shared-credit wording.
MINE = re.compile(r"\bI\b|\bmy\b", re.I)
OURS = re.compile(r"\bwe\b|\bour\b|\bteam\b", re.I)


@dataclass(frozen=True)
class Claim:
    text: str
    evidence_url: str = ""


@dataclass
class Assessment:
    claim: str
    grade: Grade
    reasons: list[str] = field(default_factory=list)

    def line(self) -> str:
        head = f"  {self.grade.value.upper():<7} {self.claim[:56]}"
        return f"{head}\n          {'; '.join(self.reasons)}" if self.reasons else head


@dataclass
class PortfolioReport:
    assessments: list[Assessment] = field(default_factory=list)

    def count(self, grade: Grade) -> int:
        return sum(1 for a in self.assessments if a.grade is grade)

    def summary(self) -> str:
        return (
            f"strong={self.count(Grade.STRONG)} weak={self.count(Grade.WEAK)} "
            f"vague={self.count(Grade.VAGUE)}"
        )


def has_measurement(text: str) -> bool:
    return MEASUREMENT.search(text) is not None


def vague_words_in(text: str) -> list[str]:
    lowered = text.lower()
    return sorted(w for w in VAGUE_WORDS if w in lowered)


def has_baseline(text: str) -> bool:
    """Whether the claim names a starting point.

    A change without a baseline is not a measurement. "Reduced latency to
    840ms" could be an improvement, a regression, or unchanged.
    """
    return BASELINE.search(text) is not None


def attribution(text: str) -> str:
    """`mine`, `shared`, `mixed` or `unattributed`.

    `mixed` -- both first-person singular and team wording in one claim -- is
    the strongest form, because it separates what you did from what the group
    did. It is also the rarest, because it takes more words.
    """
    mine, ours = bool(MINE.search(text)), bool(OURS.search(text))
    if mine and ours:
        return "mixed"
    if mine:
        return "mine"
    if ours:
        return "shared"
    return "unattributed"


def is_openable(url: str) -> bool:
    """Whether a reader could actually open this.

    Deliberately shallow: no network. A local path or a private host is not
    evidence to someone outside your machine or your company, and that is
    decidable from the string alone.
    """
    if not url:
        return False
    if url.startswith(("http://localhost", "https://localhost", "file://", "/")):
        return False
    return url.startswith(("http://", "https://"))


def assess(claim: Claim) -> Assessment:
    """Grade one claim on the four properties."""
    reasons: list[str] = []

    vague = vague_words_in(claim.text)
    measured = has_measurement(claim.text)
    baseline = has_baseline(claim.text)
    who = attribution(claim.text)
    evidenced = is_openable(claim.evidence_url)

    if vague:
        reasons.append(f"vague wording: {', '.join(vague)}")
    if not measured:
        reasons.append("no measurement")
    elif not baseline:
        reasons.append("measurement without a baseline")
    if who == "unattributed":
        reasons.append("does not say who did it")
    if not evidenced:
        reasons.append(
            "evidence link is not openable by a reader" if claim.evidence_url else "no evidence link"
        )

    # A claim with no measurement AND vague wording is the weakest kind: it
    # sounds like a result and contains none.
    if vague and not measured:
        grade = Grade.VAGUE
    elif not reasons:
        grade = Grade.STRONG
    else:
        grade = Grade.WEAK
    return Assessment(claim.text, grade, reasons)


def review(claims: list[Claim]) -> PortfolioReport:
    return PortfolioReport(assessments=[assess(c) for c in claims])


def rewrite_hint(claim: Claim) -> str:
    """What this specific claim is missing, as a sentence to act on."""
    a = assess(claim)
    if a.grade is Grade.STRONG:
        return "nothing to add"
    wants = []
    if "no measurement" in a.reasons:
        wants.append("a number with a unit")
    if "measurement without a baseline" in a.reasons:
        wants.append("the value it started from")
    if "does not say who did it" in a.reasons:
        wants.append("what you personally did")
    if any(r.startswith("no evidence") or r.startswith("evidence link") for r in a.reasons):
        wants.append("a link a stranger can open")
    if any(r.startswith("vague wording") for r in a.reasons):
        wants.append("the adjective replaced by the figure")
    return "add " + ", ".join(wants) if wants else "nothing to add"
