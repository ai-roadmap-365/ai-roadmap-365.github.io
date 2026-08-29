"""The estimator API, measured: what fit/predict/score/get_params/set_params
actually buy you, and where the "it's just a protocol" story needs a footnote.

Days 141-145 called `.fit()` and `.predict()` on scikit-learn objects
without ever explaining what those calls mean. This module builds a
classifier from first principles -- no inheritance at all -- to show that
the four core verbs are a protocol you can implement yourself, and then
measures exactly where that protocol stops being sufficient on its own in
this version of the library.

Everything here is deterministic given a seed, except the two functions
that exist specifically to measure what `random_state=None` costs, which
are documented as such.
"""

from __future__ import annotations

import subprocess
import sys

import numpy as np

from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils import all_estimators
from sklearn.utils.estimator_checks import check_estimator
from sklearn.utils.validation import check_is_fitted, validate_data


def accuracy(y_true, y_pred) -> float:
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


# --------------------------------------------------------------------------
# 1. A classifier built entirely from first principles
# --------------------------------------------------------------------------


class MajorityClassifier:
    """fit/predict/score/get_params/set_params, written out by hand.

    Nothing here inherits from scikit-learn. `__init__` stores its
    hyper-parameter exactly as given and computes nothing; `fit` is where
    everything named with a trailing underscore gets learned. It always
    predicts the class that was most frequent in the training labels --
    exactly what ``DummyClassifier(strategy="most_frequent")`` does, which
    is what makes its output directly checkable against the library.
    """

    def __init__(self, strategy: str = "most_frequent"):
        self.strategy = strategy

    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)
        self.classes_, counts = np.unique(y, return_counts=True)
        self.majority_class_ = self.classes_[np.argmax(counts)]
        self.n_features_in_ = X.shape[1]
        return self

    def _require_fitted(self):
        if not hasattr(self, "majority_class_"):
            raise NotFittedError(
                "This MajorityClassifier instance is not fitted yet. Call "
                "'fit' with appropriate arguments before using this estimator."
            )

    def predict(self, X):
        self._require_fitted()
        X = np.asarray(X)
        return np.full(X.shape[0], self.majority_class_)

    def predict_proba(self, X):
        self._require_fitted()
        X = np.asarray(X)
        row = np.zeros(len(self.classes_))
        row[int(np.argmax(self.classes_ == self.majority_class_))] = 1.0
        return np.tile(row, (X.shape[0], 1))

    def score(self, X, y):
        return accuracy(y, self.predict(X))

    def get_params(self, deep: bool = True) -> dict:
        return {"strategy": self.strategy}

    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
        return self


class MajorityClassifierBase(ClassifierMixin, BaseEstimator):
    """The same classifier, this time built on scikit-learn's own base classes.

    `get_params` and `set_params` are gone from the source -- `BaseEstimator`
    supplies both by inspecting `__init__`'s signature, which is why
    `__init__` must do nothing but store its arguments: the introspection
    only works if the parameter names and the stored attribute names match
    exactly. What else `BaseEstimator` supplies, silently, is
    `__sklearn_tags__` -- which exercise 3 shows is no longer optional for
    `Pipeline` and `cross_val_score` in this version.
    """

    def __init__(self, strategy: str = "most_frequent"):
        self.strategy = strategy

    def fit(self, X, y):
        X, y = validate_data(self, X, y)
        self.classes_, counts = np.unique(y, return_counts=True)
        self.majority_class_ = self.classes_[np.argmax(counts)]
        self.class_prior_ = counts / counts.sum()
        return self

    def predict(self, X):
        check_is_fitted(self)
        X = validate_data(self, X, reset=False)
        return np.full(X.shape[0], self.majority_class_)

    def predict_proba(self, X):
        check_is_fitted(self)
        X = validate_data(self, X, reset=False)
        row = np.zeros(len(self.classes_))
        row[int(np.argmax(self.class_prior_))] = 1.0
        return np.tile(row, (X.shape[0], 1))


