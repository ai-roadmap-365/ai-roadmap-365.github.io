"""Exercise 3 -- confirm the exact posterior by simulating a large
population and literally counting the four outcome cells.

Neither the exact formula nor the natural-frequencies table above touched
numpy.random. This script is the third, independent check: draw a
population, test it, and count -- and the empirical posterior should land
within a few standard errors of the exact 99/1098.
"""

import numpy as np

import dataset as D
import simulate as S

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print(f"Simulating {D.SIMULATION_POPULATION:,} people, seed {D.SIMULATION_SEED}")
print("-" * 60)

rng = np.random.default_rng(D.SIMULATION_SEED)
counts = S.simulate_population(
    rng,
    D.SIMULATION_POPULATION,
    float(D.PREVALENCE),
    float(D.SENSITIVITY),
    float(D.SPECIFICITY),
)

print(f"  true positives:  {counts.true_positive:,}")
print(f"  false positives: {counts.false_positive:,}")
print(f"  true negatives:  {counts.true_negative:,}")
print(f"  false negatives: {counts.false_negative:,}")
print(f"  total positives: {counts.positives:,}")

exact = float(D.OPENING_POSTERIOR_EXACT)
empirical = counts.empirical_posterior
se = D.standard_error(exact, counts.positives)
tolerance = 3.0 * se

print()
print(f"  exact posterior      = {exact:.6f}")
print(f"  simulated posterior  = {empirical:.6f}")
print(f"  gap                  = {abs(empirical - exact):.6f}")
print(f"  standard error at n={counts.positives:,} positives = {se:.6f}")
print(f"  tolerance (3 SE)     = {tolerance:.6f}")

check("some people actually have the condition in the sample", counts.true_positive + counts.false_negative > 0)
check("the simulated posterior lands within 3 standard errors of the exact value",
      abs(empirical - exact) < tolerance)
check("the simulated posterior is nowhere near the naive 0.99 guess", empirical < 0.5)

print()
if all(ok for _, ok in checks_held):
    print(f"03_simulation.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
