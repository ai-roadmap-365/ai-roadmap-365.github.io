# Day 303 Lab: Working with a Coding Agent

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Working with a Coding Agent
- **Day number:** 303 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-303-working-with-a-coding-agent
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-303-working-with-a-coding-agent` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Specification Compiler and Context Bundler in Python that automates the generation of high-leverage agent prompts with surgical context, hard constraints, non-goals, and verification commands.

## Learning objectives
- Implement surgical file context bundling with markdown formatting.
- Construct structured specification prompts with explicit boundaries.
- Attach automated verification test gates to prompts.
- Handle missing files and format constraints cleanly.

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
- `starter/spec_compiler.py`: Starter implementation skeleton
- `examples/spec_compiler.py`: Verified reference implementation
- `tests/test_spec_compiler.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/spec_compiler.py
```

## What the commands do
- Compiles specification prompts, bundles context files, and verifies prompt formatting.

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
- Context file extraction and formatting
- Missing file annotation
- Constraint and non-goal list rendering
- Complete prompt compilation containing all required sections

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure workspace root path is valid.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement an automatic token counter to measure context size.

## Navigation
Day number: 303 of 365
