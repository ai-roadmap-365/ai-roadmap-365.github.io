# The nine exercises

Work through these in order, in `sampling.py`. Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. The sampling distribution itself

`sampling_distribution(population, n, trials, rng)` and
`population_mean_std(population)`. Draw `trials` independent samples of size
`n` from `population`, with replacement, and return the array of sample
means. Assert its own mean is close to the population mean, and its own
standard deviation close to `sigma / sqrt(n)`, both within three standard
errors — a statistic has a distribution too, and this is what it looks like.

## 2. The standard error and the sqrt(n) law

`theoretical_standard_error(sigma, n)`. For `n` in `{10, 40, 160, 640}` --
each exactly 4x the one before -- assert the measured standard error roughly
**halves** each time, not quarters. Assert the *ratios* between successive
standard errors, not four hard-coded values.

## 3. The CLT from a skewed population

`skewness(values)`. Measure the skewness of the sampling distribution of the
mean for an increasingly large `n`, drawn from a heavily right-skewed
population. Assert it falls monotonically toward zero as `n` grows -- the
population's lopsidedness washes out of the statistic.

## 4. The Cauchy counterexample

`iqr(values)`, `exponential_mean_iqr(n, trials, rng, scale)`,
`cauchy_mean_iqr(n, trials, rng)`. For an Exponential population, assert the
spread of the sample mean shrinks by roughly the expected factor from n=10
to n=1000. For a **Cauchy** population, assert it does **not** shrink. Use
the IQR rather than the standard deviation -- a Cauchy sample's standard
deviation is not an estimate of anything, because the population variance it
would estimate does not exist.

## 5. Bias does not shrink

`mean_absolute_error(estimates, truth)`, `biased_pool(population)`. Build a
sampler that can only draw from the half of the population above its own
median. Assert its error stays roughly constant as `n` grows by a factor of
100, while an unbiased sampler's error shrinks by roughly ten -- more data
buys a biased sampler a more *precise* wrong answer, never a correct one.

## 6. The bootstrap, from scratch

`bootstrap_replicates(data, statistic, n_boot, rng)`,
`bootstrap_standard_error(data, statistic, n_boot, rng)`. Resample a dataset
with replacement, recompute a statistic on every resample, and read its
standard error off the spread of the results. Assert it agrees with
`sigma_hat / sqrt(n)` for the mean, then apply the same code to the
**median**, where no simple formula exists, and check the result for
sanity against the spread of medians from genuinely fresh samples.

## 7. Dependence inflates the true standard error

`ar1_series(n, phi, sigma, rng)`, `naive_standard_error(series)`,
`true_standard_error_by_replication(n, phi, sigma, replications, rng)`.
Generate an autocorrelated series, measure its TRUE standard error by
replication, and assert the naive `sample_std / sqrt(n)` formula understates
it meaningfully.

## 8. The evaluation-margin calculation

`binomial_standard_error(phat, n)`. For an accuracy of 91.4% on 500
examples, assert the standard error is about 1.25 percentage points, and
that a 0.3-point difference between two models is well inside one standard
error -- noise, not a demonstrated improvement.

## 9. Reproducibility

Nothing new to write here -- exercise 9 in `examples/09_reproducibility.py`
runs against whatever `sampling_distribution` you wrote for exercise 1. The
same seed must give identical results; a different seed must give different
results that still agree within tolerance. If exercise 1 is correct, this
one follows for free -- and if it does not hold, that is a sign exercise 1's
random-index construction is not using `rng` correctly.
