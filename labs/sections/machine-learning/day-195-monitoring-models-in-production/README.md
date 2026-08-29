# Lab: Day 195 -- Monitoring Models in Production

## Lesson
Day number: 195 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Production Model Monitoring, Data Drift, and Population Stability Index (PSI).

## Purpose
Build a complete, automated Population Stability Index (PSI) drift detection engine in pure Python and NumPy. You will implement quantile reference binning, calculate actual vs expected frequency divergences, classify statistical drift thresholds, and trigger automated retraining alerts.

## Learning objectives
- Formulate and compute Population Stability Index (PSI) using quantile binning.
- Classify distribution stability into STABLE, MODERATE_DRIFT, and SIGNIFICANT_DRIFT.
- Implement smoothing epsilons to prevent division-by-zero on empty bins.
- Build automated drift monitoring alert pipelines.

## Prerequisites
- Statistical distributions (means, standard deviations, percentiles).
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
- `starter/monitoring_models_in_production_lib.py`: Student scaffold file.
- `examples/monitoring_models_in_production_lib.py`: Complete reference implementation.
- `tests/test_monitoring_models_in_production_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/monitoring_models_in_production_lib.py
```

## What the commands do
- Evaluates PSI on stable vs shifted synthetic feature streams.
- Classifies drift levels against industry thresholds.
- Outputs diagnostic drift metrics.

## Expected output
```
Monitoring Demo: Stable PSI = 0.0142 (STABLE), Drifted PSI = 0.4285 (SIGNIFICANT_DRIFT)
```

## Validation steps
1. Check that identical distributions output a PSI &lt; 0.05.
2. Verify that severely shifted distributions output PSI &ge; 0.20.
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
- **Infinity / NaN Output:** Ensure `epsilon` is added to bin frequency counts before computing logarithms.

## Security notes
All drift calculations execute locally without external network transmission.

## Extension exercises
1. Implement a **Multi-Column Drift Scanner** across 10 tabular features.
2. Integrate with **scipy.stats.ks_2samp** for Kolmogorov-Smirnov p-value testing.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Monitoring Models in Production
- **Day number:** 195 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-195-monitoring-models-in-production
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-195-monitoring-models-in-production` when the site is running.
<!-- generated-links:end -->
