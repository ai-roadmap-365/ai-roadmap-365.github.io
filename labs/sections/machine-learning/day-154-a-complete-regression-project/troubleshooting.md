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
`regression_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My winning configuration is not `Lasso(alpha=1)`

Check `expected-output/FIELDS.md` before assuming this is a bug. The
winner at seed 0, under the pinned versions, is `('lasso', 1)` at a
cross-validated RMSE of 53.8958 -- but `Lasso(alpha=0.3)`, `Ridge(alpha=10)`
and plain OLS all score within two-tenths of a point of it. Day 145
already established that near-tied configurations trade places under
resampling. What must hold on any version: the winner's cross-validated
RMSE is comfortably below the 70.4637 baseline, and it was selected
without ever touching the test rows.

## The margin's bootstrap interval doesn't match my by-hand run

`margin_bootstrap_interval` seeds its own `np.random.default_rng(seed)`
internally (default `seed=0`), so calling it with the same arguments and
the same `seed` reproduces the same 2000 resamples under this NumPy
version. If you changed `n_boot` or the seed, your bounds will differ --
that is expected. If you used the same arguments and still see different
bounds, check your NumPy version against the pin; NumPy's own
documentation states `Generator` gives no cross-version stream guarantee.

## The residual diagnostics look different from the lesson's

If you re-split with a different seed or a different `test_size`, every
diagnostic in exercises 8, 8b and 9 will move -- they are all computed on
one seed's 111 test rows. What should hold at any seed: the Q-Q
correlation stays well above 0.9 (these residuals are close to normal),
and neither the heteroscedasticity nor the curvature signal is dramatic
(nothing near ±0.6 or higher). If yours is wildly different, check that
you selected the winner with `select_best` and predicted on the SAME
`x_test` the gate was built from.

## The leaky RMSE is higher than the honest RMSE

This should not happen, and if it does on the pinned versions with seed
0, something is genuinely broken -- open an issue rather than adjusting
the assertion. `leaky_selection_test_rmse` searches all 23 candidates and
keeps the lowest test RMSE, which by construction includes the honestly
selected winner among its options; it cannot report a higher (worse)
number than the honest evaluation.

## My leaky-gap numbers differ from the lesson's

Almost certainly fine, at the level of the decimals. What must hold
across the full 20-seed sweep in exercise 10b: every single gap is
non-negative. If a gap has gone negative at any seed, that is the one
result that would falsify this lab's central mechanism -- investigate
properly rather than adjusting the assertion.

## `Lasso` or `Ridge` prints a convergence warning

`max_iter=20000` is set on every `Lasso` in the sweep specifically to
avoid this at the smaller regularisation strengths. If you construct your
own `Lasso` with the default `max_iter=1000` you may see a
`ConvergenceWarning`. Match the library's settings, or use its helpers
directly.

## The harness takes a while

It does not, particularly -- the 20-seed leaky-gap comparison in
exercise 10b, which cross-validates all 23 candidates 20 times over, took
2.9559 seconds on the capture machine, and the full harness completes in
well under a minute. No timing is asserted anywhere, so a slower machine
changes nothing about whether it passes.

## Every number moves on my machine

Read `expected-output/FIELDS.md`. Every seeded split, cross-validation
fold and bootstrap resample in this lab depends on NumPy's `default_rng`
and scikit-learn's internal use of it, and NumPy's documentation is
explicit that `Generator` gives no stream-compatibility guarantee between
versions.

What must hold anywhere: cross-validation selects using train rows only,
the leaky RMSE is never worse than the honest RMSE across the 20-seed
sweep, and the test set is evaluated exactly once in the reference run.
Harness check 9 confirms the leaky-gap direction and the selection
mechanics survive at seeds this lab does not quote, so none of the
directional claims rest on a single lucky seed.
