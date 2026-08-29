# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are structural or mechanical facts, not measurements that happened
to come out a certain way.

- **`MajorityClassifier`'s predictions and probabilities equal
  `DummyClassifier(strategy="most_frequent")`'s, exactly.** Both compute
  the same rule from the same training labels; there is no numerical
  approximation anywhere in either.
- **Fitting a `LogisticRegression` adds exactly five attributes, every one
  ending in `_`:** `classes_`, `coef_`, `intercept_`, `n_features_in_`,
  `n_iter_`. This is `dir()` before `fit()` diffed against `dir()` after.
- **`clone()` never carries learned state forward.** A cloned estimator
  has the same `get_params()` and none of the fitted attributes, by
  construction — `clone()` is implemented as
  `type(estimator)(**estimator.get_params(deep=False))`.
- **A `Pipeline` step is refit exactly once per cross-validation fold**,
  on that fold's training rows only — 5 times under 5-fold, 10 times under
  10-fold. `cross_val_score` clones the whole pipeline once per fold.
- **`argmax(predict_proba(X), axis=1)`, mapped through `classes_`, equals
  `predict(X)`** for any fitted scikit-learn classifier that has both
  methods. This is how `predict()` is defined, not a coincidence.
- **A classifier that implements `fit`/`predict`/`score`/`get_params`/
  `set_params` by hand, inheriting nothing, works correctly when those
  five methods are called directly.** This is the load-bearing half of
  "the estimator API is a protocol."
- **Estimator discovery depends on which modules have already been
  imported, not on the scikit-learn version alone.**
  `sklearn.utils.all_estimators()` only finds estimators registered in
  modules that have actually run, and `HalvingGridSearchCV` /
  `HalvingRandomSearchCV` live behind
  `sklearn.experimental.enable_halving_search_cv` specifically. Import
  that module anywhere in a running process and the two become visible to
  every later call to `all_estimators()` in that same process, permanently
  — there is no way to un-register them. This is why
  `estimator_census()`'s bare count is measured in a **fresh subprocess**
  rather than in-process: it is the only way to get a genuinely bare
  reading regardless of what an earlier call, or an earlier test in the
  same pytest session, already imported. The *mechanism* — that the count
  depends on imports, and that the gap here is exactly two named
  estimators — is durable across scikit-learn versions; the specific
  totals below are not.

## Exact under scikit-learn 1.9.0, and only under it

- **The `AttributeError` naming `__sklearn_tags__`, raised by
  `cross_val_score` and by `Pipeline.predict()`/`.score()` on an estimator
  that does not inherit `BaseEstimator`.** `__sklearn_tags__` is recent
  scikit-learn internal machinery. A different version may fail
  differently, or not fail at all, or use different wording. The
  *direction* of this finding — that inheriting bare `BaseEstimator` fixes
  it — is what this lab treats as durable; the exact exception type and
  message are a property of 1.9.0.
- **`sklearn.utils.all_estimators()` discovers exactly 208 estimators
  bare, and exactly 210 once
  `sklearn.experimental.enable_halving_search_cv` has been imported** —
  `estimator_census()`'s `bare_total` and `total` respectively. Of the
  210, all 210 implement `fit`, 90 implement `transform`, 119 implement
  `predict`, and 20 implement both `transform` and `predict`:
  `Birch`, `BisectingKMeans`, `CCA`, `GridSearchCV`, `HalvingGridSearchCV`,
  `HalvingRandomSearchCV`, `IsotonicRegression`, `KMeans`,
  `LinearDiscriminantAnalysis`, `MiniBatchKMeans`, `PLSCanonical`,
  `PLSRegression`, `Pipeline`, `RFE`, `RFECV`, `RandomizedSearchCV`,
  `StackingClassifier`, `StackingRegressor`, `VotingClassifier`,
  `VotingRegressor`. These specific totals change between scikit-learn
  releases as estimators are added or removed; the shape that should hold
  on any version is that every discovered estimator implements `fit`, that
  `transform` and `predict` are not mutually exclusive, and that the bare
  count undercounts the enabled count by exactly the two Halving search
  estimators.
- **`check_estimator(MajorityClassifierBase())` reports 52 checks, 48
  passed, 2 skipped, 2 failed** — the failed pair being
  `check_classifiers_regression_target` and `check_classifiers_train`, the
  skipped pair being `check_array_api_input` (requires the
  `SCIPY_ARRAY_API` environment variable, not set here) and
  `check_classifier_data_not_an_array` (requires pandas, not installed in
  this lab's `.venv`). The total number and names of checks are scikit-learn
  1.9.0's own estimator-conformance suite and will differ on another
  version.

## Sampled, and therefore soft even here

- **Everything in exercise 9 (`random_state`).** `random_state=None` draws
  fresh entropy from the operating system on every call, by design, so
  none of these numbers are reproducible on any machine, including this
  one on a second run. One real capture: fitting the same
  `RandomForestClassifier(random_state=42)` five times gave five identical
  prediction vectors; fitting it five times with `random_state=None` gave
  5 of 5 distinct prediction vectors, and the accuracy over 20 such fits
  ranged from 0.7111 to 0.8222 with a standard deviation of 0.0294. The
  lab asserts only the structural claims — identical under a fixed seed,
  varying under none — never these figures.
- **The Pipeline+CV scores in exercise 6b** (`[0.3333, 0.3333, 0.3667,
  0.3667, 0.3667]`) depend on the exact fold assignment from
  `StratifiedKFold(5, shuffle=True, random_state=0)` on this lab's
  `classification_dataset()`. The pinned NumPy version and seed reproduce
  them exactly; the lab's own assertion only checks that five real,
  non-`NaN` scores between 0 and 1 come back.

## Timings

No timing is asserted anywhere in this lab. `check_estimator()` is the
heaviest single step, running 52 checks that each fit and predict on small
synthetic data; it completes in a few seconds here and will take longer
elsewhere without changing a single assertion, because every assertion is
about a shape or a value.
