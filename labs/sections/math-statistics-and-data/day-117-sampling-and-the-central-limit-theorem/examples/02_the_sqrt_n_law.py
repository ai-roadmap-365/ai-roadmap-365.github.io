"""Exercise 2 -- the sqrt(n) law.

Four sample sizes, each exactly 4x the one before it: 10, 40, 160, 640. Every
time n quadruples, the standard error of the mean should roughly HALVE, not
quarter -- that is the entire economics of measurement in one number. This
asserts the RATIOS between successive standard errors, not four hard-coded
values, so the check is honest about what simulation noise can and cannot
pin down.
"""

import math

import numpy as np

import dataset as D
from sampling import sampling_distribution

rng = np.random.default_rng(2)

standard_errors = {}
for n in D.SQRT_N_LAW_NS:
    means = sampling_distribution(D.SKEWED_POP, n, D.SQRT_N_LAW_TRIALS, rng)
    standard_errors[n] = means.std(ddof=1)
    print(f"n = {n:>4}  measured SE = {standard_errors[n]:.4f}")

print()
ratios = []
for smaller, larger in zip(D.SQRT_N_LAW_NS, D.SQRT_N_LAW_NS[1:]):
    ratio = standard_errors[smaller] / standard_errors[larger]
    ratios.append(ratio)
    print(f"SE(n={smaller}) / SE(n={larger}) = {ratio:.3f}  (expected: sqrt(4) = {math.sqrt(4):.3f})")

for (smaller, larger), ratio in zip(zip(D.SQRT_N_LAW_NS, D.SQRT_N_LAW_NS[1:]), ratios):
    gap = abs(ratio - 2.0)
    assert gap < D.SQRT_N_LAW_RATIO_TOLERANCE, (
        f"SE(n={smaller})/SE(n={larger}) = {ratio:.3f} strayed more than "
        f"{D.SQRT_N_LAW_RATIO_TOLERANCE} from the predicted 2.0"
    )

# The compounded law across all three quadruplings: from n=10 to n=640 is a
# 64x growth in sample size, so the standard error should have fallen by
# close to sqrt(64) = 8x, not 64x -- the mistake a 1/n law would predict.
overall_ratio = standard_errors[D.SQRT_N_LAW_NS[0]] / standard_errors[D.SQRT_N_LAW_NS[-1]]
print(f"\noverall SE(n=10) / SE(n=640) = {overall_ratio:.2f}  (expected: sqrt(64) = {math.sqrt(64):.2f})")
assert abs(overall_ratio - 8.0) < 1.5, "the compounded sqrt(n) law did not hold across the full range"
assert overall_ratio < 20.0, "a ratio anywhere near 64 would mean the error fell like 1/n, not 1/sqrt(n)"

print("02_the_sqrt_n_law.py: every assertion held.")
