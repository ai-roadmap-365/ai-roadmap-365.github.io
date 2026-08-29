# Lab 172: Feature Selection Algorithms and RFE from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Feature Selection
- **Day number:** 172 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-172-feature-selection
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-172-feature-selection` when the site is running.
<!-- generated-links:end -->

## Purpose
Implement and compare the three canonical feature selection paradigms: Filter methods (Variance Threshold, Correlation), Wrapper methods (Recursive Feature Elimination / RFE), and Embedded methods (Boruta Shadow Feature testing) from scratch.

## Learning objectives
1. Implement VarianceThreshold filtering to prune constant and near-constant noise columns.
2. Implement Recursive Feature Elimination (RFE) with iterative backward coefficient pruning.
3. Formulate and implement the Boruta Shadow Feature comparison algorithm.
4. Prevent selection bias data leakage by embedding feature selection inside cross-validation.
5. Construct a multi-stage feature selection funnel (Filter -> Wrapper -> Embedded).

## Prerequisites
- Feature engineering primitives (Day 171).
- Cross-Validation fundamentals (Day 167).
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
day-172-feature-selection/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── selection_lib.py
│   └── test_selection_lib.py
├── examples/
│   ├── selection_lib.py
│   └── test_selection_lib.py
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
python3 examples/selection_lib.py
```

## What the commands do
- `filter_by_variance_threshold(...)` drops constant/near-constant columns.
- `recursive_feature_elimination_scratch(...)` performs backward greedy pruning.
- `boruta_shadow_filter(...)` tests features against randomized shadow permutations.

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
1. Implement Sequential Forward Selection (SFS) from scratch evaluating candidate metric gain at each step.
2. Build an ANOVA F-test filter score calculation using Between-Group and Within-Group sum of squares.
3. Construct RFECV with automated cross-validated scoring to select the optimal number of features $K^*$.

## Navigation
- Previous lab: `../day-171-feature-engineering/`
- Next lab: `../day-173-scikit-learn-pipelines/`
