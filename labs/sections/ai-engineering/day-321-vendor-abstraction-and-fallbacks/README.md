# Day 321 Lab: Vendor Abstraction and Fallbacks

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Vendor Abstraction and Fallbacks
- **Day number:** 321 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-321-vendor-abstraction-and-fallbacks
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-321-vendor-abstraction-and-fallbacks` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Vendor Router and Fallback Engine in Python supporting multi-provider fallback priority lists, health tracking, and standardized response schemas.

## Learning objectives
- Implement vendor-neutral model invocation interfaces.
- Manage fallback priority lists across primary, secondary, and tertiary providers.
- Intercept simulated upstream errors and execute sub-second failover.
- Track attempted providers and failover status.

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
- `starter/vendor_router.py`: Starter implementation skeleton
- `examples/vendor_router.py`: Verified reference implementation
- `tests/test_vendor_router.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/vendor_router.py
```

## What the commands do
- Executes requests across provider fallback cascades.

## Expected output
```text
Normal: {'status': 'SUCCESS', 'resolved_provider': 'anthropic', 'provider_name': 'Anthropic Claude 3.5', 'response': '[Anthropic Claude 3.5] Completed: Hello', 'attempted_providers': ['anthropic'], 'fallback_occurred': False}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Successful resolution on primary provider
- Seamless failover to secondary provider when primary fails
- Fallback to tertiary replica when primary and secondary fail
- Reporting when all configured providers are unavailable
- Health state toggling and tracking

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify fallback list iteration order matches priority configuration.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement latency-based dynamic provider weight adjustments.

## Navigation
Day number: 321 of 365
