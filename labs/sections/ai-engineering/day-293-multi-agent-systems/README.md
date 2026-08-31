# Day 293 Lab: Multi-Agent Systems

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Multi-Agent Systems
- **Day number:** 293 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-293-multi-agent-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-293-multi-agent-systems` when the site is running.
<!-- generated-links:end -->

## Purpose
Implement a Multi-Agent Supervisor System with an in-memory Message Bus, specialized worker agents (Researcher, Coder, Critic), and hierarchical task delegation.

## Learning objectives
- Construct a structured asynchronous Message Bus for agent communication.
- Implement specialized subagent prompts and role privilege separation.
- Execute hierarchical supervisor task delegation and result aggregation.
- Enforce communication bounds to prevent infinite chatter loops.

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
- `starter/multi_agent_system.py`: Starter implementation skeleton
- `examples/multi_agent_system.py`: Verified reference implementation
- `tests/test_multi_agent_system.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/multi_agent_system.py
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
Day number: 293 of 365
