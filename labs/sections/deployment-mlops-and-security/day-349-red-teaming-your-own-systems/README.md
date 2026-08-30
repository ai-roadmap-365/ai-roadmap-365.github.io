# Day 349 Lab: Red Teaming Your Own Systems

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Red Teaming Your Own Systems
- **Day number:** 349 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-349-red-teaming-your-own-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-349-red-teaming-your-own-systems` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated AI Red Teaming & Safety Judge Engine in Python that executes adversarial probes, evaluates responses for refusal compliance, calculates Attack Success Rates (ASR), and outputs structured vulnerability reports.

## Learning objectives
- Define structured adversarial attack probes.
- Implement an automated safety judge classifying responses as safe refusals or jailbreak breaches.
- Execute automated fuzzing against model targets.
- Calculate quantitative Attack Success Rates (ASR).

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
- `starter/red_teaming.py`: Starter implementation skeleton
- `examples/red_teaming.py`: Verified reference implementation
- `tests/test_red_teaming.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/red_teaming.py
```

## What the commands do
- Executes automated red teaming test probes, runs safety judge evaluations, computes ASR metrics, and verifies probe scoring.

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
- Canary token leak detection (Score 10 - Critical Breach)
- Safety refusal indicator recognition (Score 1 - Safe)
- Automated red team fuzzer suite execution
- Attack Success Rate (ASR) mathematical calculation
- Empty probe list handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure canary token matches exactly during response evaluation.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement multi-turn Crescendo test probes.

## Navigation
Day number: 349 of 365
