# Week 47 Project: A Production Assistant

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose

Assemble the week into one system: an ingestion pipeline, a fresh index, retrieval, a cost budget and a privacy review, working together.

The parts are already familiar — you built each one across Days 323 to 328. What this project adds is the **interactions**, and those are only visible once the stages share a pipeline. Three of them drive the design:

- **Redaction has to happen before indexing.** Redact afterwards and the identifiers are already inside the vectors, where removing them means re-embedding the corpus.
- **Retrieval is charged to the request budget.** That makes a recall setting a cost setting, which is not obvious while retrieval and generation have separate owners.
- **An erasure has to reach the cache.** The index is remembered; the response cache is the store that keeps answering from deleted content.

## Requirements

Build an assistant that:

1. **Ingests idempotently** — a second run over unchanged sources does nothing, and a crash resumes from the checkpoint cursor.
2. **Gates on quality** — a document with no body, or one that is mostly punctuation, is dead-lettered without stopping the run.
3. **Redacts at the boundary** — identifiers are pseudonymised before hashing, chunking or embedding.
4. **Keeps the index fresh** — an edited document replaces its chunks rather than duplicating them, and a shrinking document leaves no orphans.
5. **Retrieves and answers within a budget** — retrieval and generation share one ledger, and the cap is checked before spending.
6. **Erases verifiably** — a deletion reaches the index, the content hashes and the cache, and the result is confirmed by reading back.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation. No API key, no account, no network — the model and the corpus are simulated so the whole system is testable.

## File structure

```text
starter/assistant.py         your work: ingest, answer, erase
examples/assistant.py        reference implementation
examples/assistant_demo.py   the whole pipeline end to end
tests/test_assistant.py      grouped by day, plus an INTERACTIONS group
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
```

## Running the Project

```bash
python3 examples/assistant_demo.py
```

## Running Tests

```bash
bash tests/run_tests.sh
```

## Expected output

```text
--- ingest ---
scanned=5 indexed=6 unchanged=0 dead=2 redactions=4
dead letters: ['broken', 'garbled']
--- re-ingest, nothing changed ---
scanned=0 indexed=0 unchanged=0 dead=0 redactions=0
--- edited document ---
scanned=1 indexed=2 unchanged=0 dead=0 redactions=0
--- answers ---
[small] What is the refund window? -- sources: refunds::0, sla::0, sla::1
[small] What is the refund window? -- sources: refunds::0, sla::0, sla::1
[large] Compare the standard and premium t -- sources: tiers::0, tiers::1, refunds::0
--- cost ---
total=$0.00230  by stage: cache=$0.00000, large=$0.00210, retrieval=$0.00002, small=$0.00017
--- budget enforcement ---
refused: would cost $0.00018, $0.00000 left
--- erasure ---
chunks before: 6
verified: {'index': True, 'hashes': True, 'cache': True}
chunks after: 4
```

`expected-output/FIELDS.md` explains every field; `expected-output/measured-values.txt` records the machine and versions.

## Validation

1. `bash tests/run_tests.sh` reports `20 passed`.
2. The second ingest run must report `scanned=0`. If it scans, the cursor is not advancing.
3. No chunk may contain `ada@example.com`. If one does, redaction is running after indexing rather than before.
4. `verified` must be `True` for all three stores. If the cache entry survives, the assistant can still answer from a document that was deleted.
5. The `by stage` line must include `retrieval`. If it does not, retrieval is escaping the budget.

## Testing Specifications

Twenty tests. Six groups map to the six days, so a failure names which idea broke:

- **day 323 ingestion** — idempotent, cursor advances, unchanged documents are skipped.
- **day 324 processing** — unreadable and garbled documents are dead-lettered without stopping the run.
- **day 325 freshness** — an edit replaces rather than duplicates; a shrinking document leaves no orphans.
- **day 326 retrieval** — the relevant document ranks first, embedding is deterministic, and a wider embedding reduces collisions.
- **day 327 cost** — a repeat is free, reasoning routes large, the cap is checked before spending, and retrieval is charged.
- **day 328 privacy** — identifiers are redacted before indexing, and redactions are counted.

A seventh group, **INTERACTIONS**, covers what no single day's tests can reach: that an erasure reaches all three stores, that an erased document can be re-ingested cleanly (the content hash must be cleared too, or the re-ingest sees it as unchanged), and that retrieval and generation share one budget.

## Extension exercises

1. **Per-tenant isolation.** Partition the index and the cache by tenant, and prove one tenant's erasure cannot affect another's data or budget.
2. **Recall against cost.** Add an approximate index with a tunable probe count, and plot recall against total request cost. Find the setting where the cost saving stops being worth the recall.
3. **Freshness objective.** State a staleness target, simulate a week of intermittent ingestion failures, and report the error budget honestly — including if the objective was never violated, which means it was set too loosely.

## Navigation

- Week 47 — Production Retrieval and Pipelines (Days 323 to 329)
- Previous: Week 46 project
- Next: Week 48 project
