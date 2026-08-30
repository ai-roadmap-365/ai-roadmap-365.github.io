# Day 279 Lab: PagedAttention Block Allocator & Scheduler

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Serving Open Models
- **Day number:** 279 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-279-serving-open-models
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-279-serving-open-models` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a simulated PagedAttention virtual block memory allocator and continuous iteration-level batching scheduler in Python to model production LLM serving dynamics.

## Learning objectives
- Implement a physical block memory allocator with free-list tracking.
- Manage logical-to-physical block tables for dynamic KV cache expansion.
- Execute iteration-level continuous batch scheduling.
- Quantify memory fragmentation reduction compared to static batching.

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
- Python Standard Library

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/serving_scheduler.py`: Starter implementation skeleton
- `examples/serving_scheduler.py`: Verified reference implementation
- `tests/test_serving_scheduler.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/serving_scheduler.py
```

## What the commands do
- Runs an iteration-level continuous batching simulation over multi-sequence arrivals and measures memory efficiency.

## Expected output
```text
[PAGED ATTENTION] Active Requests: 4 | Blocks Used: 8/64 | Tokens: 32/step
[METRICS] Paged Waste: 4.2% | Static Waste: 72.8%
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Physical block allocation and deallocation
- Continuous batching request admission and early eviction
- Dynamic block table expansion as token length grows
- OutOfMemory error triggers on pool exhaustion

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify that block allocation calculates ceil(tokens / block_size).

## Security notes
Runs completely offline on local CPU using standard Python lists and sets.

## Extension exercises
Implement shared prefix caching with block reference counters.

## Navigation
Day number: 279 of 365
