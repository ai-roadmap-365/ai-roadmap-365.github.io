"""Grouped by drift category, so a failure names which one is misclassified.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from freshness import (  # noqa: E402
    Drift,
    Record,
    compare,
    percentile,
    reconcile,
    safe_to_delete,
    staleness_age,
)


def rec(doc_id: str, version: str, updated_at: int = 0) -> Record:
    return Record(doc_id, version, updated_at)


# ------------------------------------------------------------ classification


def test_identical_documents_are_fresh():
    src = {"a": rec("a", "v1")}
    idx = {"a": rec("a", "v1")}
    report = compare(src, idx)
    assert report.count(Drift.FRESH) == 1
    assert report.summary() == "fresh=1 missing=0 stale=0 orphaned=0"


def test_document_only_at_source_is_missing():
    report = compare({"a": rec("a", "v1")}, {})
    assert report.by_drift(Drift.MISSING)[0].doc_id == "a"


def test_differing_version_is_stale():
    report = compare({"a": rec("a", "v2")}, {"a": rec("a", "v1")})
    finding = report.by_drift(Drift.STALE)[0]
    assert finding.doc_id == "a"
    assert "v1" in finding.detail and "v2" in finding.detail


def test_document_only_in_index_is_orphaned():
    # The category a source-only scan can never find, because an orphan is
    # exactly a document the source no longer mentions.
    report = compare({}, {"gone": rec("gone", "v1")})
    assert report.by_drift(Drift.ORPHANED)[0].doc_id == "gone"


def test_every_document_lands_in_exactly_one_category():
    src = {"a": rec("a", "v1"), "b": rec("b", "v2")}
    idx = {"b": rec("b", "v1"), "c": rec("c", "v1")}
    report = compare(src, idx)
    ids = [f.doc_id for f in report.findings]
    assert sorted(ids) == ["a", "b", "c"]
    assert len(ids) == len(set(ids))


def test_comparison_walks_the_union_not_just_the_source():
    # Iterating the source alone would report a clean index here.
    report = compare({}, {"x": rec("x", "v1"), "y": rec("y", "v1")})
    assert report.count(Drift.ORPHANED) == 2


# ----------------------------------------------------------------- staleness


def test_staleness_age_measures_only_stale_documents():
    src = {"a": rec("a", "v2", updated_at=10), "b": rec("b", "v1", updated_at=3)}
    idx = {"a": rec("a", "v1", updated_at=4), "b": rec("b", "v1", updated_at=3)}
    ages = staleness_age(src, idx, now=20)
    assert set(ages) == {"a"}
    assert ages["a"] == 10


def test_staleness_age_is_never_negative():
    src = {"a": rec("a", "v2", updated_at=30)}
    idx = {"a": rec("a", "v1", updated_at=1)}
    assert staleness_age(src, idx, now=10)["a"] == 0


def test_percentile_of_empty_is_zero():
    assert percentile([], 95) == 0


def test_percentile_picks_a_real_observation():
    values = [1, 2, 3, 4, 100]
    assert percentile(values, 95) == 100
    assert percentile(values, 50) == 3
    assert percentile(values, 100) == 100


# --------------------------------------------------------------- reconcile


def test_reconcile_fixes_every_category():
    src = {"a": rec("a", "v1"), "b": rec("b", "v2")}
    idx = {"b": rec("b", "v1"), "c": rec("c", "v1")}
    report = compare(src, idx)
    result = reconcile(src, idx, report)

    assert result.indexed == ["a"]
    assert result.updated == ["b"]
    assert result.deleted == ["c"]
    assert compare(src, idx).summary() == "fresh=2 missing=0 stale=0 orphaned=0"


def test_reconcile_is_idempotent():
    src = {"a": rec("a", "v1"), "b": rec("b", "v2")}
    idx = {"b": rec("b", "v1"), "c": rec("c", "v1")}
    reconcile(src, idx, compare(src, idx))
    snapshot = dict(idx)

    second = reconcile(src, idx, compare(src, idx))
    assert second.summary() == "indexed=0 updated=0 deleted=0"
    assert idx == snapshot


def test_deletes_can_be_withheld():
    src: dict[str, Record] = {}
    idx = {"gone": rec("gone", "v1")}
    result = reconcile(src, idx, compare(src, idx), allow_deletes=False)
    assert result.deleted == []
    assert "gone" in idx


# ------------------------------------------------------------- delete guard


def test_guard_blocks_an_implausible_mass_deletion():
    # The source enumeration returned nothing -- an auth failure, say. Every
    # indexed document now looks orphaned.
    idx = {f"doc-{i}": rec(f"doc-{i}", "v1") for i in range(20)}
    report = compare({}, idx)
    assert report.count(Drift.ORPHANED) == 20
    assert safe_to_delete(report) is False


def test_guard_allows_a_normal_amount_of_deletion():
    src = {f"doc-{i}": rec(f"doc-{i}", "v1") for i in range(19)}
    idx = dict(src)
    idx["doc-gone"] = rec("doc-gone", "v1")
    report = compare(src, idx)
    assert report.count(Drift.ORPHANED) == 1
    assert safe_to_delete(report) is True


def test_guard_permits_an_empty_index():
    assert safe_to_delete(compare({}, {})) is True


def test_guard_threshold_is_configurable():
    src = {"a": rec("a", "v1")}
    idx = {"a": rec("a", "v1"), "b": rec("b", "v1"), "c": rec("c", "v1")}
    report = compare(src, idx)  # 2 of 3 orphaned
    assert safe_to_delete(report, max_fraction=0.25) is False
    assert safe_to_delete(report, max_fraction=0.9) is True
