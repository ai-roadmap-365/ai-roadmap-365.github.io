# Lab 165: XGBoost and LightGBM in Practice

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** XGBoost and LightGBM in Practice
- **Day number:** 165 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-165-xgboost-and-lightgbm-in-practice
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-165-xgboost-and-lightgbm-in-practice` when the site is running.
<!-- generated-links:end -->

## Purpose
Master the architectural and mathematical innovations of modern gradient boosting libraries: implement XGBoost's exact second-order Taylor split gain, construct uint8 histogram-based feature binning, and benchmark `HistGradientBoostingClassifier` with native missing-value support against traditional ensembles.

## Learning objectives
1. Implement XGBoost's exact second-order Taylor expansion split gain formula with L2 regularization (`lambda`) and complexity penalty (`gamma`).
2. Construct histogram binning algorithms that map continuous `float64` features into `uint8` discrete bins (256 bins).
3. Train histogram gradient boosted trees natively on tabular data containing missing values (`NaN`) without imputation.
4. Compare level-wise (depth-first) vs leaf-wise (best-first) tree growth paradigms.
5. Benchmark histogram boosting speed and accuracy against standard Random Forests.

## Prerequisites
- Gradient Boosting foundations (Day 164).
- Taylor series expansions and second-order optimization.
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
day-165-xgboost-and-lightgbm-in-practice/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── boost_practice_lib.py
│   └── test_boost_practice_lib.py
├── examples/
│   ├── boost_practice_lib.py
│   └── test_boost_practice_lib.py
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
python3 examples/boost_practice_lib.py
```

## What the commands do
- `compute_xgboost_split_gain(...)` evaluates second-order split profitability.
- `histogram_bin_feature(...)` compresses continuous features to 256 uint8 bins.
- `HistogramGBSimplified` trains optimized histogram boosting with native NaN handling.

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
1. Implement Sparsity-Aware Split Finding by evaluating default left vs default right branches for missing values.
2. Implement Gradient-based One-Side Sampling (GOSS) that subsamples instances based on gradient magnitudes.
3. Compare CatBoost's Ordered Boosting against LightGBM on a high-cardinality categorical dataset.

## Navigation
- Previous lab: `../day-164-gradient-boosting/`
- Next lab: `../day-166-hyperparameter-tuning/`
