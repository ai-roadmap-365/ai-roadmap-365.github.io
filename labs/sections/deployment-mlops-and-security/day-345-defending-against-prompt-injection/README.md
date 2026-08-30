# Day 345 Lab: Defending Against Prompt Injection

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Defending Against Prompt Injection
- **Day number:** 345 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-345-defending-against-prompt-injection
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-345-defending-against-prompt-injection` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production Prompt Defense Firewall in Python incorporating heuristic jailbreak detection, XML delimiter escaping, canary token injection, and outbound exfiltration filtering.

## Learning objectives
- Detect and block direct prompt injection attempts using regex heuristics.
- Escape XML tags to prevent tag breakout injection attacks.
- Inject randomized session canary tokens into system prompts.
- Intercept and block outbound canary token exfiltration.

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
- `starter/prompt_defense.py`: Starter implementation skeleton
- `examples/prompt_defense.py`: Verified reference implementation
- `tests/test_prompt_defense.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/prompt_defense.py
```

## What the commands do
- Executes prompt firewall tests, verifying input blocking, tag escaping, and canary exfiltration dropping.

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
- Heuristic detection of common prompt injection patterns
- XML tag escaping (`<`, `>`, `&`)
- Structured delimiter context wrapping
- Outbound canary token leakage interception
- Legitimate prompt passthrough without false positives

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify that `&` is replaced before `<` and `>` in XML tag escaping.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement Base64 payload decoding before regex evaluation.

## Navigation
Day number: 345 of 365
