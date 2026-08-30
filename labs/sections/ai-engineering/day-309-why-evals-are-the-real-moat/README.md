# Day 309 Lab: Why Evals Are the Real Moat

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Why Evals Are the Real Moat
- **Day number:** 309 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-309-why-evals-are-the-real-moat
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-309-why-evals-are-the-real-moat` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated AI Evaluation Metric Engine in Python that calculates normalized Exact Match, field-level JSON schema F1 scores, and token-level overlap F1 metrics.

## Learning objectives
- Calculate normalized exact match binary scores.
- Parse JSON predictions and compute precision, recall, and F1 across dictionary keys.
- Compute token-level overlap F1 metrics for free-form text.
- Guard against malformed JSON and division-by-zero edge cases.

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
- `starter/eval_metrics.py`: Starter implementation skeleton
- `examples/eval_metrics.py`: Verified reference implementation
- `tests/test_eval_metrics.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/eval_metrics.py
```

## What the commands do
- Evaluates exact match, JSON field F1, and token overlap metrics across test cases.

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
- Exact match normalization (case, whitespace)
- JSON field-level precision, recall, and F1 calculation
- Malformed JSON error handling (returns 0.0)
- Token overlap F1 calculation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify inputs are valid strings and dictionaries.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement weighted Levenshtein distance metrics.

## Navigation
Day number: 309 of 365
