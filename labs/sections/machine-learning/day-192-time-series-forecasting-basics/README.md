# Lab: Day 192 -- Time Series Forecasting Basics

## Lesson
Day number: 192 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Time Series Forecasting and Temporal Feature Engineering.

## Purpose
Build a complete temporal feature engineering and walk-forward cross-validation engine in pure NumPy. You will implement autoregressive lag extraction, rolling window moving statistics without lookahead bias, symmetric MAPE evaluation, and expanding window temporal splits.

## Learning objectives
- Transform sequential time series into tabular lag matrices.
- Compute rolling window statistics strictly on past intervals.
- Implement walk-forward expanding window cross-validation.
- Evaluate forecasting accuracy using sMAPE and MAE.

## Prerequisites
- Sequential data arrays and time-series concepts.
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
- `starter/time_series_forecasting_basics_lib.py`: Student scaffold file.
- `examples/time_series_forecasting_basics_lib.py`: Complete reference implementation.
- `tests/test_time_series_forecasting_basics_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/time_series_forecasting_basics_lib.py
```

## What the commands do
- Generates a synthetic daily time-series with trend and weekly seasonality.
- Extracts lag features and rolling statistics.
- Executes walk-forward temporal splitting.

## Expected output
```
Forecasting Demo: Features Shape (93, 4), Walk-Forward Splits Count = 3
```

## Validation steps
1. Check that train indices strictly precede test indices in every split.
2. Verify that rolling statistics exclude current step `t`.
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
- **Index Out of Bounds:** Ensure `max_lag` considers both lag offsets and rolling window widths.

## Security notes
All calculations execute locally without external network transmission.

## Extension exercises
1. Implement **Cyclical Sine/Cosine Encodings** for day of week.
2. Benchmark against an **ARIMA(1,1,1)** statistical baseline.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Time Series Forecasting Basics
- **Day number:** 192 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-192-time-series-forecasting-basics
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-192-time-series-forecasting-basics` when the site is running.
<!-- generated-links:end -->
