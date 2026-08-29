"""Many predictors, measured: what changes when there is more than one.

Day 148 covered the line through one predictor. Day 149 covered why the
loss is squared error. This module measures what is new once a second
predictor joins the first: a coefficient's meaning becomes conditional on
"holding the others constant", and when predictors are correlated with
each other -- not just with the target -- that condition gets expensive.

The centrepiece is a duplicated predictor. Two columns that carry the same
information cannot be told apart by the normal equations, so the fit
smears one true effect across both coefficients in whatever proportion
happens to minimise squared error that day -- while the *sum* of the two
coefficients, and every prediction the model makes, barely moves at all.

Everything here is deterministic given a seed, and every dataset is either
the bundled `sklearn.datasets.load_diabetes(scaled=False)` -- ten raw-unit
clinical predictors, real measurements, no download -- or built from it.
"""

from __future__ import annotations

import numpy as np

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


# --------------------------------------------------------------------------
# 0. The dataset itself
# --------------------------------------------------------------------------


def load_raw_diabetes():
    """The ten raw-unit predictors and the target, with feature names.

    `scaled=False` matters: it returns age in years, sex coded 1/2, bmi,
    average blood pressure, and six serum measurements s1-s6 in their
    original units, which is what makes a coefficient's magnitude mean
    anything. The default `scaled=True` mean-centres and unit-norm scales
    every column before you ever see it -- exercise 8 measures exactly
    what that substitution does and does not change.
    """
    bunch = load_diabetes(scaled=False)
    return bunch.data, bunch.target, list(bunch.feature_names)


def fit(X, y):
    """A plain ordinary-least-squares fit -- the one tool this lesson uses."""
    return LinearRegression().fit(X, y)


# --------------------------------------------------------------------------
# 1. Correlation and variance inflation
# --------------------------------------------------------------------------


def correlation(X, names, a: str, b: str) -> float:
    """The Pearson correlation between two named predictor columns."""
    i, j = names.index(a), names.index(b)
    return float(np.corrcoef(X[:, i], X[:, j])[0, 1])


def variance_inflation_factors(X, names) -> dict:
    """VIF for every column: regress it on the rest, VIF = 1 / (1 - R2).

    A VIF of 1 means a predictor is unrelated to the others. Above 5 or 10
    is the usual rule of thumb for "correlated enough to worry about" --
    this function does not apply the rule, it only computes the number the
    rule is applied to.
    """
    result = {}
    for i, name in enumerate(names):
        others = np.delete(X, i, axis=1)
        target = X[:, i]
        r2 = LinearRegression().fit(others, target).score(others, target)
        result[name] = float("inf") if r2 >= 1.0 else round(1.0 / (1.0 - r2), 4)
    return result


# --------------------------------------------------------------------------
# 2. The centrepiece: an exact duplicate column
# --------------------------------------------------------------------------


def duplicate_column_exact(X, y, col_index: int):
    """Append an exact copy of one column and refit.

    Returns ``(original_coef, dup_coef_a, dup_coef_b, max_abs_pred_diff,
    r2_original, r2_dup)``. The two duplicate coefficients need not equal
    the original one individually -- only their sum does, because the
    normal equations only ever "see" the combined effect of two identical
    columns, and there is no unique way to split it.
    """
    original = fit(X, y)
    X_dup = np.hstack([X, X[:, [col_index]]])
    dup = fit(X_dup, y)
    pred_original = original.predict(X)
    pred_dup = dup.predict(X_dup)
    return (
        float(original.coef_[col_index]),
        float(dup.coef_[col_index]),
        float(dup.coef_[-1]),
        float(np.max(np.abs(pred_dup - pred_original))),
        float(original.score(X, y)),
        float(dup.score(X_dup, y)),
    )


