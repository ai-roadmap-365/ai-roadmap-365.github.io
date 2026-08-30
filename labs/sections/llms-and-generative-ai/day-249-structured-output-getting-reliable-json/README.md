# Lab: Day 249 -- Structured Output: Getting Reliable JSON

## Lesson
Day number: 249 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Structured Output, JSON Generation, and Constrained CFG Decoding.

## Purpose
Build and test a type-safe JSON extraction and auto-repair engine in Python. Sanitize markdown code fences and conversational preambles, repair trailing commas and unclosed brackets, and validate schemas.

## Learning objectives
- Implement regex and AST sanitization for raw LLM JSON responses.
- Auto-repair trailing commas and truncated closing brackets.
- Validate required schema keys against strict contracts.
- Understand the mechanics of Constrained Grammar FSM logit masking.

## Prerequisites
- Day 248 (Few-Shot Examples and Chain of Thought).
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
Python standard json and regex modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/structured_output_getting_reliable_json_lib.py`: Student scaffold file.
- `examples/structured_output_getting_reliable_json_lib.py`: Complete reference implementation.
- `tests/test_structured_output_getting_reliable_json_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/structured_output_getting_reliable_json_lib.py
```

## What the commands do
- Cleans conversational preambles and markdown fences.
- Auto-repairs truncated JSON strings.
- Runs unit test assertions.

## Expected output
```
JSON Demo Extracted Successfully: INC-101
```

## Validation steps
1. Verify `clean_json_string` removes markdown code fences.
2. Confirm trailing comma regex fixes trailing commas.
3. Validate missing key detection raises `KeyError`.
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
- **No JSON delimiter:** Ensure the raw input contains at least one object or array opening delimiter.

## Security notes
Never use `eval()` to parse untrusted model outputs.

## Extension exercises
1. Implement a nested Pydantic V2 validator with custom regex validators.
2. Build an FSM-based logit masking simulator for token vocabularies.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Structured Output: Getting Reliable JSON
- **Day number:** 249 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-249-structured-output-getting-reliable-json
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-249-structured-output-getting-reliable-json` when the site is running.
<!-- generated-links:end -->
