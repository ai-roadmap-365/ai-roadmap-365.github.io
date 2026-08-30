# Day 277 Lab: Running Local Models with Ollama

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Running Local Models with Ollama
- **Day number:** 277 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-277-running-local-models-with-ollama
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-277-running-local-models-with-ollama` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Ollama Modelfile generator, mock streaming REST server, and client library in Python to simulate local LLM lifecycle operations and NDJSON token streaming.

## Learning objectives
- Generate declarative Modelfiles with `FROM`, `PARAMETER`, and `SYSTEM` blocks.
- Simulate Ollama REST API endpoints (`/api/tags`, `/api/generate`).
- Parse chunked NDJSON streaming responses in Python.

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
- Python Standard Library

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/ollama_client.py`: Starter implementation
- `examples/ollama_client.py`: Verified reference implementation
- `tests/test_ollama_client.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/ollama_client.py
```

## What the commands do
- Compiles Modelfile configurations and streams simulated tokens through the client.

## Expected output
```text
[MODELFILE] Compiled Modelfile for 'custom-sql'
[STREAMING] Emitted 6 tokens | Duration: 120ms
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Modelfile string generation and parsing round-trips
- Tags endpoint response formatting
- Streaming NDJSON chunk parsing
- Error raising when requested models are absent

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify Modelfile parameter casting parses integers and floats accurately.

## Security notes
Zero external network transmission. Runs entirely locally on CPU.

## Extension exercises
Add support for simulating `/api/chat` multi-turn message history.

## Navigation
Day number: 277 of 365
