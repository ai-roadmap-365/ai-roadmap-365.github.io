# Day 154 lab brief — A Complete Regression Project

Days 148 through 153 each isolated one discipline in a lab built to show
it in isolation: the one-predictor model and its four assumptions, the
loss function as a choice, multicollinearity, ridge and lasso, the
metrics that can be gamed or inverted, and OLS built from scratch.

This lab is not a new discipline. It is all six of them, spent on one
real dataset, in the order a working project actually uses them: frame,
baseline, split, pipeline, cross-validate, select, **one** test
evaluation, residual diagnostics, a fairness check, prediction intervals,
an honest verdict with an interval on the margin.

## The dataset, and why there is only one choice

`sklearn.datasets.load_diabetes` is the only regression dataset that
ships inside scikit-learn and needs no download.
`fetch_california_housing` downloads on first use and is forbidden by
this lab's offline rule. Exercise 1 checks both facts directly.

`load_diabetes(scaled=False)` gives 442 rows of 10 real-valued
measurements — age, sex, bmi, average blood pressure, and six serum
measures — in their **raw units**: age in years, not a mean-centred
fraction. scikit-learn's own default (`scaled=True`) mean-centres and
variance-scales every column to tiny floats; exercise 1b measures the
difference directly.

**The target has no physical unit.** It is a composite disease-
progression score assembled from clinical measurements a year after
baseline — not mg/dL, not a count, not anything with a name. Every RMSE
and MAE in this lab is in those same unitless composite-score points, and
this brief says so plainly rather than inventing a unit that does not
exist.

442 rows is small. A 25 percent test set is 111 rows — small enough that
every interval this lab computes is wide, and that is the point, not a
flaw: an honest verdict on data this size can legitimately come out
"cannot distinguish," and this lab's own margin check (exercise 7)
reports what actually happened rather than assuming an answer.

## What the honest run measures

Twenty-three candidate pipelines — 11 ridge regularisation strengths, 11
lasso regularisation strengths, and 1 plain OLS — are cross-validated
five ways on the training rows only, scored by RMSE. The winner is
`Lasso(alpha=1)`, at a cross-validated RMSE of **53.8958**. Fitted on the
full training set and evaluated **exactly once** against the test rows,
it scores **56.5566** RMSE (R2 0.3557, MAE 45.2846).

## The margin, and whether it survives an interval

The mean-predictor baseline scores 70.4637 RMSE. The winning model's
margin over that baseline is **13.9071** RMSE points. A 2000-draw
bootstrap resample of the 111 test rows gives a 95 percent interval on
that margin of **[5.5852, 22.3324]** — the interval excludes zero, so
this project's honest verdict is that the model IS distinguishable from
the baseline at this test-set size. It could easily have come out the
other way on a smaller improvement or a smaller test set, which is
exactly why the bootstrap runs rather than being assumed.

## Residual diagnostics — the centrepiece of this lab

No other day in this course owns reading the residuals themselves.
Exercise 8 measures whether the errors fan out as predictions rise
(a **heteroscedasticity signal** of 0.2386 — mild, not dramatic), whether
there is a missed curve in the fit (a **curvature signal** of -0.1278 —
weak), and how close the residuals are to normally distributed (a
**Q-Q correlation** of 0.9901, built from scratch with no scipy
dependency, since scipy is not one of this lab's three pinned packages).
Exercise 8b names the five largest individual mistakes: the biggest is a
patient whose true score was 52 and whose prediction was 209.3 — a
residual of -157.3 points.

## Is the model worse for high-value targets? Measured, not assumed.

Exercise 9 splits the test set at the median true value and compares
RMSE on each half: 55.2464 on the below-median half, 57.8601 on the
above-median half — a ratio of **1.0473**. Only 4.73 percent worse on the
more severe half at this seed: not the dramatic fairness problem the
exercise sets out to check for, and that is a real finding, not a
disappointing one — it had to be measured to be known.

## The leak this lab lets you cause on purpose

Exercise 10 rebuilds the mistake Day 147 spent a whole lesson on, for
regression: selecting a model by fitting every candidate and scoring it
**on the test set directly**, keeping whichever scores the lowest RMSE,
instead of selecting on cross-validated train rows and looking at test
once.

At the reported seed the leak reports 55.5212 RMSE against the honest
56.5566 — a gap of 1.0354 points in the leak's favour. Over 20 seeds the
mean gap is **0.5279** (sd 0.3686, min 0.011, max 1.1451), and it is
**never negative** — the leak can only make the reported error look as
good or better than the honest one, never worse. That asymmetry is the
mechanism, not luck.

## Prediction intervals, and their realised coverage

Exercise 11 builds a constant-width 95 percent prediction interval from
the standard deviation of **training** out-of-fold residuals — never from
the test residuals themselves, which would be circular — and checks what
fraction of the 111 test targets actually fall inside it: **0.9459**,
against a 0.95 nominal rate. Close, on 111 rows.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see five passes (the
   machinery checks in `test_regression_lib.py`) and fourteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regression_lib.py`, `test_regression_lib.py` and
`test_regression_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## And the rule, made mechanical, again

Exercise 6 wraps the test set in the same `GatedTestSet` pattern Day 144
built and Day 147 reused: exactly one evaluation, `TestSetTouchedTwice`
on the second, and a counter that does not advance on a refused attempt.
Thirteen days in, this is not a new idea — it is the same discipline,
proven on a regression problem instead of a classification one.
