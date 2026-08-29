"""Exercise 6 -- the bootstrap, from scratch.

Resample a single dataset with replacement, recompute a statistic on every
resample, and read the statistic's standard error straight off the spread of
the results -- no formula for the statistic's own sampling distribution
required.

First check it against the MEAN, where a formula (sigma_hat / sqrt(n)) does
exist, so the bootstrap can be judged against a known answer. Then apply the
exact same code to the MEDIAN, where no simple closed form exists, and check
its answer for sanity against the spread of medians computed from genuinely
fresh, independent samples of the same population -- the bootstrap's whole
reason for existing.
"""

import dataset as D
from sampling import bootstrap_standard_error
import numpy as np

rng = np.random.default_rng(6)

sample = rng.normal(loc=D.BOOTSTRAP_SAMPLE_MEAN, scale=D.BOOTSTRAP_SAMPLE_STD, size=D.BOOTSTRAP_SAMPLE_SIZE)
sigma_hat = sample.std(ddof=1)
theoretical_se = sigma_hat / np.sqrt(D.BOOTSTRAP_SAMPLE_SIZE)

boot_se_mean = bootstrap_standard_error(
    sample, lambda a: a.mean(axis=1), D.BOOTSTRAP_N_BOOT, rng
)
boot_se_median = bootstrap_standard_error(
    sample, lambda a: np.median(a, axis=1), D.BOOTSTRAP_N_BOOT, rng
)

# "Genuinely fresh samples", drawn straight from the same Normal population
# rather than resampled from the one dataset above -- this is the sanity
# check the median bootstrap is measured against, since no formula exists.
fresh = rng.normal(
    loc=D.BOOTSTRAP_SAMPLE_MEAN,
    scale=D.BOOTSTRAP_SAMPLE_STD,
    size=(D.FRESH_MEDIAN_REPLICATIONS, D.BOOTSTRAP_SAMPLE_SIZE),
)
fresh_median_se = np.median(fresh, axis=1).std(ddof=1)

relative_error_mean = abs(boot_se_mean - theoretical_se) / theoretical_se
median_ratio = boot_se_median / fresh_median_se

print(f"sample size = {D.BOOTSTRAP_SAMPLE_SIZE}, sigma_hat = {sigma_hat:.4f}")
print(f"theoretical SE of the mean (sigma_hat / sqrt(n)) = {theoretical_se:.4f}")
print(f"bootstrap SE of the mean ({D.BOOTSTRAP_N_BOOT} resamples) = {boot_se_mean:.4f}")
print(f"  relative error = {relative_error_mean:.3%}")
print()
print(f"bootstrap SE of the MEDIAN ({D.BOOTSTRAP_N_BOOT} resamples) = {boot_se_median:.4f}")
print(f"SE of the median from {D.FRESH_MEDIAN_REPLICATIONS} genuinely fresh samples = {fresh_median_se:.4f}")
print(f"  ratio (bootstrap / fresh) = {median_ratio:.2f}")

assert relative_error_mean < D.BOOTSTRAP_MEAN_RELATIVE_TOLERANCE, (
    f"the bootstrap SE of the mean disagreed with sigma_hat / sqrt(n) by "
    f"{relative_error_mean:.1%}, expected under {D.BOOTSTRAP_MEAN_RELATIVE_TOLERANCE:.0%}"
)
assert D.BOOTSTRAP_MEDIAN_SANITY_LOW < median_ratio < D.BOOTSTRAP_MEDIAN_SANITY_HIGH, (
    f"the bootstrap SE of the median ({boot_se_median:.4f}) is not within a sane "
    f"range of the fresh-sample benchmark ({fresh_median_se:.4f})"
)

print("06_bootstrap_from_scratch.py: every assertion held.")
