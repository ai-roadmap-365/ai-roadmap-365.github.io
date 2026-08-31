# Day 316 Lab: Architecture of an AI Product

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Architecture of an AI Product
- **Day number:** 316 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-316-architecture-of-an-ai-product
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-316-architecture-of-an-ai-product` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Full-Stack AI Product Architecture Dispatcher in Python that integrates authentication, token-bucket rate limiting, credit quota gating, semantic caching, and streaming token delivery.

## Learning objectives
- Implement multi-tenant authentication and quota verification.
- Enforce token-bucket rate limits per organization.
- Manage response caching for identical queries.
- Execute simulated token streaming with accurate credit deductions.

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
- `starter/product_dispatcher.py`: Starter implementation skeleton
- `examples/product_dispatcher.py`: Verified reference implementation
- `tests/test_product_dispatcher.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/product_dispatcher.py
```

## What the commands do
- Executes request dispatch across authentication, rate limiting, caching, and generation.

## Expected output
```text
Org Alpha: {'status': 'SUCCESS', 'tokens_streamed': ['This', ' is', ' a', ' streamed', ' AI', ' response.'], 'response': 'This is a streamed AI response.', 'cost_usd': 0.002, 'cached': False, 'remaining_credits': 49.998}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Valid tenant authentication and request dispatch
- Rejection on invalid tenant ID
- Rejection on rate limit exhaustion
- Rejection on zero credit balance
- Zero-cost delivery on cached query hits

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure credit balance deductions occur only on successful model executions.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add multi-provider fallback routing when primary mock fails.

## Navigation
Day number: 316 of 365
