# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because every number here is pinned to exact package versions. Build the
environment first:

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
`classification_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## The harness takes a while

It does. Exercises 7b and 10b each cross-validate all 36 candidate
pipelines across 20 independent seeds — 720 five-fold cross-validations
apiece. On the capture machine the whole harness runs in well under a
minute; on a slower one it will take longer.

No timing is asserted anywhere, so a slow machine changes nothing about
whether it passes. If you want a faster loop while developing, call
`selection_optimism_over_seeds` or `leaky_vs_honest_over_seeds` directly
with a smaller `seeds=range(...)` argument, and put it back before running
the harness.

## My winning configuration is not `LogisticRegression(C=1)`

Check `expected-output/FIELDS.md` before assuming this is a bug. The
winner at seed 0, under the pinned versions, is `('logreg', 1)` at a
cross-validated accuracy of 0.9780 — but several other configurations
score within a point or two of it, and Day 145 already established that
near-tied configurations trade places under resampling. What must hold on
any version: the winner's cross-validated accuracy is comfortably above
the 0.6316 baseline, and it was selected without ever touching the test
rows.

## `sqrt(2 ln K)` or the predicted optimism does not match

If you compute it by hand and get something other than 0.0326, check
which `n` you used. `predicted_selection_optimism` uses the size of one
cross-validation *fold* (`len(y_train) // folds`, which is 455 // 5 = 91
here) as the "validation set" size, because that is the number of rows
each fold's held-out score is actually computed from — not the full 455
training rows.

If your number is correct and simply does not match the measured drop,
that is the point of exercise 7b, not a bug: the formula assumes
independent, zero-skill candidates, and this sweep's 36 candidates are
neither. Read the honesty note in `starter/00_brief.md` before concluding
anything is broken.

## My leaky-gap numbers differ from the lesson's

Almost certainly fine. At any single seed the gap can land at exactly
zero — a ceiling effect, since 114 test rows only support accuracy moving
in steps of about 0.0088, and the honest and leaky searches sometimes land
on the identical winner. What must hold across the 20-seed sweep in
exercise 10b: the gap is never negative at any seed. If it has gone
negative, investigate properly rather than adjusting the assertion.

## `LogisticRegression` warns about convergence

`max_iter=5000` is set everywhere in this lab specifically to avoid this
on the smaller regularisation strengths in the sweep. If you construct
your own `LogisticRegression` with the default `max_iter=100` you may see
a `ConvergenceWarning`. Match the library's settings, or use its helpers
directly.

## The selection-optimism and leaky-gap numbers move on my machine

Read `expected-output/FIELDS.md`. Every seeded split and every
cross-validation fold in this lab depends on NumPy's `default_rng` and
scikit-learn's internal use of it, and NumPy's documentation is explicit
that `Generator` gives no stream-compatibility guarantee between versions.

What must hold anywhere: cross-validation selects using train rows only,
the leaky gap is never negative across the 20-seed sweep, and the test set
is evaluated exactly once in the reference run. Harness check 9 confirms
the leaky-gap direction and the selection mechanics survive at seeds this
lab does not quote, so none of the directional claims rest on a single
lucky seed.
