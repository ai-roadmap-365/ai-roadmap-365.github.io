# Lab: Day 246 -- Prompting Fundamentals

## Lesson
Day number: 246 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Prompting Fundamentals, 6-Part Anatomy, and Delimiter Sandboxing.

## Purpose
Build and test a modular, template-driven prompt compiler and validation engine in Python. Construct structured production prompts, enforce XML delimiter sandboxing, and validate recency ordering.

## Learning objectives
- Formulate prompts using the 6 canonical architectural components.
- Enforce XML delimiter sandboxing to isolate untrusted input payloads.
- Apply recency positioning for output formatting and constraints.
- Implement programmatic validation assertions for prompt structures.

## Prerequisites
- Day 245 (Benchmarking Models Yourself).
- Python 3.11+ with Pytest.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 1 GB RAM.
- 100 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
Python and standard string manipulation tools are free and open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/prompting_fundamentals_lib.py`: Student scaffold file.
- `examples/prompting_fundamentals_lib.py`: Complete reference implementation.
- `tests/test_prompting_fundamentals_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/prompting_fundamentals_lib.py
```

## What the commands do
- Compiles modular prompts with XML delimiter tags.
- Verifies primacy and recency positioning.
- Runs unit test assertions.

## Expected output
```
Prompt Demo Compiled Successfully.
```

## Validation steps
1. Verify `compile` generates matching opening and closing XML tags.
2. Confirm `<role_and_task>` appears at index 0 (Primacy).
3. Confirm `<output_format>` appears at the end (Recency).
4. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **Missing tag closure:** Ensure every tag opened with `<tag>` has a corresponding `</tag>`.

## Security notes
All prompt compilation runs locally in memory.

## Extension exercises
1. Implement a prompt linter that flags negative constraint keywords.
2. Build an automated prompt caching token boundary calculator.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Prompting Fundamentals
- **Day number:** 246 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-246-prompting-fundamentals
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-246-prompting-fundamentals` when the site is running.
<!-- generated-links:end -->
