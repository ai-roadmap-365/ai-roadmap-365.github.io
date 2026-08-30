# Lab: Day 265 -- Evaluating RAG with RAGAS and TruLens

## Lesson
Day number: 265 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Evaluating RAG with RAGAS, TruLens, and the RAG Triad.

## Purpose
Build and test a RAG Triad Evaluation Harness in Python. Implement automated Faithfulness claim verification, Context Relevance signal-to-noise scoring, and evaluate grounding.

## Learning objectives
- Calculate Faithfulness (groundedness) to detect hallucinations mathematically.
- Measure Context Relevance to identify noisy retrieved chunks.
- Build automated regression testing harnesses for RAG systems.
- Explain the role of LLM-as-a-Judge in modern CI/CD pipelines.

## Prerequisites
- Day 264 (Hybrid Search and Re-Ranking).
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
- `starter/rag_eval_lib.py`: Student scaffold file.
- `examples/rag_eval_lib.py`: Complete reference implementation.
- `tests/test_rag_eval_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/rag_eval_lib.py
```

## What the commands do
- Evaluates grounded vs. hallucinated answers.
- Calculates Context Relevance signal density.
- Runs unit test assertions.

## Expected output
```
Good Answer Faithfulness: 1.00
Hallucinated Answer Faithfulness: 0.00
```

## Validation steps
1. Verify grounded answers achieve 1.00 Faithfulness.
2. Confirm hallucinated claims reduce the score proportionally.
3. Validate Context Relevance reflects sentence relevance ratios.
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
- **Missing claim splits:** Ensure regex includes periods, question marks, and exclamation points.

## Security notes
All evaluation metrics compute locally in memory.

## Extension exercises
1. Implement Answer Relevance cosine scoring against synthetic questions.
2. Build a Pytest CI/CD regression gate.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Evaluating Retrieval Quality
- **Day number:** 265 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-265-evaluating-retrieval-quality
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-265-evaluating-retrieval-quality` when the site is running.
<!-- generated-links:end -->
