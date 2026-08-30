"""Tests for the seam auditor.

An auditor needs two kinds of test: that it passes a conformant system, and --
more importantly -- that it FAILS a broken one. A checker that has never caught
anything is not evidence of anything.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from seam_audit import (  # noqa: E402
    CHECKS,
    BrokenAssistant,
    ConformantAssistant,
    Doc,
    audit,
    check_erasure_is_complete,
    check_redaction_before_indexing,
    check_shared_budget,
    sample_docs,
)


# ------------------------------------------------- the auditor passes good


def test_conformant_assistant_passes_every_check():
    report = audit(ConformantAssistant)
    assert report.conformant, f"unexpected failures: {report.failures()}"
    assert report.summary() == "CONFORMANT (5/5 checks passed)"


def test_every_check_is_actually_run():
    report = audit(ConformantAssistant)
    assert len(report.checks) == len(CHECKS) == 5
    names = {c.name for c in report.checks}
    assert names == {
        "redaction_before_indexing",
        "shared_budget",
        "erasure_is_complete",
        "cursor_advances_on_failure",
        "no_orphans_on_shrink",
    }


# ------------------------------------------- the auditor catches the broken


def test_broken_assistant_is_reported_non_conformant():
    report = audit(BrokenAssistant)
    assert not report.conformant


def test_it_catches_redaction_running_after_indexing():
    check = check_redaction_before_indexing(BrokenAssistant)
    assert not check.passed
    assert "address" in check.detail


def test_it_catches_retrieval_escaping_the_shared_budget():
    check = check_shared_budget(BrokenAssistant)
    assert not check.passed
    assert "retrieval" in check.detail


def test_it_catches_an_erasure_that_forgets_the_cache():
    check = check_erasure_is_complete(BrokenAssistant)
    assert not check.passed
    assert "cache" in check.detail


def test_it_names_exactly_the_three_planted_defects():
    # Precision matters as much as recall: an auditor that fails everything is
    # as useless as one that fails nothing.
    report = audit(BrokenAssistant)
    assert sorted(report.failures()) == [
        "erasure_is_complete",
        "redaction_before_indexing",
        "shared_budget",
    ]


# ------------------------------------------------ the reference assistant


def test_conformant_ingest_is_idempotent():
    bot = ConformantAssistant()
    bot.ingest(sample_docs())
    first = dict(bot.chunks)
    bot.ingest(sample_docs())
    assert bot.chunks == first


def test_dead_letter_advances_the_cursor():
    bot = ConformantAssistant()
    bot.ingest(sample_docs())
    # The third document has no body; the cursor must still pass it.
    assert bot.cursor == 3


def test_conformant_erase_clears_all_three_stores():
    bot = ConformantAssistant()
    bot.ingest(sample_docs())
    bot.answer("What is the refund window?")
    bot.erase("policy")
    assert not any(c.startswith("policy::") for c in bot.chunks)
    assert "policy" not in bot.hashes
    assert not any("policy" in a for a in bot.cache.values())


def test_shrinking_document_leaves_no_orphans():
    bot = ConformantAssistant()
    bot.ingest([Doc("long", 1, "alpha beta gamma delta " * 30)])
    many = sum(1 for c in bot.chunks if c.startswith("long::"))
    bot.ingest([Doc("long", 2, "alpha beta")])
    few = sum(1 for c in bot.chunks if c.startswith("long::"))
    assert 1 == few < many


def test_cached_answer_is_free_and_recorded():
    bot = ConformantAssistant()
    bot.ingest(sample_docs())
    bot.answer("q")
    spend = sum(c for _, c in bot.ledger)
    bot.answer("q")
    assert sum(c for _, c in bot.ledger) == spend
    assert any(stage == "cache" for stage, _ in bot.ledger)
