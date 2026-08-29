# Lab 157: k-Nearest Neighbors from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** k-Nearest Neighbors
- **Day number:** 157 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-157-k-nearest-neighbors
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-157-k-nearest-neighbors` when the site is running.
<!-- generated-links:end -->

## Purpose
Implement a vectorized k-Nearest Neighbors classifier from first principles using NumPy and SciPy, explore distance metrics (Euclidean, Manhattan, Cosine), compare uniform vs distance-weighted voting, and benchmark scaling sensitivity.

## Learning objectives
1. Vectorize pairwise distance matrix computation using matrix broadcasting.
2. Implement top-k neighbor search and plurality voting.
3. Construct distance-inverse weighted probability estimation.
4. Evaluate the effect of neighborhood size `k` on decision boundary smoothness and bias-variance trade-off.
5. Demonstrate why feature standardization is mandatory for distance-based models.

## Prerequisites
- Decision boundaries and classification geometry (Day 156).
- NumPy 2D array broadcasting and matrix multiplication.
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
day-157-k-nearest-neighbors/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── knn_lib.py
│   └── test_knn_lib.py
├── examples/
│   ├── knn_lib.py
│   └── test_knn_lib.py
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
python3 examples/knn_lib.py
```

## What the commands do
- `compute_distance_matrix(X_train, X_test)` evaluates pairwise Euclidean distances.
- `predict_proba_knn(...)` estimates class probabilities via uniform or inverse-distance voting.
- `predict_knn(...)` returns discrete class predictions matching `argmax P(y|x)`.

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
1. Implement a KD-Tree search structure in Python to accelerate nearest neighbor queries in 2D.
2. Implement radius-based neighbors classification (`RadiusNeighborsClassifier`).
3. Evaluate the Curse of Dimensionality by measuring the ratio of max/min distance as dimension `d` grows from 2 to 1,000.

## Navigation
- Previous lab: `../day-156-decision-boundaries/`
- Next lab: `../day-158-naive-bayes-and-text-classification/`