# --------------------------------------------------------------------------
# 2. Datasets shared by the exercises below
# --------------------------------------------------------------------------


def classification_dataset(n: int = 150, n_features: int = 4, n_classes: int = 3, seed: int = 42):
    """A small, well-separated classification dataset. Nothing rare, nothing grouped."""
    rng = np.random.default_rng(seed)
    centers = rng.normal(scale=4.0, size=(n_classes, n_features))
    y = rng.integers(0, n_classes, size=n)
    X = centers[y] + rng.normal(size=(n, n_features))
    return X, y


def skewed_dataset(n: int = 80, seed: int = 0):
    """A dataset with a clear majority class, for the DummyClassifier comparison."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    y = rng.integers(0, 3, size=n)
    y[: (2 * n) // 3] = 0  # force an unambiguous majority
    return X, y


# --------------------------------------------------------------------------
# 3. Does the hand-built estimator agree with the library one?
# --------------------------------------------------------------------------


def matches_dummy_classifier(seeds=range(5)) -> bool:
    """True only if MajorityClassifier's output is byte-identical to DummyClassifier's."""
    for seed in seeds:
        X, y = skewed_dataset(n=60 + seed * 11, seed=seed)
        ours = MajorityClassifier().fit(X, y)
        theirs = DummyClassifier(strategy="most_frequent").fit(X, y)
        if not np.array_equal(ours.predict(X), theirs.predict(X)):
            return False
        if not np.array_equal(ours.predict_proba(X), theirs.predict_proba(X)):
            return False
    return True


# --------------------------------------------------------------------------
# 4. What fitting actually adds
# --------------------------------------------------------------------------


def gained_attributes(estimator, X, y) -> list[str]:
    """dir(estimator) after fit, minus dir(estimator) before -- what fit() adds."""
    before = set(dir(estimator))
    estimator.fit(X, y)
    after = set(dir(estimator))
    return sorted(after - before)


def predict_before_fit_message(estimator, n_features: int = 4) -> str:
    """Call predict on an unfitted estimator and return the exception's message."""
    try:
        estimator.predict(np.zeros((3, n_features)))
    except NotFittedError as exc:
        return str(exc)
    raise AssertionError("predict() on an unfitted estimator did not raise NotFittedError")


# --------------------------------------------------------------------------
# 5. get_params, set_params, and clone
# --------------------------------------------------------------------------


def params_roundtrip(estimator, **overrides) -> dict:
    """set_params with overrides, then get_params -- the values that made the round trip."""
    estimator.set_params(**overrides)
    return estimator.get_params()


def clone_is_fresh(fitted_estimator, fitted_attr: str) -> dict:
    """clone() of a fitted estimator: same hyper-parameters, no learned state."""
    fresh = clone(fitted_estimator)
    return {
        "params_equal": fresh.get_params() == fitted_estimator.get_params(),
        "fresh_is_unfitted": not hasattr(fresh, fitted_attr),
        "original_still_fitted": hasattr(fitted_estimator, fitted_attr),
    }


# --------------------------------------------------------------------------
# 6. Pipeline and ColumnTransformer are estimators themselves
# --------------------------------------------------------------------------


def pipeline_param_keys(pipeline) -> list[str]:
    return sorted(pipeline.get_params(deep=True).keys())


def pipeline_set_nested(pipeline, **overrides):
    """set_params on the pipeline, addressing a step's own parameter by name."""
    pipeline.set_params(**overrides)
    return pipeline.get_params(deep=True)


class _CountingScaler(StandardScaler):
    """A StandardScaler that counts how many times fit() is actually called."""

    calls = 0

    def fit(self, X, y=None):
        type(self).calls += 1
        return super().fit(X, y)


