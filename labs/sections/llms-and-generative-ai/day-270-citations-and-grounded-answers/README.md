# Lab: Day 270 -- Citations and Grounded Answers

## Lesson
Day number: 270 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Sentence-Level Citation Grounding and Claim Attribution.

## Purpose
Build and test a modular Python RAG implementation. Implement document chunking, sparse BM25 indexing, dense vector search, Reciprocal Rank Fusion, grounded prompt synthesis, and inline citation attribution.

## Learning objectives
- Implement sliding-window document chunking preserving document metadata.
- Build an in-memory Okapi BM25 inverted index with token frequency and IDF weighting.
- Implement Reciprocal Rank Fusion (RRF) for hybrid retrieval candidate scoring.
- Synthesize prompt context blocks enforcing verifiable inline bracket citations.
- Validate RAG grounding and retrieval precision with automated unit tests.

## Prerequisites
- Day 269 (RAG over PDFs and Messy Documents).
- Python 3.11+ with Pytest.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
Pure Python standard libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/grounded_citations_lib.py`: Student scaffold file.
- `examples/grounded_citations_lib.py`: Complete reference implementation.
- `tests/test_grounded_citations_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/grounded_citations_lib.py
```

## What the commands do
- Chunks sample documents into token overlapping windows.
- Indexes chunks in BM25 inverted index.
- Executes keyword query retrieval.
- Formats grounded system prompt with numbered citation tags.
- Runs Pytest unit validation suite.

## Expected output
```
Ingested 1 chunks.
Top Result Score: 1.2500
Synthesized Prompt Length: 390 characters.
```

## Validation steps
1. Verify document chunking preserves metadata and title strings.
2. Confirm BM25 search scores target documents highest for matching keywords.
3. Validate Reciprocal Rank Fusion correctly prioritizes documents appearing in multiple candidate lists.
4. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **Zero scores on BM25:** Verify queries are tokenized using regex word boundaries (`re.findall(r'\w+', query.lower())`).

## Security notes
All data is processed in-memory within local Python runtime.

## Extension exercises
1. Implement in-memory cosine vector similarity search.
2. Add support for PDF extraction using pdfplumber.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Citations and Grounded Answers
- **Day number:** 270 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-270-citations-and-grounded-answers
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-270-citations-and-grounded-answers` when the site is running.
<!-- generated-links:end -->
