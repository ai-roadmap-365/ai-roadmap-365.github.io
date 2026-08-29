# Lab: Day 185 -- Principal Component Analysis

## Lesson
Day number: 185 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Principal Component Analysis and Linear Dimensionality Reduction.

## Purpose
Build a complete, pure NumPy implementation of Principal Component Analysis from scratch using Singular Value Decomposition (SVD). You will implement data mean centering, singular vector extraction, explained variance ratio calculation, projection transformations, and inverse reconstruction.

## Learning objectives
- Implement zero-mean data centering and economy SVD.
- Derive covariance eigenvalues from SVD singular values.
- Calculate Explained Variance Ratios and cumulative variance profiles.
- Transform high-dimensional data onto orthogonal principal axes and invert projections.

## Prerequisites
- Linear algebra: Matrix multiplication, orthogonal matrices, SVD factorizations.
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
- `starter/principal_component_analysis_lib.py`: Student scaffold file.
- `examples/principal_component_analysis_lib.py`: Complete reference implementation.
- `tests/test_principal_component_analysis_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/principal_component_analysis_lib.py
```

## What the commands do
- Generates a synthetic 5D dataset with correlated feature dimensions.
- Fits `PCAFromScratch` to compress data from 5D to 2D.
- Reconstructs original coordinates and computes Mean Squared Error.

## Expected output
```
PCA Demo: Input Shape (200, 5) -> Reduced (200, 2), Reconstruction MSE = 0.142
```

## Validation steps
1. Verify that `components_` vectors are orthonormal (V^T V = I).
2. Check that `explained_variance_ratio_` sums to <= 1.0.
3. Verify that retaining all components yields near-zero reconstruction MSE (< 1e-5).

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
- **Reconstruction Bias:** Ensure `self.mean_` is added back during `inverse_transform()`.

## Security notes
All computations execute strictly on local CPU memory.

## Extension exercises
1. Implement **Whitening** and verify that transformed features have identity covariance.
2. Build an automated **Scree Plot** generator in matplotlib.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Principal Component Analysis
- **Day number:** 185 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-185-principal-component-analysis
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-185-principal-component-analysis` when the site is running.
<!-- generated-links:end -->
