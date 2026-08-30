# Lab — Day 323: Data Ingestion Pipelines

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Ingestion Pipelines
- **Day number:** 323 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-323-data-ingestion-pipelines
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-323-data-ingestion-pipelines` when the site is running.
<!-- generated-links:end -->

## Purpose

Build an incremental ingestion pipeline that is safe to schedule and forget. You implement content-hash change detection, stable chunk identifiers, a durable cursor committed in the correct order, and a dead-letter queue — the four mechanisms that make a re-run harmless instead of destructive.

Everything runs offline against an in-memory source and index. The endpoints are simulated; the mechanisms are real, which is what makes their behaviour testable.

## Learning objectives

- Derive a chunk identifier that is reproducible across runs, so a second write upserts rather than duplicates.
- Prove a document is unchanged with a content hash rather than trusting modification metadata.
- Order the cursor commit after the batch write, so a crash reprocesses instead of losing records.
- Capture a failing record in a dead-letter queue and let the batch continue.
- Delete orphaned chunks when a document shrinks.

## Prerequisites

- Day 322, "A Full-Stack AI Application".
- Comfortable with Python dataclasses, dictionaries and exceptions.
- Familiar with `pytest` basics.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing in this lab is platform-specific.

## Hardware requirements

Any machine that runs Python 3.10 or newer. No GPU. The full suite finishes in well under a second and uses a few megabytes of memory.

## Required software

- Python 3.10 or newer (uses `X | None` type syntax).
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source. Python is PSF-licensed; `pytest` is MIT-licensed. There is no paid tier, no account and no hosted service anywhere in this lab.

## Installation

Build a virtual environment inside this lab directory so nothing touches your system Python:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/ingest.py          your work: content_hash, chunk_document, run_once
examples/ingest.py         reference implementation
examples/ingest_demo.py    three consecutive runs over a changing source
tests/test_ingest.py       one test per property
tests/run_tests.sh         suite entry point
expected-output/           real captured output, including the starter's failures
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/ingest_demo.py     # see the reference pipeline behave
bash tests/run_tests.sh             # run the suite
```

To work on the exercise, edit `starter/ingest.py`, then copy it over the reference to test your version:

```bash
cp starter/ingest.py examples/ingest.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/ingest_demo.py` runs the pipeline three times over a source where one document is edited between runs and one document is permanently malformed. It prints a summary line per run plus the final index state.

`bash tests/run_tests.sh` changes into the lab root and runs `python3 -m pytest tests -q`. The suite is grouped by property, so a failure names which of idempotent, incremental, resumable or isolated is not yet satisfied.

## Expected output

```text
run 1: scanned=5 changed=4 embedded=7 indexed=7 dead_lettered=1 cursor=5
run 2: scanned=0 changed=0 embedded=0 indexed=0 dead_lettered=0 cursor=5
run 3: scanned=1 changed=1 embedded=2 indexed=2 dead_lettered=0 cursor=6
index: 7 chunks across 4 documents
dead letters: 1 (doc-3: ExtractionError)
```

Run 2 scans nothing because the cursor has not moved. `expected-output/FIELDS.md` explains every field; `expected-output/starter-run.txt` records what an untouched starter produces.

## Validation steps

1. `bash tests/run_tests.sh` reports `11 passed`.
2. Run `python3 examples/ingest_demo.py` twice in succession. The index size must be identical both times — if it grows, your chunk ids are not stable.
3. Confirm run 2 reports `embedded=0`. If it does not, you are comparing timestamps rather than content hashes.

## Tests

Eleven tests across five groups:

- **idempotent** — a second run leaves the index identical; ids are stable across independent runs; reindexing from a clean checkpoint does not duplicate.
- **incremental** — unchanged documents are not re-embedded even when re-presented; edited documents are; the hash ignores whitespace reformatting.
- **resumable** — a simulated crash resumes from the last committed cursor; the cursor never advances past uncommitted work.
- **isolated** — the failing record is dead-lettered with its error and the other four documents still index.
- **reconciliation** — a shrinking document leaves no orphaned chunks.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible: the virtual environment rebuilds from `requirements/requirements.txt`.

## Troubleshooting

See `troubleshooting.md` for the failure modes this lab is designed to produce, including a doubling index, a run that re-embeds everything, and a crash that loses records.

## Security notes

See `security.md`. In short: no network, no credentials, no API key, and every write stays inside this directory.

## Extension exercises

1. **Deletion reconciliation.** Add `deleted_ids` to the source and remove those documents' chunks. Then add a full reconciliation pass comparing all source ids against all indexed ids.
2. **Bounded concurrency.** Extract with a small `ThreadPoolExecutor` while preserving the cursor guarantee — the cursor may only pass a record once it and everything before it has committed. Measure both versions and record the real numbers, including a null result.
3. **Retry policy.** Give dead letters a retry count and an abandon threshold, so a transient failure recovers but a permanently poisoned record does not retry forever.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-323-data-ingestion-pipelines/README.md)
- Previous: Day 322 — A Full-Stack AI Application
- Next: Day 324 — Document Processing at Scale