def fits_per_fold(X, y, folds: int = 5, seed: int = 0) -> int:
    """How many times a preprocessing step inside a Pipeline is fit, under k-fold CV.

    Not a re-measurement of Day 143's leaked-preprocessing cost. This
    measures the mechanism that makes the leak impossible in the first
    place: cross_val_score clones the whole pipeline once per fold and
    fits the clone on that fold's training rows only.
    """
    _CountingScaler.calls = 0
    pipe = Pipeline([("scaler", _CountingScaler()), ("clf", LogisticRegression(max_iter=1000))])
    cross_val_score(pipe, X, y, cv=StratifiedKFold(folds, shuffle=True, random_state=seed))
    return _CountingScaler.calls


# --------------------------------------------------------------------------
# 7. Where "just a protocol" needs a footnote
# --------------------------------------------------------------------------


def bare_estimator_breaks_in_cross_val_score(X, y, folds: int = 5, seed: int = 0) -> str:
    """cross_val_score on the from-scratch estimator that inherits nothing.

    fit/predict/score/get_params/set_params all work fine when called
    directly. This is what stops working the moment scikit-learn's OWN
    machinery -- not our code -- needs to check whether the estimator is
    fitted, which in this version happens through `__sklearn_tags__`.
    Returns the exact AttributeError message raised.
    """
    try:
        cross_val_score(
            MajorityClassifier(), X, y, cv=StratifiedKFold(folds, shuffle=True, random_state=seed)
        )
    except AttributeError as exc:
        return str(exc)
    raise AssertionError("cross_val_score did not fail on the bare estimator, unexpectedly")


def base_estimator_works_in_pipeline_and_cv(X, y, folds: int = 5, seed: int = 0):
    """The identical classifier, inheriting ClassifierMixin and BaseEstimator,
    inside a real Pipeline, scored with a real cross_val_score."""
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", MajorityClassifierBase())])
    return cross_val_score(pipe, X, y, cv=StratifiedKFold(folds, shuffle=True, random_state=seed))


# --------------------------------------------------------------------------
# 8. How many estimators implement fit?
# --------------------------------------------------------------------------


def _bare_estimator_count() -> int:
    """How many estimators all_estimators() reports in a brand-new interpreter.

    Measured via a fresh subprocess, deliberately, rather than in-process.
    Importing sklearn.experimental.enable_halving_search_cv anywhere in a
    running process registers HalvingGridSearchCV and HalvingRandomSearchCV
    PERMANENTLY for that process's remaining lifetime -- there is no way to
    un-register them. So a second in-process call to this module's own
    census, later in the same pytest session, would otherwise silently
    report the already-enabled count even when asked for the bare one. A
    subprocess has no such history and is bare every single time.
    """
    result = subprocess.run(
        [sys.executable, "-c", "from sklearn.utils import all_estimators; print(len(all_estimators()))"],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout.strip())


def estimator_census() -> dict:
    """A census of every estimator scikit-learn's own discovery mechanism finds.

    "How many estimators does scikit-learn have" has no single answer --
    all_estimators() only finds estimators registered in modules that have
    actually been imported. HalvingGridSearchCV and HalvingRandomSearchCV
    live behind sklearn.experimental.enable_halving_search_cv and are
    invisible until that import runs, whether by this function or by pure
    accident somewhere upstream (scikit-learn's own estimator_checks module
    imports it transitively, which is precisely how this was first noticed:
    the count differed depending on what had already been imported before
    this function ran). The import below is explicit for exactly that
    reason -- so the "enabled" count is deterministic regardless of the
    caller's import history, and the gap between the two counts is reported
    rather than hidden.
    """
    bare_total = _bare_estimator_count()

    # Explicit and local: makes the two Halving search estimators visible to
    # all_estimators() regardless of what any caller has already imported.
    from sklearn.experimental import enable_halving_search_cv  # noqa: F401

    discovered = all_estimators()
    total = len(discovered)
    has_fit = sum(1 for _name, klass in discovered if hasattr(klass, "fit"))
    has_transform = sum(1 for _name, klass in discovered if hasattr(klass, "transform"))
    has_predict = sum(1 for _name, klass in discovered if hasattr(klass, "predict"))
    both = sorted(
        name for name, klass in discovered if hasattr(klass, "transform") and hasattr(klass, "predict")
    )
    newly_visible = sorted(
        name for name, _klass in discovered if name in ("HalvingGridSearchCV", "HalvingRandomSearchCV")
    )
    return {
        "bare_total": bare_total,
        "total": total,
        "newly_visible_after_experimental_enable": newly_visible,
        "has_fit": has_fit,
        "has_transform": has_transform,
        "has_predict": has_predict,
        "both_transform_and_predict": both,
    }


