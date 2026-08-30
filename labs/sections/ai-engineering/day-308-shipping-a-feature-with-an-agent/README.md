# Day 308 Lab: Shipping a Feature with an Agent

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Shipping a Feature with an Agent
- **Day number:** 308 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-308-shipping-a-feature-with-an-agent
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-308-shipping-a-feature-with-an-agent` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an End-to-End Feature Orchestrator in Python that executes automated verification quality gates and compiles comprehensive Walkthrough artifacts for peer review.

## Learning objectives
- Execute verification commands and evaluate exit codes.
- Synthesize structured Walkthrough markdown artifacts.
- Format modified file lists and test execution evidence.
- Manage end-to-end feature delivery telemetry.

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
- `starter/feature_orchestrator.py`: Starter implementation skeleton
- `examples/feature_orchestrator.py`: Verified reference implementation
- `tests/test_feature_orchestrator.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/feature_orchestrator.py
```

## What the commands do
- Executes test command, captures output, and compiles Walkthrough markdown summary.

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
- Passing and failing quality gate execution
- Walkthrough formatting with feature name, modified files, and test output
- Evidence attachment and review note generation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify test command paths and string formatting.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add code coverage percentage extraction.

## Navigation
Day number: 308 of 365
