# Lab 168: Winning on Tabular Data

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Winning on Tabular Data
- **Day number:** 168 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-168-winning-on-tabular-data
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-168-winning-on-tabular-data` when the site is running.
<!-- generated-links:end -->

## Purpose
Master the end-to-end engineering playbook for tabular data: implement out-of-fold meta-feature generation, multi-model stacking ensembles, and permutation feature importance from scratch.

## Learning objectives
1. Implement leak-free Out-of-Fold (OOF) prediction generation across $K$ folds.
2. Build a 2-level Stacking Ensemble combining tree ensembles and linear meta-learners.
3. Formulate and compute Permutation Feature Importance.
4. Analyze model diversity in ensemble stacking and blending.
5. Deploy an end-to-end tabular machine learning pipeline adhering to production best practices.

## Prerequisites
- Decision Trees and Tree Ensembles (Days 162–165).
- Hyperparameter tuning and Cross-Validation (Days 166–167).
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
day-168-winning-on-tabular-data/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── tabular_lib.py
│   └── test_tabular_lib.py
├── examples/
│   ├── tabular_lib.py
│   └── test_tabular_lib.py
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
python3 examples/tabular_lib.py
```

## What the commands do
- `generate_out_of_fold_predictions(...)` builds Level-1 meta-feature matrix $Z$.
- `fit_stacking_ensemble(...)` trains base estimators and meta-learner.
- `predict_stacking_ensemble(...)` predicts test samples using full ensemble.
- `compute_permutation_importance(...)` calculates empirical feature impact.

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
1. Implement Rank Averaging blending for probability calibration across divergent model scales.
2. Implement TreeSHAP approximation to explain individual row predictions.
3. Benchmark LightGBM vs TabNet vs Stacking on high-cardinality categorical data.

## Navigation
- Previous lab: `../day-167-cross-validation-done-right/`
- Next lab (Week 24 Project): `../projects/week-24/`
