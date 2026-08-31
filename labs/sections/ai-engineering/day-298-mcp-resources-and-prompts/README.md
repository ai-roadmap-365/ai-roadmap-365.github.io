# Day 298 Lab: MCP Resources and Prompts

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** MCP Resources and Prompts
- **Day number:** 298 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-298-mcp-resources-and-prompts
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-298-mcp-resources-and-prompts` when the site is running.
<!-- generated-links:end -->

## Purpose
Construct an MCP server subsystem in Python managing URI-addressable Resources with MIME types, live change notifications, and parameterized Prompt Templates.

## Learning objectives
- Architect URI-addressable MCP Resources using standard scheme conventions.
- Implement MIME-type negotiation and payload streaming.
- Design dynamic resource change notifications.
- Create parameterized Prompt Templates returning multi-role message arrays.

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
- `starter/mcp_resources_prompts.py`: Starter implementation skeleton
- `examples/mcp_resources_prompts.py`: Verified reference implementation
- `tests/test_mcp_resources_prompts.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/mcp_resources_prompts.py
```

## What the commands do
- Registers resources and prompts and evaluates reading, subscription, and template generation.

## Expected output
```text
Resources: {'resources': [{'uri': 'memo://active', 'name': 'Active Note', 'mimeType': 'text/plain'}]}
Prompts: {'prompts': [{'name': 'summarize', 'description': 'Summarize a document', 'arguments': [{'name': 'doc', 'required': True}]}]}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- `resources/list` catalog output
- `resources/read` payload retrieval and MIME typing
- URI not found error handling
- `prompts/list` discovery output
- `prompts/get` parameter interpolation and message array formatting

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify resource URIs follow valid RFC 3986 format.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic URI pattern matching for templated resources.

## Navigation
Day number: 298 of 365
