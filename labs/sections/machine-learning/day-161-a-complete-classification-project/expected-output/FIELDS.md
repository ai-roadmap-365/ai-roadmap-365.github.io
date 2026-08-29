# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The stratified splitting proportions** (60/20/20 train/val/test with exact class balance) hold deterministically for random_state=42.
- **The test evaluation single-access lock** raises a RuntimeError on any repeated invocation.
- **Metric arithmetic** (Precision, Recall, F1, MCC, ROC AUC) is exact.

## Exact under these pins, and only these

- **Winning candidate 5-fold CV F1 score**: `0.9839`.
- **Final held-out test F1 score**: `0.9861` and **ROC AUC**: `0.9974`.
