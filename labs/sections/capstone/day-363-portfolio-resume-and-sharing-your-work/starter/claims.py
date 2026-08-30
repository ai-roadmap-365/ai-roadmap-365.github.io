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


# Addresses that resolve only on the author's own machine. A loopback IP is
# exactly as unopenable as the name it usually stands for, and people write
# both, so both belong here.
LOCAL_PREFIXES = (
    "http://localhost",
    "https://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://[::1]",
    "https://[::1]",
    "file://",
    "/",
)


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
    # TASK 1: True when the text contains a real quantity.
    # Three shapes count: a number with a unit or percentage or multiplier, a
    # currency amount, and a STATED CHANGE between two figures ("from 0.71 to
    # 0.94"). The third matters: a ratio is a measurement without a unit, and
    # demanding one pushes writers into padding sentences.
    raise NotImplementedError("implement has_measurement")

def vague_words_in(text: str) -> list[str]:
    lowered = text.lower()
    return sorted(w for w in VAGUE_WORDS if w in lowered)


def has_baseline(text: str) -> bool:
    """Whether the claim names a starting point.

    A change without a baseline is not a measurement. "Reduced latency to
    840ms" could be an improvement, a regression, or unchanged.
    """
    # TASK 2: True when the claim names a starting point -- "from",
    # "previously", "was", "compared to". A figure without one describes the
    # present rather than a change.
    raise NotImplementedError("implement has_baseline")

def attribution(text: str) -> str:
    """`mine`, `shared`, `mixed` or `unattributed`.

    `mixed` -- both first-person singular and team wording in one claim -- is
    the strongest form, because it separates what you did from what the group
    did. It is also the rarest, because it takes more words.
    """
    # TASK 3: return "mine", "shared", "mixed" or "unattributed".
    # Both singular and team wording present is "mixed", and it is the
    # STRONGEST form -- it separates your work from the group's, which is the
    # question the reader actually has.
    raise NotImplementedError("implement attribution")

def is_openable(url: str) -> bool:
    """Whether a reader could actually open this.

    Deliberately shallow: no network. A local path or a private host is not
    evidence to someone outside your machine or your company, and that is
    decidable from the string alone.
    """
    # TASK 4: True only for an http(s) URL a stranger could follow.
    # Empty, a local address, file:// and a bare absolute path are all evidence to
    # the author alone. No network: this is decidable from the string.
    raise NotImplementedError("implement is_openable")

def assess(claim: Claim) -> Assessment:
    """Grade one claim on the four properties."""
    # TASK 5: grade one claim, collecting a reason for each missing property.
    #   vague wording        -> name the words found
    #   no measurement       -> "no measurement"
    #   measured, no baseline-> "measurement without a baseline"
    #   unattributed         -> "does not say who did it"
    #   no openable evidence -> "no evidence link" / "evidence link is not
    #                            openable by a reader"
    # Grade VAGUE only when there is vague wording AND no measurement -- that
    # is the claim that sounds like a result and contains none. STRONG when
    # there are no reasons at all. Otherwise WEAK, which means fixable.
    raise NotImplementedError("implement assess")

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
