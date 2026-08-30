# Day 330 Lab: Containerizing AI Applications

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Docker Fundamentals
- **Day number:** 330 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-330-docker-fundamentals
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-330-docker-fundamentals` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Container Builder and GPU Environment Validator in Python simulating multi-stage builds, non-root security context verification, and Kubernetes readiness probes.

## Learning objectives
- Model multi-stage build artifact separation.
- Configure GPU device detection and compute VRAM allocation.
- Enforce non-root security context checks.
- Implement Kubernetes HTTP readiness probes.

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
- `starter/container_validator.py`: Starter implementation skeleton
- `examples/container_validator.py`: Verified reference implementation
- `tests/test_container_validator.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/container_validator.py
```

## What the commands do
- Simulates container build stages, GPU configuration, and readiness verification.

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
- Multi-stage build purging compiler toolchains
- GPU device registration and total VRAM calculation
- Readiness probe passing with HTTP 200 on valid setup
- Readiness probe failing with HTTP 503 on missing GPUs
- Security failure when running as root

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure runner stage marks `is_running_as_non_root = True`.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic layer size budgeting.

## Navigation
Day number: 330 of 365
