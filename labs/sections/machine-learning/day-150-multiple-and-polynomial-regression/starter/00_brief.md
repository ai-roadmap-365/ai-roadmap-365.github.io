# Day 150 lab brief — Many Predictors, One Model

Day 148 gave you a line through one predictor. Day 149 gave you a reason
to square the error before minimising it. Neither told you what changes
once a second predictor joins the first -- and the honest answer is: more
than you would guess.

This lab measures it, on `sklearn.datasets.load_diabetes(scaled=False)`:
442 patients, ten predictors in their real units -- age in years, sex
coded 1 or 2, bmi, average blood pressure, and six serum measurements
`s1`-`s6` -- and one target, a quantitative measure of disease progression
a year after baseline.

## The claim you are here to measure

> A coefficient in a multiple regression means "the change in the target
> for one unit of this predictor, holding every other predictor fixed" --
> and that phrase is doing enormous work.

Two predictors that are correlated with each other, not just with the
target, can be held "fixed" relative to each other only approximately,
because moving one tends to move the other in real data. The regression
still fits -- the predictions can be excellent -- but the individual
coefficients become an accounting exercise between correlated columns
rather than a stable description of anything.

## The centrepiece, and the number to watch

`s1` and `s2`, two of the six serum measurements, correlate at **0.8967**.
Append an exact copy of `s1` to the design matrix and refit:

| | original | duplicate model |
| --- | --- | --- |
| `s1` coefficient | −1.0900 | −0.5450 |
| copy's coefficient | -- | −0.5450 |
| **sum** | −1.0900 | **−1.0900** |
| R2 | 0.5177 | 0.5177 |
| max prediction change | -- | 3.98 × 10⁻¹² |

Neither half matches the original coefficient. Their **sum** does, to
eight decimal places, because the normal equations only ever see the
*combined* effect of two identical columns and have no way to prefer one
split over another.

Now break the exact tie with one percent of noise and refit at ten
different noise seeds:

```text
  coefficient a : sd 4.4258, range -6.9523 to 5.6258
  coefficient b : sd 4.4141, range -6.6988 to 5.8570
  their sum     : sd 0.0144, mean -1.0891
  largest single prediction move across all ten seeds: 6.5911
```

**Wild coefficients, stable predictions.** That contrast is the whole
lesson. A model can be excellent at what it predicts and worthless as a
description of "the effect of `s1`" at the same time, and nothing about
its accuracy will tell you so.

## Variance inflation, computed directly

Exercise 1 computes the standard diagnostic: regress each predictor on
the other nine, and take `1 / (1 - R2)`.

| predictor | VIF | predictor | VIF |
| --- | --- | --- | --- |
| age | 1.2173 | s1 | 59.2025 |
| sex | 1.2781 | s2 | 39.1934 |
| bmi | 1.5094 | s3 | 15.4022 |
| bp | 1.4594 | s4 | 8.8910 |
| s6 | 1.4846 | s5 | 10.0760 |

The four clinical measurements sit near 1 -- barely explained by the other
nine. Every serum measurement sits above the common rule-of-thumb cutoff
of 5, and `s1` at 59.2 is the worst of them: 59 times the variance a truly
independent predictor would have.

## Two things that are true and easy to misread

**A polynomial fit is still a linear model.** "Linear regression" does not
mean "a straight line" -- it means linear *in the parameters*. Fit
`PolynomialFeatures(degree=2)` followed by `LinearRegression` on `bmi` and
`bp`, and solve the identical expanded design matrix by hand with
`numpy.linalg.lstsq`. The two answers agree to thirteen decimal places,
because they are solving the same linear system by two different routes.

**R2 never decreases when you add a predictor -- even a column of pure
noise.** Add 1, 2, 5 and 10 columns of `numpy.random.default_rng` noise
with no relationship to the target whatsoever, and R2 climbs from 0.5177
to 0.5325. Nothing was learned; the model simply has more knobs to turn.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see five passes (the
   machinery checks in `test_regression_lib.py`) and twelve skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regression_lib.py`, `test_regression_lib.py` and
`test_regression_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## What this lab deliberately does not cover

Ridge and lasso -- the standard fix for the instability you are about to
measure -- belong to Day 151. Adjusted R2, the fix for the never-decreases
problem in exercise 7, belongs to Day 152. Neither is implemented here;
this lab only measures the two problems those days solve.
