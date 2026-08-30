# Week 43 Project: Personal MCP Server

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Project Overview
Build and package a complete production-grade Personal Developer MCP Server in Python. Your server will act as a local developer assistant daemon integrating:
1. **Developer Memo & Task Engine:** SQLite-backed storage for developer notes, project snippets, and tasks.
2. **Live Workspace Resources:** Dynamic URI endpoints (`memo://pending-tasks`, `memo://all-memos`, `sys://telemetry`) with change synchronization.
3. **Workflow Prompt Templates:** Pre-engineered templates (`/standup`, `/code-audit`) that aggregate git logs and tasks.
4. **Security Middleware:** Path traversal sandboxing and Human-in-the-Loop gates.
5. **Full Protocol Compliance:** Standard JSON-RPC 2.0 stdio transport compatible with Claude Desktop and autonomous agent clients.

## Learning objectives
- Synthesize Tools, Resources, and Prompts into a single cohesive MCP service.
- Implement robust SQLite database persistence with WAL mode.
- Enforce strict security sandboxing and path canonicalization.
- Deliver automated developer workflow prompt templates.

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
- Python Standard Library, SQLite3, Pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/personal_mcp_daemon.py`: Starter implementation skeleton
- `examples/personal_mcp_daemon.py`: Verified reference implementation
- `tests/test_personal_mcp_daemon.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/personal_mcp_daemon.py
```

## What the commands do
- Launches the Personal MCP daemon and verifies end-to-end tool execution, resource streaming, and prompt compilation.

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
- Server JSON-RPC handshake (`initialize`)
- `tools/list` and `tools/call` for memo and task operations
- `resources/list` and `resources/read` for live state
- `prompts/list` and `prompts/get` for `/standup` workflow
- Path sandboxing rejecting directory traversal
- Clean exception handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure SQLite database path is in a writable directory.

## Security notes
Runs completely offline on local CPU with path sandboxing.

## Extension exercises
Integrate with Claude Desktop by adding the server to `claude_desktop_config.json`.

## Navigation
Week 43 Capstone Project
