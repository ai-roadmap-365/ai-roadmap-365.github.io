# Lab 173: Custom Scikit-Learn Transformers and Composite Pipelines

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** scikit-learn Pipelines
- **Day number:** 173 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-173-scikit-learn-pipelines
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-173-scikit-learn-pipelines` when the site is running.
<!-- generated-links:end -->

## Purpose
Master the software engineering backbone of production machine learning: implement custom estimators inheriting `BaseEstimator` and `TransformerMixin`, compose heterogeneous multi-branch `ColumnTransformer` workflows, and build atomic, leak-free `Pipeline` architectures.

## Learning objectives
1. Implement custom transformers following the `BaseEstimator` and `TransformerMixin` contract.
2. Build an `OutlierClipperTransformer` and `CustomLogTransformer` with `clone()` compatibility.
3. Construct heterogeneous `ColumnTransformer` preprocessing graphs (numerical vs categorical).
4. Eliminate train/test data leakage by encapsulating all transformations inside atomic Pipelines.
5. Perform composite hyperparameter tuning across preprocessing and modeling steps with `GridSearchCV`.

## Prerequisites
- Feature scaling and encoding (Day 170).
- Feature selection (Day 172).
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
day-173-scikit-learn-pipelines/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── pipeline_lib.py
│   └── test_pipeline_lib.py
├── examples/
│   ├── pipeline_lib.py
│   └── test_pipeline_lib.py
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
python3 examples/pipeline_lib.py
```

## What the commands do
- `CustomLogTransformer(...)` applies log transformations with offset.
- `OutlierClipperTransformer(...)` clips to empirical training percentiles.
- `build_heterogeneous_tabular_pipeline(...)` builds an end-to-end ColumnTransformer pipeline.

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
1. Implement a custom Target Encoding transformer inheriting `BaseEstimator` and `TransformerMixin` with out-of-fold cross-validation inside `fit_transform`.
2. Build a `FeatureUnion` combining TF-IDF text features with dense numerical summary statistics.
3. Save and load an entire composite pipeline with `joblib` and verify exact prediction identity.

## Navigation
- Previous lab: `../day-172-feature-selection/`
- Next lab: `../day-174-handling-missing-data/`
