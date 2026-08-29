# Lab: Day 190 -- The ML Project Lifecycle

## Lesson
Day number: 190 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Machine Learning Project Lifecycle and Deployment Quality Gates.

## Purpose
Build a complete, automated deployment quality gate engine in pure Python. You will implement statistical superiority checks, cohort slice regression guards, operational latency/memory SLA validations, and safety infrastructure checks before promoting candidate models to production traffic.

## Learning objectives
- Model the 6 phases of the production ML lifecycle.
- Formulate quantitative deployment readiness criteria.
- Enforce strict subgroup slicing checks to prevent demographic or cohort regression.
- Validate operational SLA bounds (p99 latency, container RAM) and circuit breaker readiness.

## Prerequisites
- Python 3.11+ data structures (`dataclasses`, dictionaries).
- Core understanding of classification metrics (PR-AUC, precision, recall).

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
All tools used in this lab (Python, pytest) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/the_ml_project_lifecycle_lib.py`: Student scaffold file.
- `examples/the_ml_project_lifecycle_lib.py`: Complete reference implementation.
- `tests/test_the_ml_project_lifecycle_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/the_ml_project_lifecycle_lib.py
```

## What the commands do
- Evaluates candidate model report `v1.1.0` against production champion `v1.0.0`.
- Executes the 4-quadrant quality gate checklist.
- Logs final canary promotion decision.

## Expected output
```
ML Lifecycle Demo: Candidate Passed All Gates = True
```

## Validation steps
1. Verify that overall PR-AUC improvement is &gt;= 0.015 (+1.5%).
2. Verify that no subgroup slice regresses by more than 0.02 (-2.0%).
3. Verify that p99 latency is within 20ms.
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
- **Missing Slice Key:** Ensure candidate dictionary includes all cohorts evaluated in champion report.

## Security notes
All computations execute locally without external network transmission.

## Extension exercises
1. Integrate **Expected Value Cost Matrix** calculation into decision rules.
2. Build an automated markdown Model Card audit generator.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The ML Project Lifecycle
- **Day number:** 190 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-190-the-ml-project-lifecycle
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-190-the-ml-project-lifecycle` when the site is running.
<!-- generated-links:end -->
