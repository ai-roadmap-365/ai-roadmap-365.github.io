# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The distance matrix mathematical properties** (zero diagonal, non-negativity, symmetry) are analytical identities of metric spaces.
- **k=1 memorization accuracy (1.0 on distinct training points)** holds analytically across all implementations.
- **The distance weighting inversion `w = 1 / (d + eps)`** produces deterministic probabilities.

## Exact under these pins, and only these

- **Standardized Iris 5-fold cross-validation accuracies**: `k=1: 0.9467`, `k=5: 0.9667`, `k=15: 0.9600`.
