# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-29: macOS (Apple Silicon, arm64), Python 3.14.0,
in this lab's virtual environment with numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, and scipy 1.15.2.

## Exact on any machine, for any reason

- **The Expected Improvement formula `EI(x) = (mu - best) * Phi(Z) + sigma * phi(Z)`** yields `0.1085` analytically for `mu=0.90, sigma=0.10, best=0.80`.
- **Cartesian product size for grid search** is strictly `prod(|V_i|)`.

## Exact under these pins, and only these

- **GridSearchCV best 3-fold accuracy on Breast Cancer**: `0.9631` with `max_depth=5, n_estimators=50`.
