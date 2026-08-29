"""Exercise 1 -- the sampling distribution of the mean.

Draw 20,000 independent samples of size 40 from a skewed population, compute
each sample's mean, and look at the DISTRIBUTION of those 20,000 means -- not
any single one of them. Its own mean should sit close to the population mean,
and its own spread should sit close to sigma / sqrt(n).
"""

import numpy as np

import dataset as D
from sampling import population_mean_std, sampling_distribution, theoretical_standard_error

rng = np.random.default_rng(1)

pop_mean, pop_sigma = population_mean_std(D.SKEWED_POP)
means = sampling_distribution(D.SKEWED_POP, D.EX1_N, D.EX1_TRIALS, rng)

measured_mean = means.mean()
measured_se = means.std(ddof=1)
theoretical_se = theoretical_standard_error(pop_sigma, D.EX1_N)

# The standard error OF the measured mean itself, so "close" below is a
# statement with a real yardstick rather than a guessed number: with 20,000
# trials, the mean of the sampling distribution should sit within a few of
# these of the true population mean almost always.
se_of_measured_mean = measured_se / np.sqrt(D.EX1_TRIALS)
# The sample standard deviation of 20,000 draws has its own standard error,
# approximately sigma / sqrt(2 * trials) for a roughly-normal statistic.
se_of_measured_se = measured_se / np.sqrt(2 * D.EX1_TRIALS)

print(f"population mean = {pop_mean:.4f}, population sigma = {pop_sigma:.4f}")
print(f"n = {D.EX1_N}, trials = {D.EX1_TRIALS}")
print(f"measured mean of the sampling distribution = {measured_mean:.4f}")
print(f"measured standard error (std of the {D.EX1_TRIALS} sample means) = {measured_se:.4f}")
print(f"theoretical standard error (sigma / sqrt(n)) = {theoretical_se:.4f}")

mean_gap_in_ses = abs(measured_mean - pop_mean) / se_of_measured_mean
se_gap_in_ses = abs(measured_se - theoretical_se) / se_of_measured_se
print(f"gap between measured and population mean = {mean_gap_in_ses:.2f} standard errors")
print(f"gap between measured and theoretical SE = {se_gap_in_ses:.2f} standard errors")

assert mean_gap_in_ses < 3.0, "the sampling distribution's own mean drifted too far from the population mean"
assert se_gap_in_ses < 3.0, "the sampling distribution's own spread drifted too far from sigma / sqrt(n)"

print("01_sampling_distribution.py: every assertion held.")
