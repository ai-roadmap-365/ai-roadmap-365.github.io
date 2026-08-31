# Day 346 Lab: Data Privacy and PII Handling

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Data Privacy and PII Handling
- **Day number:** 346 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-346-data-privacy-and-pii-handling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-346-data-privacy-and-pii-handling` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production PII Token Vault and Differential Privacy Engine in Python implementing entity pseudonymization, reversible detokenization, right-to-forget key shredding, and calibrated Laplace noise addition.

## Learning objectives
- Tokenize sensitive SSNs, emails, and credit cards into synthetic surrogates.
- Maintain reversible mapping tables and detokenize model responses.
- Implement right-to-be-forgotten deletion workflows.
- Apply the Laplace Mechanism for Differential Privacy.

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
- `starter/data_privacy.py`: Starter implementation skeleton
- `examples/data_privacy.py`: Verified reference implementation
- `tests/test_data_privacy.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/data_privacy.py
```

## What the commands do
- Executes PII tokenization tests, detokenization verification, key deletion checks, and Laplace noise bounds testing.

## Expected output
```text
Test email is <EMAIL_1>
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- PII entity tokenization (SSN, Email, Credit Card)
- Reversible response detokenization
- Right-to-forget key shredding and unlearning
- Laplace mechanism differential privacy noise addition
- Zero division error handling on invalid epsilon

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure epsilon is strictly positive (`epsilon > 0`).

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement phone number and address tokenization rules.

## Navigation
Day number: 346 of 365
