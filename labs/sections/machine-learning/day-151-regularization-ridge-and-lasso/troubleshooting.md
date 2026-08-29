# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because every number here is pinned to exact package versions. Build the
environment first:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want a different interpreter, the harness honours
`PYTHON` and `PYTEST`:

```
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Expect version-check failures if those do not match the pins. That is the
harness working, not the harness breaking.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names (`regularization_lib`,
`test_regularization_lib`, `test_regularization_claims`), so pytest
cannot decide which one a test meant. Run them separately:

```
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My near-duplicate columns don't give lasso an exact zero

At the default seed (`near_duplicate_dataset()`, seed=0) they do:
`[5.0848, 0.0, 0.0]` at alpha=1.0. But the two columns are correlated at
0.999918, not identically collinear, so at other seeds lasso can leave a
tiny nonzero residual on the coefficient it is effectively dropping —
harness check 8 found `[5.0215, 0.0007]` at seed 3. That is still the
same story: an overwhelmingly asymmetric split, ridge's stays nearly
even. If your run gives two roughly EQUAL nonzero lasso coefficients on
this dataset, something is genuinely wrong.

## `ElasticNet(l1_ratio=0)` doesn't match `Ridge` at the "same" alpha

It should not, and exercise 5b measures exactly why. Ridge's objective
sums the squared error across all rows; ElasticNet's averages it over
`n_samples`. So `Ridge(alpha=a)` corresponds to
`ElasticNet(alpha=a / n_train, l1_ratio=0)`, not
`ElasticNet(alpha=a, l1_ratio=0)`. This lab fits `Ridge(alpha=a * n_train)`
and checks it against `ElasticNet(alpha=a, l1_ratio=0)` for exactly this
reason. If you skip the correction you will see ElasticNet look far more
aggressively regularised than Ridge at a nominally matching alpha — for
example alpha=0.1 gives ElasticNet a test R2 of 0.0555 against Ridge's
0.3690, which is not a bug, it is the uncorrected comparison.

## `Lasso` warns about convergence, or the coefficients look different from the lesson

`max_iter=50000` is set everywhere in this lab specifically to avoid a
`ConvergenceWarning` — the default `max_iter=1000` does not converge on
this dataset at small alphas. If you construct your own `Lasso()` with
the default, expect a warning and possibly slightly different
coefficients. Match the library's settings.

## My scale-dependence numbers differ from the lesson's

Read `expected-output/FIELDS.md`. The *directions* — raw keeps the most
features, standardized keeps fewer, scikit-learn's own unit-norm
convention keeps fewer still, at the identical alpha — must hold on any
version. The exact kept sets and counts are pinned to the exact package
versions in `requirements/requirements.txt`.

## The harness takes a while

It should not: the heaviest step is the 60-point alpha sweep in exercise
2, which refits ten small linear models sixty times. On the capture
machine the whole harness runs in well under a minute. No timing is
asserted anywhere, so a slower machine changes nothing about whether it
passes.

## `sqrt`, `n_iter_`, or another attribute is missing on my fitted model

Check which model you fitted. `Ridge` has no `n_iter_` under its default
solver (`solver="auto"`, which resolves to a direct linear-algebra
solve); `Lasso` and `ElasticNet` always have `n_iter_`, because they are
solved by coordinate descent. Exercise 7 asserts this contrast directly.
