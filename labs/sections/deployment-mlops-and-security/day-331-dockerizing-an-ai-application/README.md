# Day 331 Lab: vLLM, TGI, and Inference Servers

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dockerizing an AI Application
- **Day number:** 331 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-331-dockerizing-an-ai-application
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-331-dockerizing-an-ai-application` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an LLM Inference Server Simulator in Python supporting Paged KV Cache block allocation and continuous iteration-level request scheduling.

## Learning objectives
- Implement PagedAttention non-contiguous block memory allocation.
- Build continuous iteration-level scheduling allowing requests to enter/exit dynamically.
- Eliminate static batching idle bubbles.
- Manage memory block freeing on request completion.

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
- `starter/inference_server.py`: Starter implementation skeleton
- `examples/inference_server.py`: Verified reference implementation
- `tests/test_inference_server.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/inference_server.py
```

## What the commands do
- Simulates paged memory allocation, continuous batch stepping, and dynamic request departure.

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
- Paged block allocation based on token count
- Continuous batch admission and token generation
- Early completion of short requests freeing blocks
- Throttling waiting queue when VRAM blocks are exhausted
- Complete cache reclamation on batch drain

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure block ceiling division formula allocates sufficient blocks.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement copy-on-write prefix sharing.

## Navigation
Day number: 331 of 365
