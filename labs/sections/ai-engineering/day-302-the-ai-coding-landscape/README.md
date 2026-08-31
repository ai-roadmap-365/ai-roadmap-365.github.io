# Day 302 Lab: The AI Coding Landscape

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The AI Coding Landscape
- **Day number:** 302 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-302-the-ai-coding-landscape
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-302-the-ai-coding-landscape` when the site is running.
<!-- generated-links:end -->

## Purpose
Construct an AI Coding Agent Engine in Python featuring AST-based repository mapping, targeted search-and-replace patch application, and automated test verification.

## Learning objectives
- Build an AST-based repository structure generator.
- Implement targeted search-and-replace file patch application.
- Execute automated test verification harnesses and capture stdout/stderr diagnostics.
- Handle missing files, target mismatches, and syntax validation.

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
- `starter/coding_agent_engine.py`: Starter implementation skeleton
- `examples/coding_agent_engine.py`: Verified reference implementation
- `tests/test_coding_agent.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/coding_agent_engine.py
```

## What the commands do
- Generates repository structural map, applies search-and-replace patches, and runs test harness.

## Expected output
```text
Repo map preview:
 File: starter/coding_agent_engine.py
  class CodingAgentEngine:
  def __init__(self, workspace_root: str):
  def generate_repo_map(self) -> str:
  def apply_search_replace(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
  def run_verification_tests(self, test_command: str = "python3 -m unittest discover") -> Dict[str, Any]:
File: examples/coding_agent_engine.py
  class CodingAgentEngine:
  def __init__(self, workspace_root: str):
  def generate_repo_map(self) -> str:
  def apply_search_replace(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
  def run_verification_tests(self, test_command: str = "python3 -m unittest discover") -> Dict[str, Any]:
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Repo map generation and class/def symbol extraction
- Successful search-and-replace patch modification
- Missing file and search block mismatch error handling
- Subprocess test execution and stdout/stderr capture

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure workspace root is a valid directory path.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add unified diff parsing support.

## Navigation
Day number: 302 of 365
