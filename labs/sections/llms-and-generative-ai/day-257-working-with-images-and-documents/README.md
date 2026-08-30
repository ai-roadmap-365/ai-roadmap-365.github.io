# Lab: Day 257 -- Working with Images and Documents

## Lesson
Day number: 257 of 365.
Course: Course06-SS02 (LLMs and Generative AI - LLM APIs).
Topic: Working with Images and Documents, Base64 Payloads, and Vision Token Economics.

## Purpose
Build and test a Multimodal Document Analysis Engine in Python. Formulate Base64-encoded image and PDF payloads, validate media types, and compute vision tile token costs.

## Learning objectives
- Encode image files into Base64 ASCII strings.
- Structure multimodal message arrays matching standard schemas.
- Calculate vision token costs across resolution detail modes.
- Implement media validation guardrails.

## Prerequisites
- Day 256 (Tool Use and Function Calling).
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
Python and standard base64/math modules are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/working_with_images_and_documents_lib.py`: Student scaffold file.
- `examples/working_with_images_and_documents_lib.py`: Complete reference implementation.
- `tests/test_working_with_images_and_documents_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/working_with_images_and_documents_lib.py
```

## What the commands do
- Constructs Base64 image payload.
- Calculates vision token costs.
- Runs unit test assertions.

## Expected output
```
Multimodal Demo Executed. Tokens: 765
```

## Validation steps
1. Verify payload construction includes image and prompt blocks.
2. Confirm unsupported media types raise ValueError.
3. Validate low-detail returns fixed 85 tokens.
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
- **Invalid media type error:** Use standard MIME types (e.g. `image/jpeg`).

## Security notes
Base64 payload processing executes locally in memory.

## Extension exercises
1. Build an automated receipt expense parser with Pydantic.
2. Implement automated client-side image downscaling.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Working with Images and Documents
- **Day number:** 257 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-257-working-with-images-and-documents
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-257-working-with-images-and-documents` when the site is running.
<!-- generated-links:end -->
