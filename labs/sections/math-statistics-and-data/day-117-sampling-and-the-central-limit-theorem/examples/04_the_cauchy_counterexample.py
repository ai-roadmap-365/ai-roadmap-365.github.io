"""Exercise 4 -- where the central limit theorem actually fails.

The Exponential distribution has a finite variance, so its sample mean's
spread should shrink by close to sqrt(100) = 10x when n grows from 10 to
1,000. The Cauchy distribution has NO defined mean or variance -- its tails
are too heavy -- and the mean of n Cauchy draws is itself standard-Cauchy
distributed, for every n. Averaging a thousand of them should be no better
than averaging ten.

The interquartile range (IQR) is used as the spread measure here rather than
the standard deviation, and that choice is load-bearing: a Cauchy sample's
standard deviation is not an estimate of anything, because the population
quantity it would estimate does not exist. The IQR depends only on the order
of the data, so it stays meaningful even when the mean and variance do not.
"""

import dataset as D
from sampling import cauchy_mean_iqr, exponential_mean_iqr
import numpy as np

rng = np.random.default_rng(4)

exp_iqr_small = exponential_mean_iqr(D.CAUCHY_DEMO_N_SMALL, D.CAUCHY_DEMO_TRIALS, rng, D.EXPONENTIAL_SCALE)
exp_iqr_large = exponential_mean_iqr(D.CAUCHY_DEMO_N_LARGE, D.CAUCHY_DEMO_TRIALS, rng, D.EXPONENTIAL_SCALE)
exp_ratio = exp_iqr_small / exp_iqr_large

cauchy_iqr_small = cauchy_mean_iqr(D.CAUCHY_DEMO_N_SMALL, D.CAUCHY_DEMO_TRIALS, rng)
cauchy_iqr_large = cauchy_mean_iqr(D.CAUCHY_DEMO_N_LARGE, D.CAUCHY_DEMO_TRIALS, rng)
cauchy_ratio = cauchy_iqr_small / cauchy_iqr_large

print(f"Exponential(scale={D.EXPONENTIAL_SCALE}): IQR of the mean at n={D.CAUCHY_DEMO_N_SMALL} = "
      f"{exp_iqr_small:.4f}, at n={D.CAUCHY_DEMO_N_LARGE} = {exp_iqr_large:.4f}")
print(f"  ratio = {exp_ratio:.2f}  (100x more data, expected shrink ~ sqrt(100) = 10x)")
print()
print(f"standard Cauchy: IQR of the mean at n={D.CAUCHY_DEMO_N_SMALL} = "
      f"{cauchy_iqr_small:.4f}, at n={D.CAUCHY_DEMO_N_LARGE} = {cauchy_iqr_large:.4f}")
print(f"  ratio = {cauchy_ratio:.2f}  (100x more data, expected shrink: NONE)")

assert exp_ratio > D.EXPONENTIAL_SHRINK_FLOOR, (
    f"the Exponential mean's spread shrank by only {exp_ratio:.2f}x, "
    f"expected close to 10x"
)
assert D.CAUCHY_NO_SHRINK_LOW < cauchy_ratio < D.CAUCHY_NO_SHRINK_HIGH, (
    f"the Cauchy mean's spread shrank by {cauchy_ratio:.2f}x -- it should have stayed "
    f"roughly flat, not shrunk toward the Exponential's ~10x"
)
assert cauchy_ratio < exp_ratio / 3.0, (
    "the Cauchy ratio was not clearly smaller than the Exponential ratio -- "
    "the whole point of this exercise is the contrast between the two"
)

print("04_the_cauchy_counterexample.py: every assertion held.")
