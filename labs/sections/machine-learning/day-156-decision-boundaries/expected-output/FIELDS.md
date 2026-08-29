# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The distance formula `d = (w^T x + b) / ||w||`** is an exact geometric definition.
- **The line slope `-w1/w2` and intercept `-b/w2`** are exact algebraic consequences of `w1*x1 + w2*x2 + b = 0`.
- **The polynomial expansion dimensions** (2 features to 5 features for degree 2) are exact combinatorial counts.

## Exact under these pins, and only these

- **Linear LogisticRegression on 2D Iris sepal features** achieves `0.8200` training accuracy.
- **Degree-2 Polynomial LogisticRegression on 2D Iris** achieves `0.8333` training accuracy.
