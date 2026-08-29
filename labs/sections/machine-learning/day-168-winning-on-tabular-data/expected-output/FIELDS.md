# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **Out-of-fold prediction matrix shape** is strictly `(N, M)` where `N` is sample count and `M` is number of base models.
- **Permutation feature importance** assigns higher mean accuracy drop to informative features over uninformative Gaussian noise.

## Exact under these pins, and only these

- **RandomForest baseline test accuracy on Breast Cancer holdout**: `0.9408` (94.08%).
