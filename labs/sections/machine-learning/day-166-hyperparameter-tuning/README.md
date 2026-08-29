# Lab 166: Hyperparameter Tuning and Optimization from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Hyperparameter Tuning
- **Day number:** 166 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-166-hyperparameter-tuning
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-166-hyperparameter-tuning` when the site is running.
<!-- generated-links:end -->

## Purpose
Master systematic hyperparameter optimization techniques: implement exhaustive Grid Search, efficient Randomized Search over parameter distributions, and the Bayesian Optimization Expected Improvement (EI) acquisition function from first principles.

## Learning objectives
1. Implement Cartesian product Grid Search with cross-validation.
2. Implement Randomized Search across discrete and continuous distributions.
3. Formulate and compute the analytical Expected Improvement (EI) acquisition function.
4. Analyze the Low Effective Dimensionality phenomenon (Bergstra & Bengio, 2012).
5. Benchmark tuning strategies on clinical tabular datasets without validation leakage.

## Prerequisites
- Decision Trees and Tree Ensembles (Days 162–165).
- Probability distributions and Gaussian processes.
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
day-166-hyperparameter-tuning/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── tuning_lib.py
│   └── test_tuning_lib.py
├── examples/
│   ├── tuning_lib.py
│   └── test_tuning_lib.py
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
python3 examples/tuning_lib.py
```

## What the commands do
- `grid_search_scratch(...)` evaluates all grid combinations.
- `random_search_scratch(...)` samples `n_iter` configurations randomly.
- `compute_expected_improvement(...)` computes Bayesian acquisition scores.

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
1. Implement Successive Halving to discard bottom 50% of trials after 10 iterations.
2. Implement Upper Confidence Bound (UCB) acquisition function: `UCB(x) = mu(x) + kappa * sigma(x)`.
3. Integrate Optuna TPE (Tree-structured Parzen Estimators) to optimize LightGBM hyperparameters.

## Navigation
- Previous lab: `../day-165-xgboost-and-lightgbm-in-practice/`
- Next lab: `../day-167-cross-validation-done-right/`
