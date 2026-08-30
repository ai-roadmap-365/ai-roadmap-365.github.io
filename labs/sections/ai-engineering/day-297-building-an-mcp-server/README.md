# Day 297 Lab: Building an MCP Server

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building an MCP Server
- **Day number:** 297 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-297-building-an-mcp-server
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-297-building-an-mcp-server` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a custom FastMCP-style Model Context Protocol server engine in Python featuring decorator registration, automated JSON Schema generation from type annotations, and structured error propagation.

## Learning objectives
- Construct an MCP server using FastMCP/Python decorator abstractions.
- Generate JSON Schema parameter specifications automatically from Python type hints and docstrings.
- Implement type validation, boundary enforcement, and structured error responses.
- Expose real-world database and file utility tools over a standard stdio event loop.

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
- `starter/custom_mcp_server.py`: Starter implementation skeleton
- `examples/custom_mcp_server.py`: Verified reference implementation
- `tests/test_custom_mcp_server.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/custom_mcp_server.py
```

## What the commands do
- Registers custom tools with type hints and verifies JSON Schema reflection and execution.

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
- `@tool` decorator registration and tool catalog listing
- Automatic JSON Schema property type mapping (str, int, float, bool)
- Required parameter detection from function signatures
- Successful execution returning formatted text content
- Exception handling and error response formatting with `isError: True`

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure function signatures include type annotations for all parameters.

## Security notes
Runs completely offline on local CPU without network calls or API keys.

## Extension exercises
Add support for Pydantic BaseModel schemas.

## Navigation
Day number: 297 of 365
