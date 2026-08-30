# Lab: Day 266 -- End-to-End RAG System

## Lesson
Day number: 266 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: End-to-End RAG System Architecture, Ingestion, Generation, and Citations.

## Purpose
Build and test a complete Modular End-to-End RAG System in Python. Implement document ingestion, candidate retrieval, confidence threshold fallback gating, citation-enforced prompt synthesis, and grounded answer generation.

## Learning objectives
- Synthesize ingestion, retrieval, re-ranking, and prompt synthesis into a single unified pipeline.
- Implement confidence threshold gating to prevent hallucinations.
- Enforce source citations and claim verification.
- Structure modular, production-ready Python RAG architectures.

## Prerequisites
- Day 265 (Evaluating RAG with RAGAS and TruLens).
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
- `starter/e2e_rag_lib.py`: Student scaffold file.
- `examples/e2e_rag_lib.py`: Complete reference implementation.
- `tests/test_e2e_rag_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/e2e_rag_lib.py
```

## What the commands do
- Ingests documentation corpus.
- Executes query retrieval and prompt synthesis.
- Generates answer with verified citations.
- Triggers fallback refusal for unknown queries.
- Runs unit test assertions.

## Expected output
```
Known Query Answer: According to documentation, API gateway tokens expire after 3600 seconds. [1].
Unknown Query Answer: I do not have sufficient documentation to answer this question accurately.
```

## Validation steps
1. Verify high-confidence queries return grounded answers with `[1]` citation tags.
2. Confirm unknown queries trigger graceful refusal messages.
3. Validate prompt synthesis correctly formats source metadata blocks.
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
- **Refusal on valid queries:** Lower the `confidence_threshold` parameter (e.g. from 0.50 to 0.20).

## Security notes
All data is processed in-memory within local Python runtime.

## Extension exercises
1. Implement OpenTelemetry distributed tracing spans.
2. Add multi-turn conversation history buffer.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Semantic Search over Your Own Notes
- **Day number:** 266 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-266-semantic-search-over-your-own-notes
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-266-semantic-search-over-your-own-notes` when the site is running.
<!-- generated-links:end -->
