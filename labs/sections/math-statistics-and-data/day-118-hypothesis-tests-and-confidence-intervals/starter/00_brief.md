# The nine exercises

Work through these in order, in `inference.py`. Check yourself as you go:

```bash
.venv/bin/pytest starter -q
```

Unattempted work reports as **skipped**, never failed. Wrong work **fails**
with your answer printed beside the correct one.

## 1. The two-sample z-test, from scratch

`phi(z)`, `p_from_z_two_sided(z)`, `two_sample_z_test(a, b)`. Build the
standard normal CDF from `math.erf`, turn a z-statistic into a two-sided
p-value, and combine them into a two-sample test that uses each sample's
own variance. Check the result against a hand computation done with the
standard library's `statistics` module -- they must match to the ninth
decimal place, because both are exact arithmetic on the same numbers.

## 2. The critical value, and the centrepiece: coverage

`z_critical_two_sided(alpha)`, `confidence_interval_mean(sample, alpha)`.
There is no closed form for the inverse of `phi`, so find the z whose
two-sided tail probability is `alpha` by bisecting `phi` itself. Then build
a confidence interval as `mean +/- z * standard_error`. Build 10,000 such
intervals from a population with a KNOWN true mean and assert the fraction
that actually contain it lands within three standard errors of 0.95 --
this is what "95% confidence" measures.

## 3. `ci_excludes` and the duality

`ci_excludes(interval, value)`, `one_sample_z_test_against_value(sample,
null_value)`. A test at level alpha should reject the null value exactly
when the `(1 - alpha)` interval excludes it. Assert this holds with ZERO
mismatches across many datasets -- not approximately, exactly, because both
come from the same z.

## 4. The permutation test, from scratch

`permutation_test_diff_means(a, b, n_perm, rng)`. Shuffle the pooled group
labels, recompute the difference in means, repeat `n_perm` times, and count
how many shuffles were at least as extreme as what was actually observed.
No distributional assumption anywhere. Assert it agrees closely with the
z-test on a moderate-n normal case, and diverges more (while remaining a
valid probability) on a small-n, skewed case.

## 5. Multiple comparisons and Bonferroni

`bonferroni_alpha(alpha, m)`. Assert the exact family-wise false-positive
rate for 20 independent alpha=0.05 tests is `1 - 0.95**20 = 0.6415`,
confirm it by simulation, then assert the Bonferroni-corrected rate lands
near `0.0488`.

## 6. Power

`power_two_sample_z(effect, sigma, n_per_group, alpha)`. Derive the power
of the test above from the shifted normal distribution of the test
statistic under a true effect. Assert it rises monotonically with both `n`
and `effect`, and check the closed form against a direct simulation.

## 7. Effect size versus n

Nothing new to write here -- exercise 7 in
`examples/07_effect_size_vs_n.py` runs against whatever `two_sample_z_test`
you wrote for exercise 1. A tiny, fixed relative difference should not be
significant at a small n and should be significant at an enormous one, with
the effect size itself unchanged.

## 8. Peeking

Nothing new to write here either -- exercise 8 in `examples/08_peeking.py`
runs against `one_sample_z_test_against_value` from exercise 3. Checking
after every 10 observations and stopping at the first p < 0.05 should push
the true false-positive rate well above the nominal alpha, under a null
hypothesis that is true the entire time.

## 9. The bootstrap interval, versus the normal-approximation interval

`bootstrap_ci(sample, statistic, n_boot, alpha, rng)`. Resample with
replacement, recompute the statistic, take percentiles of the result.
Assert it agrees closely with `confidence_interval_mean` for the sample
mean -- both center and width -- where both are valid.
