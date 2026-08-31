# Day 343 Lab: A Monitored Production Deployment

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Monitored Production Deployment
- **Day number:** 343 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-343-a-monitored-production-deployment
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-343-a-monitored-production-deployment` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Unified Monitored Production AI Deployment Platform in Python integrating in-memory PII sanitization, deterministic feature flag routing, latency percentile tracking, multi-tenant cost attribution, and automated circuit breaker rollbacks.

## Learning objectives
- Scrub PII (SSNs, emails) from user prompts.
- Route user traffic deterministically to canary or baseline variants.
- Compute rolling percentile latencies (P50, P95).
- Attribute financial costs by tenant ID.
- Execute automated fast rollbacks when error rates spike.

## Prerequisites
- Python 3.10+ installed
- pytest, numpy installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, numpy

## Free and open-source options
- Python Standard Library, Pytest, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/production_deployment.py`: Starter implementation skeleton
- `examples/production_deployment.py`: Verified reference implementation
- `tests/test_production_deployment.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/production_deployment.py
```

## What the commands do
- Executes unified inference, computes observability metrics, and verifies automated rollback.

## Expected output
```text
{'trace_id': 'a0de7e3ad0354054b18897f6b5d63174', 'tenant_id': 't1', 'user_id': 'u1', 'variant': 'BASELINE_V1', 'prompt_sanitized': 'test', 'tokens': 150, 'cost_usd': 0.0005, 'is_error': False, 'circuit_tripped': False, 'timestamp': 1788138002.306768}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- PII scrubbing and trace ID generation
- Multi-tenant cost attribution ledger
- Observability report percentile calculation
- Automated circuit breaker rollback on error rate spike
- Empty platform report handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure numpy is installed for percentile calculation.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a real-time gross margin calculator.

## Navigation
Day number: 343 of 365