def duplicate_column_noisy(X, y, col_index: int, noise_scale: float, seed: int):
    """Append a near-duplicate: the same column plus a little noise.

    Breaking the exact tie lets ordinary least squares pick a *unique*
    split of the combined effect again -- but which split it picks depends
    on which way the noise happened to fall, which is the whole point.
    Returns ``(coef_a, coef_b, sum_coefs, max_abs_pred_diff, r2)``.
    """
    original = fit(X, y)
    pred_original = original.predict(X)
    rng = np.random.default_rng(seed)
    noise = rng.normal(scale=noise_scale, size=X.shape[0])
    near_dup = X[:, col_index] + noise
    X_noisy = np.hstack([X, near_dup.reshape(-1, 1)])
    model = fit(X_noisy, y)
    pred = model.predict(X_noisy)
    return (
        float(model.coef_[col_index]),
        float(model.coef_[-1]),
        float(model.coef_[col_index] + model.coef_[-1]),
        float(np.max(np.abs(pred - pred_original))),
        float(model.score(X_noisy, y)),
    )


def spread(values) -> dict:
    """Mean, standard deviation, minimum and maximum, rounded for reporting."""
    values = np.asarray(values, dtype=float)
    return {
        "mean": round(float(values.mean()), 4),
        "sd": round(float(values.std()), 4),
        "min": round(float(values.min()), 4),
        "max": round(float(values.max()), 4),
    }


def duplicate_noisy_spread(X, y, col_index: int, noise_scale: float, seeds) -> dict:
    """Across many noise draws: how the two coefficients wander, and how
    their sum, the predictions and R2 do not.

    Returns a dict with ``coef_a``, ``coef_b`` and ``sum`` spreads (each
    from :func:`spread`), plus ``max_pred_diff`` (the largest single
    prediction movement seen across every seed) and an ``r2`` spread.
    """
    coef_a, coef_b, coef_sum, max_diffs, r2s = [], [], [], [], []
    for seed in seeds:
        a, b, total, max_diff, r2 = duplicate_column_noisy(X, y, col_index, noise_scale, seed)
        coef_a.append(a)
        coef_b.append(b)
        coef_sum.append(total)
        max_diffs.append(max_diff)
        r2s.append(r2)
    return {
        "coef_a": spread(coef_a),
        "coef_b": spread(coef_b),
        "sum": spread(coef_sum),
        "max_pred_diff_overall": round(max(max_diffs), 4),
        "r2": spread(r2s),
    }


# --------------------------------------------------------------------------
# 3. Bootstrap coefficient instability, across all ten predictors
# --------------------------------------------------------------------------


def bootstrap_coefficient_spread(X, y, names, reps: int = 500, seed: int = 0) -> dict:
    """Resample the rows with replacement, refit, and record each coefficient.

    Returns ``{name: {"mean": ..., "sd": ..., "cv": ...}}`` where ``cv`` is
    the coefficient of variation, ``abs(sd / mean)`` -- a scale-free way to
    compare how much a coefficient wanders relative to its own size.
    """
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    collected = {name: [] for name in names}
    for _ in range(reps):
        idx = rng.integers(0, n, size=n)
        model = fit(X[idx], y[idx])
        for i, name in enumerate(names):
            collected[name].append(model.coef_[i])
    result = {}
    for name in names:
        arr = np.asarray(collected[name])
        mean = float(arr.mean())
        sd = float(arr.std())
        result[name] = {
            "mean": round(mean, 4),
            "sd": round(sd, 4),
            "cv": round(abs(sd / mean), 4) if mean != 0 else None,
        }
    return result


# --------------------------------------------------------------------------
# 4. What "holding the others constant" changes: simple vs. multiple
# --------------------------------------------------------------------------


def simple_vs_multiple_coefficients(X, y, names) -> dict:
    """Each predictor's coefficient alone, and again inside the full model.

    Returns ``{name: {"simple": ..., "multiple": ..., "sign_flip": bool}}``.
    A sign flip means the predictor's *apparent* relationship with the
    target, taken alone, points the opposite way from its *conditional*
    relationship once the other nine predictors are held constant.
    """
    result = {}
    full = fit(X, y)
    for i, name in enumerate(names):
        alone = fit(X[:, [i]], y)
        simple_coef = float(alone.coef_[0])
        multiple_coef = float(full.coef_[i])
        result[name] = {
            "simple": round(simple_coef, 4),
            "multiple": round(multiple_coef, 4),
            "sign_flip": bool(np.sign(simple_coef) != np.sign(multiple_coef)),
        }
    return result


# --------------------------------------------------------------------------
# 5. A polynomial fit is linear in its parameters
# --------------------------------------------------------------------------


