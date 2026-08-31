# Day 355 Lab: Agent and Tool Integration

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Agent and Tool Integration
- **Day number:** 355 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-355-agent-and-tool-integration
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-355-agent-and-tool-integration` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production ReAct Agent Engine in Python featuring a schema-validated tool registry, sandboxed tool dispatcher, multi-turn reasoning loop, and JSON state checkpointing.

## Learning objectives
- Register tool schemas and execution handlers.
- Execute tools safely within a sandboxed dispatcher.
- Run a multi-turn ReAct reasoning loop with turn limits.
- Capture serializable execution checkpoints.

## Prerequisites
- Python 3.10+ installed
- pydantic and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, pydantic

## Free and open-source options
- Python Standard Library, Pytest, Pydantic

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/agent.py`: Starter implementation skeleton
- `examples/agent.py`: Verified reference implementation
- `tests/test_agent.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/agent.py
```

## What the commands do
- Executes multi-turn agent reasoning, runs sandboxed tools, and records state checkpoints.

## Expected output
```text
{'status': 'SUCCESS', 'total_turns': 1, 'final_answer': '15000', 'checkpoints': [{'turn': 1, 'thought': 'done', 'action': 'FINAL_ANSWER', 'action_input': {'answer': '15000'}, 'observation': 'COMPLETED'}]}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Tool registration and schema definition
- Sandboxed tool execution and error capture
- Multi-turn ReAct reasoning workflow
- Max turn limit enforcement
- State checkpoint serialization

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure tool return values are JSON-serializable.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement a rate limiter on tool executions.

## Navigation
Day number: 355 of 365
