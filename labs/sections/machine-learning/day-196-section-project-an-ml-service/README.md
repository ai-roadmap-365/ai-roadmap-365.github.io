# Lab: Day 196 -- Section Project: An ML Service

## Lesson
Day number: 196 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Section Project: An End-to-End Deployed ML Service.

## Purpose
Build a complete, integrated production machine learning service combining model registration, SHA-256 provenance tracking, low-latency REST inference with Pydantic-style contracts, fallback circuit breakers, and real-time Population Stability Index (PSI) drift monitoring in pure Python and NumPy.

## Learning objectives
- Synthesize all Course 04 machine learning foundations into a unified production architecture.
- Enforce cryptographic SHA-256 checksum validation for registered model artifacts.
- Implement sub-10ms REST prediction endpoints with circuit-breaker error fallbacks.
- Build automated Population Stability Index (PSI) data drift observability monitors.

## Prerequisites
- Completion of Days 190 to 195.
- Python 3.11+ with NumPy.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
All tools used in this lab (Python, NumPy, pytest) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/section_project_an_ml_service_lib.py`: Student scaffold file.
- `examples/section_project_an_ml_service_lib.py`: Complete reference implementation.
- `tests/test_section_project_an_ml_service_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/section_project_an_ml_service_lib.py
```

## What the commands do
- Registers and promotes model artifact `churn_service:v1.0.0`.
- Executes single prediction and measures inference latency.
- Evaluates PSI drift on live streaming feature batches.

## Expected output
```
Capstone Demo: Churn Prob = 0.7311, Drift Status = STABLE (PSI: 0.0124)
```

## Validation steps
1. Verify that model registration computes a 64-character SHA-256 hash.
2. Check that predictions execute in under 10ms with valid probability bounds.
3. Verify that shifted data streams trigger SIGNIFICANT_DRIFT (PSI &ge; 0.20).
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
- **Unregistered Model Error:** Ensure `register_and_promote()` is executed prior to calling service inference.

## Security notes
All operations execute locally in memory without external network transmission.

## Extension exercises
1. Implement **Canary Routing** across champion and candidate versions.
2. Build an automated Model Card markdown generator.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Project: An ML Service
- **Day number:** 196 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-196-section-project-an-ml-service
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-196-section-project-an-ml-service` when the site is running.
<!-- generated-links:end -->
