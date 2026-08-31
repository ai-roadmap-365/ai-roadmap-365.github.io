# Day 314 Lab: Observability and Tracing for AI

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Observability and Tracing for AI
- **Day number:** 314 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-314-observability-and-tracing-for-ai
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-314-observability-and-tracing-for-ai` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an OpenInference-Compatible AI Tracing and Telemetry Engine in Python supporting hierarchical span trees, duration timing, token accounting, and JSON trace export.

## Learning objectives
- Implement hierarchical span management with parent-child relationships.
- Measure elapsed execution duration for operations.
- Calculate token usage and financial cost attribution.
- Export nested JSON trace trees for observability backends.

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
- `starter/tracing_engine.py`: Starter implementation skeleton
- `examples/tracing_engine.py`: Verified reference implementation
- `tests/test_tracing_engine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/tracing_engine.py
```

## What the commands do
- Executes span creation, token cost calculations, and trace exports.

## Expected output
```text
Trace Root: {'span_id': '09571464', 'parent_id': None, 'name': 'Test_Trace', 'kind': 'ROOT', 'duration_ms': 0.0, 'attributes': {}, 'children': []}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Root span creation and termination
- Nested child span relationships and attributes
- Duration timing (> 0.0 ms)
- Accurate token cost calculations
- JSON serialization of the full span tree

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Remember to invoke `.finish()` on spans to record durations.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add Time to First Token (TTFT) tracking attributes.

## Navigation
Day number: 314 of 365
