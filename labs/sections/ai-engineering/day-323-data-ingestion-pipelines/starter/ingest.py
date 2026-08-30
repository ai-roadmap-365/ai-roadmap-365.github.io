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
    # TODO(1): return a stable digest of the NORMALISED body.
    # Normalise whitespace first, or a source that reformats on every read will
    # look changed on every run. hashlib.sha256 over utf-8 bytes is fine.
    raise NotImplementedError("implement content_hash")

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
    # TODO(2): split `text` into chunks of `size` words and give each a STABLE
    # id of the form f"{doc_id}::{position}". The id must depend only on the
    # document and the position within it -- never on run order or a global
    # counter. Return [] for empty text.
    raise NotImplementedError("implement chunk_document")

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

    TODO(3): implement the run loop so that all four properties hold.

      idempotent  stable chunk ids mean a second write REPLACES; after writing,
                  call index.delete_orphans(doc_id, keep) so a document that
                  shrinks leaves nothing behind.

      incremental compare content_hash(text) against checkpoint.hashes[doc_id].
                  If they match, the body is provably unchanged -- advance the
                  cursor and skip the expensive embed step entirely.

      resumable   advance checkpoint.cursor ONLY AFTER the batch is written.
                  A crash between write and commit then reprocesses a record,
                  which is harmless because the write was idempotent. Commit
                  first and the same crash loses the record silently.

      isolated    wrap extract() in try/except ExtractionError. On failure,
                  append a DeadLetter(doc_id, error=type(exc).__name__), count
                  it, advance the cursor, and CONTINUE the loop.

    `fail_after` simulates a crash: after that many documents have been
    committed, raise RuntimeError("simulated crash after commit"). Call
    on_commit(n) with the running commit count when it is not None. Both exist
    so the tests can prove resumability.

    Process records with seq > checkpoint.cursor, in ascending seq order, and
    return a RunStats describing what happened.
    """
    raise NotImplementedError("implement run_once")
