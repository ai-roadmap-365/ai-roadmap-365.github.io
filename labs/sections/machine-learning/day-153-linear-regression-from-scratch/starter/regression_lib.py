"""Ordinary least squares, three ways: what the library was doing for you.

Three implementations of the same fit -- the normal equations, an
lstsq-based solve, and gradient descent -- plus a scikit-learn-compatible
estimator wrapping all three, and then a direct measurement of where they
agree and where they do not.

Day 111 already derived gradient descent, its update rule, the stability
condition ``|1 - eta * a| < 1`` for an eigenvalue ``a`` of the loss's
Hessian, and the condition number as the ratio of the Hessian's largest and
smallest eigenvalues. None of that is re-derived here; it is applied.

Day 146 already established the scikit-learn estimator API contract --
``fit``/``predict``, learned attributes with a trailing underscore -- and
measured that a from-scratch estimator raises ``AttributeError`` on
``__sklearn_tags__`` inside ``Pipeline.predict()`` and ``cross_val_score``
unless it inherits ``BaseEstimator``. ``OLSRegressor`` below inherits it for
exactly that reason, without re-teaching the contract.

Everything here is deterministic given a seed.
"""

from __future__ import annotations

import numpy as np

from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.utils.validation import check_array, check_is_fitted, check_X_y

# --------------------------------------------------------------------------
# 1. Loading the data, and the two condition numbers
# --------------------------------------------------------------------------


def load_diabetes_data(scaled: bool = True):
    """The bundled diabetes regression dataset: X (442, 10), y (442,).

    ``scaled=True`` (the default) gives sklearn's own mean-centred,
    unit-L2-norm-scaled columns. ``scaled=False`` gives the raw clinical
    units -- age in years, sex coded 1/2, six serum measurements on very
    different scales -- which is the badly scaled version used to show
    gradient descent struggling.
    """
    data = load_diabetes(scaled=scaled)
    return data.data, data.target


def add_intercept_column(X: np.ndarray) -> np.ndarray:
    """Prepend a column of ones, the classic way to fold in an intercept."""
    ones = np.ones((X.shape[0], 1))
    return np.hstack([ones, X])


def condition_numbers(A: np.ndarray) -> tuple[float, float]:
    """``(cond(A), cond(A'A))`` -- the second is exactly the square of the first.

    ``cond`` here is the ratio of largest to smallest singular value. Squaring
    a matrix's condition number is the textbook reason the normal equations
    lose precision that a direct solve of ``A`` does not.
    """
    cond_a = float(np.linalg.cond(A))
    cond_ata = float(np.linalg.cond(A.T @ A))
    return cond_a, cond_ata


# --------------------------------------------------------------------------
# 2. Three ways to fit: normal equations, lstsq, and sklearn as the referee
# --------------------------------------------------------------------------


