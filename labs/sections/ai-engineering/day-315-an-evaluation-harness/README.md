# Day 315 Lab: An Evaluation Harness

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** An Evaluation Harness
- **Day number:** 315 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-315-an-evaluation-harness
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-315-an-evaluation-harness` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Unified End-to-End AI Evaluation Harness in Python supporting multi-metric scoring (Exact Match and Overlap F1), composite score aggregation, golden invariant tracking, and CI regression gate reporting.

## Learning objectives
- Implement multi-metric scoring across test predictions.
- Calculate composite weighted scores.
- Track critical golden invariant test cases.
- Compute metric deltas against pinned baselines and enforce CI deployment gates.

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
- `starter/eval_harness.py`: Starter implementation skeleton
- `examples/eval_harness.py`: Verified reference implementation
- `tests/test_eval_harness.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/eval_harness.py
```

## What the commands do
- Executes batch evaluation scoring and outputs CI gate status reports.

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
- Single case exact match and overlap scoring
- Composite score aggregation across batch runs
- Approval on positive delta improvement
- Rejection on severe accuracy regressions exceeding tolerance
- Rejection when critical golden invariant cases fail

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure test cases specify `is_golden` appropriately.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add category stratification breakdown to the final report.

## Navigation
Day number: 315 of 365
