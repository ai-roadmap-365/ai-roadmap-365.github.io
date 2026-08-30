# Lab: Day 259 -- Building a CLI Assistant

## Lesson
Day number: 259 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Building a Command-Line AI Assistant Core in Python.

## Purpose
Build and test a Modular CLI Assistant Core in Python. Implement sliding window memory management, slash command routing, tool registration, and session token/financial tracking.

## Learning objectives
- Build context message arrays with pinned system prompts and sliding history.
- Implement slash command handlers for session management.
- Register and execute local tools.
- Track cumulative session token and cost expenditure.

## Prerequisites
- Day 258 (Cost, Caching, and Rate Limits).
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
Python and standard collections/typing modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/building_a_cli_assistant_lib.py`: Student scaffold file.
- `examples/building_a_cli_assistant_lib.py`: Complete reference implementation.
- `tests/test_building_a_cli_assistant_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/building_a_cli_assistant_lib.py
```

## What the commands do
- Builds message context array.
- Processes `/cost` slash command.
- Runs unit test assertions.

## Expected output
```
Assistant Demo Executed. Context Len: 3, Cost Msg: Session Tokens: 100 | Total Cost: $0.0003
```

## Validation steps
1. Verify system prompt remains pinned at message index 0.
2. Confirm sliding window evicts oldest non-system turns when max turns exceeded.
3. Validate `/clear` empties conversational history.
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
- **Memory window sizing error:** Ensure deque `maxlen` is initialized to `max_history_turns * 2`.

## Security notes
All assistant state runs locally in memory.

## Extension exercises
1. Implement a Git commit message generator slash command (`/commit`).
2. Build an automated conversation session exporter (`/export`).

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building a CLI Assistant
- **Day number:** 259 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-259-building-a-cli-assistant
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-259-building-a-cli-assistant` when the site is running.
<!-- generated-links:end -->
