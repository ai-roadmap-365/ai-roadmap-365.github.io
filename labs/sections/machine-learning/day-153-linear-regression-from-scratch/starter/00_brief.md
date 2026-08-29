# Day 153 lab brief -- Linear Regression from Scratch

Day 148 through 152 taught you what a fitted line means, where the formula
for its coefficients comes from, what happens with many predictors, and how
to regularize and score the result. Nobody in that run asked what
`LinearRegression().fit()` actually *does* when you call it.

This lab builds it three ways and finds out.

## The claim you are here to measure

> The textbook formula for linear regression is not what a good library
> actually runs, and you can show exactly why.

Exercise 1 fits ordinary least squares two ways -- the normal equations
`(X'X)^-1 X'y`, straight off the textbook page, and an `lstsq`-based solve
-- and checks both against scikit-learn's own `LinearRegression` on the
bundled diabetes dataset:

```text
max |normal equations - sklearn| : 1.2153e-10
max |lstsq            - sklearn| : 1.1990e-12
```

`lstsq` lands about a hundred times closer. Exercise 1b explains why:
`cond(X'X)` is exactly the square of `cond(X)` -- 51631.11 against 227.22
here -- and squaring a condition number is precisely how many digits of
precision the normal equations throw away that a direct solve of `X` does
not.

## The part that should genuinely surprise you

Exercise 2 makes the effect impossible to miss. Take three random columns,
add a fourth that is column 0 plus a sliver of noise -- 1e-7 in scale, far
below any real measurement error -- and fit with true coefficients
`[1, 2, 3, 4]`:

```text
normal-equation coefficients : [0.001, 196747.976, 1.997, 2.994, -196742.975]
lstsq coefficients           : [0.001, 207112.776, 1.997, 2.994, -207107.775]
sklearn coefficients         : [0.001, 2.501, 2.0, 2.997, 2.501]
```

Both from-scratch methods explode to plus and minus two hundred thousand.
sklearn stays sane, splitting the true value of 1 (which the near-duplicate
pair shares between them, since column 3 is almost column 0) into 2.5 and
2.5 -- an SVD-based minimum-norm solve that neither of the two textbook
routes performs.

## Gradient descent, and where Day 111 arrives

Exercise 3 fits the same problem with gradient descent instead, on
standardized features, and measures exactly how many iterations it takes
to agree with the closed form to 3, 6 and 9 decimal places. Exercise 3b
repeats it on the RAW, unscaled diabetes columns -- age in years next to
sex coded 1 or 2 next to serum measurements in the hundreds -- and shows
gradient descent barely moving, because Day 111's condition number (the
ratio of the loss's largest to smallest Hessian eigenvalue) is over a
hundred times worse unscaled. Exercise 4 finds the exact learning rate
where gradient descent stops converging and starts diverging, and shows it
lines up with Day 111's stability formula `|1 - eta * a| < 1` to the
decimal.

## What each method costs, without a stopwatch

Exercise 5 counts operations instead of timing anything -- the closed form
needs `n*p^2 + p^3` multiply-adds; gradient descent needs `2*n*p` per
iteration. On the diabetes shape, the closed form wins by a factor of over
a thousand, for the number of iterations exercise 3 measured.

## The estimator, and the two things it does not do

Exercise 6 wraps all three fitting routes in an `OLSRegressor` that
inherits `BaseEstimator` and `RegressorMixin` -- Day 146 already measured
why a from-scratch estimator needs that inheritance to survive
`Pipeline.predict()` and `cross_val_score`, and this lesson does not
re-teach it. Then it runs `sklearn.utils.estimator_checks.check_estimator`
against it and reports the real result: 48 of 52 checks pass, and two fail
by name, both about input validation this implementation does not perform.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see five passes (the
   machinery checks in `test_regression_lib.py`) and ten skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print is
   a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regression_lib.py`, `test_regression_lib.py` and
`test_regression_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.
