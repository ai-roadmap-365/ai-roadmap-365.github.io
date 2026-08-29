# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`, because
several numbers here depend on the exact LAPACK routines behind this
lab's pinned NumPy and scikit-learn. Build the environment first:

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

## The harness takes a while

Section 3b runs gradient descent for 200,000 iterations on ten-column
raw-feature data, several times over, plus `check_estimator`'s full suite.
On the capture machine the whole harness runs in a few seconds; on a
slower one it may take longer. No timing is asserted anywhere, so a slow
machine changes nothing about whether it passes.

## My exploded coefficients in exercise 2 have different exact numbers

Expected, and the lab does not assert the exact magnitude. The near-
duplicate column carries a `1e-7`-scale noise term, and the exact size of
the resulting explosion is sensitive to that noise, the seed, and even the
platform's floating-point rounding in the matrix solve. What is asserted,
and what must hold, is the direction: the normal-equation and lstsq
coefficients for the duplicated pair both exceed `1e5` in magnitude, in
opposite signs, while sklearn's stay near 2.5. If your exploded values are
a different number of digits from the lesson's, nothing is wrong. If they
are NOT enormous compared to the true coefficient of 4, something is.

## `cond(X'X) / cond(X)**2` is not exactly 1.0 in exercise 2b

Correct, and asserted -- deliberately not as an equality. At the extreme
ill-conditioning of the near-duplicate-column dataset (`cond(X)` above ten
million), computing the smallest singular value of an already
near-singular matrix is itself numerically imprecise, so the theoretical
squaring relationship becomes hard to verify even though it remains true
in exact arithmetic. Exercise 1b, on the much better-conditioned diabetes
data, verifies the same relationship to ten decimal places -- read the two
exercises together, not exercise 2b in isolation.

## My gradient-descent iteration counts differ from the lesson's

If they differ by a small amount (single-digit percentage), this is almost
certainly a LAPACK or NumPy version difference in the closed-form target
the iteration counts are measured against -- see
`expected-output/FIELDS.md`. If gradient descent at 80 percent of the
stability threshold diverges instead of converging, or converges in wildly
more iterations (an order of magnitude off), something is genuinely wrong;
investigate rather than adjusting the assertion.

## `check_estimator` reports different failures on my machine

Read `expected-output/FIELDS.md`. The two named failures
(`check_n_features_in_after_fitting`, `check_dtype_object`) and the two
named skips (`check_array_api_input`, `check_regressor_data_not_an_array`)
are specific to scikit-learn 1.9.0's exact check suite. A different
scikit-learn version can add, remove, or rename checks -- if you are on a
different pin and only the NAMES differ while the overall pass count stays
close to 48 of 52, nothing is broken. If dramatically fewer checks pass,
something in `OLSRegressor` itself has likely regressed.

## I tried `noise_scale=0.0` in `make_dramatic_collinear_dataset` and did NOT get an error

Checked directly on this machine: an exactly duplicated column makes `X'X`
mathematically singular, but `np.linalg.solve` does not reliably raise
`LinAlgError` for it -- floating-point rounding during the matrix
multiplication that forms `X'X` typically leaves it *numerically* just
shy of exactly singular, so `solve` returns a number anyway, and that
number is exactly as unreliable as the `1e-7`-noise case this lab
measures, just for a different underlying reason. `np.linalg.lstsq` is the
version of this problem that degrades predictably regardless: it never
forms or inverts `X'X` at all, so it does not depend on this floating-point
accident either way.
