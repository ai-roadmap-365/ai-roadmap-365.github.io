"""A small but complete incremental ingestion pipeline.

Everything here runs offline with the standard library only. The source and the
index are in-memory fakes; the mechanisms around them -- content hashing, stable
chunk ids, a durable cursor and a dead-letter queue -- are the real thing, which
is what makes their behaviour testable.

The four properties the tests check:

  idempotent  running twice over unchanged sources leaves the index identical
  incremental a second run embeds only documents whose content hash changed
  resumable   a crash resumes from the last committed cursor
  isolated    a record that fails extraction is dead-lettered; the run continues
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable, Iterable


class ExtractionError(RuntimeError):
    """Raised when a source record cannot be turned into text."""


@dataclass(frozen=True)
class SourceRecord:
    """A record as the source system presents it."""

    doc_id: str
    seq: int  # monotonic; the cursor is expressed in these terms
    payload: str | None  # None simulates a document that cannot be extracted


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str


@dataclass
class DeadLetter:
    doc_id: str
    error: str


@dataclass
class RunStats:
    scanned: int = 0
    changed: int = 0
    embedded: int = 0
    indexed: int = 0
    dead_lettered: int = 0
    cursor: int = 0

    def line(self, label: str) -> str:
        return (
            f"{label}: scanned={self.scanned} changed={self.changed} "
            f"embedded={self.embedded} indexed={self.indexed} "
            f"dead_lettered={self.dead_lettered} cursor={self.cursor}"
        )


@dataclass
class Index:
    """A fake vector index with upsert semantics keyed on chunk_id."""

    chunks: dict[str, Chunk] = field(default_factory=dict)

    def upsert(self, chunks: Iterable[Chunk]) -> int:
        written = 0
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
            written += 1
        return written

    def delete_orphans(self, doc_id: str, keep: set[str]) -> int:
        """Remove chunks of `doc_id` that are not in `keep`.

        A document that shrinks from twelve chunks to eight leaves four
        orphans behind. They stay retrievable and surface as stale answers, so
        reconciliation is part of a correct write, not an optimisation.
        """
        stale = [
            cid
            for cid, chunk in self.chunks.items()
            if chunk.doc_id == doc_id and cid not in keep
        ]
        for cid in stale:
            del self.chunks[cid]
        return len(stale)

    def doc_ids(self) -> set[str]:
        return {chunk.doc_id for chunk in self.chunks.values()}


@dataclass
class Checkpoint:
    """Durable-ish state: the cursor plus one content hash per document.

    Deliberately small. Storing extracted text here would make the checkpoint a
    second copy of the corpus.
    """

    cursor: int = 0
    hashes: dict[str, str] = field(default_factory=dict)


def content_hash(text: str) -> str:
    """Digest of the normalised body.

    Normalising before hashing matters: a source that rewrites whitespace on
    every read would otherwise look changed on every run.
    """
    normalised = " ".join(text.split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def extract(record: SourceRecord) -> str:
    """Turn a source record into text, or fail loudly.

    This is where a pipeline meets the real world's file formats, so it is the
    stage most likely to raise. Callers must treat a raise as a dead letter
    rather than letting it end the run.
    """
    if record.payload is None:
        raise ExtractionError(f"unreadable payload for {record.doc_id}")
    return record.payload


def chunk_document(doc_id: str, text: str, size: int = 40) -> list[Chunk]:
    """Split text and give each piece a STABLE id.

    The id is derived from the document id and the chunk's position within that
    document. It never depends on run order or on how many other documents were
    processed, which is what makes a second write an update rather than a
    duplicate.
    """
    words = text.split()
    if not words:
        return []
    chunks: list[Chunk] = []
    for position, start in enumerate(range(0, len(words), size)):
        body = " ".join(words[start : start + size])
        chunks.append(
            Chunk(chunk_id=f"{doc_id}::{position}", doc_id=doc_id, text=body)
        )
    return chunks


def embed(chunks: list[Chunk]) -> list[Chunk]:
    """Stand-in for the expensive stage.

    Real embedding costs money per chunk, which is the whole reason the content
    hash exists: an unchanged document must never reach this function.
    """
    return chunks


def run_once(
    source: list[SourceRecord],
    index: Index,
    checkpoint: Checkpoint,
    dead_letters: list[DeadLetter],
    *,
    fail_after: int | None = None,
    on_commit: Callable[[int], None] | None = None,
) -> RunStats:
    """Process everything above the cursor, in order.

    `fail_after` simulates a crash after N documents have been committed, so a
    test can prove the run resumes rather than restarts.
    """
    stats = RunStats(cursor=checkpoint.cursor)
    pending = sorted(
        (r for r in source if r.seq > checkpoint.cursor), key=lambda r: r.seq
    )

    committed = 0
    for record in pending:
        stats.scanned += 1

        try:
            text = extract(record)
        except ExtractionError as exc:
            # Isolated: the record is captured with its error and the run
            # continues. The cursor still advances, because retrying this
            # record on every future run would stall the pipeline forever --
            # draining the dead-letter queue is separate work.
            dead_letters.append(DeadLetter(doc_id=record.doc_id, error=type(exc).__name__))
            stats.dead_lettered += 1
            checkpoint.cursor = record.seq
            stats.cursor = record.seq
            continue

        digest = content_hash(text)
        if checkpoint.hashes.get(record.doc_id) == digest:
            # Incremental: provably unchanged, so skip the expensive stage.
            checkpoint.cursor = record.seq
            stats.cursor = record.seq
            continue

        stats.changed += 1
        chunks = embed(chunk_document(record.doc_id, text))
        stats.embedded += len(chunks)

        # Idempotent: stable ids mean this replaces rather than appends.
        stats.indexed += index.upsert(chunks)
        index.delete_orphans(record.doc_id, {c.chunk_id for c in chunks})

        # Resumable: the cursor advances only after the batch is written. A
        # crash between the write and this line reprocesses the record, which
        # is harmless precisely because the write was idempotent.
        checkpoint.hashes[record.doc_id] = digest
        checkpoint.cursor = record.seq
        stats.cursor = record.seq

        committed += 1
        if on_commit is not None:
            on_commit(committed)
        if fail_after is not None and committed >= fail_after:
            raise RuntimeError("simulated crash after commit")

    return stats
