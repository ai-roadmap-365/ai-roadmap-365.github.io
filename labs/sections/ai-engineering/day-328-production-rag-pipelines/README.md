# Day 328 Lab: Production RAG Pipelines

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a Production Ingestion and Idempotent Indexing Pipeline Engine in Python supporting SHA-256 hashing, deduplication, cascade deletes, and dead-letter queues.

## Learning objectives
- Implement SHA-256 cryptographic content hashing.
- Execute idempotent deduplication skipping unchanged documents.
- Implement atomic cascade deletions removing child vectors.
- Isolate corrupt payloads into a Dead-Letter Queue (DLQ).

## Prerequisites
- Python 3.10+ installed
- pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest

## Free and open-source options
- Python Standard Library, Pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/ingestion_pipeline.py`: Starter implementation skeleton
- `examples/ingestion_pipeline.py`: Verified reference implementation
- `tests/test_ingestion_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/ingestion_pipeline.py
```

## What the commands do
- Executes document ingestion, duplicate checking, cascade deletion, and DLQ handling.

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Ingestion and chunk creation
- Idempotent skip when hash matches
- Cascade deletion of child chunks on document update
- Cascade deletion on document removal
- Diverting empty/invalid payloads to DLQ

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all chunk IDs are tracked in metadata store for cascade deletes.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement soft-delete with timestamp archiving.

## Navigation
Day number: 328 of 365
