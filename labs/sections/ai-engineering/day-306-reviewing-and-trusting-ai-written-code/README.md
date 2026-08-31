# Day 306 Lab: Reviewing and Trusting AI-Written Code

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Reviewing and Trusting AI-Written Code
- **Day number:** 306 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-306-reviewing-and-trusting-ai-written-code
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-306-reviewing-and-trusting-ai-written-code` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Automated AI Code Review & Security Scanner in Python that analyzes Python AST nodes to detect unapproved hallucinated dependencies (slopsquatting), insecure shell executions, and weak test assertions.

## Learning objectives
- Traverse Python Abstract Syntax Trees using the `ast` module.
- Detect insecure shell calls (`os.system`, `os.popen`).
- Audit package imports against an approved package whitelist.
- Identify weak tautological assertions (`assert True`).

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
- Python Standard Library (ast), Pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/code_review_scanner.py`: Starter implementation skeleton
- `examples/code_review_scanner.py`: Verified reference implementation
- `tests/test_code_review.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/code_review_scanner.py
```

## What the commands do
- Parses Python source files into ASTs and identifies security/quality rule violations.

## Expected output
```text
{'file': '<string>', 'passed': False, 'issue_count': 1, 'issues': [{'line': 2, 'rule': 'INSECURE_SHELL_EXECUTION', 'severity': 'CRITICAL', 'message': 'Avoid using os.system; use safe subprocess APIs.'}]}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Passing clean code with approved imports
- Detection of unapproved external imports (slopsquatting risk)
- Detection of `os.system` and `os.popen` shell calls
- Detection of weak `assert True` statements

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure Python code to scan contains valid syntax without SyntaxErrors.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add detection of hardcoded AWS and OpenAI API keys.

## Navigation
Day number: 306 of 365
