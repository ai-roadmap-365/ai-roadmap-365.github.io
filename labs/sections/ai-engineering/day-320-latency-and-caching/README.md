# Day 320 Lab: Latency and Caching

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Latency and Caching
- **Day number:** 320 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-320-latency-and-caching
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-320-latency-and-caching` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Exact and Semantic Multi-Tier LLM Cache Engine in Python supporting SHA-256 hashing, vector cosine similarity evaluation, and TTL eviction.

## Learning objectives
- Implement sub-millisecond Tier 1 exact hash caching.
- Build Tier 2 semantic vector caching comparing embedding cosine similarity.
- Enforce strict similarity thresholds to eliminate false positive cache hits.
- Manage TTL-based cache expiration and eviction.

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
- `starter/caching_engine.py`: Starter implementation skeleton
- `examples/caching_engine.py`: Verified reference implementation
- `tests/test_caching_engine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/caching_engine.py
```

## What the commands do
- Executes exact hash lookups, semantic vector comparisons, and TTL evictions.

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
- Tier 1 exact hash hit on identical query
- Tier 2 semantic hit on high-similarity query
- Cache miss on novel query below similarity threshold
- TTL expiration evicting stale cache records
- Multi-query put and get lifecycle

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure similarity threshold is set to >= 0.90 to prevent false positives.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add prefix cache key generation for system prompts.

## Navigation
Day number: 320 of 365
