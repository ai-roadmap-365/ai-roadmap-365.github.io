# Lab: Day 191 -- Building Datasets and Labeling

## Lesson
Day number: 191 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Data Curation, Active Learning, and Weak Supervision.

## Purpose
Build a complete data curation and programmatic labeling engine in pure NumPy and Python. You will implement Shannon Entropy uncertainty sampling for active learning, calculate Cohen's Kappa inter-annotator agreement, and aggregate multi-heuristic Labeling Functions via majority voting.

## Learning objectives
- Implement Shannon entropy uncertainty calculations.
- Calculate chance-corrected Cohen's Kappa agreement coefficients.
- Build majority vote consensus aggregators for programmatic weak supervision.
- Evaluate annotation reliability and label coverage.

## Prerequisites
- Probability: Shannon entropy and probability distributions.
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
- `starter/building_datasets_and_labeling_lib.py`: Student scaffold file.
- `examples/building_datasets_and_labeling_lib.py`: Complete reference implementation.
- `tests/test_building_datasets_and_labeling_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/building_datasets_and_labeling_lib.py
```

## What the commands do
- Evaluates prediction entropy on sample probabilities.
- Computes maximum uncertainty scores.
- Logs entropy values.

## Expected output
```
Data Engine Demo: Max Entropy = 0.9997
```

## Validation steps
1. Check that 50/50 binary probabilities output an entropy of 1.0.
2. Verify that identical rating vectors yield a Cohen Kappa of 1.0.
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
- **Log Domain Error:** Ensure probabilities are clipped with `1e-12` prior to logarithm computation.

## Security notes
All computations execute locally without external network transmission.

## Extension exercises
1. Implement **Margin Sampling** and **Least Confident** active learning strategies.
2. Build an automated label error detector using Confident Learning.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building Datasets and Labeling
- **Day number:** 191 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-191-building-datasets-and-labeling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-191-building-datasets-and-labeling` when the site is running.
<!-- generated-links:end -->
