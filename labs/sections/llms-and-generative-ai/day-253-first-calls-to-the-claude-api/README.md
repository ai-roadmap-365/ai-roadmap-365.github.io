# Lab: Day 253 -- First Calls to the Claude API

## Lesson
Day number: 253 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Anthropic Messages API, Python SDK, and Exponential Retries.

## Purpose
Build and test a resilient Anthropic API client wrapper in Python. Implement secure environment key loading, configure message parameter schemas, and execute jittered exponential backoff retries on transient failures.

## Learning objectives
- Initialize the Anthropic client using environment variables.
- Structure Messages API calls with separated system parameters.
- Implement exponential backoff with full jitter for rate limits.
- Parse typed content blocks and token usage statistics.

## Prerequisites
- Day 252 (A Tested Prompt Library).
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
Python and standard random/time modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/first_calls_to_the_claude_api_lib.py`: Student scaffold file.
- `examples/first_calls_to_the_claude_api_lib.py`: Complete reference implementation.
- `tests/test_first_calls_to_the_claude_api_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/first_calls_to_the_claude_api_lib.py
```

## What the commands do
- Initializes API client with authentication.
- Sends structured message request.
- Runs unit test assertions.

## Expected output
```
Anthropic Client Demo Executed. Stop reason: end_turn
```

## Validation steps
1. Verify system parameter separation raises error if passed in messages.
2. Confirm exponential backoff handles transient failures.
3. Validate stop_reason equals `end_turn`.
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
- **Missing API key:** Set `ANTHROPIC_API_KEY` in environment.

## Security notes
Never hardcode API keys in source files or git commits.

## Extension exercises
1. Implement an async Messages API dispatcher with `asyncio`.
2. Build an automated token cost ledger in SQLite.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** First Calls to the Claude API
- **Day number:** 253 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-253-first-calls-to-the-claude-api
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-253-first-calls-to-the-claude-api` when the site is running.
<!-- generated-links:end -->
