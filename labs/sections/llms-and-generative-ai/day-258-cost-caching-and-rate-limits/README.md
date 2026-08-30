# Lab: Day 258 -- Cost, Caching, and Rate Limits

## Lesson
Day number: 258 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Cost Optimization, Prompt Caching, and Rate Limits.

## Purpose
Build and test a Rate-Limited Cost Optimization Ledger in Python. Calculate multi-tier prompt token costs with cache discounts, implement a Token Bucket rate limiter, and compute full jitter backoff retry intervals.

## Learning objectives
- Calculate exact token costs across standard, cached, and completion tiers.
- Implement a Token Bucket traffic shaping rate limiter.
- Compute exponential backoff with full jitter for HTTP 429 resilience.
- Maintain a cumulative multi-model token expenditure ledger.

## Prerequisites
- Day 257 (Working with Images and Documents).
- Python 3.11+ with Pytest.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 1 GB RAM.
- 100 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
Python and standard time/random modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/cost_caching_and_rate_limits_lib.py`: Student scaffold file.
- `examples/cost_caching_and_rate_limits_lib.py`: Complete reference implementation.
- `tests/test_cost_caching_and_rate_limits_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/cost_caching_and_rate_limits_lib.py
```

## What the commands do
- Records cached prompt usage.
- Consumes tokens from TokenBucket.
- Runs unit test assertions.

## Expected output
```
Cost Demo Executed. Cost: $0.0075, Token Consumed: True
```

## Validation steps
1. Verify cached token cost reflects 90% discount rate.
2. Confirm TokenBucket rejects requests exceeding capacity.
3. Validate exponential jitter stays within mathematical bounds.
4. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **Cost scaling error:** Ensure pricing rates per million tokens are divided by 1,000,000.

## Security notes
All cost accounting runs locally in memory.

## Extension exercises
1. Implement a distributed Redis Token Bucket using atomic scripts.
2. Build an automated prompt cache prefix linter.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cost, Caching, and Rate Limits
- **Day number:** 258 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-258-cost-caching-and-rate-limits
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-258-cost-caching-and-rate-limits` when the site is running.
<!-- generated-links:end -->
