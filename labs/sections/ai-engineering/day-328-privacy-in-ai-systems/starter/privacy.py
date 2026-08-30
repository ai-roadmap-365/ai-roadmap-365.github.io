"""Redaction, data-flow tracking and deletion verification for an AI pipeline.

Offline and standard-library only. Everything here is defensive: the detectors
exist to find personal data so it can be removed before it spreads, and the
audit exists to prove a deletion actually reached every store.

Three ideas, in the order they matter:

  redact   remove personal data at the boundary, before it multiplies
  track    know every store a piece of data reached
  verify   prove a deletion landed everywhere, rather than assuming

The third is the one that fails silently. A record deleted from the database
but left in the vector index, the cache and yesterday's logs has not been
deleted -- and nothing in the system reports a problem.

The synthetic identifiers in the fixtures are invalid by construction: the card
numbers fail the Luhn check and the emails use the reserved example.com domain.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    CARD = "card"
    NATIONAL_ID = "national_id"
    IP = "ip"


# Detectors are deliberately conservative in shape and generous in matching.
# Under-detection leaks; over-detection costs a little utility. When the two
# trade off, privacy work should prefer the recoverable mistake.
PATTERNS: dict[Category, re.Pattern[str]] = {
    Category.EMAIL: re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    # No leading \b: a word boundary cannot match before "+", so the country
    # code would survive redaction as a bare "+". A negative lookbehind on
    # word characters does what \b was meant to do here.
    Category.PHONE: re.compile(r"(?<![\w+])\+?(?:\d[ -]?){9,13}\d\b"),
    Category.CARD: re.compile(r"(?<![\w+])(?:\d[ -]?){12,15}\d\b"),
    Category.NATIONAL_ID: re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    Category.IP: re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

# Longer, more specific patterns must run first, or a card number is partly
# consumed by the phone matcher and the redaction is incomplete.
ORDER: tuple[Category, ...] = (
    Category.EMAIL,
    Category.NATIONAL_ID,
    Category.CARD,
    Category.PHONE,
    Category.IP,
)


@dataclass
class Finding:
    category: Category
    start: int
    end: int
    token: str


@dataclass
class Redaction:
    text: str
    findings: list[Finding] = field(default_factory=list)

    def count(self, category: Category) -> int:
        return sum(1 for f in self.findings if f.category is category)

    def summary(self) -> str:
        if not self.findings:
            return "clean"
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.category.value] = counts.get(finding.category.value, 0) + 1
        return " ".join(f"{k}={v}" for k, v in sorted(counts.items()))


def pseudonym(value: str, category: Category, *, salt: str = "lab-salt") -> str:
    """A stable, non-reversible stand-in for a value.

    Stable so the same person is recognisable across records, which keeps the
    data useful for debugging and analytics. Non-reversible so the token is not
    the personal data wearing a hat.

    The salt matters: without one, a hash of a short value is trivially
    reversed by enumerating the space. There are only so many phone numbers.
    """
    # TASK 1: return f"[{category.value}:{digest}]" where digest is the first
    # 10 hex characters of sha256(salt + value). The salt is not decoration:
    # without it, a hash of a short value is reversed by enumerating the space.
    raise NotImplementedError("implement pseudonym")

def redact(text: str, *, salt: str = "lab-salt") -> Redaction:
    """Replace every detected identifier with a stable pseudonym."""
    # TASK 2: replace every detected identifier with its pseudonym.
    # Walk PATTERNS in ORDER -- longer, more specific detectors first -- and
    # skip any match overlapping a span already claimed, or a phone matcher
    # will eat part of a card number and leave the rest in the text.
    # Apply replacements from the END of the string backwards so earlier
    # offsets stay valid. Return findings sorted by position.
    raise NotImplementedError("implement redact")

@dataclass
class DataFlow:
    """Which stores a subject's data has reached.

    Personal data does not sit still. It arrives in a request, is written to a
    database, embedded into an index, cached, and logged -- and every one of
    those is a place a deletion has to reach.
    """

    stores: dict[str, set[str]] = field(default_factory=dict)

    def record(self, store: str, subject_id: str) -> None:
        self.stores.setdefault(store, set()).add(subject_id)

    def where(self, subject_id: str) -> set[str]:
        return {name for name, ids in self.stores.items() if subject_id in ids}

    def delete(self, store: str, subject_id: str) -> bool:
        ids = self.stores.get(store, set())
        if subject_id in ids:
            ids.discard(subject_id)
            return True
        return False


@dataclass
class ErasureReport:
    subject_id: str
    deleted_from: list[str] = field(default_factory=list)
    still_present: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.still_present

    def summary(self) -> str:
        status = "COMPLETE" if self.complete else "INCOMPLETE"
        remaining = ",".join(self.still_present) if self.still_present else "none"
        return (
            f"{status} deleted_from={len(self.deleted_from)} "
            f"still_present={remaining}"
        )


def erase(flow: DataFlow, subject_id: str, *, stores: list[str] | None = None) -> ErasureReport:
    """Delete a subject from the named stores, then VERIFY.

    The verification is the point. Issuing deletes and reporting success is how
    a right-to-erasure request quietly fails -- a store the code forgot, or one
    that accepted the call and did not act. Re-reading afterwards is what turns
    an intention into evidence.
    """
    # TASK 3: delete the subject from each target store, then VERIFY.
    # Record which stores actually held them (delete returns a bool), then
    # re-read flow.where(subject_id) and put whatever remains in
    # still_present. Reporting from the delete calls alone is how an erasure
    # silently fails -- a store nobody remembered looks identical to one that
    # was empty.
    raise NotImplementedError("implement erase")

def minimise(record: dict[str, str], keep: set[str]) -> dict[str, str]:
    """Keep only the fields a purpose actually needs.

    The cheapest privacy control there is: data you never collected cannot
    leak, cannot be subpoenaed, and does not need deleting.
    """
    # TASK 4: return only the fields named in `keep`. Fields in `keep` that
    # are absent from the record are simply not present in the result.
    raise NotImplementedError("implement minimise")
