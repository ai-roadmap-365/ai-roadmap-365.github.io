# Day 332 Lab: Autoscaling and GPU Orchestration

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Docker Compose for Multi-Service Apps
- **Day number:** 332 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-332-docker-compose-for-multi-service-apps
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-332-docker-compose-for-multi-service-apps` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a GPU Autoscaling Decision Engine in Python calculating target replica counts based on waiting request queue depth, immediate scale-up, and scale-down stabilization cooldowns.

## Learning objectives
- Calculate target replicas based on queue backlog metrics.
- Execute immediate scale-up actions on traffic surges.
- Enforce stabilization cooldown windows before scale-down.
- Clamp replica counts within minimum and maximum bounds.

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
- `starter/gpu_autoscaling.py`: Starter implementation skeleton
- `examples/gpu_autoscaling.py`: Verified reference implementation
- `tests/test_gpu_autoscaling.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/gpu_autoscaling.py
```

## What the commands do
- Evaluates queue spikes, immediate scale-up, and stabilization cooldowns.

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
- Immediate scale-up on queue surge
- Max replica clamp enforcement
- Cooldown hold on immediate queue drop
- Scale-down execution after cooldown expiration
- Zero change when queue load matches current capacity

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure `idle_since_timestamp` resets when scale-up occurs.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement step-down rate limits.

## Navigation
Day number: 332 of 365
