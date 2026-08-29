# Lab: Day 187 -- Anomaly Detection

## Lesson
Day number: 187 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Anomaly Detection and Isolation Forests.

## Purpose
Build a complete, pure NumPy implementation of the Isolation Forest algorithm from scratch. You will implement random axis-aligned partition trees, compute the theoretical BST average path length normalization factor c(n), calculate exponential anomaly scores, and calibrate contamination percentiles.

## Learning objectives
- Implement recursive randomized spatial partitioning trees.
- Derive and implement the Euler-Mascheroni BST normalization constant c(n).
- Compute average path lengths h(x) across tree ensembles.
- Calculate continuous anomaly scores and assign binary outlier predictions.

## Prerequisites
- Data structures: Recursive binary trees and path length traversal.
- Probability: Uniform split thresholding and random feature selection.
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
All tools used in this lab (Python, NumPy, pytest, scikit-learn) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/anomaly_detection_lib.py`: Student scaffold file.
- `examples/anomaly_detection_lib.py`: Complete reference implementation.
- `tests/test_anomaly_detection_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/anomaly_detection_lib.py
```

## What the commands do
- Generates 300 nominal 2D Gaussian inliers and 15 uniform spatial outliers.
- Fits `IsolationForestFromScratch` with 50 trees and max_samples=128.
- Logs the mean anomaly score for inliers vs outliers.

## Expected output
```
Anomaly Demo: Inlier Mean Score = 0.3912, Outlier Mean Score = 0.7645
```

## Validation steps
1. Check that `c_factor(1) == 0.0` and `c_factor(2) == 1.0`.
2. Verify that outliers have significantly higher anomaly scores than inliers (> 0.6).
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
- **Recursion Limit Exceeded:** Check `min_val == max_val` to terminate node splits early.

## Security notes
All computations execute strictly on local CPU memory without network transmission.

## Extension exercises
1. Implement **Extended Isolation Forest (EIF)** with random hyperplane cuts.
2. Benchmark against **Local Outlier Factor (LOF)** on multi-density clusters.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Anomaly Detection
- **Day number:** 187 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-187-anomaly-detection
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-187-anomaly-detection` when the site is running.
<!-- generated-links:end -->
