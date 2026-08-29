# The nine exercises

Work through these in order. Predict the answer to each `answers.py`
question *before* running anything — the breakdown-point question and the
percentile-agreement question only catch you if you commit to a guess
first.

Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. Mean, median, mode (`descriptive.py`)

Write `mean()`, `median()` (handling both odd and even lengths) and
`modes()` (returning every tied value, not just one) from scratch. Assert
against the `statistics` module on the same inputs.

## 2. The breakdown point (`descriptive.py`)

`breakdown_point_mean()` and `breakdown_point_median()`. Replace the salary
list's largest value with an absurd one and watch the mean move by over a
million dollars while the median does not move at all — exact equality is
the right assertion for the median.

## 3. Bessel's correction, measured (`simulate.py`)

`bessel_trial_variances()` draws many small samples from a population of
known variance and computes both the divide-by-n and divide-by-(n-1)
estimators for each one. The divide-by-n estimator should average out
biased low by the factor `(n-1)/n`; the divide-by-(n-1) estimator should
land within a few standard errors of the truth.

## 4. Percentile ambiguity (`descriptive.py`)

`percentile_under()` wraps `numpy.percentile` with an explicit `method=`.
Call it under several conventions on the same small array and confirm that
at least two of them genuinely disagree about the 75th percentile.

## 5. Pearson versus Spearman (`descriptive.py`)

`pearson()` and `spearman()`. A perfect symmetric parabola should give a
Pearson correlation essentially zero; a perfect monotone cubic should give
a Spearman correlation of exactly 1.0.

## 6. Anscombe's quartet (`descriptive.py`)

`anscombe_summary()` computes the five classic statistics (mean x, mean y,
variance x, variance y, correlation, slope) for each of the four published
sets — they should all agree. `shape_statistics()` computes three
diagnostics the classic five cannot see, and those should tell the four
sets apart.

## 7. Simpson's paradox (`descriptive.py`)

`success_rate()` and `combined_rate()`. Confirm treatment A beats treatment
B in *both* subgroups of the smallest table that shows the paradox, and
that treatment B still wins *overall* — both directions, from the same
four numbers.

## 8. Robust spread under contamination (`descriptive.py`, `simulate.py`)

`contaminated_sample()` adds a handful of extreme values to a clean sample.
`median_absolute_deviation()` measures spread the way the standard
deviation does, but robustly. Confirm the standard deviation inflates by a
large multiplier while the MAD barely moves.

## 9. Standardisation (`descriptive.py`)

`zscores()`. Confirm the standardised sample has mean 0 and standard
deviation 1, and that standardising does not change the Pearson correlation
between two variables.
