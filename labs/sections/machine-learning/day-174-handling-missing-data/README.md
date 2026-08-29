# Lab 174: Missing Data Imputation and NaN-Euclidean Metrics from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Handling Missing Data
- **Day number:** 174 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-174-handling-missing-data
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-174-handling-missing-data` when the site is running.
<!-- generated-links:end -->

## Purpose
Master the statistical principles and algorithmic mechanics of handling missing data: implement NaN-aware Euclidean distance metrics, MissingIndicator feature flags, and distance-weighted KNNImputer from scratch.

## Learning objectives
1. Classify missing data mechanisms into MCAR, MAR, and MNAR (Donald Rubin, 1976).
2. Formulate and implement the NaN-Euclidean distance metric with dimension scaling.
3. Implement `generate_missing_indicator` to capture informative missingness signals.
4. Implement `KNNImputer` from scratch to reconstruct multi-column missing values.
5. Contrast SimpleImputer, KNNImputer, IterativeImputer (MICE), and native GBDT tree branching.

## Prerequisites
- Feature scaling and encoding (Day 170).
- Scikit-Learn Pipelines (Day 173).
- Python 3.11+ virtual environment.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (x86_64, aarch64)
- Windows (WSL2 / native PowerShell)

## Hardware requirements
- CPU: 1 core
- Memory: 512 MB RAM
- Disk: 50 MB for virtual environment

## Required software
- Python 3.11 or newer
- Virtual environment (`venv`)

## Free and open-source options
- Python standard library + NumPy / scikit-learn (free, open source).

## Installation
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## File structure
```
day-174-handling-missing-data/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── imputation_lib.py
│   └── test_imputation_lib.py
├── examples/
│   ├── imputation_lib.py
│   └── test_imputation_lib.py
├── tests/
│   └── run_tests.sh
├── expected-output/
│   ├── FIELDS.md
│   ├── measured-values.txt
│   ├── test-run.txt
│   ├── examples-run.txt
│   └── starter-run.txt
├── troubleshooting.md
└── security.md
```

## How to run
Run the reference implementation:
```bash
python3 examples/imputation_lib.py
```

## What the commands do
- `compute_nan_euclidean_distance(...)` calculates NaN-scaled Euclidean distance.
- `generate_missing_indicator(...)` creates boolean missingness feature flags.
- `knn_imputer_scratch(...)` imputes missing values using k-nearest neighbors.

## Expected output
See `expected-output/test-run.txt` and `expected-output/measured-values.txt`.

## Validation steps
Execute the full test harness:
```bash
./tests/run_tests.sh
```

## Tests
Run pytest on the reference implementation:
```bash
pytest examples -v
```

## Cleanup
```bash
rm -rf .venv __pycache__ .pytest_cache
```

## Troubleshooting
Refer to [troubleshooting.md](troubleshooting.md).

## Security notes
Refer to [security.md](security.md).

## Extension exercises
1. Implement IterativeImputer (MICE / Chained Equations) using Bayesian Ridge regression round-robin cycles.
2. Benchmark LightGBM native NaN handling vs SimpleImputer + MissingIndicator on synthetic MAR data.
3. Build a soft-impute matrix factorization algorithm using SVD thresholding for sparse recommendation matrices.

## Navigation
- Previous lab: `../day-173-scikit-learn-pipelines/`
- Next lab: `../day-175-features-beat-algorithms/`
