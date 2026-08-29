"""Exercise 9 -- reproducibility.

Every simulation in this lab depends on a seeded `numpy.random.Generator`.
The same seed must give bit-identical results -- otherwise none of the
"measured X" claims elsewhere in this lab mean anything, because a rerun
could silently produce a different number. A different seed should give a
DIFFERENT sampling distribution that still agrees with the first one within
a tolerance derived from the standard error, since both are estimating the
same underlying quantity.
"""

import numpy as np

import dataset as D
from sampling import sampling_distribution, theoretical_standard_error, population_mean_std

rng_a1 = np.random.default_rng(D.REPRO_SEED_A)
rng_a2 = np.random.default_rng(D.REPRO_SEED_A)
rng_b = np.random.default_rng(D.REPRO_SEED_B)

means_a1 = sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, rng_a1)
means_a2 = sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, rng_a2)
means_b = sampling_distribution(D.SKEWED_POP, D.REPRO_N, D.REPRO_TRIALS, rng_b)

identical = np.array_equal(means_a1, means_a2)
different = not np.array_equal(means_a1, means_b)

pop_mean, pop_sigma = population_mean_std(D.SKEWED_POP)
theoretical_se = theoretical_standard_error(pop_sigma, D.REPRO_N)
# The standard error of an estimate built from REPRO_TRIALS sample means.
se_of_mean_estimate = theoretical_se / np.sqrt(D.REPRO_TRIALS)

gap_a_b = abs(means_a1.mean() - means_b.mean())

print(f"seed {D.REPRO_SEED_A}, run 1: first three means = {means_a1[:3]}")
print(f"seed {D.REPRO_SEED_A}, run 2: first three means = {means_a2[:3]}")
print(f"seed {D.REPRO_SEED_B}, run 1: first three means = {means_b[:3]}")
print()
print(f"same seed produces bit-identical arrays: {identical}")
print(f"different seed produces a different array: {different}")
print(f"gap between seed {D.REPRO_SEED_A}'s and seed {D.REPRO_SEED_B}'s estimate of the mean "
      f"= {gap_a_b:.5f} ({gap_a_b / se_of_mean_estimate:.2f} standard errors)")

assert identical, "the same seed did not reproduce identical results"
assert different, "two different seeds produced identical results, which should not happen"
assert gap_a_b < 5.0 * se_of_mean_estimate, (
    "two different seeds' estimates of the population mean disagreed by more than "
    "5 standard errors -- they should agree within simulation noise"
)

print("09_reproducibility.py: every assertion held.")
