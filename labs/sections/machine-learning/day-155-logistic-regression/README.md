# Lab 155: Logistic Regression from First Principles

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Logistic Regression
- **Day number:** 155 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-155-logistic-regression
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-155-logistic-regression` when the site is running.
<!-- generated-links:end -->

## Purpose
Build, train, and validate a binary logistic regression classifier from first principles using NumPy, then benchmark against scikit-learn's `LogisticRegression`.

## Learning objectives
1. Implement the numerically stable sigmoid activation function.
2. Compute predicted probabilities and binary cross-entropy (log loss).
3. Derive and implement analytical gradients with respect to weights and bias.
4. Train the model with batch gradient descent on standardized features.
5. Benchmark scratch convergence and accuracy against scikit-learn.

## Prerequisites
- Linear regression concepts (Day 148-153).
- Vectorized NumPy array operations and matrix multiplication (`np.dot`).
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
- Python standard library + NumPy / scikit-learn (free, BSD/MIT open source).

## Installation
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## File structure
```
day-155-logistic-regression/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── logistic_lib.py
│   └── test_logistic_lib.py
├── examples/
│   ├── logistic_lib.py
│   └── test_logistic_lib.py
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
python3 examples/logistic_lib.py
```

## What the commands do
- `sigmoid(z)` maps any real-valued score to `(0, 1)`.
- `predict_proba(X, w, b)` evaluates linear combinations through the sigmoid.
- `binary_cross_entropy(y, p)` computes the negative log likelihood.
- `compute_gradients(X, y, p)` calculates exact gradient steps.

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
1. Add L2 regularization (Ridge penalty) to gradient descent.
2. Implement Newton-Raphson optimization (Iteratively Reweighted Least Squares / IRLS).
3. Extend to multiclass classification via Softmax / Multinomial cross-entropy.

## Navigation
- Previous lab: `../day-154-a-complete-regression-project/`
- Next lab: `../day-156-decision-boundaries/`
