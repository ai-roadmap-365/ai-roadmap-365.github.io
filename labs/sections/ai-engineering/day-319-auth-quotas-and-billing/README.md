# Day 319 Lab: Auth, Quotas, and Billing

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Auth, Quotas, and Billing
- **Day number:** 319 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-319-auth-quotas-and-billing
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-319-auth-quotas-and-billing` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Auth, Quotas, and Two-Phase Credit Billing Engine in Python supporting SHA-256 API key hashing, RPM/TPM rate limiting, pre-authorization credit holds, and token settlement.

## Learning objectives
- Hash and verify API keys securely.
- Enforce dual Requests-per-Minute and Tokens-per-Minute limits.
- Implement credit pre-authorization holds preventing account overdrafts.
- Settle exact token costs and reconcile tenant balances.

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
- `starter/auth_billing.py`: Starter implementation skeleton
- `examples/auth_billing.py`: Verified reference implementation
- `tests/test_auth_billing.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/auth_billing.py
```

## What the commands do
- Executes tenant registration, authentication, pre-auth holds, and settlement reconciliation.

## Expected output
```text
(True, 'HOLD_RESERVED', 'hold_1')
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Valid authentication and credit pre-authorization hold
- Rejection on incorrect API key
- Rejection when available balance is insufficient
- Rejection when RPM or TPM limits are exceeded
- Accurate settlement, hold release, and balance deduction

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure `reserved_holds` is deducted upon settlement.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement Stripe metered billing event payload emission.

## Navigation
Day number: 319 of 365
