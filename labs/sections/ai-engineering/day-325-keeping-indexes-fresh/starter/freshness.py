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
    # TASK 1: classify every document into exactly one drift category.
    # Iterate sorted(set(source) | set(index)) -- the UNION. Iterating the
    # source alone can never find an orphan, because an orphan is precisely a
    # document the source no longer mentions.
    #   at source, not indexed        -> Drift.MISSING,  "at source, not indexed"
    #   indexed, not at source        -> Drift.ORPHANED, "deleted at source, still indexed"
    #   both, versions differ         -> Drift.STALE,    f"index at {i.version}, source at {s.version}"
    #   both, versions equal          -> Drift.FRESH,    no detail
    raise NotImplementedError("implement compare")

def staleness_age(source: dict[str, Record], index: dict[str, Record], *, now: int) -> dict[str, int]:
    """How long each stale document has been stale, in logical ticks.

    Freshness is a distribution, not a boolean. A p95 staleness age is what you
    can actually put in an objective; "the index is fresh" is not measurable.
    """
    # TASK 2: for each document present in BOTH sides with differing
    # versions, return now - source.updated_at, floored at 0. Documents that
    # are fresh, missing or orphaned do not appear in the result.
    raise NotImplementedError("implement staleness_age")

def percentile(values: list[int], p: float) -> int:
    """Nearest-rank percentile. Returns 0 for an empty input.

    The rank is `ceil(p/100 * N)`, which is the standard nearest-rank
    definition. `round` is wrong here and wrong in a way that is easy to miss:
    Python rounds halves to even, so `round(2.5)` is 2, and the p50 of
    [1, 2, 3, 4, 100] comes out as 2 rather than 3.
    """
    # TASK 3: nearest-rank percentile; return 0 for an empty list.
    # rank = ceil(p/100 * N), clamped to [1, N], then return ordered[rank-1].
    # Use math.ceil, NOT round: Python rounds halves to even, so round(2.5) is
    # 2 and the p50 of [1,2,3,4,100] would come out as 2 rather than 3.
    raise NotImplementedError("implement percentile")

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
    # TASK 4: apply the report.
    #   MISSING  -> index[doc_id] = source[doc_id];  result.indexed.append(id)
    #   STALE    -> index[doc_id] = source[doc_id];  result.updated.append(id)
    #   ORPHANED -> del index[doc_id] IF allow_deletes; result.deleted.append(id)
    # Reconciling twice against an unchanged source must do nothing the second
    # time.
    raise NotImplementedError("implement reconcile")

def safe_to_delete(report: FreshnessReport, *, max_fraction: float = 0.25) -> bool:
    """Refuse a reconciliation that would delete an implausible share of the index.

    If the source enumeration silently returned nothing, every indexed document
    looks orphaned and a naive reconcile empties the index. The guard is crude
    on purpose: a threshold a human can reason about beats a clever heuristic
    nobody trusts at 3 a.m.
    """
    # TASK 5: return False when the orphaned share of the INDEXED total
    # (fresh + stale + orphaned) exceeds max_fraction. An empty index is safe.
    # This is what stops a failed source enumeration -- one that returned
    # nothing but looked successful -- from emptying the whole index.
    raise NotImplementedError("implement safe_to_delete")