# --------------------------------------------------------------------------
# 9. predict, predict_proba, decision_function
# --------------------------------------------------------------------------


def proba_argmax_matches_predict(X, y) -> bool:
    model = LogisticRegression(max_iter=1000).fit(X, y)
    proba = model.predict_proba(X)
    predicted_by_proba = model.classes_[np.argmax(proba, axis=1)]
    return bool(np.array_equal(predicted_by_proba, model.predict(X)))


def decision_function_matches_predict(X, y) -> bool:
    model = LogisticRegression(max_iter=1000).fit(X, y)
    df = model.decision_function(X)
    if df.ndim == 1:
        predicted = model.classes_[(df > 0).astype(int)]
    else:
        predicted = model.classes_[np.argmax(df, axis=1)]
    return bool(np.array_equal(predicted, model.predict(X)))


# --------------------------------------------------------------------------
# 10. random_state: what None actually costs
# --------------------------------------------------------------------------


def random_state_reproducibility(X, y, repeats: int = 5, spread_repeats: int = 20, split_seed: int = 0) -> dict:
    """Fit the same forest repeatedly with a fixed seed, then with none at all.

    The `random_state=42` half of this is fully deterministic. The
    `random_state=None` half draws fresh entropy from the OS on every call
    by design -- that unpredictability is exactly what is being measured --
    so only structural facts about it are asserted anywhere in this lab:
    that the fixed half is identical every time, that the unseeded half is
    not, and that its accuracy genuinely varies.
    """
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=split_seed)

    fixed_preds = []
    for _ in range(repeats):
        model = RandomForestClassifier(n_estimators=50, random_state=42).fit(Xtr, ytr)
        fixed_preds.append(tuple(model.predict(Xte).tolist()))

    none_preds = []
    for _ in range(repeats):
        model = RandomForestClassifier(n_estimators=50, random_state=None).fit(Xtr, ytr)
        none_preds.append(tuple(model.predict(Xte).tolist()))

    accs = []
    for _ in range(spread_repeats):
        model = RandomForestClassifier(n_estimators=50, random_state=None).fit(Xtr, ytr)
        accs.append(accuracy(yte, model.predict(Xte)))

    return {
        "fixed_identical_across_repeats": len(set(fixed_preds)) == 1,
        "none_distinct_prediction_vectors": len(set(none_preds)),
        "none_repeats": repeats,
        "accuracy_spread_min": round(min(accs), 4),
        "accuracy_spread_max": round(max(accs), 4),
        "accuracy_spread_sd": round(float(np.std(accs)), 4),
    }


# --------------------------------------------------------------------------
# 11. The estimator contract, checked mechanically
# --------------------------------------------------------------------------


def check_estimator_report(estimator) -> dict:
    """Run scikit-learn's own estimator_checks against `estimator` and report honestly."""
    results: dict[str, str] = {}

    def record(*, estimator, check_name, exception, status, expected_to_fail, expected_to_fail_reason):
        results[check_name] = status

    check_estimator(estimator, on_fail=None, on_skip=None, callback=record)

    return {
        "total": len(results),
        "passed": sum(1 for v in results.values() if v == "passed"),
        "failed": sorted(k for k, v in results.items() if v == "failed"),
        "skipped": sorted(k for k, v in results.items() if v == "skipped"),
    }
