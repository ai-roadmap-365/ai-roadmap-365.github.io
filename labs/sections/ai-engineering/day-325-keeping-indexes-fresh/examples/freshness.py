"""Index freshness: detecting drift between a source and an index, and fixing it.

Offline and standard-library only. The source and index are in-memory, but the
drift categories are the real ones, and the point of the lab is that they are
genuinely different problems with genuinely different fixes.

Four ways an index drifts from its source:

  missing    at the source, absent from the index    -> a user cannot find it
  stale      in both, but the index holds an old copy -> answers cite old text
  orphaned   in the index, deleted at the source      -> the serious one
  fresh      in both and identical                    -> nothing to do

Orphaned is the category that matters most and gets noticed least. A missing
document produces a complaint. An orphaned one produces a confident answer from
content that was deleted -- sometimes for legal reasons.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class Drift(str, Enum):
    FRESH = "fresh"
    MISSING = "missing"
    STALE = "stale"
    ORPHANED = "orphaned"


@dataclass(frozen=True)
class Record:
    """A document as either side holds it."""

    doc_id: str
    version: str  # a content hash in production; a short token here
    updated_at: int  # logical clock, so tests are deterministic


@dataclass
class Finding:
    doc_id: str
    drift: Drift
    detail: str = ""


@dataclass
class FreshnessReport:
    findings: list[Finding] = field(default_factory=list)
    checked_at: int = 0

    def by_drift(self, drift: Drift) -> list[Finding]:
        return [f for f in self.findings if f.drift is drift]

    def count(self, drift: Drift) -> int:
        return len(self.by_drift(drift))

    def summary(self) -> str:
        return (
            f"fresh={self.count(Drift.FRESH)} missing={self.count(Drift.MISSING)} "
            f"stale={self.count(Drift.STALE)} orphaned={self.count(Drift.ORPHANED)}"
        )


def compare(source: dict[str, Record], index: dict[str, Record], *, now: int = 0) -> FreshnessReport:
    """Classify every document on either side into exactly one drift category.

    The union of both key sets matters, not just the source: iterating the
    source alone can never find an orphan, because an orphan is precisely a
    document the source no longer mentions. That asymmetry is why deletion
    propagation is so often missed.
    """
    findings: list[Finding] = []
    for doc_id in sorted(set(source) | set(index)):
        src = source.get(doc_id)
        idx = index.get(doc_id)
        if src is not None and idx is None:
            findings.append(Finding(doc_id, Drift.MISSING, "at source, not indexed"))
        elif src is None and idx is not None:
            findings.append(Finding(doc_id, Drift.ORPHANED, "deleted at source, still indexed"))
        elif src.version != idx.version:
            findings.append(
                Finding(doc_id, Drift.STALE, f"index at {idx.version}, source at {src.version}")
            )
        else:
            findings.append(Finding(doc_id, Drift.FRESH))
    return FreshnessReport(findings=findings, checked_at=now)


def staleness_age(source: dict[str, Record], index: dict[str, Record], *, now: int) -> dict[str, int]:
    """How long each stale document has been stale, in logical ticks.

    Freshness is a distribution, not a boolean. A p95 staleness age is what you
    can actually put in an objective; "the index is fresh" is not measurable.
    """
    ages: dict[str, int] = {}
    for doc_id, src in source.items():
        idx = index.get(doc_id)
        if idx is not None and idx.version != src.version:
            ages[doc_id] = max(0, now - src.updated_at)
    return ages


def percentile(values: list[int], p: float) -> int:
    """Nearest-rank percentile. Returns 0 for an empty input.

    The rank is `ceil(p/100 * N)`, which is the standard nearest-rank
    definition. `round` is wrong here and wrong in a way that is easy to miss:
    Python rounds halves to even, so `round(2.5)` is 2, and the p50 of
    [1, 2, 3, 4, 100] comes out as 2 rather than 3.
    """
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(p / 100 * len(ordered))))
    return ordered[rank - 1]


@dataclass
class ReconcileResult:
    indexed: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"indexed={len(self.indexed)} updated={len(self.updated)} "
            f"deleted={len(self.deleted)}"
        )


def reconcile(
    source: dict[str, Record],
    index: dict[str, Record],
    report: FreshnessReport,
    *,
    allow_deletes: bool = True,
) -> ReconcileResult:
    """Bring the index into agreement with the source.

    `allow_deletes` exists because deletion is the irreversible half. A
    reconciliation run against a source that failed to enumerate correctly --
    an auth error returning an empty list, say -- would otherwise delete the
    entire index. Production systems gate deletes behind a sanity check; see
    `safe_to_delete`.
    """
    result = ReconcileResult()
    for finding in report.findings:
        if finding.drift is Drift.MISSING:
            index[finding.doc_id] = source[finding.doc_id]
            result.indexed.append(finding.doc_id)
        elif finding.drift is Drift.STALE:
            index[finding.doc_id] = source[finding.doc_id]
            result.updated.append(finding.doc_id)
        elif finding.drift is Drift.ORPHANED and allow_deletes:
            del index[finding.doc_id]
            result.deleted.append(finding.doc_id)
    return result


def safe_to_delete(report: FreshnessReport, *, max_fraction: float = 0.25) -> bool:
    """Refuse a reconciliation that would delete an implausible share of the index.

    If the source enumeration silently returned nothing, every indexed document
    looks orphaned and a naive reconcile empties the index. The guard is crude
    on purpose: a threshold a human can reason about beats a clever heuristic
    nobody trusts at 3 a.m.
    """
    indexed_total = report.count(Drift.FRESH) + report.count(Drift.STALE) + report.count(Drift.ORPHANED)
    if indexed_total == 0:
        return True
    return (report.count(Drift.ORPHANED) / indexed_total) <= max_fraction
