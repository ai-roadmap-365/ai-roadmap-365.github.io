# Day 353 Lab: Data and Retrieval Layer

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data and Retrieval Layer
- **Day number:** 353 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-353-data-and-retrieval-layer
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-353-data-and-retrieval-layer` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a high-performance Capstone Hybrid Retrieval Engine in Python featuring SHA256 deduplication, sparse BM25 indexing, dense vector search, and Reciprocal Rank Fusion (RRF).

## Learning objectives
- Ingest documents with cryptographic content hashing.
- Build in-memory sparse BM25 inverted indexes.
- Execute dense cosine similarity lookups.
- Fuse rankings using Reciprocal Rank Fusion ($k=60$).

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
- `starter/retrieval.py`: Starter implementation skeleton
- `examples/retrieval.py`: Verified reference implementation
- `tests/test_retrieval.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/retrieval.py
```

## What the commands do
- Ingests test documents, constructs sparse and dense indices, and performs hybrid search queries.

## Expected output
```text
[{'id': 'doc1', 'text': 'Contract indemnity clause specifies liability limits under $1,000,000.', 'rrf_score': 0.03278688524590164, 'metadata': {}}, {'id': 'doc2', 'text': 'Server error code 0x80040154 occurs during database initialization.', 'rrf_score': 0.016129032258064516, 'metadata': {}}]
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Ingestion and SHA256 content deduplication
- Sparse BM25 exact keyword lookup accuracy
- Dense vector cosine similarity calculation
- Reciprocal Rank Fusion ranking fusion
- Top-K result formatting and metadata preservation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure vector lengths match across all indexed passages.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement a cross-encoder reranker stage on top of RRF results.

## Navigation
Day number: 353 of 365
