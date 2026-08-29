# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **Confusion matrix arithmetic** `TN + FP + FN + TP = N` is an exact partition identity.
- **Harmonic mean formula `F1 = 2*P*R / (P+R)`** evaluates identically across all platforms.
- **The cost minimization objective `cost = cost_fp * FP + cost_fn * FN`** is exact.

## Exact under these pins, and only these

- **Breast cancer logistic regression ROC AUC**: `0.9950`.
- **Optimal cost threshold under 10:1 penalty**: `tau* = 0.23`.
