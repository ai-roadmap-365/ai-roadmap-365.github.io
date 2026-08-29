# Day 149 lab brief — Loss Functions and Least Squares

A loss function is not part of the mathematics of a straight line. It is a
choice you make, and this lab measures what that choice actually decides.

## The claim you are here to measure

> Squared error and absolute error agree on the easy cases and disagree
> sharply on the hard ones, and the disagreement is exactly outlier
> sensitivity.

Exercise 1 starts with five numbers: `2.0, 3.0, 5.0, 7.0, 100.0`. A grid
search over every candidate value confirms two textbook facts as
measurements rather than assertions:

| loss | minimiser | value here |
| --- | --- | --- |
| squared error, `sum((v - c)^2)` | the **mean** | 23.4000 |
| absolute error, `sum(|v - c|)` | the **median** | 5.0000 |

The mean is dragged nearly to 23.4 by the single value of 100.0. The
median does not move — it only counts how many points sit on each side of
it, never how far away they are. That single fact is the whole reason a
squared-error fit and an absolute-error fit disagree about outliers.

## The shape of the two landscapes

Exercise 2 sweeps a candidate slope from 2.0 to 4.0 against the same
sixty-row dataset and totals both losses at each value:

| loss | second differences | what that means |
| --- | --- | --- |
| squared error | constant (sd = 0.000000) | a parabola: smooth, one minimum |
| absolute error | varies (sd = 1.9366) | piecewise-linear: kinked at every point where a residual crosses zero |

Constant curvature is why squared error has a closed-form solution.
Exercise 3 solves that closed form directly — the **normal equations** —
and confirms it matches `LinearRegression` to thirteen decimal places.
Absolute error has no equivalent closed form, because its derivative does
not exist at a residual of exactly zero; fitting it needs an iterative
solver instead.

## The centrepiece: one outlier, three losses

Exercises 4 and 4b move a single point 80 units off the line and re-fit
three estimators on identical data:

| estimator | loss it minimises | slope before | slope after | movement |
| --- | --- | --- | --- | --- |
| `LinearRegression` | squared error | 3.0465 | 3.8010 | **+0.7545** |
| `HuberRegressor` | Huber (blended) | 2.9870 | 3.0308 | +0.0437 |
| `QuantileRegressor(0.5)` | absolute error | 2.9961 | 3.0064 | +0.0104 |

One point, and least squares moves seventeen times further than Huber and
seventy-two times further than the median fit. Squaring the residual
means a residual of 80 contributes 6,400 to the total loss instead of 80
— the optimizer will trade a great deal of fit elsewhere to shrink that
one huge term, and "elsewhere" is every other point on the line.

Exercise 5 sweeps Huber's `epsilon` parameter on that same contaminated
data, from 1.0 up to 100.0. The slope climbs smoothly from
absolute-error-like behaviour toward the least-squares answer, and at
large epsilon it lands exactly on the OLS slope — Huber's blend of the two
losses is genuinely continuous, not a discrete switch.

## What squared error is betting on

Exercises 6 and 6b are the payoff. Fit OLS and Huber on 500 independently
generated datasets, twice — once with Gaussian errors, once with
heavy-tailed (Student's t, 3 degrees of freedom) errors of similar central
spread:

| errors | OLS spread (sd) | Huber spread (sd) | ratio OLS/Huber |
| --- | --- | --- | --- |
| Gaussian | 0.0560 | 0.0588 | 0.9524 — OLS tighter |
| heavy-tailed | 0.0589 | 0.0422 | 1.3957 — Huber tighter |

Both estimators stay close to unbiased in both settings. What changes is
which one is more *precise*. Gauss-Markov's theorem says ordinary least
squares is the **best linear unbiased estimator** under its assumptions —
every one of those four words is load-bearing, and "best" specifically
means lowest variance *among linear, unbiased estimators*, not lowest
variance full stop, and not under any distribution of errors whatsoever.
Change the error distribution and the ranking measurably flips.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_loss_lib.py`) and ten skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `loss_lib.py`, `test_loss_lib.py` and `test_loss_claims.py`; pytest
aborts on the module-name collision. Run them separately, always.
