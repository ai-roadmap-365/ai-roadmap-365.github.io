# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The balanced weight formula `w_c = N / (K * N_c)`** is an exact analytical identity.
- **The weighted sum conservation `sum N_c * w_c = N`** holds exactly.
- **SMOTE linear interpolation `x + lambda * (x_nn - x)`** produces points strictly bounded by convex hulls.

## Exact under these pins, and only these

- **Unweighted Logistic Regression recall on 5% imbalanced synthetic data**: `0.4000`.
- **Balanced class-weighted Logistic Regression recall**: `0.8600`.
