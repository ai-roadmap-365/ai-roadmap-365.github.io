"""Exercise 7 -- an inverse-CDF sampler for an arbitrary discrete pmf,
written from scratch, applied to the dice-sum pmf from exercise 1.

One uniform draw per sample, pushed through the pmf's own cdf, reproduces
the pmf's shape -- and the same seed reproduces the same draws, byte for
byte.
"""

import numpy as np

import dataset as D
import distributions as dist
import sampling as samp

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


pmf = dist.dice_sum_pmf()
pmf_float = {k: float(v) for k, v in pmf.items()}

print(f"Sampling {D.DISCRETE_SAMPLER_TRIALS:,} draws from the dice-sum pmf via inverse-CDF")
print("-" * 60)

rng = np.random.default_rng(D.SEED)
draws = samp.sample_discrete_inverse_cdf(pmf_float, rng, D.DISCRETE_SAMPLER_TRIALS)

values, counts = np.unique(draws, return_counts=True)
empirical = {int(v): c / D.DISCRETE_SAMPLER_TRIALS for v, c in zip(values, counts)}

worst_se = max(
    D.standard_error_of_proportion(p, D.DISCRETE_SAMPLER_TRIALS) for p in pmf_float.values()
)
tolerance = 3.0 * worst_se

for value in sorted(pmf):
    exact = pmf_float[value]
    got = empirical.get(value, 0.0)
    gap = abs(exact - got)
    flag = "ok" if gap < tolerance else "FAIL"
    print(f"  {flag}: P(Y={value:>2}) exact {exact:.4f}  empirical {got:.4f}  gap {gap:.5f}")

max_gap = max(abs(pmf_float[v] - empirical.get(v, 0.0)) for v in pmf_float)
print()
print(f"  worst gap across all 11 values: {max_gap:.5f}, tolerance (3 SE): {tolerance:.5f}")
check("every empirical frequency lands within 3 standard errors", max_gap < tolerance)
check(
    "only values 2 through 12 were ever drawn",
    set(empirical) == set(range(2, 13)),
)

print()
print("Reproducibility: the same seed must give byte-identical draws")
print("-" * 60)
rng_a = np.random.default_rng(D.SEED)
rng_b = np.random.default_rng(D.SEED)
draws_a = samp.sample_discrete_inverse_cdf(pmf_float, rng_a, 5_000)
draws_b = samp.sample_discrete_inverse_cdf(pmf_float, rng_b, 5_000)
identical = np.array_equal(draws_a, draws_b)
print(f"  two Generators built from seed {D.SEED}: identical draws = {identical}")
check("the same seed reproduces identical draws", identical)

rng_c = np.random.default_rng(D.SEED + 1)
draws_c = samp.sample_discrete_inverse_cdf(pmf_float, rng_c, 5_000)
check("a different seed does NOT reproduce the same draws", not np.array_equal(draws_a, draws_c))

print()
if all(ok for _, ok in checks_held):
    print(f"07_inverse_cdf_discrete_sampler.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
