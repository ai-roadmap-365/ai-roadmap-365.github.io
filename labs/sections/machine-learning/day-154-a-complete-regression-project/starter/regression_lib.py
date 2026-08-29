"""One regression project, run properly, once.

Days 148-153 each isolated one discipline: the one-predictor model and its
four assumptions, the loss as a choice, multicollinearity, ridge and lasso,
the metrics that can be gamed or inverted, and OLS built from scratch. This
module spends every one of those disciplines on a single real dataset and
produces one defensible verdict, with residual diagnostics as the
centrepiece no other day owns.

Frame, baseline, split, pipeline, cross-validate, select, ONE test
evaluation, residual diagnostics, a fairness check, prediction intervals,
an honest interval on the margin. Nothing here is taught for the first
time; everything here is used.
"""

from __future__ import annotations

import numpy as np

from sklearn.datasets import load_diabetes
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------------------------------
# 1. The dataset -- the only bundled regression set that needs no download
# --------------------------------------------------------------------------


def load_dataset():
    """The Wisconsin/diabetes progression set, in raw measurement units.

    ``load_diabetes`` is the only regression dataset scikit-learn bundles
    offline; ``fetch_california_housing`` downloads and is not used here.
    ``scaled=False`` keeps the ten features in their original units (age in
    years, bmi, average blood pressure, six serum measures) so a coefficient
    would still mean something if this project stopped to interpret one --
    Day 148's point, carried forward. The target itself is a composite
    disease-progression score with no physical unit; it is not measured in
    anything, and this project never pretends otherwise.
    """
    d = load_diabetes(scaled=False)
    return d.data, d.target, list(d.feature_names)


# --------------------------------------------------------------------------
# 2. The frame and the baseline -- before any model
# --------------------------------------------------------------------------


def baseline_metrics(x_train, y_train, x_test, y_test):
    """The mean-predictor baseline: RMSE and R^2, computed before any model.

    Day 141's rule, restated for regression: a score is not evidence until
    you know what it beats. Predicting the training mean for every row is
    the simplest possible non-model.
    """
    dummy = DummyRegressor(strategy="mean").fit(x_train, y_train)
    pred = dummy.predict(x_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    r2 = float(r2_score(y_test, pred))
    return round(rmse, 4), round(r2, 4)


# --------------------------------------------------------------------------
# 3. The split -- 442 rows is small, so the test set stays small too
# --------------------------------------------------------------------------


def split_once(X, y, seed: int = 0, test_size: float = 0.25):
    """One split. The test half is touched once, later, for scoring.

    A 25 percent test set on 442 rows is about 110 rows -- small enough
    that every interval in this project is wide, and that is reported
    honestly rather than smoothed over.
    """
    return train_test_split(X, y, test_size=test_size, random_state=seed)


# --------------------------------------------------------------------------
# 4. The candidate pipelines -- ridge, lasso and plain OLS, K counted
# --------------------------------------------------------------------------

_ALPHAS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]


def candidate_configs():
    """23 candidate pipelines: 11 ridge, 11 lasso, 1 plain OLS.

    Every candidate is a scikit-learn ``Pipeline`` with a ``StandardScaler``
    ahead of the estimator, so cross-validation refits the scaler on each
    fold's training rows only -- Day 143's stage-ordering rule, enforced by
    the estimator's own contract. Returns ``(family, hyperparameter,
    make_pipeline)`` where ``make_pipeline`` is a zero-argument callable
    returning a fresh, unfitted ``Pipeline``.
    """
    configs = []
    for a in _ALPHAS:
        configs.append(
            ("ridge", a, lambda a=a: Pipeline([("scale", StandardScaler()), ("clf", Ridge(alpha=a))]))
        )
    for a in _ALPHAS:
        configs.append(
            (
                "lasso",
                a,
                lambda a=a: Pipeline(
                    [("scale", StandardScaler()), ("clf", Lasso(alpha=a, max_iter=20000))]
                ),
            )
        )
    configs.append(
        ("ols", 0.0, lambda: Pipeline([("scale", StandardScaler()), ("clf", LinearRegression())]))
    )
    return configs


def candidate_count() -> int:
    """K, the number of configurations this project actually tries."""
    return len(candidate_configs())


# --------------------------------------------------------------------------
# 5. Cross-validate, then select -- honest spending of the train rows
# --------------------------------------------------------------------------


