# Lab 164: Gradient Boosting from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Gradient Boosting
- **Day number:** 164 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-164-gradient-boosting
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-164-gradient-boosting` when the site is running.
<!-- generated-links:end -->

## Purpose
Build complete Gradient Boosting Regressors and Classifiers from first principles in NumPy: derive negative gradients (pseudo-residuals) for Squared Error and Binary Cross-Entropy loss, implement sequential additive tree fitting with shrinkage (learning rate `eta`), and apply Newton-Raphson leaf updates.

## Learning objectives
1. Derive and compute pseudo-residuals (negative loss gradients) for regression and classification.
2. Initialize boosting models with optimal constant predictions (`F_0`).
3. Train sequential weak regression trees on residual error signals.
4. Implement Newton-Raphson second-order leaf step adjustments for classification.
5. Apply shrinkage regularization (`learning_rate`) to prevent premature overfitting.
6. Benchmark custom gradient boosted trees against scikit-learn on regression and classification tasks.

## Prerequisites
- Decision Trees (Day 162) and Random Forests (Day 163).
- Gradient descent and differential calculus.
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
day-164-gradient-boosting/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── gradient_boosting_lib.py
│   └── test_gradient_boosting_lib.py
├── examples/
│   ├── gradient_boosting_lib.py
│   └── test_gradient_boosting_lib.py
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
python3 examples/gradient_boosting_lib.py
```

## What the commands do
- `compute_pseudo_residuals_classification(y, raw)` calculates negative loss gradients.
- `GradientBoostingRegressorScratch` performs sequential residual minimization.
- `GradientBoostingClassifierScratch` performs Newton-Raphson boosted classification.

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
1. Implement Stochastic Gradient Boosting by randomly subsampling 80% of rows at each iteration.
2. Implement Huber Loss for robust regression in the presence of extreme outliers.
3. Implement an Early Stopping mechanism that monitors validation loss and halts tree addition when improvement stalls.

## Navigation
- Previous lab: `../day-163-random-forests/`
- Next lab: `../day-165-xgboost-and-lightgbm-in-practice/`