def fit_normal_equations(A: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Solve the normal equations ``A'A b = A'y`` directly.

    This is the formula from the textbook page: form ``A'A``, form ``A'y``,
    solve the square system. It is also, as this module measures, the least
    numerically careful of the three routes here.
    """
    return np.linalg.solve(A.T @ A, A.T @ y)


def fit_lstsq(A: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Solve the same least-squares problem via ``numpy.linalg.lstsq``.

    ``lstsq`` factors ``A`` directly (an SVD-based solve under the hood)
    rather than forming and inverting ``A'A``, which is why it does not
    inherit the squared condition number of the normal equations.
    """
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


def sklearn_reference_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Fit scikit-learn's own ``LinearRegression`` and return ``[intercept, *coef]``.

    Used as the referee throughout this module: not because it is a fourth
    algorithm, but because it is the thing every from-scratch attempt here is
    being measured against.
    """
    model = LinearRegression().fit(X, y)
    return np.concatenate([[float(model.intercept_)], model.coef_])


def max_abs_difference(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a - b)))


# --------------------------------------------------------------------------
# 3. The dramatic case: a near-duplicate column
# --------------------------------------------------------------------------


def make_dramatic_collinear_dataset(n: int = 100, seed: int = 0, noise_scale: float = 1e-7):
    """Three random predictors plus a fourth that is almost the first.

    The fourth column is column 0 plus a sliver of noise -- 1e-7 in scale,
    far smaller than any real measurement error. The true coefficients are
    [1, 2, 3, 4]; a well-conditioned fit should recover something close to
    that. It does not, for two of the three methods below.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    duplicate = X[:, 0] + rng.normal(scale=noise_scale, size=n)
    X = np.column_stack([X, duplicate])
    true_coef = np.array([1.0, 2.0, 3.0, 4.0])
    y = X @ true_coef + rng.normal(scale=0.1, size=n)
    return X, y, true_coef


# --------------------------------------------------------------------------
# 4. Gradient descent, and the Day 111 stability threshold arriving here
# --------------------------------------------------------------------------


def standardize(X: np.ndarray) -> np.ndarray:
    """Zero mean, unit standard deviation, column by column."""
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    return (X - mu) / sd


def center(X: np.ndarray, y: np.ndarray):
    """Subtract each column's mean from X and y's mean from y.

    Centring removes the need for a separate intercept term: the fitted
    hyperplane through centred data passes through the origin, and the
    intercept is recovered afterwards as ``y.mean() - X.mean(axis=0) @ coef``.
    """
    X_mean = X.mean(axis=0)
    y_mean = y.mean()
    return X - X_mean, y - y_mean, X_mean, y_mean


def hessian_eigenvalues(X: np.ndarray, n: int) -> np.ndarray:
    """Eigenvalues of the mean-squared-error loss's Hessian, ``(2/n) X'X``.

    Day 111 established that gradient descent on a quadratic loss is stable
    exactly when ``|1 - eta * a| < 1`` for every eigenvalue ``a`` of this
    Hessian, and that the ratio of its largest to smallest eigenvalue is the
    condition number governing how slowly the slowest direction converges.
    """
    XtX = X.T @ X
    return np.linalg.eigvalsh((2.0 / n) * XtX)


def stability_threshold(X: np.ndarray) -> float:
    """The largest learning rate for which every eigenvalue keeps |1 - eta*a| < 1.

    From Day 111's condition: stability requires ``eta < 2 / a`` for every
    eigenvalue ``a``, so the binding constraint is the largest eigenvalue.
    """
    n = X.shape[0]
    eig_max = float(hessian_eigenvalues(X, n).max())
    return 2.0 / eig_max


def fit_gradient_descent(X: np.ndarray, y: np.ndarray, lr: float, n_iter: int) -> np.ndarray:
    """Plain batch gradient descent on the centred mean-squared-error loss.

    Starts at the zero vector. ``X`` and ``y`` are assumed already centred,
    so no intercept term appears in this loop -- see ``center`` above.
    """
    n, p = X.shape
    coef = np.zeros(p)
    for _ in range(n_iter):
        grad = (2.0 / n) * (X.T @ (X @ coef - y))
        coef = coef - lr * grad
    return coef


def iters_to_tolerance(X: np.ndarray, y: np.ndarray, lr: float, target: np.ndarray, tol: float, max_iter: int):
    """How many gradient-descent iterations until every coefficient is within tol of target.

    Returns ``(iterations, final_coef)``, or ``(None, final_coef)`` if the
    tolerance was never reached within ``max_iter`` -- either because
    convergence needs more steps, or because the run diverged. A run that
    stops producing finite numbers returns ``("diverged", coef)``.
    """
    n, p = X.shape
    coef = np.zeros(p)
    for i in range(1, max_iter + 1):
        grad = (2.0 / n) * (X.T @ (X @ coef - y))
        coef = coef - lr * grad
        if not np.all(np.isfinite(coef)):
            return "diverged", coef
        if float(np.max(np.abs(coef - target))) < tol:
            return i, coef
    return None, coef


# --------------------------------------------------------------------------
# 5. Counting operations instead of timing them
# --------------------------------------------------------------------------


def normal_equation_op_count(n: int, p: int) -> int:
    """Multiply-adds to form A'A (n*p^2) plus solve the p-by-p system (p^3)."""
    return n * p * p + p**3


def gradient_descent_op_count(n: int, p: int, iterations: int) -> int:
    """Multiply-adds for `iterations` steps: two n*p matrix-vector products each."""
    return 2 * n * p * iterations


# --------------------------------------------------------------------------
# 6. A scikit-learn-compatible estimator
# --------------------------------------------------------------------------


class OLSRegressor(RegressorMixin, BaseEstimator):
    """Ordinary least squares, fit by one of three methods, as a real estimator.

    Inherits ``RegressorMixin`` and ``BaseEstimator`` because Day 146 already
    measured what happens without them: ``fit``, ``predict`` and ``score``
    work perfectly well called directly, but ``Pipeline.predict()`` and
    ``cross_val_score`` both raise ``AttributeError`` on ``__sklearn_tags__``,
    which only ``BaseEstimator`` supplies. That lesson is assumed, not
    repeated.

    ``fit_intercept=True`` centres X and y, fits the centred problem, and
    recovers the intercept afterwards -- rather than appending a column of
    ones -- because the two are measured elsewhere in this module to agree
    to about ten decimal places and centring avoids growing the design
    matrix by one column.
    """

    def __init__(self, method: str = "lstsq", fit_intercept: bool = True, lr: float = 0.1, n_iter: int = 1000):
        self.method = method
        self.fit_intercept = fit_intercept
        self.lr = lr
        self.n_iter = n_iter

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        if self.fit_intercept:
            Xc, yc, X_mean, y_mean = center(X, y)
        else:
            Xc, yc = X, y
            X_mean, y_mean = np.zeros(X.shape[1]), 0.0

        if self.method == "normal":
            coef = fit_normal_equations(Xc, yc)
        elif self.method == "lstsq":
            coef = fit_lstsq(Xc, yc)
        elif self.method == "gd":
            coef = fit_gradient_descent(Xc, yc, self.lr, self.n_iter)
        else:
            raise ValueError(f"unknown method {self.method!r}; use 'normal', 'lstsq' or 'gd'")

        self.coef_ = coef
        self.intercept_ = float(y_mean - X_mean @ coef) if self.fit_intercept else 0.0
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X):
        check_is_fitted(self, "coef_")
        X = check_array(X)
        return X @ self.coef_ + self.intercept_


