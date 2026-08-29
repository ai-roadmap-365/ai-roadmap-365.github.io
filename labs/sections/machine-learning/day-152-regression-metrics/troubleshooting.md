# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`, because
every number here is pinned to exact package versions. Build the
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
`regression_metrics_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My MAPE number is astronomically large and I think something is broken

Nothing is broken -- exercise 4 asserts exactly this. `sklearn.metrics.
mean_absolute_percentage_error` does not raise or warn when a true value is
zero; it floors the denominator at machine epsilon and returns whatever
that division produces. On the exact rows this lab uses, that is roughly
`5.6e15`, not a small mistake. If your number is a different enormous
figure, that is expected too -- the floor value is `np.finfo(np.float64).
eps`, and the exact result depends on the numerator, but "enormous and
meaningless" is the point being demonstrated, not a specific digit.

## My adjusted R2 at 100 noise columns is HIGHER than at 0 noise columns and that looks backwards

It is not backwards, and exercise 1b asserts exactly this. Adjusted R2 does
correctly penalise the climb at a modest number of extra columns -- at 20
noise columns it drops below the no-noise baseline, as it should. But once
the number of predictors (110, once you count the ten real features) gets
close to a third of the number of training rows (331), the correction
term `(n-1)/(n-p-1)` itself becomes large and unstable, and it can push
adjusted R2 back above the baseline even though every added column is still
pure noise. The lesson calls this out explicitly: the correction is not a
cure, it has its own failure mode.

## `sklearn.linear_model.LinearRegression()` gives different numbers on raw versus scaled features

It should not, and exercise 7 asserts that it does not. Ordinary least
squares is invariant to a per-column affine rescaling of its inputs, so
`load_diabetes(scaled=True)` and `load_diabetes(scaled=False)` produce
identical predictions, and therefore identical RMSE, MAE and R2, once a
model is fit on each. If your numbers differ, check that you fit two
separate models -- one per feature set -- rather than reusing a model fit
on one set of features to predict from the other.

## The r2_score argument order thing seems too small to matter

Try it on your own data before deciding that. `sklearn.metrics.r2_score`
is not symmetric in its two arguments: the denominator is the variance of
whichever array is passed first. On this lab's exact predictions, the
correct call reports 0.359409 (a usable model) and the swapped call
reports -0.209635 (worse than guessing the mean, for the exact same
predictions). This is a real and common bug, not a contrived one -- it is
easy to write `r2_score(y_pred, y_test)` out of habit from functions where
argument order does not matter.

## `LogisticRegression` warns about convergence

This lab does not use `LogisticRegression` -- every model here is
`LinearRegression`, which has a closed-form solution and never warns about
convergence. If you see that warning, check that you have not accidentally
imported from a different day's lab directory.

## The harness takes a while

It should not, on any machine that can run Python at all. The heaviest
step fits eleven `LinearRegression` models on at most 331 rows and 110
columns, which completes in well under a second on the capture machine. No
timing is asserted anywhere, so a slow machine changes nothing about
whether the harness passes.
