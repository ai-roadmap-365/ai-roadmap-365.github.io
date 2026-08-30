"""A conformance auditor for the three seams of a production assistant.

The week 47 project builds an assistant. This lab checks one -- which is a
different skill, and the one you need when reviewing someone else's system or
your own six months later.

Each check targets an interaction that no single stage's tests can reach:

  redaction_before_indexing   identifiers must not survive into any chunk
  shared_budget               retrieval must charge the same ledger as
                              generation, or one path escapes the cap
  erasure_is_complete         a deletion must reach the index, the content
                              hashes AND the response cache
  cursor_advances_on_failure  a dead-lettered document must not block the head
                              of the queue forever
  no_orphans_on_shrink        a shorter document must not leave stale chunks

The audit works against any object exposing the small protocol below, so it can
be pointed at a real implementation. Two are supplied: one that conforms, and
one that is deliberately broken in three specific ways -- because an auditor
that has never caught anything is not evidence of anything.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Protocol

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


@dataclass(frozen=True)
class Doc:
    doc_id: str
    seq: int
    body: str | None


class AssistantLike(Protocol):
    """The surface an assistant must expose to be auditable."""

    chunks: dict[str, str]  # chunk_id -> text
    hashes: dict[str, str]  # doc_id -> content hash
    cache: dict[str, str]  # question -> answer
    cursor: int
    ledger: list[tuple[str, float]]  # (stage, cost)

    def ingest(self, docs: list[Doc]) -> None: ...
    def answer(self, question: str) -> str: ...
    def erase(self, doc_id: str) -> None: ...


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""

    def line(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        return f"  {mark}  {self.name}" + (f" -- {self.detail}" if self.detail else "")


@dataclass
class AuditReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def conformant(self) -> bool:
        return all(c.passed for c in self.checks)

    def failures(self) -> list[str]:
        return [c.name for c in self.checks if not c.passed]

    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.passed)
        verdict = "CONFORMANT" if self.conformant else "NON-CONFORMANT"
        return f"{verdict} ({passed}/{len(self.checks)} checks passed)"


def sample_docs() -> list[Doc]:
    return [
        Doc("policy", 1, "The refund window is thirty days. Write to ada@example.com. " * 3),
        Doc("sla", 2, "Uptime guarantee is 99.99 percent per calendar month. " * 3),
        Doc("broken", 3, None),
    ]


# ------------------------------------------------------------------ checks


def check_redaction_before_indexing(make: type) -> Check:
    bot = make()
    bot.ingest(sample_docs())
    leaked = [cid for cid, text in bot.chunks.items() if EMAIL.search(text)]
    return Check(
        "redaction_before_indexing",
        not leaked,
        f"{len(leaked)} chunk(s) contain an address: {leaked[:2]}" if leaked else "",
    )


def check_shared_budget(make: type) -> Check:
    bot = make()
    bot.ingest(sample_docs())
    bot.answer("What is the refund window?")
    stages = {stage for stage, _ in bot.ledger}
    return Check(
        "shared_budget",
        "retrieval" in stages,
        "retrieval is not charged to the request ledger" if "retrieval" not in stages else "",
    )


def check_erasure_is_complete(make: type) -> Check:
    bot = make()
    bot.ingest(sample_docs())
    bot.answer("What is the refund window?")
    bot.erase("policy")

    remaining = []
    if any(cid.startswith("policy::") for cid in bot.chunks):
        remaining.append("index")
    if "policy" in bot.hashes:
        remaining.append("hashes")
    if any("policy" in answer for answer in bot.cache.values()):
        remaining.append("cache")
    return Check(
        "erasure_is_complete",
        not remaining,
        f"still present in: {', '.join(remaining)}" if remaining else "",
    )


def check_cursor_advances_on_failure(make: type) -> Check:
    bot = make()
    bot.ingest(sample_docs())
    before = bot.cursor
    bot.ingest(sample_docs())
    return Check(
        "cursor_advances_on_failure",
        before >= 3,
        f"cursor stuck at {before}; the dead-lettered document blocks the queue"
        if before < 3
        else "",
    )


def check_no_orphans_on_shrink(make: type) -> Check:
    bot = make()
    bot.ingest([Doc("long", 1, "alpha beta gamma delta " * 30)])
    many = sum(1 for cid in bot.chunks if cid.startswith("long::"))
    bot.ingest([Doc("long", 2, "alpha beta")])
    ids = {cid for cid in bot.chunks if cid.startswith("long::")}
    expected = {f"long::{i}" for i in range(len(ids))}
    return Check(
        "no_orphans_on_shrink",
        many > 1 and ids == expected,
        f"orphans left behind: {sorted(ids - expected)}" if ids != expected else "",
    )


CHECKS = (
    check_redaction_before_indexing,
    check_shared_budget,
    check_erasure_is_complete,
    check_cursor_advances_on_failure,
    check_no_orphans_on_shrink,
)


def audit(make: type) -> AuditReport:
    """Run every seam check against a factory producing a fresh assistant."""
    return AuditReport(checks=[check(make) for check in CHECKS])


# ------------------------------------------------- two assistants to audit


def _digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()


@dataclass
class ConformantAssistant:
    """Does all three seams correctly."""

    chunks: dict[str, str] = field(default_factory=dict)
    hashes: dict[str, str] = field(default_factory=dict)
    cache: dict[str, str] = field(default_factory=dict)
    cursor: int = 0
    ledger: list[tuple[str, float]] = field(default_factory=list)

    def ingest(self, docs: list[Doc]) -> None:
        for doc in sorted((d for d in docs if d.seq > self.cursor), key=lambda d: d.seq):
            if doc.body is None:
                self.cursor = doc.seq  # advance anyway, or the queue head blocks
                continue
            clean = EMAIL.sub("[email]", doc.body)  # redact BEFORE anything else
            digest = _digest(clean)
            if self.hashes.get(doc.doc_id) == digest:
                self.cursor = doc.seq
                continue
            words = clean.split()
            fresh = set()
            for position, start in enumerate(range(0, len(words), 20)):
                cid = f"{doc.doc_id}::{position}"
                self.chunks[cid] = " ".join(words[start : start + 20])
                fresh.add(cid)
            for stale in [
                c for c in list(self.chunks) if c.startswith(f"{doc.doc_id}::") and c not in fresh
            ]:
                del self.chunks[stale]
            self.hashes[doc.doc_id] = digest
            self.cursor = doc.seq

    def answer(self, question: str) -> str:
        if question in self.cache:
            self.ledger.append(("cache", 0.0))
            return self.cache[question]
        self.ledger.append(("retrieval", 0.000002))  # same ledger as generation
        self.ledger.append(("small", 0.00002))
        hit = next((c for c in self.chunks if c.startswith("policy")), "none")
        reply = f"answer citing {hit}"
        self.cache[question] = reply
        return reply

    def erase(self, doc_id: str) -> None:
        for cid in [c for c in list(self.chunks) if c.startswith(f"{doc_id}::")]:
            del self.chunks[cid]
        self.hashes.pop(doc_id, None)
        self.cache = {q: a for q, a in self.cache.items() if doc_id not in a}


@dataclass
class BrokenAssistant(ConformantAssistant):
    """Broken in three specific ways, so the audit has something to catch.

    1. redacts after chunking, so identifiers reach the index
    2. charges retrieval to a separate counter, so it escapes the cap
    3. erases the index but forgets the cache
    """

    side_ledger: list[tuple[str, float]] = field(default_factory=list)

    def ingest(self, docs: list[Doc]) -> None:
        for doc in sorted((d for d in docs if d.seq > self.cursor), key=lambda d: d.seq):
            if doc.body is None:
                self.cursor = doc.seq
                continue
            words = doc.body.split()  # NOT redacted
            fresh = set()
            for position, start in enumerate(range(0, len(words), 20)):
                cid = f"{doc.doc_id}::{position}"
                self.chunks[cid] = " ".join(words[start : start + 20])
                fresh.add(cid)
            for stale in [
                c for c in list(self.chunks) if c.startswith(f"{doc.doc_id}::") and c not in fresh
            ]:
                del self.chunks[stale]
            self.hashes[doc.doc_id] = _digest(doc.body)
            self.cursor = doc.seq

    def answer(self, question: str) -> str:
        if question in self.cache:
            self.ledger.append(("cache", 0.0))
            return self.cache[question]
        self.side_ledger.append(("retrieval", 0.000002))  # escapes the cap
        self.ledger.append(("small", 0.00002))
        hit = next((c for c in self.chunks if c.startswith("policy")), "none")
        reply = f"answer citing {hit}"
        self.cache[question] = reply
        return reply

    def erase(self, doc_id: str) -> None:
        for cid in [c for c in list(self.chunks) if c.startswith(f"{doc_id}::")]:
            del self.chunks[cid]
        self.hashes.pop(doc_id, None)
        # cache deliberately untouched
