# Lab: Day 194 -- Serving a Model over an API

## Lesson
Day number: 194 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: FastAPI Microservice Serving, Pydantic Schema Contracts, and Circuit Breakers.

## Purpose
Build a complete, low-latency REST Model Serving Engine in pure Python and NumPy. You will implement preloaded in-memory model execution, Pydantic-style feature boundary validation, vectorized batch inference, Kubernetes health probes, and automated fallback circuit breakers.

## Learning objectives
- Architect preloaded in-memory model inference services.
- Enforce schema contracts with strict type and boundary validations.
- Implement single-item and vectorized batch prediction endpoints.
- Build Kubernetes-compatible liveness and readiness health probes.
- Guarantee uptime via automated fallback circuit breakers.

## Prerequisites
- Linear models (logistic sigmoid activation).
- Python 3.11+ dataclasses and NumPy.

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
- `starter/serving_a_model_over_an_api_lib.py`: Student scaffold file.
- `examples/serving_a_model_over_an_api_lib.py`: Complete reference implementation.
- `tests/test_serving_a_model_over_an_api_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/serving_a_model_over_an_api_lib.py
```

## What the commands do
- Initializes the serving engine and preloads model weights.
- Executes single-item prediction with latency profiling.
- Evaluates output probabilities and fallback states.

## Expected output
```
Serving Demo: Churn Probability = 0.7042, Latency = 0.042ms
```

## Validation steps
1. Check that predictions before `load_model()` raise a RuntimeError.
2. Verify that negative feature values raise a ValueError.
3. Ensure all unit test assertions pass.

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
- **Unloaded Model Error:** Ensure `load_model()` is executed prior to calling inference methods.

## Security notes
All computations execute locally in memory without external network transmission.

## Extension exercises
1. Implement a **Dynamic Batching Queue** that flushes after 10ms or 32 items.
2. Build an automated Prometheus latency counter exporter.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Serving a Model over an API
- **Day number:** 194 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-194-serving-a-model-over-an-api
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-194-serving-a-model-over-an-api` when the site is running.
<!-- generated-links:end -->
