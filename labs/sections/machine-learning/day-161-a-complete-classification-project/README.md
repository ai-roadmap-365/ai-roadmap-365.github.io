# Lab 161: A Complete Classification Project

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Complete Classification Project
- **Day number:** 161 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-161-a-complete-classification-project
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-161-a-complete-classification-project` when the site is running.
<!-- generated-links:end -->

## Purpose
Build, validate, benchmark, and deploy an end-to-end production-grade classification project pipeline integrating feature preprocessing, Stratified 5-Fold Cross-Validation across candidate models, cost-sensitive threshold calibration, and gated single test-set sign-off.

## Learning objectives
1. Structure a modular, production-ready classification engineering pipeline.
2. Prevent feature scaling leakage and target distribution shifts using Stratified splitting.
3. Benchmark diverse model families (Logistic Regression, KNN, Naive Bayes) under identical cross-validation folds.
4. Optimize operating decision thresholds using asymmetric validation cost functions.
5. Perform a single, uncompromised test set evaluation with comprehensive metric reporting.

## Prerequisites
- Weeks 23 fundamentals: Logistic Regression, Decision Boundaries, KNN, Naive Bayes, Metrics, and Class Imbalance (Days 155-160).
- Python classes and object-oriented architecture.
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
day-161-a-complete-classification-project/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── project_lib.py
│   └── test_project_lib.py
├── examples/
│   ├── project_lib.py
│   └── test_project_lib.py
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
python3 examples/project_lib.py
```

## What the commands do
- `fit_and_select(X_train, y_train)` runs Stratified 5-Fold CV model benchmarking.
- `calibrate_threshold(X_val, y_val)` finds the cost-optimal decision threshold.
- `evaluate_test(X_test, y_test)` runs the gated single final evaluation.

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
1. Export the fitted pipeline to disk using `joblib` and build a lightweight FastAPI inference endpoint.
2. Integrate SMOTE into training folds using `imblearn.pipeline.Pipeline`.
3. Add hyperparameter grid search for regularized logistic regression penalties.

## Navigation
- Previous lab: `../day-160-class-imbalance/`
- Next lab: `../day-162-decision-trees-and-how-they-split/`
