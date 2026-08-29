# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The XGBoost second-order split gain formula** `Gain = 0.5 * [ G_L^2 / (H_L + lambda) + G_R^2 / (H_R + lambda) - (G_L+G_R)^2 / (H_L+H_R+lambda) ] - gamma` is mathematically exact.
- **Histogram binning `uint8` reduction factor** is exactly `8x` relative to `float64` precision.

## Exact under these pins, and only these

- **HistGradientBoosting training accuracy on synthetic dataset**: `1.0000` (500/500 samples in 50 iterations).
