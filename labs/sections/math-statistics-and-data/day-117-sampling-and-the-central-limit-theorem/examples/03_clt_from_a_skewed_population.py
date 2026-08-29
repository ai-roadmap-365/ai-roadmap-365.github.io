"""Exercise 3 -- the central limit theorem, measured rather than assumed.

The population itself is heavily right-skewed (an Exponential shape). As n
grows, the SKEWNESS of the sampling distribution of the mean should fall
toward zero, monotonically -- the population's lopsidedness washing out of
the statistic even though it never leaves the population itself.

Two more populations that look nothing like a bell -- a biased coin and a
lumpy two-spike distribution -- are reported alongside, to show the same
flattening is not a fact about this one population's shape.
"""

import numpy as np

import dataset as D
from sampling import population_mean_std, sampling_distribution, skewness

rng = np.random.default_rng(3)

pop_mean, pop_sigma = population_mean_std(D.SKEWED_POP)
pop_skew = skewness(D.SKEWED_POP)
print(f"population (Exponential-shaped): mean = {pop_mean:.3f}, skewness = {pop_skew:.3f}")
print()

skews = []
for n in D.SKEW_DEMO_NS:
    means = sampling_distribution(D.SKEWED_POP, n, D.SKEW_DEMO_TRIALS, rng)
    s = skewness(means)
    skews.append(s)
    print(f"n = {n:>4}  skewness of the sampling distribution = {s:.4f}")

print()
for smaller_n, larger_n, s_small, s_large in zip(
    D.SKEW_DEMO_NS, D.SKEW_DEMO_NS[1:], skews, skews[1:]
):
    assert s_large < s_small, (
        f"skewness did not decrease going from n={smaller_n} ({s_small:.4f}) "
        f"to n={larger_n} ({s_large:.4f})"
    )
print(f"skewness fell monotonically across n = {D.SKEW_DEMO_NS}: "
      + " > ".join(f"{s:.3f}" for s in skews))

# Two more non-bell populations, reported for the lesson's narrative. Both
# show the same qualitative flattening; neither is asserted to the same
# precision as the primary skewed population above, since a Bernoulli
# population's sampling-distribution skewness is much noisier at small n.
for label, population in (("biased coin", D.COIN_POP), ("two-spike", D.TWO_SPIKE_POP)):
    p_skew = skewness(population)
    small_n_skew = skewness(sampling_distribution(population, 5, D.SKEW_DEMO_TRIALS, rng))
    large_n_skew = skewness(sampling_distribution(population, 320, D.SKEW_DEMO_TRIALS, rng))
    print(
        f"{label}: population skewness = {p_skew:.3f}, "
        f"sampling-distribution skewness at n=5 -> {small_n_skew:.3f}, "
        f"at n=320 -> {large_n_skew:.3f}"
    )
    assert abs(large_n_skew) < abs(small_n_skew), (
        f"{label}: skewness at n=320 was not smaller in magnitude than at n=5"
    )

print("03_clt_from_a_skewed_population.py: every assertion held.")
