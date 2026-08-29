# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The `fit`/`transform` contract** strictly returns an instance of `self` from `fit()` and transformed arrays from `transform()`.
- **Outlier clipping bounds** strictly bound transformed values to `[lower_bound, upper_bound]`.
