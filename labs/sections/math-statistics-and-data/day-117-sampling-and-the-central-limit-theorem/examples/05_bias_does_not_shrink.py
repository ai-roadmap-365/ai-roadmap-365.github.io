"""Exercise 5 -- sampling bias is not sampling error, and n does not fix it.

An UNBIASED sampler draws from the whole population; a BIASED sampler draws
only from the half of the population strictly above the population's own
median, no matter how many draws it takes. Both errors -- mean absolute
distance from the true population mean -- are tracked as the sample size
grows 100x, from 30 to 3,000.

The unbiased sampler's error should shrink by close to 10x, exactly the
sqrt(n) law from exercise 2. The biased sampler's error should stay roughly
FLAT: more data buys it a more precise estimate of the wrong number, and the
mathematics does not know the difference between "confident" and "correct".
"""

import dataset as D
from sampling import biased_pool, mean_absolute_error, sampling_distribution
import numpy as np

rng = np.random.default_rng(5)

true_mean = float(D.SKEWED_POP.mean())
pool = biased_pool(D.SKEWED_POP)
print(f"true population mean = {true_mean:.4f}")
print(f"biased pool (values above the population median) mean = {pool.mean():.4f}  "
      f"-- this is what the biased sampler converges to, not the true mean")
print()

unbiased_small = mean_absolute_error(
    sampling_distribution(D.SKEWED_POP, D.BIAS_DEMO_N_SMALL, D.BIAS_DEMO_TRIALS, rng), true_mean
)
unbiased_large = mean_absolute_error(
    sampling_distribution(D.SKEWED_POP, D.BIAS_DEMO_N_LARGE, D.BIAS_DEMO_TRIALS, rng), true_mean
)
biased_small = mean_absolute_error(
    sampling_distribution(pool, D.BIAS_DEMO_N_SMALL, D.BIAS_DEMO_TRIALS, rng), true_mean
)
biased_large = mean_absolute_error(
    sampling_distribution(pool, D.BIAS_DEMO_N_LARGE, D.BIAS_DEMO_TRIALS, rng), true_mean
)

unbiased_ratio = unbiased_small / unbiased_large
biased_ratio = biased_small / biased_large

print(f"UNBIASED sampler: mean abs error at n={D.BIAS_DEMO_N_SMALL} = {unbiased_small:.4f}, "
      f"at n={D.BIAS_DEMO_N_LARGE} = {unbiased_large:.4f}  (ratio = {unbiased_ratio:.2f})")
print(f"BIASED sampler:   mean abs error at n={D.BIAS_DEMO_N_SMALL} = {biased_small:.4f}, "
      f"at n={D.BIAS_DEMO_N_LARGE} = {biased_large:.4f}  (ratio = {biased_ratio:.2f})")

assert unbiased_ratio > D.UNBIASED_SHRINK_FLOOR, (
    f"the unbiased sampler's error only shrank by {unbiased_ratio:.2f}x, expected close to 10x"
)
assert D.BIASED_FLAT_LOW < biased_ratio < D.BIASED_FLAT_HIGH, (
    f"the biased sampler's error changed by {biased_ratio:.2f}x -- it should have stayed roughly flat"
)
assert biased_large > 3.0 * unbiased_large, (
    "at the LARGE sample size the biased sampler's error should still dwarf the unbiased "
    "sampler's -- more data did not rescue it"
)

print("05_bias_does_not_shrink.py: every assertion held.")
