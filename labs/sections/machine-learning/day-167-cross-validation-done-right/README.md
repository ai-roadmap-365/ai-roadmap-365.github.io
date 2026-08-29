# Lab 167: Cross-Validation Done Right

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cross-Validation Done Right
- **Day number:** 167 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-167-cross-validation-done-right
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-167-cross-validation-done-right` when the site is running.
<!-- generated-links:end -->

## Purpose
Build robust, leak-free cross-validation architectures from scratch in NumPy: implement Stratified K-Fold, Group K-Fold for entity isolation, Expanding-Window Time Series Split, and Double (Nested) Cross-Validation to eliminate optimization bias.

## Learning objectives
1. Implement Stratified K-Fold cross-validation that preserves exact class ratios across folds.
2. Construct Group K-Fold partitioning to eliminate multi-record entity data leakage.
3. Build temporal expanding-window Time Series splits that strictly enforce causality.
4. Implement Nested (Double) Cross-Validation to decouple model selection from generalization estimation.
5. Identify and eliminate subtle preprocessing and feature selection data leakages.

## Prerequisites
- Supervised classification metrics (Week 23).
- Hyperparameter tuning concepts (Day 166).
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
day-167-cross-validation-done-right/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── cv_lib.py
│   └── test_cv_lib.py
├── examples/
│   ├── cv_lib.py
│   └── test_cv_lib.py
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
python3 examples/cv_lib.py
```

## What the commands do
- `stratified_kfold_scratch(...)` creates class-balanced folds.
- `group_kfold_scratch(...)` ensures disjoint entity grouping across splits.
- `time_series_split_scratch(...)` creates temporal expanding windows.
- `nested_cross_validation_score(...)` executes leak-free outer/inner CV.

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
1. Implement StratifiedGroupKFold from scratch that satisfies both class balancing and entity isolation.
2. Implement Purged and Embargoed Time Series Split for financial modeling.
3. Compare standard cross-validation score vs nested cross-validation score across 100 random feature trials.

## Navigation
- Previous lab: `../day-166-hyperparameter-tuning/`
- Next lab: `../day-168-winning-on-tabular-data/`
