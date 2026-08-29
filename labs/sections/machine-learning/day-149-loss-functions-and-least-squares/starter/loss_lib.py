"""Loss functions, measured: what choosing squared error over absolute error
actually decides, and what each is implicitly betting on.

A loss function is a choice, not a law of nature. This module measures four
consequences of that choice: the minimiser of squared error is the mean and
the minimiser of absolute error is the median; the squared-error landscape is
smooth with one minimum while the absolute-error landscape is piecewise
linear and kinked; the normal equations solve squared error in closed form
because that smoothness gives a zero derivative one can solve for directly,
while absolute error has no such closed form; and swapping which loss you
minimise changes how far a single outlier can move your line, and which loss
wins depends on what the errors actually look like -- Gaussian, or
heavy-tailed.

Everything here is deterministic given a seed.
"""

from __future__ import annotations

import numpy as np

from sklearn.linear_model import HuberRegressor, LinearRegression, QuantileRegressor


# --------------------------------------------------------------------------
# 1. What each loss minimises
# --------------------------------------------------------------------------


def sse(values, candidate: float) -> float:
    """Sum of squared error between a scalar candidate and every value."""
    values = np.asarray(values, dtype=float)
    return float(np.sum((values - candidate) ** 2))


def sae(values, candidate: float) -> float:
    """Sum of absolute error between a scalar candidate and every value."""
    values = np.asarray(values, dtype=float)
    return float(np.sum(np.abs(values - candidate)))


def grid_minimize(values, loss_fn, lo: float, hi: float, steps: int = 200_001) -> float:
    """Find the candidate in a fine grid that minimises the given loss.

    A brute-force numerical stand-in for calculus: since it searches a
    finite grid it lands within ``(hi - lo) / (steps - 1)`` of the true
    minimiser, not exactly on it.
    """
    grid = np.linspace(lo, hi, steps)
    losses = np.array([loss_fn(values, c) for c in grid])
    return float(grid[int(np.argmin(losses))])


# --------------------------------------------------------------------------
# 2. The shape of the loss landscape: smooth, or kinked
# --------------------------------------------------------------------------


def make_line_data(n: int = 150, seed: int = 0, true_intercept: float = 5.0,
                    true_slope: float = 3.0, noise_sd: float = 2.0,
                    heavy_tailed: bool = False, heavy_df: int = 3,
                    heavy_scale: float = 1.2):
    """A simple one-predictor dataset with a known true line.

    ``heavy_tailed=True`` swaps the Gaussian error for a scaled Student's t
    with ``heavy_df`` degrees of freedom, which has the same rough central
    spread but far fatter tails -- the construction used to measure what
    squared error implicitly assumes about the errors.
    """
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.0, 10.0, n)
    if heavy_tailed:
        errors = rng.standard_t(df=heavy_df, size=n) * heavy_scale
    else:
        errors = rng.normal(0.0, noise_sd, n)
    y = true_intercept + true_slope * x + errors
    return x, y


def loss_landscape(x, y, intercept: float, slopes):
    """Total squared error and total absolute error at each candidate slope,
    with the intercept held fixed. Returns ``(sq_losses, abs_losses)``.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    slopes = np.asarray(slopes, dtype=float)
    sq_losses = np.empty_like(slopes)
    abs_losses = np.empty_like(slopes)
    for i, m in enumerate(slopes):
        residual = y - (intercept + m * x)
        sq_losses[i] = np.sum(residual**2)
        abs_losses[i] = np.sum(np.abs(residual))
    return sq_losses, abs_losses


def second_differences(values) -> np.ndarray:
    """The discrete second derivative of a sequence: ``diff(diff(values))``.

    Constant second differences mean the curve is a parabola -- smooth,
    with a single well-defined slope of the slope. Jumping second
    differences mean the curve bends only at particular points -- a
    piecewise-linear, kinked shape.
    """
    return np.diff(np.asarray(values, dtype=float), n=2)


# --------------------------------------------------------------------------
# 3. The normal equations: squared error's closed form
# --------------------------------------------------------------------------


def normal_equations(x, y):
    """Solve for (intercept, slope) directly from the normal equations.

    Squared error is smooth everywhere, so setting its derivative to zero
    gives a linear system to solve: ``(X^T X) beta = X^T y``. Absolute
    error has no derivative at a residual of zero, so no equivalent closed
    form exists for it -- fitting it requires an iterative solver instead
    (which is what ``QuantileRegressor`` runs).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    design = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.solve(design.T @ design, design.T @ y)
    return float(beta[0]), float(beta[1])


