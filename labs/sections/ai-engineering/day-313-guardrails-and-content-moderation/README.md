# Day 313 Lab: Guardrails and Content Moderation

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Guardrails and Content Moderation
- **Day number:** 313 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-313-guardrails-and-content-moderation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-313-guardrails-and-content-moderation` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production AI Guardrail Defense Engine in Python supporting PII redaction (SSNs, Emails, Credit Cards), prompt injection interception, and safe fallback response generation.

## Learning objectives
- Implement deterministic regex token redaction for SSNs, emails, and credit cards.
- Detect prompt injection and jailbreak keywords.
- Enforce input filtering and generate deterministic fallback responses.
- Protect against empty and malformed inputs.

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
- `starter/guardrail_engine.py`: Starter implementation skeleton
- `examples/guardrail_engine.py`: Verified reference implementation
- `tests/test_guardrails.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/guardrail_engine.py
```

## What the commands do
- Executes PII masking, injection screening, and fallback response validation.

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
- PII redaction of SSNs, emails, and credit cards with counts
- Prompt injection detection and blocking
- Clean input pass-through
- Empty input rejection
- Fallback message generation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify regex patterns match standard formats (e.g. `XXX-XX-XXXX` for SSN).

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add API key redaction for OpenAI and AWS secret patterns.

## Navigation
Day number: 313 of 365
