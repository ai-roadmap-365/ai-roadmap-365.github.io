# Day 341 Lab: Rollouts, A/B Tests, and Feature Flags

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Rollouts, A/B Tests, and Feature Flags
- **Day number:** 341 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-341-rollouts-ab-tests-and-feature-flags
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-341-rollouts-ab-tests-and-feature-flags` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an AI Feature Flag & Shadow Routing Engine in Python implementing deterministic user hashing, percentage canary splits, and asynchronous shadow traffic mirroring.

## Learning objectives
- Implement deterministic user hashing across persistent buckets.
- Route user traffic based on configurable percentage thresholds.
- Execute shadow traffic mirroring without affecting live response latency.
- Log shadow execution metrics for offline model comparison.

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
- `starter/feature_flags.py`: Starter implementation skeleton
- `examples/feature_flags.py`: Verified reference implementation
- `tests/test_feature_flags.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/feature_flags.py
```

## What the commands do
- Evaluates deterministic user hashing, tests canary thresholds, and verifies shadow logging.

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
- Deterministic hashing producing identical buckets for same user
- Correct routing to Candidate when bucket < canary percentage
- Correct routing to Baseline when bucket >= canary percentage
- Shadow execution and audit logging when enabled
- Zero shadow execution when disabled

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Use MD5 or SHA256 for deterministic hashing across runs.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a Thompson Sampling Multi-Armed Bandit router.

## Navigation
Day number: 341 of 365
