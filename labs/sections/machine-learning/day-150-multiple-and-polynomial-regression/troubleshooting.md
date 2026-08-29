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

## My duplicate-column coefficients do not match the lesson's

If you are on the exact pins and the *exact* duplicate (exercise 2) does
not match, something is genuinely wrong -- that result is closed-form
arithmetic, not a sampled draw, and it holds to eight decimal places on
any machine.

If it is the *noisy* duplicate (exercise 3) that differs, check which
seed you used. The individual coefficients are supposed to look different
at every seed -- that instability is the entire point of the exercise.
What must hold on any seed: both coefficients have a standard deviation
well above 4 across ten seeds, their sum's standard deviation is under
0.05, and predictions move by only a few units on a target whose own
spread is 77. Harness check 8 re-confirms the instability at seeds the
lesson never quotes and on a second predictor (s2), so it is not an
artefact of s1 or of seed 0.

## `ModuleNotFoundError: No module named 'pandas'`

`sklearn.datasets.load_diabetes` can return a pandas `DataFrame` if you
pass `as_frame=True`, but pandas is not one of this lab's pinned
dependencies and is not installed. Every function in `regression_lib.py`
calls `load_diabetes(scaled=False)` without `as_frame`, which returns
plain NumPy arrays and needs no pandas at all. If you add your own
exploration code, avoid `as_frame=True` unless you also install pandas.

## The bootstrap or noise-column exercises run slowly

The bootstrap in exercise 4 refits a ten-predictor linear regression 500
times; the noisy-duplicate spread in exercise 3b refits ten times. Both
finish in well under a second on the capture machine because
`LinearRegression` on 442 rows and at most 11 columns is a tiny
least-squares solve. No timing is asserted anywhere, so a slower machine
changes nothing about whether the harness passes.

## The variance inflation factor for a column is `inf`

That is correct behaviour, not a bug -- `variance_inflation_factors`
returns `float("inf")` when a predictor is perfectly explained by the
others (`R2 == 1.0` in the auxiliary regression), which is exactly what
happens if you duplicate a column and then compute VIFs on the duplicated
matrix. The machinery test
`test_an_exact_duplicate_of_a_column_has_infinite_vif` asserts this
directly. None of the ten original diabetes predictors triggers it; their
VIFs range from 1.2173 to 59.2025.

## `LogisticRegression` or `LinearRegression` warns about convergence

`LinearRegression` in scikit-learn solves the normal equations directly
and does not iterate, so it has no convergence warning to raise. If you
see one, you have introduced a different estimator somewhere in your own
exploration code -- this lab uses `LinearRegression` throughout, on
purpose, because Day 149 already covers loss functions and Day 151
already covers regularised estimators.
