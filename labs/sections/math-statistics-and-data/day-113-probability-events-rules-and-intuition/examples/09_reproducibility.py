"""Exercise 9 -- reproducibility: same seed, byte-identical results.

`numpy.random.default_rng(seed)` builds an independent, stateful Generator.
Two Generators built from the same seed produce identical sequences, so a
whole simulation reproduces exactly. Two Generators built from different
seeds diverge -- but both still land close to the true probability, because
they are both honest estimates of the same thing.
"""

import numpy as np

import dataset as D
import simulate as S

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


target = float(D.MONTE_CARLO_TARGET)
n = D.REPRODUCIBILITY_TRIALS

print(f"Two independent Generators, same seed ({D.REPRODUCIBILITY_SEED_A})")
print("-" * 60)
rng_a1 = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
rng_a2 = np.random.default_rng(D.REPRODUCIBILITY_SEED_A)
result_a1 = S.simulate_sum_seven(rng_a1, n)
result_a2 = S.simulate_sum_seven(rng_a2, n)
print(f"  run 1: {result_a1}")
print(f"  run 2: {result_a2}")
check("the same seed gives byte-identical results", result_a1 == result_a2)

print()
print(f"A different seed ({D.REPRODUCIBILITY_SEED_B})")
print("-" * 60)
rng_b = np.random.default_rng(D.REPRODUCIBILITY_SEED_B)
result_b = S.simulate_sum_seven(rng_b, n)
print(f"  seed {D.REPRODUCIBILITY_SEED_A}: {result_a1}")
print(f"  seed {D.REPRODUCIBILITY_SEED_B}: {result_b}")
check("a different seed gives a different result", result_a1 != result_b)

tol = 4.0 * D.standard_error(target, n)
print()
print(f"Both still estimate the true probability, {target:.6f}, within tolerance")
print(f"(4 standard errors at n = {n:,}: {tol:.6f})")
print(f"  seed {D.REPRODUCIBILITY_SEED_A}: gap {abs(result_a1 - target):.6f}")
print(f"  seed {D.REPRODUCIBILITY_SEED_B}: gap {abs(result_b - target):.6f}")
check("seed A's estimate is within tolerance of the true value", abs(result_a1 - target) < tol)
check("seed B's estimate is within tolerance of the true value", abs(result_b - target) < tol)

print()
print("Why this matters, and why numpy.random.seed is the wrong tool")
print("-" * 60)
print("  numpy.random.seed(n) mutates ONE GLOBAL state shared by every piece")
print("  of code that calls numpy.random.* -- importing a library that seeds")
print("  it, or calling a function twice, silently changes your results.")
print("  default_rng(seed) hands back an independent object: two Generators")
print("  never interfere with each other, and reproducibility does not")
print("  depend on what else your program happened to do first.")

print()
if all(ok for _, ok in checks_held):
    print(f"09_reproducibility.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
