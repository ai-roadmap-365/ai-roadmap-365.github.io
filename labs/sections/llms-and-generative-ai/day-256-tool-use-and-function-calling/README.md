# Lab: Day 256 -- Tool Use and Function Calling

## Lesson
Day number: 256 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Tool Use, Function Calling, and Automated Dispatchers.

## Purpose
Build and test an Automated Tool Dispatcher and Agent Loop in Python. Register custom mathematical and lookup tools with JSON Schema declarations, parse tool use stop reasons, and package structured tool results.

## Learning objectives
- Register custom Python functions in a typed tool dispatcher.
- Format declarative JSON Schema tool definitions.
- Execute local functions safely and handle execution exceptions.
- Package `tool_result` payloads for multi-turn agent loops.

## Prerequisites
- Day 255 (Streaming Responses).
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
Python and standard typing/json modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/tool_use_and_function_calling_lib.py`: Student scaffold file.
- `examples/tool_use_and_function_calling_lib.py`: Complete reference implementation.
- `tests/test_tool_use_and_function_calling_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/tool_use_and_function_calling_lib.py
```

## What the commands do
- Registers calculation tool.
- Simulates tool calling response turn.
- Runs unit test assertions.

## Expected output
```
Dispatcher Demo Executed. Result: 107.25
```

## Validation steps
1. Verify tool registration stores valid schemas.
2. Confirm dispatcher executes target Python function with arguments.
3. Validate error message is returned for unregistered tools.
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
- **Argument mismatch error:** Ensure function argument names match JSON schema properties.

## Security notes
All tools execute strictly in local memory.

## Extension exercises
1. Implement an async parallel tool runner with `asyncio.gather`.
2. Build an AST-validated SQL query executor tool.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Tool Use and Function Calling
- **Day number:** 256 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-256-tool-use-and-function-calling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-256-tool-use-and-function-calling` when the site is running.
<!-- generated-links:end -->
