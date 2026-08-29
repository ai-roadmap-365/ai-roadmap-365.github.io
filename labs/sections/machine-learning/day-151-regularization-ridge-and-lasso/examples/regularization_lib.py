"""Ridge and lasso, measured: what the penalty does, and why the two differ
in kind rather than degree.

Day 145 already measured that a ridge penalty rescued an overfit polynomial
by a factor of 39,588, and that a penalty trades variance for bias. This
module does not re-measure that trade; it measures the CONTRAST between the
two penalty shapes: an L2 penalty that shrinks every coefficient toward zero
but never quite reaches it, and an L1 penalty that drives some coefficients
to exactly zero and leaves the rest alone.

Everything here is deterministic given a seed, and every dataset is either
scikit-learn's bundled ``load_diabetes`` or generated on the spot with
``numpy.random.default_rng`` or ``sklearn.datasets.make_regression``.
"""

from __future__ import annotations

import numpy as np

from sklearn.datasets import load_diabetes, make_regression
from sklearn.linear_model import ElasticNet, Lasso, LassoCV, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]


# --------------------------------------------------------------------------
# 1. Ridge zeros nothing; lasso zeros progressively more
# --------------------------------------------------------------------------


def load_train_test(scaled: bool = True, seed: int = 0):
    """The diabetes dataset, split the way every exercise in this lab uses.

    ``scaled=True`` is scikit-learn's own bundled version: mean-centred and
    scaled so every column has unit L2 norm. ``scaled=False`` returns the raw
    measurement units (age in years, bmi as a ratio, bp in mm Hg, and so on).
    """
    X, y = load_diabetes(return_X_y=True, scaled=scaled)
    return train_test_split(X, y, test_size=0.25, random_state=seed)


def zero_counts_and_r2(alphas):
    """For each alpha, how many lasso coefficients are exactly zero, how
    many ridge coefficients are exactly zero, and each model's test R2.

    Returns rows of ``(alpha, lasso_zeros, lasso_r2, ridge_zeros, ridge_r2)``.
    ``Lasso`` needs ``max_iter=50000`` on this dataset -- the default 1000
    does not converge and emits a ``ConvergenceWarning``.
    """
    X_train, X_test, y_train, y_test = load_train_test()
    rows = []
    for alpha in alphas:
        lasso = Lasso(alpha=alpha, max_iter=50000).fit(X_train, y_train)
        ridge = Ridge(alpha=alpha).fit(X_train, y_train)
        lasso_zeros = int(np.sum(lasso.coef_ == 0))
        ridge_zeros = int(np.sum(ridge.coef_ == 0))
        lasso_r2 = round(r2_score(y_test, lasso.predict(X_test)), 4)
        ridge_r2 = round(r2_score(y_test, ridge.predict(X_test)), 4)
        rows.append((alpha, lasso_zeros, lasso_r2, ridge_zeros, ridge_r2))
    return rows


def lasso_cv_selection():
    """The alpha LassoCV picks by 5-fold cross-validation on the training
    split, how many coefficients it zeros, and which features it keeps.
    """
    X_train, X_test, y_train, y_test = load_train_test()
    model = LassoCV(cv=5, random_state=0, max_iter=50000).fit(X_train, y_train)
    zeros = int(np.sum(model.coef_ == 0))
    kept = [name for name, coef in zip(FEATURE_NAMES, model.coef_) if coef != 0]
    return {
        "alpha": float(model.alpha_),
        "zeros": zeros,
        "kept": kept,
        "r2": round(r2_score(y_test, model.predict(X_test)), 4),
    }


# --------------------------------------------------------------------------
# 2. The coefficient path: where each lasso coefficient hits exactly zero
# --------------------------------------------------------------------------


def coefficient_path(alphas):
    """Every coefficient, for both models, at every alpha in the sweep.

    Returns ``(lasso_path, ridge_path)``, each an array of shape
    ``(len(alphas), 10)`` in ``FEATURE_NAMES`` order, fitted on the full
    diabetes dataset (scaled) so the path is not split-dependent.
    """
    X, y = load_diabetes(return_X_y=True)
    lasso_path = np.zeros((len(alphas), X.shape[1]))
    ridge_path = np.zeros((len(alphas), X.shape[1]))
    for i, alpha in enumerate(alphas):
        lasso_path[i] = Lasso(alpha=alpha, max_iter=50000).fit(X, y).coef_
        ridge_path[i] = Ridge(alpha=alpha).fit(X, y).coef_
    return lasso_path, ridge_path


def alpha_where_each_lasso_coefficient_first_hits_zero(alphas):
    """The first alpha in the (ascending) sweep at which each lasso
    coefficient becomes exactly zero, and whether ridge ever hits zero at
    any alpha in the same sweep.

    Returns ``(zero_at, ridge_ever_zero)`` where ``zero_at`` maps each name
    in ``FEATURE_NAMES`` to the alpha value, or ``None`` if it never zeroed
    inside this sweep.
    """
    lasso_path, ridge_path = coefficient_path(alphas)
    zero_at = {name: None for name in FEATURE_NAMES}
    for i, alpha in enumerate(alphas):
        for j, name in enumerate(FEATURE_NAMES):
            if lasso_path[i, j] == 0.0 and zero_at[name] is None:
                zero_at[name] = float(alpha)
    ridge_ever_zero = bool(np.any(ridge_path == 0.0))
    return zero_at, ridge_ever_zero


