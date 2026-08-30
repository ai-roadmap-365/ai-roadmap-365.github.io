"""One test per property, so a failure names what is broken.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from ingest import (  # noqa: E402
    Checkpoint,
    DeadLetter,
    ExtractionError,
    Index,
    SourceRecord,
    chunk_document,
    content_hash,
    extract,
    run_once,
)


def make_source() -> list[SourceRecord]:
    return [
        SourceRecord("doc-1", 1, "alpha " * 45),
        SourceRecord("doc-2", 2, "beta " * 80),
        SourceRecord("doc-3", 3, None),
        SourceRecord("doc-4", 4, "delta " * 30),
        SourceRecord("doc-5", 5, "epsilon " * 55),
    ]


def fresh():
    return Index(), Checkpoint(), []


# ---------------------------------------------------------------- idempotent


def test_second_run_over_unchanged_source_leaves_index_identical():
    source = make_source()
    index, checkpoint, dlq = fresh()

    run_once(source, index, checkpoint, dlq)
    after_first = dict(index.chunks)

    run_once(source, index, checkpoint, dlq)

    assert index.chunks.keys() == after_first.keys()
    assert len(index.chunks) == len(after_first)


def test_chunk_ids_are_stable_across_independent_runs():
    text = "gamma " * 100
    first = [c.chunk_id for c in chunk_document("doc-7", text)]
    second = [c.chunk_id for c in chunk_document("doc-7", text)]
    assert first == second
    # Scoped to the document, not to global processing order.
    assert all(cid.startswith("doc-7::") for cid in first)


def test_reindexing_from_a_clean_checkpoint_does_not_duplicate():
    source = make_source()
    index, checkpoint, dlq = fresh()
    run_once(source, index, checkpoint, dlq)
    size_once = len(index.chunks)

    # Same index, brand-new checkpoint: every document is reprocessed, but the
    # stable ids mean the writes replace rather than append.
    run_once(source, index, Checkpoint(), [])
    assert len(index.chunks) == size_once


# --------------------------------------------------------------- incremental


def test_unchanged_documents_are_not_embedded_again():
    source = make_source()
    index, checkpoint, dlq = fresh()
    run_once(source, index, checkpoint, dlq)

    # Cursor has not moved, so nothing is even scanned.
    second = run_once(source, index, checkpoint, dlq)
    assert second.scanned == 0
    assert second.embedded == 0

    # A document re-presented at a higher sequence with identical content is
    # scanned but must NOT be embedded -- that is the content hash working.
    source.append(SourceRecord("doc-1", 6, "alpha " * 45))
    third = run_once(source, index, checkpoint, dlq)
    assert third.scanned == 1
    assert third.changed == 0
    assert third.embedded == 0


def test_edited_document_is_embedded_again():
    source = make_source()
    index, checkpoint, dlq = fresh()
    run_once(source, index, checkpoint, dlq)

    source.append(SourceRecord("doc-1", 6, "alpha revised " * 40))
    stats = run_once(source, index, checkpoint, dlq)
    assert stats.changed == 1
    assert stats.embedded > 0


def test_content_hash_ignores_whitespace_reformatting():
    assert content_hash("a  b\n\nc") == content_hash("a b c")


# ------------------------------------------------------------------ resumable


def test_crash_resumes_from_last_committed_cursor():
    source = make_source()
    index, checkpoint, dlq = fresh()

    with pytest.raises(RuntimeError, match="simulated crash"):
        run_once(source, index, checkpoint, dlq, fail_after=2)

    # Two documents committed; the cursor reflects exactly that.
    crashed_at = checkpoint.cursor
    assert crashed_at > 0
    indexed_before = len(index.chunks)

    stats = run_once(source, index, checkpoint, dlq)

    # It resumed rather than restarted.
    assert stats.cursor == 5
    assert len(index.chunks) > indexed_before
    # And nothing below the cursor was scanned a second time.
    assert stats.scanned == len([r for r in source if r.seq > crashed_at])


def test_cursor_never_advances_past_uncommitted_work():
    source = make_source()
    index, checkpoint, dlq = fresh()
    seen: list[int] = []

    with pytest.raises(RuntimeError):
        run_once(source, index, checkpoint, dlq, fail_after=1, on_commit=seen.append)

    # Exactly one commit happened, and the cursor is at a real record boundary.
    assert seen == [1]
    assert checkpoint.cursor in {r.seq for r in source}


# ------------------------------------------------------------------- isolated


def test_failing_record_is_dead_lettered_and_run_continues():
    source = make_source()
    index, checkpoint, dlq = fresh()

    stats = run_once(source, index, checkpoint, dlq)

    assert stats.dead_lettered == 1
    assert dlq[0].doc_id == "doc-3"
    assert dlq[0].error == "ExtractionError"
    # The four healthy documents still made it in.
    assert index.doc_ids() == {"doc-1", "doc-2", "doc-4", "doc-5"}


def test_extract_raises_on_unreadable_payload():
    with pytest.raises(ExtractionError):
        extract(SourceRecord("doc-x", 99, None))


# ------------------------------------------------------- orphan reconciliation


def test_shrinking_document_leaves_no_orphaned_chunks():
    index, checkpoint, dlq = fresh()
    long_doc = [SourceRecord("doc-1", 1, "word " * 200)]
    run_once(long_doc, index, checkpoint, dlq)
    many = len([c for c in index.chunks.values() if c.doc_id == "doc-1"])
    assert many > 2

    short_doc = long_doc + [SourceRecord("doc-1", 2, "word " * 20)]
    run_once(short_doc, index, checkpoint, dlq)
    few = len([c for c in index.chunks.values() if c.doc_id == "doc-1"])

    assert few < many, "chunk count should shrink with the document"
    ids = {c.chunk_id for c in index.chunks.values() if c.doc_id == "doc-1"}
    assert ids == {f"doc-1::{i}" for i in range(few)}, "orphans were left behind"
