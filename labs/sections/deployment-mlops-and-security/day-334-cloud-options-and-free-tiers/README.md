# Day 334 Lab: Caching and Speculative Decoding

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cloud Options and Free Tiers
- **Day number:** 334 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-334-cloud-options-and-free-tiers
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-334-cloud-options-and-free-tiers` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Speculative Decoding and Prefix Cache Simulator in Python verifying draft tokens, executing rejection replacement, and calculating speedup factors.

## Learning objectives
- Match prompt prefixes against an in-memory prefix cache.
- Execute speculative verification over candidate draft tokens.
- Apply rejection sampling upon token mismatches.
- Calculate speculative speedup factors and acceptance counts.

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
- `starter/speculative_decoding.py`: Starter implementation skeleton
- `examples/speculative_decoding.py`: Verified reference implementation
- `tests/test_speculative_decoding.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/speculative_decoding.py
```

## What the commands do
- Executes prefix lookup, speculative step verification, and speedup evaluation.

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
- Prefix cache matching and miss handling
- 100% draft token acceptance with bonus token emission
- Partial acceptance with replacement token on mismatch
- Immediate rejection on first token mismatch
- Speculative speedup factor calculation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure speculation terminates immediately after the first mismatch.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement Radix tree branching data structure.

## Navigation
Day number: 334 of 365
