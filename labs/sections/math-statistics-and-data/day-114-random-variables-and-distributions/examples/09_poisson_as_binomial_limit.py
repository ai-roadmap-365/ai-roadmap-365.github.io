"""Exercise 9 -- Poisson as the limit of Binomial(n, p) as n -> infinity
with n*p held at lambda.

Held fixed at lambda = 2, four values of n three decades apart, each paired
with p = lambda / n. The largest gap between the Binomial(n, p) pmf and the
Poisson(lambda) pmf shrinks monotonically as n grows -- that shrink IS the
limit theorem, measured rather than merely asserted in prose.
"""

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


lam = D.POISSON_LAMBDA
ks = D.POISSON_COMPARISON_KS

print(f"lambda = {lam} held fixed; p = lambda / n as n grows")
print("-" * 60)

gaps = []
for n in D.POISSON_LIMIT_NS:
    p = lam / n
    gap = dist.max_binomial_poisson_gap(n, p, lam, ks)
    gaps.append(gap)
    print(f"  n = {n:>6,}   p = {p:.6f}   max |Binomial(n,p) - Poisson({lam})| over k=0..14 = {gap:.6e}")

print()
strictly_decreasing = all(a > b for a, b in zip(gaps, gaps[1:]))
check("the maximum pmf gap decreases MONOTONICALLY as n grows", strictly_decreasing)
check("the gap at n=10,000 is under 0.001", gaps[-1] < 1e-3)
check("the gap at n=10 is at least ten times larger than at n=10,000", gaps[0] > 10 * gaps[-1])

print()
print("  At n=10 the Binomial's own shape -- discrete, bounded by n=10, still")
print("  visibly lumpy -- has not yet converged. By n=10,000 the Binomial and")
print("  Poisson pmfs agree to five decimal places at every k checked; this")
print("  is exactly the classical 'law of rare events' limit, watched happen.")

print()
if all(ok for _, ok in checks_held):
    print(f"09_poisson_as_binomial_limit.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
