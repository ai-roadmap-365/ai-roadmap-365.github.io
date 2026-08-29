# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The Gini impurity formula `G = 1 - sum(p_k^2)`** produces `0.50` for balanced 2-class data and `2/3` for balanced 3-class data analytically.
- **The Shannon entropy formula `H = -sum(p_k log2 p_k)`** produces `1.0 bit` for balanced 2-class data analytically.
- **Iris root split on petal length <= 2.45** creates a pure leaf of 50 Setosa samples.

## Exact under these pins, and only these

- **Decision tree training accuracy on Iris (max_depth=3)**: `0.9733` (146/150 correct).