# --------------------------------------------------------------------------
# 3. Does lasso pick the RIGHT features? A known sparse ground truth
# --------------------------------------------------------------------------


def sparse_recovery(alpha: float, noise: float, seed: int = 0):
    """Precision and recall of lasso's selected set against a KNOWN
    informative set, on synthetic data built with ``make_regression``.

    20 features, 5 informative, 200 rows. Returns
    ``(precision, recall, n_selected)``.
    """
    X, y, coef = make_regression(
        n_samples=200, n_features=20, n_informative=5, noise=noise, coef=True, random_state=seed
    )
    true_set = set(np.nonzero(coef)[0].tolist())
    model = Lasso(alpha=alpha, max_iter=50000).fit(X, y)
    picked = set(np.nonzero(model.coef_)[0].tolist())
    if not picked:
        return 0.0, 0.0, 0
    true_positives = len(true_set & picked)
    precision = round(true_positives / len(picked), 4)
    recall = round(true_positives / len(true_set), 4)
    return precision, recall, len(picked)


def sparse_recovery_grid(alphas, noises, seed: int = 0):
    """``sparse_recovery`` over every combination of alpha and noise.

    Returns rows of ``(alpha, noise, precision, recall, n_selected)``.
    """
    rows = []
    for noise in noises:
        for alpha in alphas:
            precision, recall, n_selected = sparse_recovery(alpha, noise, seed=seed)
            rows.append((alpha, noise, precision, recall, n_selected))
    return rows


def sparse_recovery_across_seeds(alpha: float, noise: float, seeds=range(10)):
    """``sparse_recovery`` averaged over several dataset seeds, so the
    finding does not rest on one lucky draw. Returns
    ``(mean_precision, mean_recall)``, each rounded to 4 places.
    """
    precisions = []
    recalls = []
    for seed in seeds:
        precision, recall, _n_selected = sparse_recovery(alpha, noise, seed=seed)
        precisions.append(precision)
        recalls.append(recall)
    return round(float(np.mean(precisions)), 4), round(float(np.mean(recalls)), 4)


# --------------------------------------------------------------------------
# 4. Scale-dependence: the penalty lives in whatever units the coefficients
#    happen to be in
# --------------------------------------------------------------------------


def scale_dependence(alpha: float = 1.0):
    """Lasso's selected feature set on the SAME data in three different
    units, at the SAME alpha: raw measurement units, standardised to unit
    variance, and scikit-learn's own bundled convention (unit L2 norm).

    Returns a dict with one entry per convention: ``kept`` (the feature
    names with a nonzero coefficient) and ``n_kept``.
    """
    X_raw, y = load_diabetes(return_X_y=True, scaled=False)
    X_unit_norm, _ = load_diabetes(return_X_y=True)  # sklearn's own scaled=True
    X_unit_variance = StandardScaler().fit_transform(X_raw)

    results = {}
    for label, X in (
        ("raw", X_raw),
        ("standardized", X_unit_variance),
        ("sklearn_unit_norm", X_unit_norm),
    ):
        model = Lasso(alpha=alpha, max_iter=50000).fit(X, y)
        kept = [name for name, coef in zip(FEATURE_NAMES, model.coef_) if coef != 0]
        results[label] = {"kept": kept, "n_kept": len(kept)}
    return results


# --------------------------------------------------------------------------
# 5. ElasticNet: the combination, and the alpha convention it does NOT share
#    with Ridge
# --------------------------------------------------------------------------


def elasticnet_sweep(alpha: float, l1_ratios):
    """ElasticNet's zero count and test R2 as l1_ratio moves from 0 (pure
    L2) to 1 (pure L1), at a fixed alpha, on the diabetes split.

    Returns rows of ``(l1_ratio, zeros, r2)``.
    """
    X_train, X_test, y_train, y_test = load_train_test()
    rows = []
    for l1_ratio in l1_ratios:
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=50000).fit(X_train, y_train)
        zeros = int(np.sum(model.coef_ == 0))
        r2 = round(r2_score(y_test, model.predict(X_test)), 4)
        rows.append((l1_ratio, zeros, r2))
    return rows


