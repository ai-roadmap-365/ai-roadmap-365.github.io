# Lab 162: Decision Trees and Impurity Criteria from Scratch

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Decision Trees
- **Day number:** 162 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-162-decision-trees
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-162-decision-trees` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Classification and Regression Tree (CART) decision tree classifier from scratch using NumPy: implement Gini Impurity and Shannon Entropy, write an exhaustive greedy split evaluator, construct a recursive binary tree data structure, and benchmark against scikit-learn's `DecisionTreeClassifier`.

## Learning objectives
1. Implement Gini impurity and Shannon entropy impurity criteria.
2. Find the globally optimal single-feature axis-aligned split threshold.
3. Construct a recursive binary tree data structure with base-case stopping criteria.
4. Predict class labels for unseen feature vectors by tree traversal.
5. Benchmark scratch decision tree performance against scikit-learn on the Iris dataset.

## Prerequisites
- Classification fundamentals (Weeks 23).
- Recursive data structures in Python.
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
day-162-decision-trees/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── tree_lib.py
│   └── test_tree_lib.py
├── examples/
│   ├── tree_lib.py
│   └── test_tree_lib.py
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
python3 examples/tree_lib.py
```

## What the commands do
- `compute_gini(y)` calculates Gini impurity for class labels.
- `compute_entropy(y)` calculates Shannon entropy.
- `find_best_split(X, y)` exhaustively identifies the optimal feature and threshold.
- `DecisionTreeClassifierScratch(max_depth=3)` trains recursive CART trees.

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
1. Implement Cost-Complexity Pruning (minimal cost-complexity pruning with parameter `ccp_alpha`).
2. Extend the tree to regression tasks by implementing Mean Squared Error (variance reduction) impurity.
3. Compute MDI (Mean Decrease in Impurity) feature importances from the fitted tree structure.

## Navigation
- Previous lab: `../day-161-a-complete-classification-project/`
- Next lab: `../day-163-random-forests/`
