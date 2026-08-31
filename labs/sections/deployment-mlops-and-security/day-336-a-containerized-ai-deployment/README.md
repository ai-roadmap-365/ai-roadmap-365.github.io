# Day 336 Lab: A Deployed AI System

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Containerized AI Deployment
- **Day number:** 336 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-336-a-containerized-ai-deployment
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-336-a-containerized-ai-deployment` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production AI Serving Gateway in Python featuring Least-Outstanding-Requests (LOR) load balancing, multi-replica health tracking, and circuit breaking.

## Learning objectives
- Register and monitor multi-replica GPU inference workers.
- Implement Least-Outstanding-Requests (LOR) load balancing.
- Manage circuit breaker state transitions (CLOSED, OPEN, HALF_OPEN).
- Enforce fallback responses during backend service degradation.

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
- `starter/ai_gateway.py`: Starter implementation skeleton
- `examples/ai_gateway.py`: Verified reference implementation
- `tests/test_ai_gateway.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/ai_gateway.py
```

## What the commands do
- Evaluates LOR routing, simulates replica failures, and verifies circuit breaker recovery.

## Expected output
```text
{'status': 'ROUTED', 'assigned_replica': 'w1', 'active_on_replica': 1, 'circuit_state': 'CLOSED'}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- LOR dynamic load balancing selecting least-active replicas
- Active request count increment and decrement
- Circuit breaker tripping to OPEN upon failure threshold
- Graceful fallback response emission when circuit is OPEN
- Self-healing transition to HALF_OPEN and CLOSED after probe success

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure `active_requests` is decremented in `complete_request`.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement weighted capacity LOR balancing.

## Navigation
Day number: 336 of 365
