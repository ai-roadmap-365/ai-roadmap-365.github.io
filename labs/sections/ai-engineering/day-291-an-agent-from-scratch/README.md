# Day 291 Lab: An Agent from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** An Agent from Scratch
- **Day number:** 291 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-291-an-agent-from-scratch
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-291-an-agent-from-scratch` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a fully autonomous, zero-dependency pure Python AI agent with sliding-window scratchpad memory compaction, regex stream parsing, tool dispatch, and cycle detection.

## Learning objectives
- Build a complete ReAct agent runtime using only the Python standard library.
- Implement sliding-window memory compaction to prevent context overflow.
- Execute multi-step mathematical calculations and knowledge base lookups.
- Verify cycle detection and step budget termination.

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
- `starter/scratch_agent.py`: Starter implementation skeleton
- `examples/scratch_agent.py`: Verified reference implementation
- `tests/test_scratch_agent.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/scratch_agent.py
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
Day number: 291 of 365
