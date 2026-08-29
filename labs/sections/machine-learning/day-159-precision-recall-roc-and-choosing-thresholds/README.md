# Lab 159: Precision, Recall, ROC, and Choosing Thresholds

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Precision, Recall, ROC, and Choosing Thresholds
- **Day number:** 159 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-159-precision-recall-roc-and-choosing-thresholds
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-159-precision-recall-roc-and-choosing-thresholds` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a complete classification evaluation toolkit from first principles: confusion matrices, Precision, Recall, Specificity, F1, F-beta, Matthews Correlation Coefficient (MCC), ROC and PR curves, and cost-sensitive threshold selection.

## Learning objectives
1. Compute the 2x2 confusion matrix ($TN, FP, FN, TP$) from ground truth and predictions.
2. Derive and calculate Precision, Recall, Specificity, F1, F2, and MCC metrics.
3. Construct the Receiver Operating Characteristic (ROC) curve and calculate ROC AUC via trapezoidal integration.
4. Construct the Precision-Recall (PR) curve and explain why it excels on imbalanced data.
5. Implement cost-sensitive threshold optimization to minimize asymmetric business or clinical risk.

## Prerequisites
- Logistic regression and predicted probability scores (Day 155).
- Python dictionary manipulation and NumPy array operations.
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
day-159-precision-recall-roc-and-choosing-thresholds/
├── README.md
├── metadata.yml
├── requirements/
│   └── requirements.txt
├── starter/
│   ├── metrics_lib.py
│   └── test_metrics_lib.py
├── examples/
│   ├── metrics_lib.py
│   └── test_metrics_lib.py
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
python3 examples/metrics_lib.py
```

## What the commands do
- `compute_confusion_matrix(y_true, y_pred)` creates the 2x2 matrix.
- `compute_metrics(y_true, y_pred)` returns precision, recall, f1, mcc.
- `compute_roc_curve(y_true, y_scores)` sweeps thresholds to build the ROC curve.
- `find_optimal_cost_threshold(...)` computes the optimal operating point.

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
1. Implement multi-class macro and micro-averaged F1 metrics.
2. Implement Brier Score and calibration curves (reliability diagrams).
3. Implement Cohen's Kappa metric for inter-annotator agreement.

## Navigation
- Previous lab: `../day-158-naive-bayes-and-text-classification/`
- Next lab: `../day-160-class-imbalance/`
