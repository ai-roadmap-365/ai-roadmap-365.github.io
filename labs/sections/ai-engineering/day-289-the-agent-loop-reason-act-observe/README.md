# Day 289 Lab: The Agent Loop: Reason, Act, Observe

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Agent Loop: Reason, Act, Observe
- **Day number:** 289 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-289-the-agent-loop-reason-act-observe
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-289-the-agent-loop-reason-act-observe` when the site is running.
<!-- generated-links:end -->

## Purpose
Implement an autonomous ReAct (Reason + Act) execution loop with regex token stream parsing, self-healing JSON error observation feedback, and deterministic termination predicates.

## Learning objectives
- Deconstruct the ReAct Thought-Action-Observation execution cycle.
- Build regex-based parsers extracting structured Action and Action Input payloads.
- Implement self-healing error observation injection for malformed parameters.
- Enforce deterministic termination on Final Answer extraction.

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
- `starter/react_engine.py`: Starter implementation skeleton
- `examples/react_engine.py`: Verified reference implementation
- `tests/test_react_engine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/react_engine.py
```

## What the commands do
- Executes agent runtime algorithms and logs state transitions to stdout.

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
Day number: 289 of 365