def polynomial_matches_normal_equations(X2, y, degree: int = 2, feature_names=None):
    """PolynomialFeatures + LinearRegression against a direct normal-equations solve.

    Builds the degree-``degree`` design matrix two ways: once through
    scikit-learn's transformer-plus-estimator pipeline, once by hand with
    ``numpy.linalg.lstsq`` on the identical expanded matrix. If a
    polynomial fit really is "linear in its parameters, not in x", the two
    must agree to floating-point precision, because they are solving the
    same linear system.

    Returns ``(feature_names, sklearn_coefs, sklearn_intercept,
    normal_eq_coefs, normal_eq_intercept, max_abs_coef_diff,
    max_abs_intercept_diff)``.
    """
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly.fit_transform(X2)
    expanded_names = list(poly.get_feature_names_out(feature_names))

    sklearn_model = fit(X_poly, y)

    design = np.hstack([np.ones((X_poly.shape[0], 1)), X_poly])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)

    coef_diff = float(np.max(np.abs(beta[1:] - sklearn_model.coef_)))
    intercept_diff = float(abs(beta[0] - sklearn_model.intercept_))

    return (
        expanded_names,
        [round(float(c), 6) for c in sklearn_model.coef_],
        round(float(sklearn_model.intercept_), 6),
        [round(float(b), 6) for b in beta[1:]],
        round(float(beta[0]), 6),
        coef_diff,
        intercept_diff,
    )


def interaction_term_effect(X2, y):
    """Compare a degree-2 fit with and without its interaction term.

    ``bmi^2`` and ``bp^2`` describe how each predictor curves on its own.
    ``bmi bp`` describes something neither can: whether the *effect* of
    one depends on the level of the other. Drop it and refit on the
    remaining four columns; the gap in R2 is what the interaction term was
    buying.

    Returns ``(r2_with_interaction, r2_without_interaction,
    interaction_coefficient)``.
    """
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X2)
    feature_names = list(poly.get_feature_names_out(["a", "b"]))
    interaction_index = feature_names.index("a b")

    with_interaction = fit(X_poly, y)
    X_without = np.delete(X_poly, interaction_index, axis=1)
    without_interaction = fit(X_without, y)

    return (
        float(with_interaction.score(X_poly, y)),
        float(without_interaction.score(X_without, y)),
        float(with_interaction.coef_[interaction_index]),
    )


# --------------------------------------------------------------------------
# 6. R-squared never decreases when you add a predictor -- even noise
# --------------------------------------------------------------------------


def r2_with_added_noise_columns(X, y, noise_counts, seed: int = 42) -> list:
    """R2 of the fit as pure-noise columns are appended, one count at a time.

    Returns rows of ``(n_noise_columns, r2, delta_from_baseline)``. Every
    added column is `numpy.random.default_rng` noise with no relationship
    to the target whatsoever -- Day 152 owns the fix (adjusted R2); this
    function only measures the problem it fixes.
    """
    base_r2 = fit(X, y).score(X, y)
    rng = np.random.default_rng(seed)
    rows = []
    for n_noise in noise_counts:
        noise_columns = rng.normal(size=(X.shape[0], n_noise))
        X_aug = np.hstack([X, noise_columns])
        r2 = fit(X_aug, y).score(X_aug, y)
        rows.append((n_noise, round(r2, 6), round(r2 - base_r2, 6)))
    return rows


# --------------------------------------------------------------------------
# 7. Scaling changes the coefficients, not the model
# --------------------------------------------------------------------------


def scaling_effect(X, y):
    """Fit on raw units and on standardised units; compare everything.

    Returns ``(raw_coefs, scaled_coefs, raw_r2, scaled_r2,
    max_abs_pred_diff)``. Standardising centres and unit-variance-scales
    every column before fitting, which changes what one unit of a
    predictor means and therefore changes every coefficient's size -- but
    changes nothing about what the model actually predicts.
    """
    raw_model = fit(X, y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    scaled_model = fit(X_scaled, y)

    pred_raw = raw_model.predict(X)
    pred_scaled = scaled_model.predict(X_scaled)

    return (
        [round(float(c), 4) for c in raw_model.coef_],
        [round(float(c), 4) for c in scaled_model.coef_],
        float(raw_model.score(X, y)),
        float(scaled_model.score(X_scaled, y)),
        float(np.max(np.abs(pred_raw - pred_scaled))),
    )
