# Day 178 Lab: Interpreting Models: Importances and SHAP

Day number: 178 of 365.

## Lesson
Covering `day-178-interpreting-models-importances-and-shap`.

## Purpose
Master mdi gini flaws, permutation importance, exact shapley values, treeshap, and partial dependence / ice curves. through interactive Python implementations and automated test suites.

## Learning objectives
- Implement core mathematical algorithms for interpreting models: importances and shap.
- Benchmark models against rigorous baselines.
- Execute automated unit and integration tests.
- Analyze failure modes and edge cases.

## Prerequisites
- Python 3.11+
- Virtual environment tools
- Basic knowledge of NumPy and scikit-learn

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu 22.04+, Debian, Fedora, Arch)
- Windows (WSL2 recommended)

## Hardware requirements
- CPU: 2+ physical cores (Apple M-series or Intel/AMD x86_64)
- RAM: 4GB minimum, 8GB recommended
- Disk: 500MB free space

## Required software
- Python 3.11 or higher
- Git
- Bash shell

## Free and open-source options
- Python: [python.org](https://python.org) (PSFL)
- scikit-learn: BSD 3-Clause
- pytest: MIT License

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/`: Scaffolded implementation files for student completion.
- `examples/`: Fully functional reference library implementation.
- `tests/`: Pytest suite and shell validation runners.
- `expected-output/`: Captured reference terminal logs.
- `requirements/`: Python package dependency specifications.
- `troubleshooting.md`: Common runtime failure solutions.
- `security.md`: Local execution safety guidance.

## How to run
```bash
python3 examples/interpreting_models_importances_and_shap_lib.py
```

## What the commands do
- Executes reference implementation demonstration and benchmarks.

## Expected output
Reference logs are captured in `expected-output/run-output.txt` and `expected-output/test-output.txt`.

## Validation steps
1. Run `./tests/run_tests.sh`.
2. Ensure exit code is 0.

## Tests
```bash
pytest tests/ -v
```

## Cleanup
```bash
rm -rf .venv __pycache__ .pytest_cache
```

## Troubleshooting
Refer to `troubleshooting.md` for common import or version issues.

## Security notes
Refer to `security.md` for isolation and data safety guidance.

## Extension exercises
- Test on imbalanced real-world datasets.
- Profile runtime latency and memory utilization.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Interpreting Models: Importances and SHAP
- **Day number:** 178 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-178-interpreting-models-importances-and-shap
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-178-interpreting-models-importances-and-shap` when the site is running.
<!-- generated-links:end -->
