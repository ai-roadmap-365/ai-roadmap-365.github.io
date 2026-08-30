# Lab: Day 252 -- A Tested Prompt Library

## Lesson
Day number: 252 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Tested Prompt Libraries, Regression Test Harnesses, and CI/CD Evals.

## Purpose
Build and test a comprehensive Prompt Evaluation and Regression Test Harness in Python. Construct a multi-case Golden Dataset with deterministic JSON and substring assertions, and evaluate batch pass rates.

## Learning objectives
- Architect an automated prompt regression test harness.
- Implement deterministic assertions for schema validation and preamble bans.
- Benchmark prompt latency and pass-rate statistics across test runs.
- Structure prompt evaluation pipelines for CI/CD integration.

## Prerequisites
- Day 251 (Prompt Injection and Safe Prompting).
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
Python standard json and time libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/a_tested_prompt_library_lib.py`: Student scaffold file.
- `examples/a_tested_prompt_library_lib.py`: Complete reference implementation.
- `tests/test_a_tested_prompt_library_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/a_tested_prompt_library_lib.py
```

## What the commands do
- Executes test cases in batch.
- Asserts JSON format and substring rules.
- Runs unit test assertions.

## Expected output
```
Prompt Evaluation Demo Completed. Pass Rate: 1.0
```

## Validation steps
1. Verify `run_evaluations` processes all test cases.
2. Confirm `is_json` assertion identifies malformed JSON.
3. Validate failure reasons are captured in the report.
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
- **Assertion failure:** Verify expected substring values match the runner outputs.

## Security notes
All prompt testing executes locally in memory.

## Extension exercises
1. Implement an automated LLM-as-a-Judge scoring rubric.
2. Build an automated GitHub Actions CI workflow for Promptfoo.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Tested Prompt Library
- **Day number:** 252 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-252-a-tested-prompt-library
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-252-a-tested-prompt-library` when the site is running.
<!-- generated-links:end -->
