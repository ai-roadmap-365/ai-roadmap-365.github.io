# Day 301 Lab: Your Personal MCP Server

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Your Personal MCP Server
- **Day number:** 301 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-301-your-personal-mcp-server
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-301-your-personal-mcp-server` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a complete personal developer MCP server in Python with embedded SQLite persistence, memo and task management tools, live URI resources, and automated standup workflow prompt templates.

## Learning objectives
- Initialize an embedded SQLite memo and task database.
- Implement memo storage, keyword search, and task management tools.
- Expose live URI resources (`memo://pending-tasks`, `memo://all-memos`).
- Generate structured workflow prompt templates (`/standup`).

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
- `starter/personal_mcp_server.py`: Starter implementation skeleton
- `examples/personal_mcp_server.py`: Verified reference implementation
- `tests/test_personal_mcp_server.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/personal_mcp_server.py
```

## What the commands do
- Executes memo management, task tracking, resource reads, and prompt generation.

## Expected output
```text
All 4 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- SQLite table schema creation
- Memo insertion and search query filtering
- task creation and status updates
- Resource URI formatting and reading
- Standup prompt message generation
- Clean error handling on empty data

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure SQLite database path is writable.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement a Git history resource reader using `subprocess`.

## Navigation
Day number: 301 of 365
