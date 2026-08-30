"""Grouped by what the plan check decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from plan import (  # noqa: E402
    Commitment,
    dropped,
    findings,
    has_artifact,
    is_actionable,
    review,
    topic_verbs_in,
    trim_to_fit,
    weekly_load,
    with_calibration,
)


def c(topic, action="build a thing", artifact="a repository", hours=1.0, weeks=4, priority=3):
    return Commitment(topic, action, artifact, hours, weeks, priority)


# ---------------------------------------------------------------- actionable


def test_an_action_verb_makes_a_next_action():
    assert is_actionable("build a 50-question eval set and run it weekly")
    assert is_actionable("publish one post on what the retrospective found")


def test_a_topic_verb_is_not_a_next_action():
    assert not is_actionable("learn how LoRA works")
    assert not is_actionable("get better at distributed systems")
    assert not is_actionable("explore the main agent frameworks")


def test_a_topic_verb_disqualifies_even_with_an_action_verb_present():
    # "build up my understanding" is a topic wearing an action's clothes.
    assert not is_actionable("build up my understanding of evals")


def test_an_empty_next_action_is_not_actionable():
    assert not is_actionable("")
    assert not is_actionable("   ")


def test_topic_verbs_are_listed_including_multiword_forms():
    assert topic_verbs_in("I want to get better at evals and read about agents") == [
        "get better at",
        "read about",
    ]


# ------------------------------------------------------------------ artifact


def test_a_commitment_with_an_artifact_is_checkable():
    assert has_artifact(c("evals", artifact="eval suite in the repository"))


def test_a_commitment_with_no_artifact_is_not():
    assert not has_artifact(c("agents", artifact=""))
    assert not has_artifact(c("agents", artifact="   "))


def test_total_hours_is_the_weekly_cost_over_the_weeks():
    assert c("evals", hours=3, weeks=8).total_hours == 24


# ---------------------------------------------------------------------- load


def test_load_sums_the_weekly_hours():
    load = weekly_load([c("a", hours=3), c("b", hours=2)], 5.0)
    assert load.weekly == 5.0
    assert load.fits


def test_a_plan_one_hour_over_does_not_fit():
    load = weekly_load([c("a", hours=3), c("b", hours=3)], 5.0)
    assert not load.fits
    assert round(load.ratio, 2) == 1.2


def test_zero_available_hours_does_not_divide_by_zero():
    assert weekly_load([c("a", hours=3)], 0.0).ratio == 0.0


# --------------------------------------------------------------- calibration


def test_calibration_recosts_every_commitment():
    costed = with_calibration([c("a", hours=3), c("b", hours=2)], 1.20)
    assert [x.hours_per_week for x in costed] == [3.6, 2.4]


def test_calibration_preserves_everything_but_the_hours():
    original = c("evals", action="build an eval set", artifact="a suite", hours=3, priority=1)
    costed = with_calibration([original], 1.5)[0]
    assert (costed.topic, costed.next_action, costed.artifact, costed.priority) == (
        "evals",
        "build an eval set",
        "a suite",
        1,
    )


def test_a_nonsensical_calibration_leaves_the_plan_alone():
    plan = [c("a", hours=3)]
    assert with_calibration(plan, 0.0) == plan
    assert with_calibration(plan, -1.0) == plan


# ---------------------------------------------------------------------- trim


def test_the_trim_keeps_highest_priority_first():
    plan = [c("low", hours=3, priority=5), c("high", hours=3, priority=1)]
    assert [x.topic for x in trim_to_fit(plan, 5.0)] == ["high"]


def test_the_trim_is_not_proportional():
    # Six commitments halved is six things done badly. The plan that fits is
    # the plan that happens.
    plan = [c(f"t{i}", hours=2, priority=i) for i in range(1, 7)]
    kept = trim_to_fit(plan, 5.0)
    assert len(kept) == 2
    assert all(x.hours_per_week == 2 for x in kept)


def test_the_trim_skips_past_something_too_big_to_fit():
    # A known and deliberate property: the top-priority commitment does not fit
    # at all, so a cheaper lower-priority one survives instead. Stopping at the
    # first thing that does not fit would waste every remaining hour.
    #
    # The right response to this output is usually to SPLIT the p1 commitment,
    # not to accept the p5 one in its place. The tool cannot make that call.
    plan = [c("dear", hours=6, priority=1), c("cheap", hours=1, priority=5)]
    assert [x.topic for x in trim_to_fit(plan, 5.0)] == ["cheap"]


def test_a_plan_that_already_fits_is_kept_whole():
    plan = [c("a", hours=2), c("b", hours=2)]
    assert len(trim_to_fit(plan, 5.0)) == 2
    assert dropped(plan, 5.0) == []


def test_dropped_names_what_the_trim_removed():
    plan = [c("keep", hours=3, priority=1), c("drop", hours=3, priority=2)]
    assert [x.topic for x in dropped(plan, 5.0)] == ["drop"]


def test_duplicate_commitments_are_not_confused_with_each_other():
    # Two identical commitments are equal as dataclasses; the trim must still
    # keep one and drop the other rather than dropping both.
    same = c("evals", hours=3, priority=1)
    plan = [same, c("evals", hours=3, priority=1)]
    assert len(trim_to_fit(plan, 5.0)) == 1
    assert len(dropped(plan, 5.0)) == 1


# -------------------------------------------------------------------- review


def test_the_review_reports_every_failure_kind():
    plan = [
        c("good", action="build an eval set", artifact="a suite", hours=2, priority=1),
        c("vague", action="learn about agents", artifact="", hours=4, priority=2),
    ]
    report = review(plan, 5.0)
    assert [x.topic for x in report.not_actionable] == ["vague"]
    assert [x.topic for x in report.no_artifact] == ["vague"]
    assert [x.topic for x in report.kept] == ["good"]


def test_the_review_applies_calibration_before_measuring_the_load():
    plan = [c("a", hours=4)]
    assert review(plan, 5.0).load.fits
    assert not review(plan, 5.0, calibration=1.5).load.fits


# ------------------------------------------------------------------ findings


def test_findings_state_how_far_over_the_plan_is():
    plan = [c(f"t{i}", hours=3) for i in range(4)]
    out = findings(plan, 5.0)
    assert any("2.40x over before it starts" in f for f in out)


def test_findings_name_each_cut_commitment():
    plan = [c("keep", hours=3, priority=1), c("cut me", hours=3, priority=2)]
    out = findings(plan, 5.0)
    assert any(f.startswith("cut: cut me") for f in out)


def test_findings_quote_the_wording_that_needs_rewriting():
    plan = [c("agents", action="explore the main agent frameworks", hours=1)]
    out = findings(plan, 5.0)
    assert any("rewrite 'explore the main agent frameworks'" in f for f in out)


def test_findings_say_so_when_the_plan_fits():
    plan = [c("a", action="build an eval set", artifact="a suite", hours=2)]
    out = findings(plan, 5.0)
    assert any("The plan fits" in f for f in out)
    assert not any(f.startswith("cut:") for f in out)


def test_findings_disclose_that_calibration_was_applied():
    plan = [c("a", action="build an eval set", artifact="a suite", hours=2)]
    assert any("1.20x" in f for f in findings(plan, 5.0, calibration=1.20))
    assert not any("rather than in optimistic hours" in f for f in findings(plan, 5.0))
