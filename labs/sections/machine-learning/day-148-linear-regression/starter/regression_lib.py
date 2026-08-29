"""One predictor, one line: what fitting it actually buys you, measured.

Simple linear regression is a claim about a straight-line relationship
between one predictor and one target, fitted so the squared vertical
distances from the line are as small as possible (Day 149 owns *why*
squared error; this module just fits it, with scikit-learn's
`LinearRegression`). Two facts about that fit are exact on any data,
forever: it passes through the point of means, and its residuals sum to
zero when an intercept is fitted. Everything else here is a measurement of
what the line gets right and what it silently hides.

The module is organised in the order the lesson uses it:

1. The line itself, fitted to real data in real units (age-adjusted
   diabetes progression against BMI, raw scale).
2. Recovering a slope you know to be true, and watching the error shrink
   with more rows.
3. Two ways a fit can look fine on a scatterplot and an R-squared, and
   still be wrong: curvature and heteroscedasticity, both visible only in
   the residuals.
4. One point that moves the whole line, and the number that names why.
5. What forcing the intercept to zero costs, measured against the same
   data fitted honestly.

Everything here is deterministic given a seed. Nothing downloads: the
diabetes dataset is bundled with scikit-learn and the rest is generated on
the spot from `numpy.random.default_rng`.
"""

from __future__ import annotations

import numpy as np

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression


# --------------------------------------------------------------------------
# 1. The line itself: BMI against disease progression, in raw units
# --------------------------------------------------------------------------


def load_bmi_and_target():
    """BMI and the disease-progression target, in their original units.

    `load_diabetes(scaled=False)` is the only way to get raw units out of
    this dataset -- the default returns every column mean-centred and
    scaled to unit norm, which makes a coefficient uninterpretable as
    "one more unit of X". Column 2 is BMI; see `load_diabetes().feature_names`.
    """
    data = load_diabetes(scaled=False)
    bmi = data.data[:, 2].reshape(-1, 1)
    y = data.target
    return bmi, y


def fit_line(x, y, fit_intercept: bool = True) -> LinearRegression:
    """Fit scikit-learn's `LinearRegression`. This module never derives it."""
    return LinearRegression(fit_intercept=fit_intercept).fit(x, y)


def slope_standard_error(x, residuals) -> float:
    """How much the fitted slope would wobble under a fresh sample.

    `SE(b1) = s / sqrt(sum((x - xbar)^2))`, where `s^2` is the residual
    variance with `n - 2` degrees of freedom spent on the slope and the
    intercept. This is the same standard-error arithmetic Days 117-118 and
    Day 144 used for a sampling proportion, applied here to a slope.
    """
    x = np.asarray(x, dtype=float).flatten()
    n = len(x)
    dof = n - 2
    s2 = float(np.sum(np.asarray(residuals) ** 2)) / dof
    sxx = float(np.sum((x - x.mean()) ** 2))
    return float(np.sqrt(s2 / sxx))


def confidence_interval(estimate: float, standard_error: float, z: float = 1.96) -> tuple:
    """A normal-approximation interval, rounded for reporting."""
    return (
        round(estimate - z * standard_error, 4),
        round(estimate + z * standard_error, 4),
    )


def passes_through_the_means(model: LinearRegression, x, y) -> tuple:
    """Confirms the fitted line predicts `mean(y)` exactly at `mean(x)`.

    Not approximately -- exactly, up to floating point. It is a property
    of the least-squares normal equations (Day 149's territory), not a
    coincidence of this dataset.
    """
    x = np.asarray(x, dtype=float)
    mean_x = x.mean(axis=0).reshape(1, -1)
    predicted_at_mean = float(model.predict(mean_x)[0])
    mean_y = float(np.asarray(y).mean())
    return predicted_at_mean, mean_y, predicted_at_mean - mean_y


def residual_sum(residuals) -> float:
    """The sum of the residuals, which is exactly zero when an intercept
    is fitted -- another consequence of the normal equations, not a
    measurement that happened to come out that way."""
    return float(np.sum(residuals))


# --------------------------------------------------------------------------
# 2. Recovering a slope you know to be true
# --------------------------------------------------------------------------


def make_known_line(n: int, seed: int, true_slope: float = 5.0, true_intercept: float = 10.0, noise_sd: float = 8.0):
    """One predictor, a known slope and intercept, and Gaussian noise."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 20, size=n).reshape(-1, 1)
    y = true_slope * x.flatten() + true_intercept + rng.normal(0, noise_sd, size=n)
    return x, y


def slope_recovery_error(n_values, replications: int = 200, true_slope: float = 5.0):
    """Mean absolute error of the fitted slope, at each sample size.

    Averaged over `replications` independently drawn datasets per `n`, for
    the same reason Days 117-118 and Day 144 always averaged rather than
    quoting one draw: a single fit's error is an anecdote.
    """
    rows = []
    for n in n_values:
        errors = [
            abs(float(fit_line(*make_known_line(n, seed, true_slope=true_slope)).coef_[0]) - true_slope)
            for seed in range(replications)
        ]
        rows.append((n, round(float(np.mean(errors)), 4)))
    return rows


# --------------------------------------------------------------------------
# 3a. Curvature: a fit that looks fine and is not
# --------------------------------------------------------------------------


def curved_dataset(n: int = 300, seed: int = 1):
    """A quadratic relationship, so a straight line is the wrong model."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 10, size=n)
    y = 2.0 + 0.5 * x**2 + rng.normal(0, 5.0, size=n)
    return x.reshape(-1, 1), y


