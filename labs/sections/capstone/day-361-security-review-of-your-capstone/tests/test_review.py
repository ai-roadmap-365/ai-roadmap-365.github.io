"""Grouped by check, plus a group proving the review CAN fail.

A review that has never found anything is not evidence of safety. Half of this
suite exists to show each check catches the weakness it owns, and only that one.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from review import (  # noqa: E402
    CHECKS,
    SOUND,
    WEAK,
    Posture,
    Severity,
    review,
)


def failing(posture) -> set[str]:
    return review(posture).names()


# ------------------------------------------------------- the sound baseline


def test_a_sound_posture_passes_cleanly():
    report = review(SOUND)
    assert report.worst is Severity.OK
    assert report.names() == set()
    assert report.summary() == "PASS high=0 medium=0 low=0"


def test_every_check_runs():
    assert len(review(SOUND).findings) == len(CHECKS) == 7


# ------------------------------------------- each check catches its own flaw


def test_unmarked_untrusted_content_is_high():
    assert failing(Posture(marks_untrusted_content=False)) == {"untrusted_content_boundary"}


def test_unescaped_output_is_high():
    assert failing(Posture(escapes_output=False)) == {"output_handling"}


def test_executing_model_output_is_high():
    report = review(Posture(executes_model_output=True))
    finding = next(f for f in report.findings if f.check == "output_handling")
    assert finding.severity is Severity.HIGH
    assert "executed" in finding.detail


def test_destructive_scope_without_confirmation_is_high():
    assert failing(Posture(tool_scopes=("read:docs", "delete:records"))) == {"tool_permissions"}


def test_missing_spend_caps_is_high():
    assert failing(Posture(per_request_cap=None, per_user_daily_cap=None)) == {"spend_bounds"}


def test_secrets_in_the_image_is_high():
    assert failing(Posture(secrets_in_image=True)) == {"secret_handling"}


def test_secrets_in_the_repository_is_high_and_mentions_rotation():
    report = review(Posture(secrets_in_repository=True))
    finding = next(f for f in report.findings if f.check == "secret_handling")
    assert finding.severity is Severity.HIGH
    # Deleting the file does not remove it from history, so rotation comes first.
    assert "rotate" in finding.remediation


def test_unpinned_dependencies_are_medium():
    report = review(Posture(image_pinned_by_digest=False, dependencies_locked=False))
    finding = next(f for f in report.findings if f.check == "dependency_pinning")
    assert finding.severity is Severity.MEDIUM


# ---------------------------------------------------------------- severity


def test_severity_reflects_blast_radius_not_novelty():
    # A missing spend cap is dull and can take the service down; an unlocked
    # dependency is more interesting and less immediately dangerous.
    spend = next(f for f in review(Posture(per_request_cap=None, per_user_daily_cap=None)).findings
                 if f.check == "spend_bounds")
    deps = next(f for f in review(Posture(dependencies_locked=False)).findings
                if f.check == "dependency_pinning")
    assert spend.severity is Severity.HIGH
    assert deps.severity is Severity.MEDIUM


def test_one_missing_cap_is_less_severe_than_both():
    one = next(f for f in review(Posture(per_user_daily_cap=None)).findings
               if f.check == "spend_bounds")
    both = next(f for f in review(Posture(per_request_cap=None, per_user_daily_cap=None)).findings
                if f.check == "spend_bounds")
    assert one.severity is Severity.MEDIUM
    assert both.severity is Severity.HIGH


def test_a_confirmed_destructive_scope_is_only_low():
    report = review(
        Posture(tool_scopes=("read:docs", "write:tickets"),
                tools_require_confirmation=("write:tickets",))
    )
    finding = next(f for f in report.findings if f.check == "tool_permissions")
    assert finding.severity is Severity.LOW
    # Low findings do not fail the review.
    assert report.summary().startswith("PASS")


def test_a_high_finding_fails_the_review():
    assert review(Posture(escapes_output=False)).summary().startswith("FAIL")


# ------------------------------------------- the review can actually fail


def test_the_weak_posture_fails_loudly():
    report = review(WEAK)
    assert report.worst is Severity.HIGH
    assert report.summary() == "FAIL high=6 medium=1 low=0"


def test_the_weak_posture_trips_every_check():
    # Precision as well as recall: all seven checks report a problem, and the
    # sound posture reports none. A checker that cannot fail proves nothing.
    assert review(WEAK).names() == {c.__name__.replace("check_", "") for c in CHECKS}


def test_findings_that_fail_carry_remediation():
    for finding in review(WEAK).findings:
        if finding.severity is not Severity.OK:
            assert finding.remediation or finding.check == "tool_permissions", (
                f"{finding.check} has no remediation"
            )


def test_at_least_filters_by_severity():
    report = review(WEAK)
    assert len(report.at_least(Severity.HIGH)) == 6
    assert len(report.at_least(Severity.MEDIUM)) == 7
