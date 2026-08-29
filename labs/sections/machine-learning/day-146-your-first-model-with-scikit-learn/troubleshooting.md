# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because the version-specific finding in exercise 6 depends on exact
package versions. Build the environment first:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want a different interpreter, the harness honours
`PYTHON` and `PYTEST`:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Expect version-check failures if those do not match the pins. That is the
harness working, not the harness breaking.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`estimator_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My hand-built estimator raises `AttributeError: '...' object has no attribute '__sklearn_tags__'`

That is exercise 6, working as intended, not a bug in your code. The
`MajorityClassifier` in this lab inherits nothing from scikit-learn, and
`fit`/`predict`/`score` all work perfectly when you call them directly.
What raises is scikit-learn's own internal fitted-check, called from
inside `Pipeline` or `cross_val_score`, which needs `__sklearn_tags__` — a
method that, in this version of the library, only `BaseEstimator` supplies.

The fix is exercise 6b: make the class inherit from
`ClassifierMixin, BaseEstimator` (nothing else), and delete the hand-written
`get_params`/`set_params` entirely — `BaseEstimator` now supplies both,
correctly, by inspecting `__init__`'s signature.

If you see this error somewhere you did **not** expect it — calling
`.fit()` or `.predict()` directly on `MajorityClassifier`, outside a
`Pipeline` or `cross_val_score` — that is a genuine bug and worth
investigating, because standalone calls should never touch this path.

## `check_estimator()` reports 2 failures. Is my implementation wrong?

No — those two failures are expected, asserted, and explained.

**`check_classifiers_train`** asserts that the classifier scores above
0.83 accuracy on a real, learnable dataset. `MajorityClassifierBase` is a
majority-class dummy by design: it always predicts whatever class was most
frequent during training, on purpose, so that its output can be checked
against `DummyClassifier`. It satisfies every structural check in the
estimator contract perfectly; it is simply not supposed to be a good
classifier, and this check assumes the estimator under test is trying to
be one.

**`check_classifiers_regression_target`** asserts that passing a
continuous target raises a `ValueError` naming `"Unknown label type"`. Our
`fit()` never validates that `y` looks like classification labels rather
than a continuous target — a real omission, and a genuinely useful one to
notice, but out of scope for what this lab is teaching.

Both are printed by name in `report_measurements.py`'s output and asserted
by name in exercise 10. If a different pair of checks fails on your
machine, or the totals differ from 52/48, that is worth investigating —
`check_estimator()`'s exact check set is a property of the installed
scikit-learn version.

## The harness takes a while

`check_estimator()` alone runs 52 separate checks, several of which fit
models on small synthetic datasets multiple times, and exercise 9 fits 25
random forests to measure what `random_state=None` costs. On the capture
machine the whole harness runs in well under a minute; on a slower one it
will take longer. No timing is asserted anywhere, so this changes nothing
about whether the harness passes.

## My `random_state=None` numbers differ from `expected-output/FIELDS.md`

They are supposed to. `random_state=None` draws fresh entropy from the
operating system on every call, which is the entire point of exercise 9 —
it is what makes a fixed `random_state` valuable in the first place. The
number captured in `FIELDS.md` is one real run, kept as an example, never
as a value to reproduce. What must hold on any machine: fitting the same
model five times with `random_state=42` gives identical predictions every
time, and fitting it five times with `random_state=None` gives at least
two different prediction vectors. Both are asserted structurally, never as
a specific count.

## `LogisticRegression` warns about convergence

`max_iter=1000` is set everywhere in this lab specifically to avoid this.
If you construct your own with the default of 100 you may see a
`ConvergenceWarning` and slightly different scores. Match the library's
settings, or use its helpers directly.

## `estimator_census()`'s numbers differ from 208/210/90/119/20

`sklearn.utils.all_estimators()` reflects exactly what is installed,
importable, **and already imported** in your environment — this is not a
typo of "installed." `HalvingGridSearchCV` and `HalvingRandomSearchCV`
live behind `sklearn.experimental.enable_halving_search_cv`, so
`all_estimators()` reports 208 estimators in a bare interpreter and 210
once that import has run, anywhere, in the current process. This is why
`estimator_census()` measures its `bare_total` in a fresh subprocess
rather than in-process: importing the enabler once makes the two
estimators visible for the rest of that process's lifetime, so an
in-process "before" reading taken after any earlier call would be wrong.

If your `bare_total` is not 208, or your `total` is not exactly
`bare_total + 2`, or `newly_visible_after_experimental_enable` is not
`['HalvingGridSearchCV', 'HalvingRandomSearchCV']`, something is
genuinely different from the capture environment — most likely a
different scikit-learn version, which adds or removes estimators between
releases; this lab pins the version for exactly this reason, see
`requirements/README.md`. What should hold on any scikit-learn 1.9.0
install regardless of import order: every discovered estimator implements
`fit`, `transform` and `predict` are not mutually exclusive — some
estimators, such as clustering models and meta-estimators, genuinely
implement both — and the bare count is undercounted from the enabled
count by exactly the two named Halving estimators.
