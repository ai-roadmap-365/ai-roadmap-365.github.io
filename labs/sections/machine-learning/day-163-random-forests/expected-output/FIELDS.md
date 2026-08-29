# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The mathematical asymptotic limit of Out-of-Bag samples `(1 - 1/N)^N`** approaches `1/e = 0.367879...` (36.79%) as `N -> infinity`.
- **Random Forest majority voting rule** produces deterministic class outputs given a fixed seed.

## Exact under these pins, and only these

- **Breast cancer training accuracy with seed 42 (B=30, max_depth=5)**: `0.9965` (567/569 samples).
- **Out-of-Bag score on Breast Cancer**: `0.9578`.