def fit_ols(x, y):
    """Fit ordinary least squares with scikit-learn; return (intercept, slope)."""
    model = LinearRegression().fit(np.asarray(x, dtype=float).reshape(-1, 1), y)
    return float(model.intercept_), float(model.coef_[0])


# --------------------------------------------------------------------------
# 4. Outlier sensitivity: squared error, Huber, and absolute error compared
# --------------------------------------------------------------------------


def fit_huber(x, y, epsilon: float = 1.35, max_iter: int = 500):
    """Fit scikit-learn's HuberRegressor; return (intercept, slope)."""
    model = HuberRegressor(epsilon=epsilon, max_iter=max_iter).fit(
        np.asarray(x, dtype=float).reshape(-1, 1), y
    )
    return float(model.intercept_), float(model.coef_[0])


def fit_quantile(x, y, quantile: float = 0.5):
    """Fit scikit-learn's QuantileRegressor at the median (absolute error's
    minimiser); return (intercept, slope). ``alpha=0`` disables the
    regulariser this estimator applies by default, so it measures plain
    absolute error.
    """
    model = QuantileRegressor(quantile=quantile, alpha=0.0, solver="highs").fit(
        np.asarray(x, dtype=float).reshape(-1, 1), y
    )
    return float(model.intercept_), float(model.coef_[0])


def outlier_shift(x, y, outlier_index: int | None = None, outlier_offset: float = 80.0):
    """Fit OLS, Huber and median regression before and after moving one
    point far off the line. Returns a dict with each estimator's slope
    before, slope after, and how far the slope moved.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if outlier_index is None:
        outlier_index = int(np.argmax(x))
    y_outlier = y.copy()
    y_outlier[outlier_index] = y_outlier[outlier_index] + outlier_offset

    result = {}
    for name, fitter in (("ols", fit_ols), ("huber", fit_huber), ("quantile", fit_quantile)):
        _b0, before = fitter(x, y)
        _a0, after = fitter(x, y_outlier)
        result[name] = {
            "before": round(before, 4),
            "after": round(after, 4),
            "movement": round(after - before, 4),
        }
    return result


def huber_epsilon_sweep(x, y, epsilons):
    """The Huber slope at each epsilon, holding the (outlier-contaminated)
    data fixed. Small epsilon leans on the absolute-error half of the
    loss and large epsilon leans on the squared-error half, converging to
    plain OLS as epsilon grows without bound.
    """
    rows = []
    for eps in epsilons:
        _intercept, slope = fit_huber(x, y, epsilon=eps)
        rows.append((float(eps), round(slope, 4)))
    return rows


# --------------------------------------------------------------------------
# 5. What each loss assumes: Gaussian errors, or something heavier-tailed
# --------------------------------------------------------------------------


def efficiency_under_noise(heavy_tailed: bool, replications: int = 500,
                            n: int = 150, true_slope: float = 3.0):
    """Fit OLS and Huber on many independent datasets with the same true
    line, and report the mean and standard deviation of each estimator's
    slope. Returns ``(ols_mean, ols_sd, huber_mean, huber_sd)``.

    Under Gaussian errors, Gauss-Markov says OLS is the best LINEAR
    UNBIASED estimator: among estimators that are linear in y and unbiased,
    OLS has the smallest variance. Under heavy-tailed errors that
    guarantee no longer implies OLS is the lowest-variance choice, and
    this function measures whether it still is.
    """
    ols_slopes = np.empty(replications)
    huber_slopes = np.empty(replications)
    for seed in range(replications):
        x, y = make_line_data(n=n, seed=seed, true_slope=true_slope, heavy_tailed=heavy_tailed)
        _i0, ols_slopes[seed] = fit_ols(x, y)
        _i1, huber_slopes[seed] = fit_huber(x, y)
    return (
        round(float(ols_slopes.mean()), 4),
        round(float(ols_slopes.std()), 4),
        round(float(huber_slopes.mean()), 4),
        round(float(huber_slopes.std()), 4),
    )
