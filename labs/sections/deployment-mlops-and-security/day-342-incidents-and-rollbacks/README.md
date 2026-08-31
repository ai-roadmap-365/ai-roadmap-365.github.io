# Day 342 Lab: Incidents and Rollbacks

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Incidents and Rollbacks
- **Day number:** 342 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-342-incidents-and-rollbacks
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-342-incidents-and-rollbacks` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an AI Incident Management & Fast Rollback Engine in Python tracking error rates, automatically tripping circuit breakers, and reverting to stable baselines.

## Learning objectives
- Track candidate model request outcomes and error percentages.
- Evaluate automated circuit breaker trip thresholds.
- Revert active inference traffic to stable baselines in under 500ms.
- Record structured incident audit logs for post-mortem analysis.

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
- `starter/incidents_rollbacks.py`: Starter implementation skeleton
- `examples/incidents_rollbacks.py`: Verified reference implementation
- `tests/test_incidents_rollbacks.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/incidents_rollbacks.py
```

## What the commands do
- Evaluates circuit breaker trip conditions, tests baseline revert, and verifies incident logs.

## Expected output
```text
[CANDIDATE_V2] Processed: test
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Initial state with Candidate active and circuit closed
- Healthy traffic preserving Candidate active
- Error rate spike tripping circuit and reverting to Baseline
- Minimum request guard preventing premature circuit trips
- Incident audit log creation with error rate and timestamp

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure error rate is calculated only when total requests >= min requests.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a half-open recovery state.

## Navigation
Day number: 342 of 365
