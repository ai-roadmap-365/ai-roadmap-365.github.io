# Day 299 Lab: Building an MCP Client

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building an MCP Client
- **Day number:** 299 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-299-building-an-mcp-client
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-299-building-an-mcp-client` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an autonomous AI agent host client in Python capable of managing multi-server MCP connections, aggregating tool catalogs, and routing execution requests across stdio pipes.

## Learning objectives
- Construct an MCPClientConnection handling initialization handshakes and tool discovery.
- Build an AutonomousMCPAgent managing multi-server connection pools.
- Dispatch dynamic tool calls with automated routing.
- Verify multi-server coordination and error recovery.

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
- `starter/mcp_client.py`: Starter implementation skeleton
- `examples/mcp_client.py`: Verified reference implementation
- `tests/test_mcp_client.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/mcp_client.py
```

## What the commands do
- Connects to simulated MCP servers, aggregates tool schemas, and executes routed tool calls.

## Expected output
```text
Unified tools: ['query_users', 'read_file']
DB Result: Alice, Bob
FS Result: File contents: OK
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Multi-server registration and connection
- Unified tool catalog aggregation
- Accurate tool dispatch routing
- Unknown tool error handling
- Clean connection teardown

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure tool names are unique across registered servers or implement namespacing.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement namespace prefixing (`server_name__tool_name`) for collision resolution.

## Navigation
Day number: 299 of 365