def ridge_elasticnet_equivalence(alpha: float = 0.1):
    """Ridge and ElasticNet(l1_ratio=1) both define an L2-only penalty, but
    at DIFFERENT alpha scales: Ridge's objective sums the squared error,
    ElasticNet's averages it over n_samples. This measures the correction
    factor and confirms the two models agree once it is applied.

    Returns ``(ridge_coef_head, elasticnet_coef_head, max_abs_difference)``
    for the first three coefficients, after refitting Ridge at
    ``alpha * n_train``.
    """
    X_train, X_test, y_train, y_test = load_train_test()
    n_train = X_train.shape[0]
    ridge = Ridge(alpha=alpha * n_train).fit(X_train, y_train)
    elastic = ElasticNet(alpha=alpha, l1_ratio=0.0, max_iter=50000).fit(X_train, y_train)
    max_diff = float(np.max(np.abs(ridge.coef_ - elastic.coef_)))
    return ridge.coef_[:3].round(4).tolist(), elastic.coef_[:3].round(4).tolist(), round(max_diff, 4)


# --------------------------------------------------------------------------
# 6. Correlated predictors: ridge splits the weight, lasso picks one
# --------------------------------------------------------------------------


def near_duplicate_dataset(n: int = 300, seed: int = 0):
    """Two columns built from the same underlying signal plus tiny
    independent noise, so they are correlated at essentially 1.0, and a
    third column that is genuinely independent.
    """
    rng = np.random.default_rng(seed)
    base = rng.normal(size=n)
    x1 = base + rng.normal(scale=0.01, size=n)
    x2 = base + rng.normal(scale=0.01, size=n)
    x3 = rng.normal(size=n)
    X = np.column_stack([x1, x2, x3])
    y = 3.0 * x1 + 3.0 * x2 + 1.0 * x3 + rng.normal(scale=0.5, size=n)
    correlation = float(np.corrcoef(x1, x2)[0, 1])
    return X, y, correlation


def ridge_vs_lasso_on_duplicates(alphas):
    """Ridge and lasso coefficients on the near-duplicate dataset, at each
    alpha. Returns rows of ``(alpha, ridge_coefs, lasso_coefs)``, each a
    3-element list rounded to 4 places, in ``(x1, x2, x3)`` order.
    """
    X, y, _correlation = near_duplicate_dataset()
    rows = []
    for alpha in alphas:
        ridge = Ridge(alpha=alpha).fit(X, y)
        lasso = Lasso(alpha=alpha, max_iter=50000).fit(X, y)
        rows.append((alpha, ridge.coef_.round(4).tolist(), lasso.coef_.round(4).tolist()))
    return rows


# --------------------------------------------------------------------------
# 7. Ridge has a closed form; lasso does not
# --------------------------------------------------------------------------


def lasso_iteration_counts(alphas):
    """How many coordinate-descent iterations ``Lasso`` needed to converge,
    at each alpha, on the diabetes training split. Ridge has no equivalent
    attribute: it is solved directly by a single linear-algebra call, never
    iterated.
    """
    X_train, _X_test, y_train, _y_test = load_train_test()
    counts = {}
    for alpha in alphas:
        model = Lasso(alpha=alpha, max_iter=50000).fit(X_train, y_train)
        counts[alpha] = int(model.n_iter_)
    return counts


def ridge_has_no_iteration_count():
    """Confirm a fitted Ridge model carries no ``n_iter_`` under its default
    (closed-form) solver, unlike a fitted Lasso model.
    """
    X_train, _X_test, y_train, _y_test = load_train_test()
    ridge = Ridge(alpha=1.0).fit(X_train, y_train)
    lasso = Lasso(alpha=1.0, max_iter=50000).fit(X_train, y_train)
    return {
        "ridge_solver": ridge.solver,
        "ridge_has_n_iter": hasattr(ridge, "n_iter_") and ridge.n_iter_ is not None,
        "lasso_has_n_iter": hasattr(lasso, "n_iter_") and lasso.n_iter_ is not None,
    }


# --------------------------------------------------------------------------
# 8. The corner, in the smallest case that shows it: two correlated features
# --------------------------------------------------------------------------


def two_feature_dataset(n: int = 200, seed: int = 3):
    """Two strongly correlated features and a real, equal-weighted signal,
    small enough to draw. Returns ``(X, y, correlation)``.
    """
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = 0.9 * x1 + rng.normal(scale=0.3, size=n)
    X = np.column_stack([x1, x2])
    y = 2.0 * x1 + 2.0 * x2 + rng.normal(scale=1.0, size=n)
    correlation = float(np.corrcoef(x1, x2)[0, 1])
    return X, y, correlation


def two_feature_corner_demo(alphas):
    """Ridge and lasso coefficients on the two-feature dataset, at each
    alpha, alongside the unregularised (OLS) coefficients for reference.

    Returns ``(ols_coef, rows)`` where each row is
    ``(alpha, ridge_coefs, lasso_coefs)``, coefficients rounded to 4 places.
    """
    from sklearn.linear_model import LinearRegression

    X, y, _correlation = two_feature_dataset()
    ols = LinearRegression().fit(X, y).coef_.round(4).tolist()
    rows = []
    for alpha in alphas:
        ridge = Ridge(alpha=alpha).fit(X, y)
        lasso = Lasso(alpha=alpha, max_iter=50000).fit(X, y)
        rows.append((alpha, ridge.coef_.round(4).tolist(), lasso.coef_.round(4).tolist()))
    return ols, rows
