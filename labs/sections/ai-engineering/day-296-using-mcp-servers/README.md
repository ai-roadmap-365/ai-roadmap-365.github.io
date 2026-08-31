# Day 296 Lab: Using MCP Servers

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Using MCP Servers
- **Day number:** 296 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-296-using-mcp-servers
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-296-using-mcp-servers` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a local MCP Subprocess Runner and Configuration Manager in Python capable of parsing client configurations, spawning stdio server processes, executing handshakes, and dispatching tool requests.

## Learning objectives
- Parse and validate `mcpServers` configuration schemas.
- Spawn unbuffered child subprocesses and hook stdio streams.
- Execute the JSON-RPC 2.0 initialize sequence and tool discovery.
- Route diagnostic traces to stderr while maintaining clean stdout JSON-RPC framing.

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
- `starter/mcp_runner.py`: Starter implementation skeleton
- `examples/mcp_runner.py`: Verified reference implementation
- `tests/test_mcp_runner.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/mcp_runner.py
```

## What the commands do
- Spawns a local MCP server mock subprocess, tests initialization, and executes tool calls.

## Expected output
```text
Initialized: {'name': 'test-srv', 'version': '1.0.0'}
Tools: [{'name': 'get_status', 'description': 'Get server health status', 'inputSchema': {'type': 'object'}}]
Call result: {"status": "ONLINE", "uptime_sec": 4200}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Configuration parsing and validation
- Subprocess spawning and environment variable injection
- Initialization handshake and capabilities extraction
- Tool execution and result content parsing
- Graceful process termination

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure Python paths are valid and standard output remains unbuffered.

## Security notes
Runs completely offline on local CPU without network calls or API keys.

## Extension exercises
Implement automatic subprocess restart upon unexpected exit.

## Navigation
Day number: 296 of 365
