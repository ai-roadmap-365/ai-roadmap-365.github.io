# Lab 156: Decision Boundaries in Linear and Non-Linear Classification

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Decision Boundaries
- **Day number:** 156 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-156-decision-boundaries
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-156-decision-boundaries` when the site is running.
<!-- generated-links:end -->

## Purpose
Calculate, visualize, and analyze linear and non-linear decision boundaries, signed distance metrics, polynomial feature expansions, and One-vs-Rest multiclass partitions.

## Learning objectives
1. Derive and compute 2D linear decision boundary lines from model parameters.
2. Calculate perpendicular signed distances from arbitrary feature vectors to the decision hyperplane.
3. Transform 2D feature space with polynomial expansions to produce curved boundaries.
4. Implement a One-vs-Rest (OvR) multiclass classifier and compute argmax class partitions.
5. Evaluate decision boundary smoothness and trade-offs between underfitting and overfitting.

## Prerequisites
- Logistic regression fundamentals (Day 155).
- Linear algebra: dot products, vector norms, and line equations.
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
day-156-decision-boundaries/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── boundary_lib.py
│   └── test_boundary_lib.py
├── examples/
│   ├── boundary_lib.py
│   └── test_boundary_lib.py
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
python3 examples/boundary_lib.py
```

## What the commands do
- `compute_linear_boundary_2d(w, b, x1)` calculates the line coordinates.
- `signed_distance_to_boundary(X, w, b)` computes point-to-plane distances.
- `polynomial_features_2d(X, degree)` expands coordinates into non-linear basis terms.
- `fit_ovr_classifier(X, y)` fits binary classifiers for multiclass datasets.

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
1. Implement a 2D decision boundary contour plotter with Matplotlib.
2. Compute the volume of ambiguous prediction regions in One-vs-Rest classification.
3. Compare OvR against Multinomial Softmax decision boundaries on a 3-class dataset.

## Navigation
- Previous lab: `../day-155-logistic-regression/`
- Next lab: `../day-157-k-nearest-neighbors/`
