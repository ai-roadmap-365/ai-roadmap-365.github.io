# Day 290 Lab: Designing Tools for Agents

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Designing Tools for Agents
- **Day number:** 290 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-290-designing-tools-for-agents
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-290-designing-tools-for-agents` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a production-grade Tool Registry in Python featuring JSON Schema declaration, automated parameter coercion, SHA-256 idempotency caching, and sandbox error isolation.

## Learning objectives
- Construct standard JSON Schema definitions for tool parameters.
- Implement type coercion and boundary constraint validation.
- Build idempotent SHA-256 result caching for side-effect-free execution.
- Isolate runtime exceptions into structured error contracts.

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
- `starter/tool_registry.py`: Starter implementation skeleton
- `examples/tool_registry.py`: Verified reference implementation
- `tests/test_tool_registry.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/tool_registry.py
```

## What the commands do
- Executes agent runtime algorithms and logs state transitions to stdout.

## Expected output
```text

```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Core state transitions and algorithm logic
- Error observation handling and recovery
- Edge cases and bounds enforcement

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify Python version is >= 3.10 and environment variables are set.

## Security notes
Runs completely offline on local CPU without network calls or API keys.

## Extension exercises
Implement async execution or enhanced caching strategies.

## Navigation
Day number: 290 of 365
