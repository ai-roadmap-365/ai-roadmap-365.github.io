# Day 335 Lab: Batch Processing and Job Queues

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** CI/CD with GitHub Actions
- **Day number:** 335 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-335-ci-cd-with-github-actions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-335-ci-cd-with-github-actions` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Distributed Batch Inference Pipeline Simulator in Python implementing task queueing, idempotent checkpoints, retry loops, and Dead-Letter Queue (DLQ) quarantine.

## Learning objectives
- Enqueue and partition batch items into a task queue.
- Commit idempotent checkpoints upon task completion.
- Execute retry cycles on transient failures.
- Quarantine permanently failing tasks to a DLQ.

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
- `starter/batch_pipeline.py`: Starter implementation skeleton
- `examples/batch_pipeline.py`: Verified reference implementation
- `tests/test_batch_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/batch_pipeline.py
```

## What the commands do
- Executes batch task runs, handles simulated errors, and evaluates DLQ captures.

## Expected output
```text
{'batches_completed': 1, 'batches_quarantined_dlq': 0, 'active_checkpoints': 1}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Successful batch processing and checkpoint creation
- Idempotent skip on already-completed batches
- Retry increment logic on failures
- DLQ quarantine when retries exceed threshold
- Multi-batch pipeline draining

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure retries increment before re-enqueueing.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement exponential backoff between retries.

## Navigation
Day number: 335 of 365
