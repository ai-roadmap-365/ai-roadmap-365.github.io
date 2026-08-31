# Day 340 Lab: Logging and Analytics for AI Features

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Logging and Analytics for AI Features
- **Day number:** 340 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-340-logging-and-analytics-for-ai-features
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-340-logging-and-analytics-for-ai-features` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production AI Structured Logging & Analytics Engine in Python sanitizing PII, generating structured JSON event records, and tracking multi-tenant token costs.

## Learning objectives
- Redact PII (SSNs, emails, credit cards) in application memory.
- Generate structured JSON event logs with W3C trace IDs.
- Compute exact financial costs based on token consumption.
- Maintain a real-time multi-tenant analytics ledger.

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
- `starter/logging_analytics.py`: Starter implementation skeleton
- `examples/logging_analytics.py`: Verified reference implementation
- `tests/test_logging_analytics.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/logging_analytics.py
```

## What the commands do
- Executes PII redaction tests, validates log structures, and verifies cost attribution.

## Expected output
```text
{'trace_id': '9bb3a8c2da24428f967b1f6146ffdf6d', 'tenant_id': 't1', 'prompt_sanitized': 'Email is [REDACTED_EMAIL]', 'completion_sanitized': 'OK', 'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150, 'cost_usd': 0.0005, 'timestamp': 1788138002.180941}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- PII scrubbing on emails, SSNs, and credit cards
- Structured JSON schema emission with trace IDs
- Accurate cost calculation across prompt and completion tokens
- Multi-tenant aggregation in financial ledger
- Custom trace ID preservation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify regex patterns match standard formats.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a monthly tenant budget quota limiter.

## Navigation
Day number: 340 of 365