def cross_validate_configs(x_train, y_train, seed: int = 0, folds: int = 5):
    """5-fold CV RMSE for every candidate, on train rows only.

    Returns rows of ``(family, hyperparameter, cv_rmse, cv_std)``, sorted
    best (lowest RMSE) first. RMSE is chosen as the selection metric because
    it is stated as the metric BEFORE any model is fitted -- Day 152's whole
    argument that the metric is a choice, made here in the units the target
    is actually in (unitless composite-score points, not mg/dL).
    """
    splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    rows = []
    for family, param, make in candidate_configs():
        scores = cross_val_score(make(), x_train, y_train, cv=splitter, scoring="neg_root_mean_squared_error")
        rows.append((family, param, round(float(-scores.mean()), 4), round(float(scores.std()), 4)))
    rows.sort(key=lambda r: r[2])
    return rows


def select_best(x_train, y_train, seed: int = 0, folds: int = 5):
    """Fit the winner of the sweep on the full training set.

    Returns ``(family, hyperparameter, cv_rmse, fitted_pipeline)``.
    """
    rows = cross_validate_configs(x_train, y_train, seed=seed, folds=folds)
    winner_family, winner_param, winner_cv, _sd = rows[0]
    for family, param, make_fn in candidate_configs():
        if family == winner_family and param == winner_param:
            fitted = make_fn().fit(x_train, y_train)
            return winner_family, winner_param, winner_cv, fitted
    raise RuntimeError("winning configuration vanished between sweep and refit")


# --------------------------------------------------------------------------
# 6. The test set -- one look, enforced mechanically
# --------------------------------------------------------------------------


class TestSetTouchedTwice(RuntimeError):
    """Raised when the test set is scored against more than once."""


class GatedTestSet:
    """A test set that permits exactly one scoring call, then refuses.

    Day 144's discipline, reused unchanged: the counter does not advance on
    a refused attempt, so a caller that never succeeds cannot drain the
    budget by retrying. ``evaluate`` returns ``(rmse, r2, mae)`` -- the one
    look this project spends. Reading predictions afterward for residual
    diagnostics is inspection, not a second selection, exactly as Day 147's
    confusion matrix read predictions after its own one evaluation.
    """

    def __init__(self, X, y):
        self._X = X
        self._y = y
        self.evaluations = 0

    def evaluate(self, model):
        if self.evaluations >= 1:
            raise TestSetTouchedTwice(
                "the test set has already been used once; any further score is a "
                "validation score, not a test score"
            )
        self.evaluations += 1
        pred = model.predict(self._X)
        rmse = float(np.sqrt(mean_squared_error(self._y, pred)))
        r2 = float(r2_score(self._y, pred))
        mae = float(mean_absolute_error(self._y, pred))
        return round(rmse, 4), round(r2, 4), round(mae, 4)


# --------------------------------------------------------------------------
# 7. The verdict -- a bootstrap interval around the margin
# --------------------------------------------------------------------------


def margin_bootstrap_interval(y_test, pred_baseline, pred_model, n_boot: int = 2000, seed: int = 0):
    """A 95 percent interval around the margin: baseline RMSE minus model RMSE.

    Resamples the test rows with replacement ``n_boot`` times and recomputes
    both RMSEs on each resample, so the interval reflects how much the
    margin itself could plausibly move at this test-set size -- the same
    question Day 144's accuracy interval asked, answered here for RMSE
    without an analytic formula, because RMSE's sampling distribution has
    no equally simple closed form.
    """
    rng = np.random.default_rng(seed)
    y_test = np.asarray(y_test)
    pred_baseline = np.asarray(pred_baseline)
    pred_model = np.asarray(pred_model)
    n = len(y_test)
    margins = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        rmse_base = np.sqrt(mean_squared_error(y_test[idx], pred_baseline[idx]))
        rmse_model = np.sqrt(mean_squared_error(y_test[idx], pred_model[idx]))
        margins[i] = rmse_base - rmse_model
    lower = round(float(np.percentile(margins, 2.5)), 4)
    upper = round(float(np.percentile(margins, 97.5)), 4)
    return lower, upper


def margin_distinguishable(lower: float, upper: float) -> bool:
    """Whether the bootstrap interval around the margin excludes zero.

    If the interval spans zero, the honest verdict is "cannot distinguish
    this model from the baseline at this test-set size" -- Day 144's
    cautionary case, now checked for a real margin instead of assumed away.
    """
    return lower > 0.0


