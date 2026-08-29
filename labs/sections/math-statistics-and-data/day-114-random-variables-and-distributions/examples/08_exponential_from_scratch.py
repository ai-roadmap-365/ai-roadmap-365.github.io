"""Exercise 8 -- the exponential distribution, sampled from scratch as
-ln(U)/lambda, compared against `numpy.random.Generator.exponential`.

Two checks: both sample means land near 1/lambda, and a hand-written
max-gap statistic between the two empirical cdfs -- the two-sample
Kolmogorov-Smirnov statistic, since scipy.stats.ks_2samp is not available
in this environment -- stays below a threshold derived from the
Dvoretzky-Kiefer-Wolfowitz inequality.
"""

import numpy as np

import dataset as D
import sampling as samp

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


rate = D.EXPONENTIAL_RATE
target_mean = 1.0 / rate
n = D.EXPONENTIAL_SAMPLE_SIZE

print(f"Exponential(rate={rate}), {n:,} samples each, seed {D.SEED}")
print("-" * 60)

rng = np.random.default_rng(D.SEED)
scratch = samp.sample_exponential_scratch(rate, rng, n)
built_in = rng.exponential(scale=target_mean, size=n)

scratch_mean = float(scratch.mean())
built_in_mean = float(built_in.mean())
var_exponential = target_mean**2
tolerance = 3.0 * D.standard_error_of_mean(var_exponential, n)

print(f"  target mean 1/rate       = {target_mean}")
print(f"  scratch  (-ln(U)/rate)   mean = {scratch_mean:.6f}  gap {abs(scratch_mean - target_mean):.6f}")
print(f"  built-in (Generator)     mean = {built_in_mean:.6f}  gap {abs(built_in_mean - target_mean):.6f}")
print(f"  tolerance (3 SE)         = {tolerance:.6f}")

check("the from-scratch sampler's mean is within 3 SE of 1/rate", abs(scratch_mean - target_mean) < tolerance)
check("NumPy's own sampler's mean is within 3 SE of 1/rate", abs(built_in_mean - target_mean) < tolerance)

print()
print("Max-gap statistic between the two empirical cdfs (hand-written, no scipy)")
print("-" * 60)

gap_stat = samp.max_gap_statistic(scratch, built_in)
threshold = D.dkw_two_sample_threshold(n, n)
print(f"  max |F_scratch(x) - F_built_in(x)| over the pooled sample = {gap_stat:.6f}")
print(f"  DKW-derived threshold (alpha=0.01, n={n:,} each)          = {threshold:.6f}")
check("the max-gap statistic is below the DKW-derived threshold", gap_stat < threshold)

print()
if all(ok for _, ok in checks_held):
    print(f"08_exponential_from_scratch.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
