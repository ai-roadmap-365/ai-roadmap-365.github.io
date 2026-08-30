#!/usr/bin/env python3
"""Detect drift between a source and an index, then reconcile it."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from freshness import (
    Drift,
    Record,
    compare,
    percentile,
    reconcile,
    safe_to_delete,
    staleness_age,
)


def build_state():
    source = {
        "doc-1": Record("doc-1", "v2", updated_at=10),
        "doc-2": Record("doc-2", "v1", updated_at=2),
        "doc-3": Record("doc-3", "v5", updated_at=18),
        "doc-4": Record("doc-4", "v1", updated_at=4),
    }
    index = {
        "doc-1": Record("doc-1", "v1", updated_at=3),
        "doc-2": Record("doc-2", "v1", updated_at=2),
        "doc-3": Record("doc-3", "v4", updated_at=11),
        "doc-9": Record("doc-9", "v1", updated_at=1),
    }
    return source, index


def main() -> int:
    source, index = build_state()
    now = 20

    report = compare(source, index, now=now)
    for finding in report.findings:
        line = f"{finding.doc_id:<8} {finding.drift.value}"
        if finding.detail:
            line = f"{finding.doc_id:<8} {finding.drift.value:<9} {finding.detail}"
        print(line)
    print(report.summary())

    ages = staleness_age(source, index, now=now)
    print(f"staleness ages: {ages}")
    print(f"p95 staleness: {percentile(list(ages.values()), 95)} ticks")

    print(f"safe to delete: {safe_to_delete(report)}")
    result = reconcile(source, index, report)
    print(result.summary())

    after = compare(source, index, now=now)
    print(f"after reconcile: {after.summary()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
