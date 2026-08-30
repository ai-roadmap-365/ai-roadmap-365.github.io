# Day 356 Lab: Tests and Evals for Your Capstone

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Tests and Evals for Your Capstone
- **Day number:** 356 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-356-tests-and-evals-for-your-capstone
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-356-tests-and-evals-for-your-capstone` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Capstone Automated Evaluation Platform in Python that calculates RAG Triad metrics (Faithfulness, Context Recall) and enforces regression quality gates.

## Learning objectives
- Formulate a golden evaluation benchmark dataset.
- Calculate Faithfulness using atomic claim verification.
- Score Context Recall against ground-truth points.
- Assert CI/CD quality gate compliance.

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
- `starter/evals.py`: Starter implementation skeleton
- `examples/evals.py`: Verified reference implementation
- `tests/test_evals.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/evals.py
```

## What the commands do
- Evaluates benchmark queries across Faithfulness and Context Recall metrics and outputs scorecard results.

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
- Perfect 1.0 Faithfulness on grounded claims
- Hallucination detection lowering Faithfulness score
- Context Recall scoring against ground-truth points
- Overall benchmark suite pass rate calculation
- Quality gate failure on low accuracy

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure claim strings contain alphanumeric tokens for matching.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement an Answer Relevancy scoring function.

## Navigation
Day number: 356 of 365
