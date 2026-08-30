# Day 329 Lab: A Production Assistant

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build an End-to-End Production RAG Assistant in Python with hybrid search scoring, confidence refusal guardrails, grounded citations, and execution telemetry.

## Learning objectives
- Ingest and index knowledge base documents with metadata.
- Execute hybrid relevance scoring on user queries.
- Apply strict confidence refusal guardrails on out-of-domain queries.
- Generate grounded responses with verifiable citation payloads.

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
- `starter/production_assistant.py`: Starter implementation skeleton
- `examples/production_assistant.py`: Verified reference implementation
- `tests/test_production_assistant.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/production_assistant.py
```

## What the commands do
- Executes document indexing, query processing, refusal gating, and citation formatting.

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
- Document indexing into internal store
- High-confidence match returning grounded citation
- Low-confidence query triggering refusal policy
- Empty document store handling
- Execution telemetry capture (latency and candidate count)

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure refusal guardrails trigger when score is below threshold.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement conversation context history buffer.

## Navigation
Day number: 329 of 365
