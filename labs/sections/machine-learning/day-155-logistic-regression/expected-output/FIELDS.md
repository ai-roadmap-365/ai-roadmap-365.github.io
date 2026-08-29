# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The sigmoid midpoint `sigma(0) = 0.5`** and symmetry `sigma(-z) = 1 - sigma(z)` are analytical mathematical identities.
- **The binary cross-entropy at `p = 0.5` equals `ln(2) = 0.693147...`** regardless of machine or operating system.
- **The gradient vanishing condition at `p = y`** is an exact analytical result of `grad = (1/N) * X^T (p - y)`.
- **The breast cancer dataset sample counts** (569 samples, 30 features, 357 benign, 212 malignant, 62.74% benign rate) are exact from `sklearn.datasets.load_breast_cancer`.

## Exact under these pins, and only these

- **Batch gradient descent loss after 1000 epochs (lr=0.2)** achieves `< 0.10` log loss and `>= 0.95` accuracy on standardized breast cancer features.
- **L-BFGS unregularized LogisticRegression accuracy** achieves `0.9912` accuracy and `0.0271` log loss on standardized breast cancer data.
