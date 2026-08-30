# Day 300 Lab: MCP Security

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** MCP Security
- **Day number:** 300 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-300-mcp-security
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-300-mcp-security` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an MCP Security Guard and Sandboxing Engine in Python providing path canonicalization, destructive action classification, Human-in-the-Loop gates, and audit logging.

## Learning objectives
- Implement canonical path sandboxing rejecting `../` traversal attacks.
- Build a risk classification engine identifying destructive actions.
- Enforce Human-in-the-Loop approval gates for high-risk operations.
- Maintain structured security audit logs for compliance.

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
- `starter/mcp_security_guard.py`: Starter implementation skeleton
- `examples/mcp_security_guard.py`: Verified reference implementation
- `tests/test_mcp_security_guard.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/mcp_security_guard.py
```

## What the commands do
- Evaluates path sandboxing, destructive tool interception, and approval workflows.

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
- Safe path resolution within sandbox root
- Path traversal rejection (`../../etc/passwd`)
- Destructive tool blocking without human approval
- Successful execution when human approval is granted
- Audit log entry verification

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure sandbox root path is an absolute real path.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement network IP range filtering for HTTP request tools.

## Navigation
Day number: 300 of 365
