"""Exercise 3 -- expectation and variance, by definition versus measured.

Expectation is a weighted average, and it need not be an attainable value:
E[Y] = 7 for two dice, which no single roll of two dice can ever equal on
its own axis of "a possible outcome that is also the average" -- 7 IS a
possible sum here, but the more instructive case is a die alone, where
E[X] = 3.5 and no face of a die ever shows 3.5. Both are computed exactly
from the pmf, then measured from a large seeded sample and shown to agree
within three standard errors.
"""

import statistics

import numpy as np

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


pmf = dist.dice_sum_pmf()
exact_mean = dist.expectation_pmf(pmf)
exact_var = dist.variance_pmf(pmf)

print("By definition, from the pmf")
print("-" * 60)
print(f"  E[Y]   = sum(k * P(Y=k))  = {exact_mean}  = {float(exact_mean)}")
print(f"  Var[Y] = E[(Y-E[Y])^2]    = {exact_var}  = {float(exact_var):.6f}")

single_die_mean = dist.expectation_pmf({k: D.ONE_DIE_WEIGHT for k in D.DIE_FACES})
print(f"  (a single die's own E[X] = {single_die_mean}, and no face ever shows it --")
print(f"   expectation need not be an attainable value)")
check("a single die's expectation is 3.5, no face of which exists", single_die_mean == 3.5)

print()
print(f"Measured from {D.EV_SIMULATION_TRIALS:,} simulated rolls, seed {D.SEED}")
print("-" * 60)

rng = np.random.default_rng(D.SEED)
first = rng.integers(1, 7, size=D.EV_SIMULATION_TRIALS, endpoint=False)
second = rng.integers(1, 7, size=D.EV_SIMULATION_TRIALS, endpoint=False)
sample = (first + second).astype(float)

# The `statistics` module -- the standard library's own numeric summary
# tool -- computed over the same sample, alongside NumPy's array methods.
sample_mean_stats = statistics.fmean(sample.tolist())
sample_var_stats = statistics.pvariance(sample.tolist())
sample_mean_np = float(sample.mean())
sample_var_np = float(sample.var())

print(f"  statistics.fmean      = {sample_mean_stats:.6f}")
print(f"  numpy .mean()         = {sample_mean_np:.6f}")
print(f"  statistics.pvariance  = {sample_var_stats:.6f}")
print(f"  numpy .var()          = {sample_var_np:.6f}")
check("statistics.fmean and numpy .mean() agree", abs(sample_mean_stats - sample_mean_np) < 1e-9)
check(
    "statistics.pvariance and numpy .var() agree",
    abs(sample_var_stats - sample_var_np) < 1e-9,
)

mean_tol = 3.0 * D.standard_error_of_mean(float(exact_var), D.EV_SIMULATION_TRIALS)
mean_gap = abs(sample_mean_np - float(exact_mean))
print()
print(f"  E[Y]:   exact {float(exact_mean):.6f}, measured {sample_mean_np:.6f}, "
      f"gap {mean_gap:.6f}, tolerance (3 SE) {mean_tol:.6f}")
check("the measured mean lands within 3 standard errors of the exact mean", mean_gap < mean_tol)

var_gap = abs(sample_var_np - float(exact_var))
print(f"  Var[Y]: exact {float(exact_var):.6f}, measured {sample_var_np:.6f}, gap {var_gap:.6f}")
check("the measured variance is within 5% of the exact variance", var_gap < 0.05 * float(exact_var))

print()
if all(ok for _, ok in checks_held):
    print(f"03_expectation_and_variance.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
