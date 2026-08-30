# Day 312 Lab: Regression Testing for Prompts and Models

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Regression Testing for Prompts and Models
- **Day number:** 312 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-312-regression-testing-for-prompts-and-models
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-312-regression-testing-for-prompts-and-models` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated AI Regression Test Runner in Python that compares candidate benchmark evaluation metrics against baseline benchmarks and enforces CI/CD deployment gates.

## Learning objectives
- Calculate metric deltas between baseline and candidate evaluation runs.
- Enforce configurable tolerance thresholds and schema validity invariants.
- Check for failures on critical golden invariant test cases.
- Generate structured pass/fail decisions for CI automation.

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
- `starter/regression_runner.py`: Starter implementation skeleton
- `examples/regression_runner.py`: Verified reference implementation
- `tests/test_regression_runner.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/regression_runner.py
```

## What the commands do
- Evaluates regression deltas and outputs CI gate status reports.

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
- Approved gate for improved candidate accuracy
- Approved gate for slight drop within tolerance threshold
- Rejected gate for severe accuracy regression exceeding tolerance
- Rejected gate for broken schema validity (even with high accuracy)
- Rejected gate when critical golden invariant cases fail

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure accuracy values are between 0.0 and 1.0.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Generate formatted markdown summary comments for GitHub Actions.

## Navigation
Day number: 312 of 365
