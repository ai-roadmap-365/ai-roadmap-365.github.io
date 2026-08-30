# Day 318 Lab: Chat UX and Streaming Frontends

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Chat UX and Streaming Frontends
- **Day number:** 318 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-318-chat-ux-and-streaming-frontends
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-318-chat-ux-and-streaming-frontends` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Chat Stream Frontend State Engine in Python supporting optimistic message appending, token stream aggregation, smart auto-scroll physics, and stream cancellation.

## Learning objectives
- Implement optimistic user message rendering.
- Aggregate streaming token chunks into assistant messages.
- Manage smart auto-scroll state based on viewport position.
- Handle user abort cancellations with partial completion retention.

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
- `starter/chat_stream_frontend.py`: Starter implementation skeleton
- `examples/chat_stream_frontend.py`: Verified reference implementation
- `tests/test_chat_stream_frontend.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/chat_stream_frontend.py
```

## What the commands do
- Simulates chat frontend user actions, streaming token delivery, scrolling, and aborting.

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
- Optimistic user message creation
- Progressive token chunk accumulation
- Smart auto-scroll sticking vs locking
- Abort cancellation preserving partial text
- Clean stream completion state

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify viewport distance <= 50.0 triggers sticky scrolling.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add code block extraction for copy-to-clipboard buttons.

## Navigation
Day number: 318 of 365
