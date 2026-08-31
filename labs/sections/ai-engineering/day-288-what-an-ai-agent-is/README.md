# Day 288 Lab: What an AI Agent Is

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What an AI Agent Is
- **Day number:** 288 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-288-what-an-ai-agent-is
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-288-what-an-ai-agent-is` when the site is running.
<!-- generated-links:end -->

## Purpose
Construct an autonomous AI agent runtime featuring an explicit discrete State Machine, Perception-Cognition-Action loop, cycle detection hash table, and step budget guards.

## Learning objectives
- Deconstruct the perception-cognition-action loop driving autonomous AI agents.
- Implement discrete state machine transitions (INITIALIZED, REASONING, ACTING, TERMINATED).
- Incorporate cycle detection and maximum execution budgets.
- Execute goal-directed tasks with observation feedback loops.

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
- `starter/agent_state_machine.py`: Starter implementation skeleton
- `examples/agent_state_machine.py`: Verified reference implementation
- `tests/test_agent_state_machine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/agent_state_machine.py
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
Day number: 288 of 365