# --------------------------------------------------------------------------
# 8. Residual diagnostics -- the centrepiece this day owns
# --------------------------------------------------------------------------


def _normal_ppf(p):
    """The inverse standard-normal CDF, by Acklam's rational approximation.

    Built from scratch because scipy is not one of this lab's three pinned
    dependencies -- Day 153's habit, applied again: when a tool is not
    available, build the minimal piece you need rather than reach past the
    pins. Accurate to about 1.15e-9 across the open interval (0, 1); good
    enough for a Q-Q correlation on 111 points. Public-domain algorithm,
    reference in sources.yml.
    """
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    p_low = 0.02425
    p = np.asarray(p, dtype=float)
    out = np.empty_like(p)
    low = p < p_low
    high = p > (1 - p_low)
    mid = ~(low | high)
    ql = np.sqrt(-2 * np.log(p[low]))
    out[low] = (((((c[0] * ql + c[1]) * ql + c[2]) * ql + c[3]) * ql + c[4]) * ql + c[5]) / (
        (((d[0] * ql + d[1]) * ql + d[2]) * ql + d[3]) * ql + 1
    )
    q = p[mid] - 0.5
    r = q * q
    out[mid] = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )
    qh = np.sqrt(-2 * np.log(1 - p[high]))
    out[high] = -(((((c[0] * qh + c[1]) * qh + c[2]) * qh + c[3]) * qh + c[4]) * qh + c[5]) / (
        (((d[0] * qh + d[1]) * qh + d[2]) * qh + d[3]) * qh + 1
    )
    return out


def residual_summary(y_test, pred_test):
    """Mean and standard deviation of the test residuals, y minus prediction."""
    resid = np.asarray(y_test, dtype=float) - np.asarray(pred_test, dtype=float)
    return round(float(resid.mean()), 4), round(float(resid.std()), 4)


def heteroscedasticity_signal(pred_test, y_test):
    """Correlation between the fitted value and the absolute residual.

    A value near zero means the spread of errors does not grow with the
    predicted value -- the "fanning out" pattern a residual-vs-fitted plot
    is built to catch. This is the from-scratch numeric version of reading
    that plot.
    """
    pred_test = np.asarray(pred_test, dtype=float)
    resid = np.asarray(y_test, dtype=float) - pred_test
    corr = np.corrcoef(pred_test, np.abs(resid))[0, 1]
    return round(float(corr), 4)


def curvature_signal(pred_test, y_test):
    """Correlation between the squared fitted value and the signed residual.

    A value far from zero suggests the model is missing a systematic curve
    -- residuals that trend up then down (or the reverse) as the fitted
    value rises, rather than scattering evenly around zero.
    """
    pred_test = np.asarray(pred_test, dtype=float)
    resid = np.asarray(y_test, dtype=float) - pred_test
    corr = np.corrcoef(pred_test**2, resid)[0, 1]
    return round(float(corr), 4)


def normal_probability_correlation(y_test, pred_test):
    """A from-scratch normal-probability (Q-Q) check, as one correlation.

    Standardises the residuals, sorts them, and correlates them against the
    theoretical normal quantiles a perfectly Gaussian set of residuals
    would produce. 1.0 is a perfectly straight Q-Q line; values noticeably
    below 1.0 flag departures from normality that a plotted Q-Q line would
    show as curvature at the tails.
    """
    resid = np.asarray(y_test, dtype=float) - np.asarray(pred_test, dtype=float)
    n = len(resid)
    std_resid = (resid - resid.mean()) / resid.std()
    sorted_resid = np.sort(std_resid)
    probs = (np.arange(1, n + 1) - 0.5) / n
    theoretical = _normal_ppf(probs)
    corr = np.corrcoef(theoretical, sorted_resid)[0, 1]
    return round(float(corr), 4)


def largest_residuals(y_test, pred_test, n: int = 5):
    """The n largest-magnitude residuals, inspected individually.

    Returns rows of ``(test_row_index, true_value, predicted_value,
    residual)``, sorted by |residual| descending. A confusion matrix reads
    the specific mistakes a classifier makes; this is that discipline's
    regression counterpart.
    """
    y_test = np.asarray(y_test, dtype=float)
    pred_test = np.asarray(pred_test, dtype=float)
    resid = y_test - pred_test
    order = np.argsort(-np.abs(resid))[:n]
    return [
        (int(i), round(float(y_test[i]), 4), round(float(pred_test[i]), 4), round(float(resid[i]), 4))
        for i in order
    ]


