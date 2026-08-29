"""Exercise 8 -- Monte Carlo error scaling: a hundred times the samples buys
a tenth of the error, not a hundredth.

Estimate P(two dice sum to 7) -- exactly 1/6 -- by simulation, at four sample
sizes four decades apart. The error shrinks like 1/sqrt(n): multiplying n by
10 should shrink the average error by about sqrt(10), roughly 3.16x, not by
10x. Day 117 explains why with the central limit theorem; this script only
measures that it is true.

The assertion is about the SHAPE of the trend, averaged over many seeds --
never a single sampled value, which would be flaky on someone else's machine.
"""

import numpy as np

import dataset as D
import simulate as S

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


target = float(D.MONTE_CARLO_TARGET)
print(f"True probability: P(sum == 7) = {D.MONTE_CARLO_TARGET} = {target:.6f}")
print(f"Averaging over {len(D.MONTE_CARLO_SEEDS)} seeds at each sample size")
print("-" * 60)

mean_errors = []
for n in D.MONTE_CARLO_SAMPLE_SIZES:
    errors = []
    for seed in D.MONTE_CARLO_SEEDS:
        rng = np.random.default_rng(seed)
        estimate = S.simulate_sum_seven(rng, n)
        errors.append(abs(estimate - target))
    mean_error = sum(errors) / len(errors)
    mean_errors.append(mean_error)
    predicted_se = D.standard_error(target, n)
    print(
        f"  n = {n:>7,}   mean |error| = {mean_error:.6f}   "
        f"predicted standard error = {predicted_se:.6f}"
    )

print()
print("Does the error shrink, and does it shrink like 1/sqrt(n)?")
print("-" * 60)
first, last = mean_errors[0], mean_errors[-1]
n_first, n_last = D.MONTE_CARLO_SAMPLE_SIZES[0], D.MONTE_CARLO_SAMPLE_SIZES[-1]
n_ratio = n_last / n_first
error_ratio = first / last
sqrt_prediction = n_ratio**0.5
linear_prediction = n_ratio
print(f"  n grew by a factor of {n_ratio:.0f} (from {n_first:,} to {n_last:,})")
print(f"  the mean error shrank by a factor of {error_ratio:.2f}")
print(f"  a 1/sqrt(n) law predicts a shrink of  {sqrt_prediction:.2f}x")
print(f"  a 1/n law predicts a shrink of        {linear_prediction:.0f}x")
print(f"  observed shrink ({error_ratio:.2f}x) sits far closer to the sqrt(n) "
      "prediction than the 1/n one")

check("the error is monotonically smaller at every larger n", all(
    mean_errors[i + 1] < mean_errors[i] for i in range(len(mean_errors) - 1)
))
check("the error at the largest n is well below the error at the smallest n", last < first / 5.0)
check(
    "the observed shrink lands within a factor of 3 of the sqrt(n) prediction",
    0.33 * sqrt_prediction < error_ratio < 3.0 * sqrt_prediction,
)
check(
    "the observed shrink is nowhere near the 1/n prediction",
    error_ratio < linear_prediction / 10.0,
)

print()
if all(ok for _, ok in checks_held):
    print(f"08_monte_carlo_error_scaling.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
