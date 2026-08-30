"""Week 47 project tests.

Grouped so a failure names which day's idea broke, plus a group for the
INTERACTIONS between them -- which is the part a section project exists to
exercise and which no single day's tests can reach.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from assistant import (  # noqa: E402
    Assistant,
    BudgetExceeded,
    SourceDoc,
    embed,
    quality_ok,
    redact,
)


def corpus() -> list[SourceDoc]:
    return [
        SourceDoc("sla", 1, "Enterprise uptime guarantee is 99.99 percent per month. " * 3),
        SourceDoc("refunds", 2, "The refund window is thirty days. Contact ada@example.com. " * 3),
        SourceDoc("broken", 3, None),
        SourceDoc("garbled", 4, "=?# " * 60),
    ]


# --------------------------------------------------- day 323: ingestion


def test_ingest_is_idempotent():
    bot = Assistant()
    bot.ingest(corpus())
    first = dict(bot.chunks)
    bot.ingest(corpus())
    assert bot.chunks.keys() == first.keys()


def test_cursor_advances_so_a_second_run_scans_nothing():
    bot = Assistant()
    bot.ingest(corpus())
    assert bot.ingest(corpus()).scanned == 0


def test_unchanged_document_is_not_reindexed():
    bot = Assistant()
    bot.ingest(corpus())
    # Same content presented at a higher sequence: scanned, but not reindexed.
    again = corpus() + [SourceDoc("sla", 9, "Enterprise uptime guarantee is 99.99 percent per month. " * 3)]
    stats = bot.ingest(again)
    assert stats.scanned == 1
    assert stats.skipped_unchanged == 1
    assert stats.indexed == 0


# -------------------------------------------------- day 324: processing


def test_unreadable_and_garbled_documents_are_dead_lettered():
    bot = Assistant()
    stats = bot.ingest(corpus())
    assert stats.dead_lettered == 2
    assert sorted(bot.dead_letters) == ["broken", "garbled"]


def test_dead_letters_do_not_stop_the_run():
    bot = Assistant()
    bot.ingest(corpus())
    assert {c.doc_id for c in bot.chunks.values()} == {"sla", "refunds"}


def test_quality_gate_rejects_low_alphabetic_text():
    assert quality_ok("real words here", 20) is True
    assert quality_ok("=?# " * 20, 80) is False


# --------------------------------------------------- day 325: freshness


def test_edited_document_replaces_rather_than_duplicates():
    bot = Assistant()
    bot.ingest(corpus())
    other_docs = {c for c in bot.chunks if not c.startswith("refunds")}
    old_text = " ".join(c.text for c in bot.chunks.values() if c.doc_id == "refunds")
    assert "thirty" in old_text

    bot.ingest(corpus() + [SourceDoc("refunds", 8, "The refund window is now sixty days. " * 3)])

    new_text = " ".join(c.text for c in bot.chunks.values() if c.doc_id == "refunds")
    assert "sixty" in new_text, "the edit should be indexed"
    assert "thirty" not in new_text, "the old version should be replaced, not kept alongside"
    # Chunk ids are positional, so an update reuses them rather than appending.
    assert {c for c in bot.chunks if not c.startswith("refunds")} == other_docs


def test_shrinking_document_leaves_no_orphans():
    bot = Assistant()
    bot.ingest([SourceDoc("long", 1, "alpha beta gamma delta " * 40)])
    many = len([c for c in bot.chunks.values() if c.doc_id == "long"])
    assert many > 1

    bot.ingest([SourceDoc("long", 2, "alpha beta gamma")])
    few = len([c for c in bot.chunks.values() if c.doc_id == "long"])
    assert few < many
    ids = {c for c in bot.chunks if c.startswith("long::")}
    assert ids == {f"long::{i}" for i in range(few)}


# --------------------------------------------------- day 326: retrieval


def test_retrieval_ranks_the_relevant_document_first():
    bot = Assistant()
    bot.ingest(corpus())
    hits = bot.retrieve("What is the refund window?", k=3)
    assert hits[0].doc_id == "refunds"


def test_embedding_is_deterministic():
    assert embed("the refund window") == embed("the refund window")


def test_wider_embedding_reduces_collisions():
    # Collision rate is a retrieval-quality parameter. At dim=8 unrelated text
    # is forced to share buckets; at dim=256 it is not.
    from assistant import cosine

    narrow = cosine(embed("refund window", dim=8), embed("uptime guarantee", dim=8))
    wide = cosine(embed("refund window", dim=256), embed("uptime guarantee", dim=256))
    assert wide < narrow


# -------------------------------------------------------- day 327: cost


def test_repeat_question_is_served_from_cache_at_no_cost():
    bot = Assistant()
    bot.ingest(corpus())
    bot.answer("What is the refund window?")
    before = bot.ledger.total
    bot.answer("What is the refund window?")
    assert bot.ledger.total == before


def test_reasoning_questions_route_to_the_large_model():
    bot = Assistant()
    bot.ingest(corpus())
    bot.answer("Compare the tiers")
    assert "large" in bot.ledger.by_stage()


def test_budget_is_enforced_before_spending():
    bot = Assistant(budget=0.000001)
    bot.ingest(corpus())
    with pytest.raises(BudgetExceeded):
        bot.answer("What is the refund window?")


def test_retrieval_is_charged_to_the_same_budget():
    # A recall setting is also a cost setting -- that only shows up once the
    # stages share a ledger.
    bot = Assistant()
    bot.ingest(corpus())
    bot.retrieve("anything")
    assert bot.ledger.by_stage()["retrieval"] > 0


# ----------------------------------------------------- day 328: privacy


def test_identifiers_are_redacted_before_indexing():
    bot = Assistant()
    bot.ingest(corpus())
    # If redaction ran after indexing, the address would be inside a chunk --
    # and inside its vector, where removing it means re-embedding.
    for chunk in bot.chunks.values():
        assert "ada@example.com" not in chunk.text
    assert any("[email:" in c.text for c in bot.chunks.values())


def test_redaction_is_counted():
    assert redact("mail ada@example.com")[1] == 1
    assert redact("no identifiers here")[1] == 0


# ------------------------------------------------------- INTERACTIONS


def test_erasure_reaches_the_index_the_hashes_and_the_cache():
    # The cache is the store that gets forgotten, and it is the one that can
    # keep answering from deleted content.
    bot = Assistant()
    bot.ingest(corpus())
    bot.answer("What is the refund window?")
    assert any("refunds" in a for a in bot.cache.values())

    verified = bot.erase("refunds")
    assert verified == {"index": True, "hashes": True, "cache": True}
    assert not any(c.doc_id == "refunds" for c in bot.chunks.values())
    assert not any("refunds" in a for a in bot.cache.values())


def test_erased_document_can_be_reingested_cleanly():
    # Erasure clears the content hash too, or a re-ingest would see the
    # document as unchanged and never restore it.
    bot = Assistant()
    bot.ingest(corpus())
    bot.erase("refunds")
    stats = bot.ingest([SourceDoc("refunds", 20, "The refund window is thirty days. " * 3)])
    assert stats.indexed > 0


def test_budget_accounts_for_retrieval_and_generation_together():
    bot = Assistant()
    bot.ingest(corpus())
    bot.answer("What is the refund window?")
    stages = bot.ledger.by_stage()
    assert "retrieval" in stages and "small" in stages
    assert bot.ledger.total == pytest.approx(sum(stages.values()))
