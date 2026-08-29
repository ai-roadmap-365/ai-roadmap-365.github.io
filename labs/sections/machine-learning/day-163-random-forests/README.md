# Lab 163: Random Forests, Bagging, and Out-of-Bag Evaluation from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Random Forests
- **Day number:** 163 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-163-random-forests
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-163-random-forests` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a complete Random Forest Classifier from scratch in NumPy: implement Bootstrap Aggregation (Bagging), random feature subspace subsampling (`max_features='sqrt'`), ensemble majority voting, and Out-of-Bag (OOB) error estimation.

## Learning objectives
1. Implement uniform bootstrap resampling with replacement and track OOB indices.
2. Build randomized decision trees that evaluate splits on random feature subsets.
3. Combine tree predictions using ensemble majority voting.
4. Compute the Out-of-Bag (OOB) generalization score without a validation set.
5. Benchmark scratch random forests against scikit-learn on breast cancer classification.

## Prerequisites
- Decision Trees and CART splitting (Day 162).
- Probability and variance reduction foundations.
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
day-163-random-forests/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── forest_lib.py
│   └── test_forest_lib.py
├── examples/
│   ├── forest_lib.py
│   └── test_forest_lib.py
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
python3 examples/forest_lib.py
```

## What the commands do
- `bootstrap_sample(X, y)` generates bootstrap training subsets and OOB masks.
- `RandomizedDecisionTree` fits trees over random feature subsets.
- `RandomForestClassifierScratch` aggregates `B` trees and computes OOB accuracy.

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
1. Implement Permutation Feature Importance across the fitted forest.
2. Parallelize tree fitting across CPU cores using `concurrent.futures`.
3. Implement ExtraTrees (Extremely Randomized Trees) where candidate thresholds are drawn completely at random.

## Navigation
- Previous lab: `../day-162-decision-trees/`
- Next lab: `../day-164-gradient-boosting/`