def run_check_estimator(estimator):
    """Run scikit-learn's estimator_checks suite and tally results by name.

    Returns ``(passed, failed, skipped)`` where ``failed`` and ``skipped``
    are lists of ``(check_name, message)`` pairs -- never silently discarded.
    """
    from sklearn.utils.estimator_checks import check_estimator

    results = []

    def record(*, estimator, check_name, exception, status, expected_to_fail, expected_to_fail_reason):
        results.append((check_name, status, str(exception)[:200] if exception else None))

    check_estimator(estimator, on_fail=None, on_skip=None, callback=record)
    passed = [name for name, status, _msg in results if status == "passed"]
    failed = [(name, msg) for name, status, msg in results if status == "failed"]
    skipped = [(name, msg) for name, status, msg in results if status == "skipped"]
    return passed, failed, skipped


# --------------------------------------------------------------------------
# 7. fit_intercept two ways: centring versus an appended column
# --------------------------------------------------------------------------


def fit_intercept_two_ways(X: np.ndarray, y: np.ndarray):
    """Compare centring against appending a ones column, on the same data.

    Returns ``(coef_column, intercept_column, coef_centred, intercept_centred)``.
    """
    n = X.shape[0]
    A = add_intercept_column(X)
    beta_column = fit_normal_equations(A, y)
    intercept_column, coef_column = float(beta_column[0]), beta_column[1:]

    Xc, yc, X_mean, y_mean = center(X, y)
    coef_centred = fit_normal_equations(Xc, yc)
    intercept_centred = float(y_mean - X_mean @ coef_centred)

    return coef_column, intercept_column, coef_centred, intercept_centred
