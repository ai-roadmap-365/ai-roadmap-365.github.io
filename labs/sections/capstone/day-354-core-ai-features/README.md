# Day 354 Lab: Core AI Features

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Core AI Features
- **Day number:** 354 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-354-core-ai-features
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-354-core-ai-features` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production Core AI Reasoning Engine in Python featuring XML prompt synthesis, Pydantic structured output validation, circuit breaker model routing, and self-healing JSON repair.

## Learning objectives
- Synthesize XML-delimited prompts with retrieved context.
- Validate structured JSON against Pydantic schemas.
- Implement circuit breaker timeout failover to backup models.
- Execute automated JSON schema repair loops.

## Prerequisites
- Python 3.10+ installed
- pydantic and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, pydantic

## Free and open-source options
- Python Standard Library, Pytest, Pydantic

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/core_ai.py`: Starter implementation skeleton
- `examples/core_ai.py`: Verified reference implementation
- `tests/test_core_ai.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/core_ai.py
```

## What the commands do
- Executes prompt synthesis, tests circuit breaker failover, and validates structured Pydantic outputs.

## Expected output
```text
Parsed: SLA is 99.9%.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- XML prompt enclosure formatting
- Type-safe Pydantic output validation
- Circuit breaker timeout failover
- Consecutive failure trip logic
- Self-healing repair loop on invalid JSON

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure markdown formatting is stripped before JSON deserialization.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement streaming token generation with SSE formatting.

## Navigation
Day number: 354 of 365
