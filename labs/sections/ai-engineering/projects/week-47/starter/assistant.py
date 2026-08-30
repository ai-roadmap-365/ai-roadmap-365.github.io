"""Week 47 project: a production assistant assembling the week's five parts.

Offline and standard-library only. Each stage is the idea from one day, wired
into a single pipeline so the interactions become visible:

  day 323  ingestion      idempotent, checkpointed, dead-lettered
  day 324  processing     format dispatch and a quality gate
  day 325  freshness      drift detection and verified erasure
  day 326  retrieval      an approximate index with a measured recall cost
  day 327  cost           a ledger, routing and a spend cap
  day 328  privacy        redaction at the boundary

The point of assembling them is the interactions, not the parts. Three show up
here and none is visible when the stages are studied alone:

  * redaction must happen BEFORE indexing, or identifiers are inside the
    vectors and removing them means re-embedding;
  * the retrieval cost lands inside the request budget, so a recall setting is
    also a cost setting;
  * an erasure has to reach the index AND the response cache, and the cache is
    the one that gets forgotten.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field

# ----------------------------------------------------------------- privacy

PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"(?<![\w+])\+?(?:\d[ -]?){9,13}\d\b"),
}


def redact(text: str, *, salt: str = "wk47") -> tuple[str, int]:
    """Replace identifiers with stable pseudonyms. Returns (text, count)."""
    found = 0
    out = text
    for label, pattern in PATTERNS.items():
        for match in sorted(pattern.finditer(out), key=lambda m: -m.start()):
            digest = hashlib.sha256((salt + match.group()).encode()).hexdigest()[:8]
            out = out[: match.start()] + f"[{label}:{digest}]" + out[match.end() :]
            found += 1
    return out, found


# -------------------------------------------------------------- processing


@dataclass(frozen=True)
class SourceDoc:
    doc_id: str
    seq: int
    body: str | None  # None simulates an extraction failure


def quality_ok(text: str, source_len: int) -> bool:
    """The day 324 gate, reduced to its two load-bearing signals."""
    if not text.strip():
        return False
    yield_ratio = min(1.0, len(text) / max(1, source_len))
    chars = [c for c in text if not c.isspace()]
    alpha = sum(1 for c in chars if c.isalpha()) / len(chars) if chars else 0.0
    return yield_ratio >= 0.10 and alpha >= 0.55


# ---------------------------------------------------------------- indexing


def embed(text: str, dim: int = 256) -> list[float]:
    """A deterministic bag-of-words embedding.

    Not a real model -- it is a hashing vectoriser -- but it is stable, needs
    no network, and preserves enough similarity structure to rank sensibly.

    The dimension matters more than it looks. At dim=24 unrelated words collide
    often enough that the wrong document wins: an early version of this project
    ranked the SLA page above the refunds page for "what is the refund window".
    Widening to 256 fixed it. Collision rate is a retrieval-quality parameter,
    not an implementation detail.
    """
    vec = [0.0] * dim
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        vec[int(hashlib.sha256(word.encode()).hexdigest(), 16) % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    vector: list[float]


# --------------------------------------------------------------------- cost

PRICES = {"small": (0.25, 1.25), "large": (3.00, 15.00)}


class BudgetExceeded(RuntimeError):
    """Raised when a request would push spend past its cap."""


@dataclass
class Ledger:
    entries: list[tuple[str, float]] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(c for _, c in self.entries)

    def by_stage(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for stage, cost in self.entries:
            out[stage] = out.get(stage, 0.0) + cost
        return out


# ----------------------------------------------------------------- pipeline


@dataclass
class IngestStats:
    scanned: int = 0
    indexed: int = 0
    skipped_unchanged: int = 0
    dead_lettered: int = 0
    redactions: int = 0

    def line(self) -> str:
        return (
            f"scanned={self.scanned} indexed={self.indexed} "
            f"unchanged={self.skipped_unchanged} dead={self.dead_lettered} "
            f"redactions={self.redactions}"
        )


@dataclass
class Assistant:
    budget: float = 0.05
    ledger: Ledger = field(default_factory=Ledger)
    chunks: dict[str, Chunk] = field(default_factory=dict)
    hashes: dict[str, str] = field(default_factory=dict)
    cursor: int = 0
    dead_letters: list[str] = field(default_factory=list)
    cache: dict[str, str] = field(default_factory=dict)

    # ---- ingest (days 323, 324, 328)

    def ingest(self, source: list[SourceDoc]) -> IngestStats:
        # TASK 1: process everything above the cursor, in order.
        #   - a body of None, or one failing quality_ok, is dead-lettered
        #     and the cursor still advances
        #   - REDACT BEFORE hashing and indexing. Redacting later puts
        #     identifiers inside the vectors, and removing them then means
        #     re-embedding the corpus
        #   - skip a document whose content hash is unchanged
        #   - chunk into 25-word pieces with stable ids f\"{doc_id}::{n}\",
        #     then delete any chunk of this document not in the new set
        raise NotImplementedError("implement Assistant.ingest")

    # ---- retrieve (day 326) and answer (day 327)

    def retrieve(self, question: str, k: int = 3) -> list[Chunk]:
        query = embed(question)
        scored = sorted(
            self.chunks.values(), key=lambda c: (-cosine(query, c.vector), c.chunk_id)
        )
        # Retrieval is not free: it is charged against the same budget the
        # generation is, which is what makes a recall setting a cost setting.
        self.ledger.entries.append(("retrieval", 0.000002 * len(self.chunks)))
        return scored[:k]

    def answer(self, question: str, *, k: int = 3) -> str:
        # TASK 2: answer one question within the budget.
        #   - a cached question is free; record it as a zero-cost entry
        #   - retrieve (which charges the SAME ledger, so a recall setting
        #     is also a cost setting), then route: \"large\" when the
        #     question contains \"compare\" or \"analyse\", else \"small\"
        #   - price it, and raise BudgetExceeded BEFORE recording if it
        #     would exceed the cap
        raise NotImplementedError("implement Assistant.answer")

    # ---- erase (days 325, 328)

    def erase(self, doc_id: str) -> dict[str, bool]:
        """Remove a document from every store, then verify.

        The cache is the store that gets forgotten, and it is the one that can
        keep answering from deleted content.
        """
        # TASK 3: remove the document from EVERY store, then verify.
        #   - its chunks, its content hash, and any cached answer that
        #     cites it
        #   - clearing the hash matters: leave it and a re-ingest sees the
        #     document as unchanged and never restores it
        #   - return a dict of store -> bool from a READ-BACK, not from
        #     the fact that the deletes ran
        raise NotImplementedError("implement Assistant.erase")
