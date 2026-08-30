# Day 351 Lab: Choosing and Scoping Your Capstone

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a Capstone Project Scoping & Feasibility Scorer in Python that audits project charters across the 6 mandatory engineering pillars and quantifies SLA feasibility.

## Learning objectives
- Define a structured project charter schema.
- Validate the 6 mandatory engineering pillars.
- Calculate SLA feasibility scores and risk ratings.
- Generate an approved Project Charter and Feasibility Report.

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
- `starter/scoping.py`: Starter implementation skeleton
- `examples/scoping.py`: Verified reference implementation
- `tests/test_scoping.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/scoping.py
```

## What the commands do
- Evaluates sample project charters and computes quantitative feasibility metrics.

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
- Mandatory engineering pillar verification
- SLA latency and accuracy auditing
- Feasibility score computation
- Incomplete charter rejection
- Production charter JSON export

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all 6 pillar keys are present in the charter dictionary.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement an automated Markdown Project Charter exporter.

## Navigation
Day number: 351 of 365
