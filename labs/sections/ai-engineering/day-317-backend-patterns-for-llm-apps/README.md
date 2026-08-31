# Day 317 Lab: Backend Patterns for LLM Apps

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Backend Patterns for LLM Apps
- **Day number:** 317 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-317-backend-patterns-for-llm-apps
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-317-backend-patterns-for-llm-apps` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Resilient LLM Backend Engine in Python supporting Idempotency Key deduplication and a 3-State Circuit Breaker with automated fallback routing.

## Learning objectives
- Implement idempotent request deduplication to prevent duplicate inference billing.
- Build a 3-state Circuit Breaker (CLOSED, OPEN, HALF-OPEN).
- Route traffic automatically to fallback replicas when upstream providers degrade.
- Verify self-healing recovery when probe requests succeed in HALF-OPEN state.

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
- `starter/backend_patterns.py`: Starter implementation skeleton
- `examples/backend_patterns.py`: Verified reference implementation
- `tests/test_backend_patterns.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/backend_patterns.py
```

## What the commands do
- Executes requests across idempotency checks and circuit breaker state transitions.

## Expected output
```text
Normal: {'status': 'SUCCESS', 'provider': 'primary_model', 'response': '[PRIMARY_CLAUDE] Processed: Hello', 'cached': False}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Normal primary model execution in CLOSED state
- Idempotent response replay on duplicate keys
- Circuit breaker tripping to OPEN after threshold failures
- Automatic fallback routing when circuit is OPEN
- Self-healing state recovery to CLOSED upon successful probe

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure reset timeout expires before expecting HALF-OPEN state transition.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add sliding window error rate calculation.

## Navigation
Day number: 317 of 365
