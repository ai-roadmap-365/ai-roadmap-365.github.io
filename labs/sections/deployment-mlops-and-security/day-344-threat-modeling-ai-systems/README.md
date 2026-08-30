# Day 344 Lab: Threat Modeling AI Systems

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Threat Modeling AI Systems
- **Day number:** 344 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-344-threat-modeling-ai-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-344-threat-modeling-ai-systems` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an AI Threat Modeling & DREAD Risk Scorer in Python calculating composite risk priorities, categorizing vulnerabilities under STRIDE and OWASP LLM, and generating prioritized remediation plans.

## Learning objectives
- Register threat vectors with STRIDE categories and OWASP Top 10 mappings.
- Validate DREAD criteria scores (1–10).
- Compute composite risk scores and assign severity ratings.
- Generate prioritized remediation plans.

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
- `starter/threat_modeling.py`: Starter implementation skeleton
- `examples/threat_modeling.py`: Verified reference implementation
- `tests/test_threat_modeling.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/threat_modeling.py
```

## What the commands do
- Evaluates DREAD criteria, verifies risk score calculations, and tests remediation plan sorting.

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
- Correct composite DREAD score calculation
- Severity tier classification (CRITICAL, HIGH, MEDIUM, LOW)
- DREAD input boundary validation (1–10 integer range)
- Prioritized remediation plan sorting descending by composite risk
- Empty threat model report handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all DREAD criteria integers are between 1 and 10 inclusive.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a return-on-security-investment (ROSI) score calculator.

## Navigation
Day number: 344 of 365
