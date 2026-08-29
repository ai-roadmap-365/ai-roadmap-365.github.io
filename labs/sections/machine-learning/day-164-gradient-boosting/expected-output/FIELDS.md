# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The pseudo-residual formula for binary classification `r_i = y_i - sigmoid(F(x_i))`** produces exactly `+0.5` for `y=1` and `-0.5` for `y=0` when initial raw score `F=0.0`.
- **Initial log-odds constant `F_0 = log(p / (1-p))`** is mathematically exact given dataset class proportions.

## Exact under these pins, and only these

- **Breast cancer training accuracy with seed 42 (M=30, eta=0.1, max_depth=3)**: `1.0000` (569/569 samples).
