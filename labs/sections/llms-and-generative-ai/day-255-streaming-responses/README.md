# Lab: Day 255 -- Streaming Responses

## Lesson
Day number: 255 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Streaming Responses, Server-Sent Events, and Latency Telemetry.

## Purpose
Build and test a Streaming Token Aggregator and Latency Monitor in Python. Consume incremental token deltas, calculate Time-To-First-Token (TTFT) and Inter-Token Latency (ITL), and aggregate complete response payloads.

## Learning objectives
- Process streaming token chunks from generators and async streams.
- Calculate Time-To-First-Token (TTFT) and Inter-Token Latency (ITL).
- Aggregate streaming chunks into full textual responses.
- Implement real-time terminal output rendering.

## Prerequisites
- Day 254 (The OpenAI-Compatible Ecosystem).
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
Python and standard time/typing modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/streaming_responses_lib.py`: Student scaffold file.
- `examples/streaming_responses_lib.py`: Complete reference implementation.
- `tests/test_streaming_responses_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/streaming_responses_lib.py
```

## What the commands do
- Initiates simulated token stream.
- Accumulates token deltas and calculates TTFT.
- Runs unit test assertions.

## Expected output
```
Streaming Demo Executed. Text: Real-time streaming slashes perceived latency drastically.
```

## Validation steps
1. Verify TTFT is recorded upon receiving chunk 1.
2. Confirm aggregated text matches all yielded deltas.
3. Validate ITL computation across streamed chunks.
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
- **Zero token count:** Ensure process_chunk is called for each emitted token.

## Security notes
Streaming tokens are processed strictly in local memory.

## Extension exercises
1. Implement an async generator stream in FastAPI.
2. Build a live words-per-second terminal speedometer.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Streaming Responses
- **Day number:** 255 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-255-streaming-responses
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-255-streaming-responses` when the site is running.
<!-- generated-links:end -->
