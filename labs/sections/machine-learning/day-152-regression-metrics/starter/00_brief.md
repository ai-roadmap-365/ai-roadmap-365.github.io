# Day 152 lab brief — What You Report Is Not What You Optimise

Day 149 drew the line: a loss is what you optimise, a metric is what you
report, and they do not have to be the same function. This lab measures
the reporting side -- RMSE, MAE, MAPE, R2 and adjusted R2 -- and the traps
in each.

## The claim you are here to measure

> R2 is the most quoted and least understood number in regression.

Exercise 1 measures why. Fit a linear model on the diabetes dataset, then
add columns of **pure noise** -- independent random numbers with zero
relationship to the target -- and watch training R2 anyway:

| noise columns added | train R2 |
| --- | --- |
| 0 | 0.5554 |
| 1 | 0.5555 |
| 5 | 0.5648 |
| 20 | 0.5754 |
| 100 | 0.7403 |

Every one of those columns is garbage. The model climbs to 0.7403 anyway,
because more predictors can only help a training-set fit -- never hurt it.
Exercise 1b brings in adjusted R2, which is built to penalise exactly this,
and shows it working at a modest number of extra columns and **breaking
down at a large one**: at 100 noise columns (110 predictors on 331 rows),
adjusted R2 climbs back above the no-noise baseline even though nothing
useful was added.

## The part most people get wrong

Most people believe R2 lives in `[0, 1]` and means "percent of variance
explained". Exercise 2 shows the first half is false: a deliberately bad
predictor scores **-4.7009**, nearly five full units below zero. There is
no floor. R2 compares your model to one specific baseline -- always predict
the training mean -- and if you do worse than that baseline, the number
goes negative with no limit.

## Why RMSE and MAE can disagree about which model is better

Exercise 6 is the single most valuable measurement in this lab. Two models,
scored on the same targets:

| Model | RMSE | MAE |
| --- | --- | --- |
| A: many small errors | 1.947 | 1.586 |
| B: a few large errors | 4.4353 | 0.8417 |

RMSE says A is better. MAE says B is better. **Both are correct, about
different things.** RMSE squares every error before averaging, so a
handful of large misses dominates it. MAE weighs every error equally, so
being right almost everywhere dominates it. Reporting only one of the two
would silently pick a winner the other metric disagrees with.

## MAPE, breaking

Exercises 4, 4b and 5 build MAPE up and then break it three ways: it
explodes (without raising or warning) when a true value is exactly zero;
it explodes almost as badly when a true value is merely close to zero; and
it is structurally asymmetric -- the worst possible under-prediction caps
out at 100 percent, while over-prediction has no ceiling at all.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_metrics_lib.py`) and twelve skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `regression_metrics_lib.py`, `test_metrics_lib.py` and
`test_metrics_claims.py`; pytest aborts on the module-name collision. Run
them separately, always.
