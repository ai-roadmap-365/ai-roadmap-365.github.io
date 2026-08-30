# Day 295 Lab: What MCP Is and Why It Exists

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What MCP Is and Why It Exists
- **Day number:** 295 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-295-what-mcp-is-and-why-it
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-295-what-mcp-is-and-why-it` when the site is running.
<!-- generated-links:end -->

## Purpose
Construct a standards-compliant JSON-RPC 2.0 Model Context Protocol (MCP) server engine in Python implementing the complete handshake, tool discovery, and execution lifecycle.

## Learning objectives
- Deconstruct the N-times-M integration dilemma solved by MCP.
- Implement JSON-RPC 2.0 message parsing and error contract handling.
- Build capability negotiation for the initialize handshake.
- Dispatch dynamic tool executions with structured content responses.

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
- `starter/mcp_protocol.py`: Starter implementation skeleton
- `examples/mcp_protocol.py`: Verified reference implementation
- `tests/test_mcp_protocol.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/mcp_protocol.py
```

## What the commands do
- Evaluates JSON-RPC message processing across initialization, discovery, and execution turns.

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
- JSON-RPC 2.0 initialize request and capability response
- Ignored notifications without response emission
- tools/list tool discovery payload
- tools/call execution and structured error handling
- Malformed JSON parse error codes (-32700)

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all JSON strings are valid and tool handlers return stringifiable values.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add support for URI-addressable resources and resource subscriptions.

## Navigation
Day number: 295 of 365
