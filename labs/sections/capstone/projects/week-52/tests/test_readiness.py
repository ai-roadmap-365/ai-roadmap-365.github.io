"""Grouped by what the delivery gate decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from readiness import (  # noqa: E402
    CHECKABLE,
    Evidence,
    Kind,
    Requirement,
    assess,
    evidence_for,
    findings,
)

TODAY = date(2026, 8, 31)
RECENT = date(2026, 8, 30)
OLD = date(2026, 1, 1)


def req(rid="deployed", day=359, title="Deployed and reachable", blocking=True):
    return Requirement(rid, day, title, blocking)


# ------------------------------------------------------------------ evidence


def test_a_command_a_url_and_a_measurement_are_checkable():
    for kind in CHECKABLE:
        assert Evidence("r", kind, "something", RECENT).is_checkable


def test_an_assertion_is_not_evidence():
    # The claim is offered by the person with the strongest reason to
    # believe it, which is exactly why it is not evidence.
    assert not Evidence("r", Kind.ASSERTION, "monitoring is set up", RECENT).is_checkable


def test_a_bare_file_is_not_checkable():
    assert not Evidence("r", Kind.FILE, "security-review.md", RECENT).is_checkable


def test_a_checkable_kind_with_no_detail_is_not_checkable():
    assert not Evidence("r", Kind.COMMAND, "", RECENT).is_checkable
    assert not Evidence("r", Kind.COMMAND, "   ", RECENT).is_checkable


# --------------------------------------------------------------------- age


def test_evidence_with_no_date_is_treated_as_ancient():
    assert Evidence("r", Kind.COMMAND, "make test").is_stale(TODAY)


def test_evidence_verified_yesterday_is_fresh():
    assert not Evidence("r", Kind.COMMAND, "make test", RECENT).is_stale(TODAY)


def test_the_staleness_window_is_configurable():
    e = Evidence("r", Kind.COMMAND, "make test", date(2026, 8, 21))  # 10 days
    assert not e.is_stale(TODAY, after=30)
    assert e.is_stale(TODAY, after=7)


# ------------------------------------------------------- picking the best


def test_the_best_evidence_wins_not_the_first_listed():
    offered = [
        Evidence("demo", Kind.ASSERTION, "the demo works"),
        Evidence("demo", Kind.COMMAND, "bash scripts/demo.sh", RECENT),
    ]
    assert evidence_for(req("demo"), offered).kind is Kind.COMMAND


def test_the_order_evidence_is_listed_in_does_not_change_the_verdict():
    strong = Evidence("demo", Kind.COMMAND, "bash scripts/demo.sh", RECENT)
    weak = Evidence("demo", Kind.ASSERTION, "the demo works")
    assert evidence_for(req("demo"), [strong, weak]).kind is Kind.COMMAND
    assert evidence_for(req("demo"), [weak, strong]).kind is Kind.COMMAND


def test_evidence_for_another_requirement_does_not_count():
    offered = [Evidence("monitoring", Kind.COMMAND, "curl /metrics", RECENT)]
    assert evidence_for(req("deployed"), offered) is None


def test_an_explicit_none_is_the_same_as_offering_nothing():
    assert evidence_for(req("deployed"), [Evidence("deployed", Kind.NONE)]) is None


# ----------------------------------------------------------------- sorting


def test_each_requirement_lands_in_exactly_one_category():
    reqs = [req("a"), req("b"), req("c"), req("d")]
    offered = [
        Evidence("a", Kind.COMMAND, "make test", RECENT),
        Evidence("b", Kind.ASSERTION, "done"),
        Evidence("c", Kind.COMMAND, "make test", OLD),
    ]
    report = assess(reqs, offered, TODAY)
    assert [r.id for r in report.solid] == ["a"]
    assert [r.id for r in report.weak] == ["b"]
    assert [r.id for r in report.stale] == ["c"]
    assert [r.id for r in report.missing] == ["d"]
    assert len(report.solid + report.weak + report.stale + report.missing) == len(reqs)


def test_missing_is_checked_before_weak_and_weak_before_stale():
    # The advice differs per category, so the order matters. Nothing offered
    # is a missing requirement, not a stale one, even with no date.
    report = assess([req("a")], [], TODAY)
    assert [r.id for r in report.missing] == ["a"]
    assert report.stale == []


# --------------------------------------------------------------- blocking


def test_only_blocking_requirements_stop_delivery():
    reqs = [req("optional", blocking=False)]
    report = assess(reqs, [], TODAY)
    assert report.missing and report.ready


def test_a_single_missing_blocking_requirement_stops_delivery():
    report = assess([req("spend-cap")], [], TODAY)
    assert not report.ready
    assert [r.id for r in report.blockers] == ["spend-cap"]


def test_blockers_are_ordered_missing_then_weak_then_stale():
    reqs = [req("stale-one"), req("weak-one"), req("missing-one")]
    offered = [
        Evidence("stale-one", Kind.COMMAND, "make test", OLD),
        Evidence("weak-one", Kind.ASSERTION, "done"),
    ]
    assert [r.id for r in assess(reqs, offered, TODAY).blockers] == [
        "missing-one",
        "weak-one",
        "stale-one",
    ]


def test_a_fully_evidenced_delivery_is_ready():
    reqs = [req("a"), req("b")]
    offered = [
        Evidence("a", Kind.COMMAND, "make test", RECENT),
        Evidence("b", Kind.MEASUREMENT, "p95 840ms", RECENT),
    ]
    report = assess(reqs, offered, TODAY)
    assert report.ready
    assert len(report.solid) == 2


def test_an_empty_delivery_with_no_requirements_is_vacuously_ready():
    assert assess([], [], TODAY).ready


# ---------------------------------------------------------------- findings


def test_findings_lead_with_the_verdict():
    out = findings([req("a")], [], TODAY)
    assert out[0].startswith("NOT deliverable: 1 blocking requirement(s) of 1.")


def test_findings_say_so_when_the_delivery_is_ready():
    offered = [Evidence("a", Kind.COMMAND, "make test", RECENT)]
    out = findings([req("a")], offered, TODAY)
    assert "Deliverable." in out[0]
    assert len(out) == 1


def test_findings_mark_blocking_and_optional_differently():
    reqs = [req("a"), req("b", blocking=False)]
    out = findings(reqs, [], TODAY)
    assert any(f.startswith("BLOCKING:") for f in out)
    assert any(f.startswith("optional:") for f in out)


def test_findings_name_the_kind_of_evidence_that_was_too_weak():
    offered = [Evidence("a", Kind.ASSERTION, "it is set up")]
    out = findings([req("a", title="Monitoring")], offered, TODAY)
    assert any("rests on an assertion" in f for f in out)


def test_findings_report_how_stale_the_stale_evidence_is():
    offered = [Evidence("a", Kind.COMMAND, "gitleaks detect", date(2026, 6, 14))]
    out = findings([req("a", title="No secrets")], offered, TODAY)
    assert any("last verified 78 days ago" in f for f in out)


def test_findings_state_the_requirement_and_the_day_it_came_from():
    out = findings([req("spend-cap", day=360, title="A hard spend cap")], [], TODAY)
    assert any("'A hard spend cap' (day 360) has no evidence at all." in f for f in out)