# --------------------------------------------------------------------------
# 9. Is the model worse for high-value targets? Measure it.
# --------------------------------------------------------------------------


def error_by_target_level(y_test, pred_test):
    """RMSE on the below-median half of test targets against the above-median half.

    Returns ``(rmse_low, rmse_high, ratio)`` where ``ratio`` is
    ``rmse_high / rmse_low``. On a disease-progression score this is a
    fairness-relevant question, not only a statistical one: are errors
    worse for patients whose true progression is more severe?
    """
    y_test = np.asarray(y_test, dtype=float)
    pred_test = np.asarray(pred_test, dtype=float)
    median_y = float(np.median(y_test))
    low_mask = y_test <= median_y
    high_mask = ~low_mask
    rmse_low = float(np.sqrt(mean_squared_error(y_test[low_mask], pred_test[low_mask])))
    rmse_high = float(np.sqrt(mean_squared_error(y_test[high_mask], pred_test[high_mask])))
    return round(rmse_low, 4), round(rmse_high, 4), round(rmse_high / rmse_low, 4)


# --------------------------------------------------------------------------
# 10. The leaky version -- selecting by peeking at the test set
# --------------------------------------------------------------------------


def leaky_selection_test_rmse(x_train, y_train, x_test, y_test):
    """Select the winner by fitting every candidate and scoring it on TEST.

    Returns the winning (lowest) test RMSE -- K looks disguised as one,
    Day 147's mistake, reconstructed for regression. Lower RMSE is better,
    so the leaky search can only match or beat the honestly selected
    model's own test RMSE, never lose to it.
    """
    best_rmse = None
    for _family, _param, make in candidate_configs():
        pipe = make().fit(x_train, y_train)
        pred = pipe.predict(x_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        if best_rmse is None or rmse < best_rmse:
            best_rmse = rmse
    return round(best_rmse, 4)


def leaky_vs_honest_over_seeds(X, y, seeds=range(20), folds: int = 5):
    """The gap between peeking at the test set and looking at it once.

    Returns rows of ``(seed, honest_rmse, leaky_rmse, gap)`` where
    ``gap = honest_rmse - leaky_rmse``. Because lower RMSE is better, a
    positive gap means the leak reported a lower (better-looking) error
    than the honest evaluation -- the leak can only help the reported
    number, never hurt it.
    """
    rows = []
    for seed in seeds:
        x_train, x_test, y_train, y_test = split_once(X, y, seed=seed)
        _family, _param, _cv, fitted = select_best(x_train, y_train, seed=seed, folds=folds)
        honest_rmse = float(np.sqrt(mean_squared_error(y_test, fitted.predict(x_test))))
        leaky_rmse = leaky_selection_test_rmse(x_train, y_train, x_test, y_test)
        rows.append((seed, round(honest_rmse, 4), leaky_rmse, round(honest_rmse - leaky_rmse, 4)))
    return rows


# --------------------------------------------------------------------------
# 11. Prediction intervals -- not just a point, and measured coverage
# --------------------------------------------------------------------------


def prediction_interval_coverage(x_train, y_train, x_test, y_test, fitted, seed: int = 0, folds: int = 5):
    """A constant-width 95 percent prediction interval, and its realised coverage.

    The half-width comes from the standard deviation of out-of-fold
    residuals on the TRAINING rows only (``cross_val_predict``), never from
    the test residuals themselves -- using the test residuals to size the
    test interval would be circular. Returns ``(half_width, coverage)``
    where ``coverage`` is the fraction of test targets that actually fall
    inside ``prediction +/- half_width``, measured against the nominal 0.95.
    """
    splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    oof_pred = cross_val_predict(fitted, x_train, y_train, cv=splitter)
    oof_resid = np.asarray(y_train, dtype=float) - oof_pred
    half_width = round(float(1.96 * oof_resid.std()), 4)
    pred_test = fitted.predict(x_test)
    y_test = np.asarray(y_test, dtype=float)
    lower = pred_test - half_width
    upper = pred_test + half_width
    coverage = round(float(np.mean((y_test >= lower) & (y_test <= upper))), 4)
    return half_width, coverage
