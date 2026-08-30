# Day 322 Lab: A Full-Stack AI Application

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Full-Stack AI Application
- **Day number:** 322 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-322-a-full-stack-ai-application
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-322-a-full-stack-ai-application` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Complete Full-Stack AI Application Engine in Python integrating authentication, rate limiting, exact caching, two-phase credit holds, and multi-provider failover routing.

## Learning objectives
- Implement multi-tenant authentication and quota verification.
- Intercept cached queries to deliver instant zero-cost responses.
- Enforce credit pre-authorization holds preventing negative balance overdrafts.
- Execute multi-provider fallback routing when upstream services degrade.
- Reconcile exact token usage charges upon stream completion.

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
- `starter/full_stack_app.py`: Starter implementation skeleton
- `examples/full_stack_app.py`: Verified reference implementation
- `tests/test_full_stack_app.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/full_stack_app.py
```

## What the commands do
- Simulates the entire end-to-end full-stack request execution lifecycle.

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
- Normal full-stack chat execution with credit deduction
- Zero-cost exact cache response delivery
- Rejection on insufficient credit balance
- Seamless secondary provider failover on primary failure
- Graceful error handling when all upstream providers fail

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure hold amount is released on total upstream failure.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic multi-tier semantic caching in the pipeline.

## Navigation
Day number: 322 of 365
