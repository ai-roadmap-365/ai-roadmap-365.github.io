# Day 146 lab brief — The Estimator API, From Scratch

Days 141-145 called `.fit(X, y)` and `.predict(X)` on scikit-learn objects
dozens of times without ever explaining what those two words mean. This
lab explains them, by building a classifier that implements the API by
hand and then measuring exactly where hand-written code and library code
agree — and, honestly, one place where they stop agreeing.

## The claim you are here to test

> The estimator API is a protocol, not magic — until it isn't.

Exercise 1 builds `MajorityClassifier`, a class that inherits nothing from
scikit-learn. `__init__` stores one hyper-parameter. `fit` learns three
things and names each with a trailing underscore. `predict`, `predict_proba`,
`score`, `get_params` and `set_params` are five ordinary methods, written
out in full. Its predictions and probabilities turn out to be **byte
identical** to `sklearn.dummy.DummyClassifier(strategy="most_frequent")` —
not similar, not close, identical — because both objects are computing the
same thing from the same rule.

## Where the protocol needs a footnote

Exercise 6 is the one that should surprise you. The exact same hand-built
classifier — the one whose predictions matched the library exactly —
raises an `AttributeError` the instant you hand it to `cross_val_score`:

```text
AttributeError: 'MajorityClassifier' object has no attribute '__sklearn_tags__'.
...Make sure to inherit from `BaseEstimator`...
```

`fit`, `predict` and `score` all still work fine when you call them
directly. What breaks is scikit-learn's *own* machinery, which needs to
check whether an estimator is fitted and does so, in this version, through
a method that only `BaseEstimator` supplies. Add one line —
`class MajorityClassifierBase(ClassifierMixin, BaseEstimator):` — delete
`get_params` and `set_params` entirely, since `BaseEstimator` now supplies
them by inspecting `__init__`'s signature, and the classifier works inside
a real `Pipeline` and a real `cross_val_score`.

That is the honest version of "it's just a protocol": five methods are
*necessary*, and this lab proves it by making them work standalone. They
are no longer *sufficient* for full interoperability in this version of
the library, and this lab proves that too, by breaking on purpose.

## What else this lab measures

| # | What it checks |
| --- | --- |
| 2 | The exact set of attributes `fit()` adds — every one ends in `_` |
| 3 | `get_params`/`set_params` round-trip; `clone()` produces a fresh, unfitted copy |
| 4-5 | `Pipeline` is an estimator itself, with nested parameters, and refits every step once per cross-validation fold on training rows only |
| 6 | Where "just a protocol" needs a footnote (above) |
| 7 | How many of scikit-learn's 210 discovered estimators implement `fit` (all of them), and how many implement both `transform` and `predict` (20 — clustering models and meta-estimators, not classifiers) |
| 8 | `predict()` is `argmax(predict_proba())`, restated as `classes_[...]` |
| 9 | What `random_state=None` costs, measured as five independent, non-reproducible fits |
| 10 | `check_estimator()` against the real estimator-conformance suite: 48 of 52 checks pass, and this lab explains, honestly, why the other two do not |

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see five passes (the
   machinery checks in `test_estimator_lib.py`) and eighteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `estimator_lib.py`, `test_estimator_lib.py` and
`test_estimator_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## Exercises 9 and 9b are honest about being unrepeatable

`random_state=None` draws fresh entropy from the operating system on every
single call, by design — that unpredictability is the entire point of the
exercise. So `report_measurements.py` prints only structural facts about
it ("identical across five fits: True", "distinct across five fits: True")
rather than the sampled counts and accuracy figures themselves, and the
tests assert the same structural claims. One real capture of the sampled
numbers, from one specific run, lives in `expected-output/FIELDS.md` —
labelled as an example, never as a value your run should reproduce.
