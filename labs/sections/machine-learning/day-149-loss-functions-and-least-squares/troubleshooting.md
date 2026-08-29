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
`loss_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## My numbers in exercises 4-6 differ slightly from the lesson's

Read `expected-output/FIELDS.md` first. Every figure past exercise 3 comes
from `numpy.random.default_rng` or from an iterative scikit-learn solver
(`HuberRegressor`, `QuantileRegressor`), and neither NumPy's random
streams nor a solver's exact stopping point are guaranteed across package
versions. What must hold on any version: OLS moves further than Huber,
which moves further than the median fit, when the same point becomes an
outlier; the Huber epsilon sweep is non-decreasing and its large-epsilon
end matches OLS; and Gaussian errors favour OLS while heavy-tailed errors
favour Huber. Harness check 8 re-confirms these directions at seeds and
replication counts the lesson does not quote.

## `QuantileRegressor` raised an error about the solver

This lab passes `solver="highs"` explicitly. If you construct your own
`QuantileRegressor` without specifying a solver, older scikit-learn
releases default to `"interior-point"`, which was deprecated and removed;
`"highs"` is the current default in 1.9.0 but naming it explicitly avoids
any ambiguity about which linear-programming backend produced a given
number.

## `HuberRegressor` gives a `ConvergenceWarning`

Not observed anywhere in this lab's captured runs — every fit converges
within the default 100 iterations on every dataset used here, and the
epsilon sweep raises `max_iter` to 500 as a margin. If you see one on data
of your own, it usually means the epsilon is very small relative to the
residual scale, which pushes the loss toward almost-everywhere-absolute
error and makes the optimisation harder; try scaling your features or
raising `max_iter`.

## My grid-search argmin in exercise 1 isn't exactly the mean or median

It should be *close*, not exact — `grid_minimize` searches a finite grid,
so it lands within `(hi - lo) / (steps - 1)` of the true minimiser. At the
default 200,001 steps over a 0-to-110 range that resolution is about
0.00055, which is why the assertions check "within 0.001" rather than
equality. The exact minimisers — `23.4` for squared error and `5.0` for
absolute error on this lab's five values — come from `numpy.mean` and
`numpy.median` directly, which are exact.

## The efficiency comparison in exercises 6 and 6b takes a while

It fits 2,000 models total (500 replications, two estimators, two error
settings). On the capture machine the whole harness — including this step
— runs in a few seconds; on a slower machine it will take longer. No
timing is asserted anywhere, so a slow machine changes nothing about
whether the checks pass.
