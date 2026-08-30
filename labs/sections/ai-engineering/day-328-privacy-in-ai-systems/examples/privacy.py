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
    digest = hashlib.sha256((salt + value).encode("utf-8")).hexdigest()[:10]
    return f"[{category.value}:{digest}]"


def redact(text: str, *, salt: str = "lab-salt") -> Redaction:
    """Replace every detected identifier with a stable pseudonym."""
    findings: list[Finding] = []
    spans: list[tuple[int, int, str]] = []
    claimed: list[tuple[int, int]] = []

    for category in ORDER:
        for match in PATTERNS[category].finditer(text):
            start, end = match.span()
            # Skip anything already covered by a more specific detector.
            if any(s < end and start < e for s, e in claimed):
                continue
            token = pseudonym(match.group(), category, salt=salt)
            findings.append(Finding(category, start, end, token))
            spans.append((start, end, token))
            claimed.append((start, end))

    out = text
    for start, end, token in sorted(spans, key=lambda s: -s[0]):
        out = out[:start] + token + out[end:]

    findings.sort(key=lambda f: f.start)
    return Redaction(text=out, findings=findings)


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
    targets = stores if stores is not None else list(flow.stores)
    report = ErasureReport(subject_id=subject_id)
    for store in targets:
        if flow.delete(store, subject_id):
            report.deleted_from.append(store)
    report.still_present = sorted(flow.where(subject_id))
    return report


def minimise(record: dict[str, str], keep: set[str]) -> dict[str, str]:
    """Keep only the fields a purpose actually needs.

    The cheapest privacy control there is: data you never collected cannot
    leak, cannot be subpoenaed, and does not need deleting.
    """
    return {k: v for k, v in record.items() if k in keep}
