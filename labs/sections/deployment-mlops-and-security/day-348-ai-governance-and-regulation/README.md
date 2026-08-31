# Day 348 Lab: AI Governance and Regulation

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** AI Governance and Regulation
- **Day number:** 348 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-348-ai-governance-and-regulation
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-348-ai-governance-and-regulation` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated AI Governance & Compliance Validator in Python that maps systems against EU AI Act risk tiers, checks fairness metrics with the Four-Fifths rule, and generates standardized Model Cards.

## Learning objectives
- Classify AI use cases into EU AI Act risk tiers.
- Identify prohibited unacceptable risk AI systems.
- Calculate Disparate Impact ratios for demographic fairness.
- Generate structured JSON Model Card manifests.

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
- `starter/ai_governance.py`: Starter implementation skeleton
- `examples/ai_governance.py`: Verified reference implementation
- `tests/test_ai_governance.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/ai_governance.py
```

## What the commands do
- Executes regulatory tier classification, checks prohibited practices, tests disparate impact ratios, and validates Model Card generation.

## Expected output
```text
('HIGH_RISK', ['Establish Continuous Risk Management System (Art. 9)', 'Conduct Data Governance & Bias Testing (Art. 10)', 'Provide Technical Documentation & Model Card (Art. 11)', 'Implement Automated Logging & Audit Trails (Art. 12)', 'Enforce Human Oversight & Kill Switches (Art. 14)', 'Obtain CE Conformity Mark & Register in EU Database (Art. 49)'])
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- EU AI Act High-Risk classification and obligation generation
- Prohibited Unacceptable-Risk system blocking
- GPAI systemic risk classification for >10^25 FLOPs
- Disparate Impact fairness computation
- Model Card JSON structure and safety limitation fields

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure reference group selection rate is non-zero in fairness calculations.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement ISO/IEC 42001 checklist verification.

## Navigation
Day number: 348 of 365
