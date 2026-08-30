# Day 304 Lab: Effective Agentic Coding Workflows

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Effective Agentic Coding Workflows
- **Day number:** 304 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-304-effective-agentic-coding-workflows
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-304-effective-agentic-coding-workflows` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated Self-Healing Test Runner and Diagnostic Parser in Python that captures test execution results, extracts stack trace diagnostics, and compiles repair prompts.

## Learning objectives
- Execute shell test commands and capture multi-stream outputs.
- Parse Python tracebacks to extract failing files, lines, and error types.
- Format structured repair prompts for coding agents.
- Enforce max iteration safety limits.

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
- `starter/self_healing_runner.py`: Starter implementation skeleton
- `examples/self_healing_runner.py`: Verified reference implementation
- `tests/test_self_healing.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/self_healing_runner.py
```

## What the commands do
- Executes test command, parses failing traceback, and formats diagnostic repair prompt.

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
- Passing command execution and exit code 0
- Failing command execution and exit code != 0
- Traceback parser extracting file, line, and exception message
- Structured repair prompt compilation

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify regex matches Python standard traceback format.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add support for pytest summary parsing (`FAILED tests/test_x.py::test_y`).

## Navigation
Day number: 304 of 365