def binned_residual_means(x, residuals, bins: int = 5):
    """Mean residual within each of `bins` equal-count groups, sorted by x.

    A straight line fitted to a curve leaves residuals that are positive
    at both ends and negative in the middle (or the reverse) -- a shape no
    single number like R-squared exposes, but a residual plot shows at a
    glance.
    """
    x = np.asarray(x, dtype=float).flatten()
    residuals = np.asarray(residuals, dtype=float)
    order = np.argsort(x)
    x_sorted, resid_sorted = x[order], residuals[order]
    groups = np.array_split(np.arange(len(x_sorted)), bins)
    return [
        (round(float(x_sorted[g].mean()), 2), round(float(resid_sorted[g].mean()), 4))
        for g in groups
    ]


def quadratic_fit_r_squared(x, residuals) -> float:
    """How much of the residuals' own variance a quadratic curve explains.

    Near zero when the residuals are patternless noise; large when the
    line missed real curvature. Fitted with `numpy.polyfit`, not
    scikit-learn -- this is a diagnostic on the residuals, not a second
    model of the data.
    """
    x = np.asarray(x, dtype=float).flatten()
    residuals = np.asarray(residuals, dtype=float)
    coeffs = np.polyfit(x, residuals, 2)
    predicted = np.polyval(coeffs, x)
    ss_res = float(np.sum((residuals - predicted) ** 2))
    ss_tot = float(np.sum((residuals - residuals.mean()) ** 2))
    return float(1.0 - ss_res / ss_tot)


# --------------------------------------------------------------------------
# 3b. Heteroscedasticity: error that grows with x
# --------------------------------------------------------------------------


def heteroscedastic_dataset(n: int = 400, seed: int = 2):
    """A line whose noise gets wider as x grows -- the fit stays roughly
    unbiased; only its residual spread reveals what is wrong."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(1, 20, size=n)
    noise_sd = 0.8 * x
    y = 3.0 + 2.0 * x + rng.normal(0, 1, size=n) * noise_sd
    return x.reshape(-1, 1), y


def residual_spread_by_half(x, residuals) -> tuple:
    """Residual standard deviation in the low-x half against the high-x half."""
    x = np.asarray(x, dtype=float).flatten()
    residuals = np.asarray(residuals, dtype=float)
    median = float(np.median(x))
    low = residuals[x < median]
    high = residuals[x >= median]
    return float(low.std()), float(high.std())


# --------------------------------------------------------------------------
# 4. One point that moves the line
# --------------------------------------------------------------------------


def leverage_dataset(n: int = 40, seed: int = 3):
    """A clean, ordinary linear relationship, forty points."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 10, size=n)
    y = 2.0 + 1.5 * x + rng.normal(0, 1.5, size=n)
    return x, y


def add_point(x, y, x_new: float, y_new: float):
    """Append one point, returning fresh arrays (never mutates the inputs)."""
    return np.append(np.asarray(x, dtype=float), x_new), np.append(np.asarray(y, dtype=float), y_new)


def leverage_of_point(x, x_target: float) -> float:
    """The hat-matrix leverage of a point at `x_target`, given the full x array.

    `h = 1/n + (x_target - xbar)^2 / sum((x - xbar)^2)` -- how much that
    single point's own y-value can pull the fitted line toward itself,
    independent of what its y-value actually is.
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    xbar = x.mean()
    sxx = float(np.sum((x - xbar) ** 2))
    return float(1.0 / n + (x_target - xbar) ** 2 / sxx)


def mean_leverage_excluding(x, x_target: float) -> float:
    """Average leverage of every point except the one at `x_target`."""
    x = np.asarray(x, dtype=float)
    return float(np.mean([leverage_of_point(x, xi) for xi in x if xi != x_target]))


# --------------------------------------------------------------------------
# 5. fit_intercept=False, and what it costs
# --------------------------------------------------------------------------


def intercept_dataset(n: int = 200, seed: int = 4, true_intercept: float = 25.0, true_slope: float = 3.0, noise_sd: float = 6.0):
    """A line whose x-values never go near zero, so a forced-zero intercept
    is a real misspecification rather than a harmless simplification."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(5, 25, size=n)
    y = true_intercept + true_slope * x + rng.normal(0, noise_sd, size=n)
    return x.reshape(-1, 1), y


def rmse(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


# --------------------------------------------------------------------------
# 6. Skewness, for a rough normality read
# --------------------------------------------------------------------------


def skewness(values) -> float:
    """The third standardised moment: 0 for a symmetric distribution.

    A rough diagnostic only -- not a formal normality test, and this
    module does not claim to be one. `abs(skewness) < 0.5` is a common
    rule of thumb for "not alarming".
    """
    values = np.asarray(values, dtype=float)
    mean = values.mean()
    sd = values.std()
    return float(np.mean(((values - mean) / sd) ** 3))
