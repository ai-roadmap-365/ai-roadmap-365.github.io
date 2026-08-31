# Day 357 Lab: Milestone Review and Course Correction

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Milestone Review and Course Correction
- **Day number:** 357 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-357-milestone-review-and-course-correction
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-357-milestone-review-and-course-correction` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Capstone Milestone 1 Audit Engine in Python that profiles component latency budgets, verifies evaluation metrics, and certifies the working vertical slice for production shipping.

## Learning objectives
- Profile end-to-end vertical slice execution latencies.
- Break down latency budgets by architectural component.
- Audit evaluation accuracy metrics against quality thresholds.
- Generate automated Milestone 1 approval reports.

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
- `starter/audit.py`: Starter implementation skeleton
- `examples/audit.py`: Verified reference implementation
- `tests/test_audit.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/audit.py
```

## What the commands do
- Profiles pipeline latency and verifies milestone quality criteria.

## Expected output
```text
{'milestone': 'CAPSTONE_MILESTONE_1', 'overall_status': 'APPROVED', 'checks': {'latency_budget': 'PASS', 'faithfulness_accuracy': 'PASS', 'schema_integrity': 'PASS'}, 'metrics': {'measured_latency_ms': 0.0, 'faithfulness_score': 0.95}}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Vertical slice latency profiling
- Latency budget compliance (<1,500ms)
- Accuracy metric threshold audit
- Schema validity checks
- Milestone approval vs rejection logic

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure pipeline return values match expected dictionary formats.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Add memory allocation profiling via `tracemalloc`.

## Navigation
Day number: 357 of 365
