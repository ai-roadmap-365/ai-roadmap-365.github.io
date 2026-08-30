# Day 338 Lab: GPU Serving and Inference Infrastructure

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** GPU Serving and Inference Infrastructure
- **Day number:** 338 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-338-gpu-serving-and-inference-infrastructure
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-338-gpu-serving-and-inference-infrastructure` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Multi-Model GPU Inference Infrastructure Simulator in Python modeling VRAM pool allocation, dynamic server-side batching, and queue delay timeouts.

## Learning objectives
- Manage GPU VRAM pool allocations and prevent OOMs.
- Enqueue incoming requests with arrival timestamps.
- Aggregate dynamic batches based on capacity and delay thresholds.
- Measure average queue latency and batch packing efficiency.

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
- `starter/gpu_infrastructure.py`: Starter implementation skeleton
- `examples/gpu_infrastructure.py`: Verified reference implementation
- `tests/test_gpu_infrastructure.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/gpu_infrastructure.py
```

## What the commands do
- Executes dynamic batch aggregation, evaluates queue timeouts, and tests VRAM limits.

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
- VRAM allocation and OOM protection
- Immediate batch dispatch when max_batch_size is met
- Timed batch flush when max_queue_delay_ms expires
- Holding state while requests are below batch size and timeout
- Empty queue handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure arrival timestamps are recorded in seconds.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a priority queue dispatch policy.

## Navigation
Day number: 338 of 365
