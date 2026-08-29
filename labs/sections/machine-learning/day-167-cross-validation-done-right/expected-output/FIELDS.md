# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **Stratified 5-Fold on 200 positive samples in 1,000 observations** allocates exactly 40 positive samples per 200-sample validation fold.
- **GroupKFold disjoint invariant** ensures that intersection of group labels between train and validation is empty.
- **TimeSeriesSplit precedence invariant** guarantees that maximum training index is strictly less than minimum validation index.
