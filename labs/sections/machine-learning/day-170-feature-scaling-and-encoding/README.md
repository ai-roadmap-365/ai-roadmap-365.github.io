# Lab 170: Feature Scaling and Categorical Encoding from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Feature Scaling and Encoding
- **Day number:** 170 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-170-feature-scaling-and-encoding
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-170-feature-scaling-and-encoding` when the site is running.
<!-- generated-links:end -->

## Purpose
Build robust feature preprocessing transformations from scratch: implement StandardScaler, outlier-resilient RobustScaler, and leak-free Out-of-Fold Smoothed Target Encoding in pure NumPy.

## Learning objectives
1. Implement Z-Score Standardization (`StandardScaler`) with zero-mean and unit-variance.
2. Implement Median and Interquartile Range scaling (`RobustScaler`) for outlier robustness.
3. Formulate and implement leak-free Out-of-Fold Smoothed Target Encoding with Bayesian shrinkage.
4. Compare One-Hot Encoding, Ordinal Encoding, and Target Encoding trade-offs.
5. Benchmark model sensitivity to feature scaling across Linear Models, SVMs, and Decision Trees.

## Prerequisites
- Linear and Logistic Regression (Days 148–155).
- Cross-Validation fundamentals (Day 167).
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
day-170-feature-scaling-and-encoding/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── scaling_encoding_lib.py
│   └── test_scaling_encoding_lib.py
├── examples/
│   ├── scaling_encoding_lib.py
│   └── test_scaling_encoding_lib.py
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
python3 examples/scaling_encoding_lib.py
```

## What the commands do
- `StandardScalerScratch().fit_transform(X)` standardizes numerical features.
- `RobustScalerScratch().fit_transform(X)` robustly centers using median and IQR.
- `out_of_fold_target_encode(cats, y)` computes leak-free smoothed category stats.

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
1. Implement Box-Cox and Yeo-Johnson Power Transformers from scratch to normalize skewed distributions.
2. Implement CatBoost-style online ordered target encoding to eliminate out-of-fold permutation variance.
3. Build a sparse MaxAbsScaler for memory-efficient scaling of large TF-IDF matrices.

## Navigation
- Previous lab: `../day-169-support-vector-machines/`
- Next lab: `../day-171-feature-engineering/`
