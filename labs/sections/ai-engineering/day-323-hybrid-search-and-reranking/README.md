# Day 323 Lab: Hybrid Search and Reranking

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a Hybrid Search and Reciprocal Rank Fusion Engine in Python combining BM25 lexical search, dense similarity scoring, and RRF rank fusion.

## Learning objectives
- Calculate BM25 term frequency and IDF scores.
- Compute dense similarity scores across document sets.
- Fuse disparate ranking lists using Reciprocal Rank Fusion (RRF).
- Evaluate hybrid recall improvements over single-modality search.

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
- `starter/hybrid_search.py`: Starter implementation skeleton
- `examples/hybrid_search.py`: Verified reference implementation
- `tests/test_hybrid_search.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/hybrid_search.py
```

## What the commands do
- Indexes sample documents, computes BM25 and dense scores, and executes RRF fusion.

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
- Accurate BM25 scoring for exact keyword matches
- Accurate dense similarity computation
- Reciprocal Rank Fusion formula calculation with k=60
- Top-k candidate ordering combining sparse and dense hits
- Empty query and edge case handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify RRF ranks are 1-indexed (`rank = 1, 2, ...`).

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic modality weighting for RRF.

## Navigation
Day number: 323 of 365
