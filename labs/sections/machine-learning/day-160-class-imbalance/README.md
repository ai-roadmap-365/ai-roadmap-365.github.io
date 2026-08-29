# Lab 160: Class Imbalance Strategies and SMOTE from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Class Imbalance
- **Day number:** 160 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-160-class-imbalance
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-160-class-imbalance` when the site is running.
<!-- generated-links:end -->

## Purpose
Master techniques for handling severe class imbalance: compute balanced class weights, implement random undersampling and oversampling, build the SMOTE (Synthetic Minority Over-sampling Technique) algorithm from scratch, and evaluate performance using Precision, Recall, and PR AUC.

## Learning objectives
1. Derive and compute balanced class weights inversely proportional to class frequencies.
2. Implement random undersampling of the majority class and random oversampling of the minority class.
3. Build the SMOTE algorithm using k-NN distance matrices and linear segment interpolation.
4. Compare algorithm-level cost-weighting against data-level resampling strategies.
5. Demonstrate why resampling must never occur prior to train-test splitting to prevent data leakage.

## Prerequisites
- k-Nearest Neighbors and distance matrices (Day 157).
- Classification evaluation metrics: Precision, Recall, PR AUC (Day 159).
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
day-160-class-imbalance/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── imbalance_lib.py
│   └── test_imbalance_lib.py
├── examples/
│   ├── imbalance_lib.py
│   └── test_imbalance_lib.py
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
python3 examples/imbalance_lib.py
```

## What the commands do
- `compute_balanced_weights(y)` computes class penalty multipliers.
- `random_undersample(X, y)` balances dataset by majority trimming.
- `random_oversample(X, y)` balances dataset by minority duplication.
- `smote_synthetic_points(X_min, n_samples)` synthesizes new minority points.

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
1. Implement Borderline-SMOTE, which generates synthetic samples only from minority instances near the decision boundary.
2. Implement Tomek Links to clean overlapping noisy pairs from resampled datasets.
3. Compare cost-sensitive Logistic Regression with Focal Loss on a 1:1,000 imbalanced fraud dataset.

## Navigation
- Previous lab: `../day-159-precision-recall-roc-and-choosing-thresholds/`
- Next lab: `../day-161-a-complete-classification-project/`
