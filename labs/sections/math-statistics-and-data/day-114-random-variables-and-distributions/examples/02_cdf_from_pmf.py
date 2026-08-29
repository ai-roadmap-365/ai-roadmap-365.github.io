"""Exercise 2 -- the cdf, as the pmf's running total.

The cdf is the workhorse of this lesson: monotone non-decreasing, it ends
at exactly 1, and a difference of two of its values gives an interval
probability directly, with no re-summing.
"""

from fractions import Fraction

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


pmf = dist.dice_sum_pmf()
cdf = dist.cdf_from_pmf(pmf)

print("F(k) = P(Y <= k), the running total of the pmf")
print("-" * 60)
for value, prob in cdf.items():
    print(f"  F({value:>2}) = {str(prob):>7}  {float(prob):.4f}")

values = sorted(cdf)
running = [cdf[v] for v in values]
check("the cdf is monotone non-decreasing", all(a <= b for a, b in zip(running, running[1:])))
check("the cdf ends at exactly 1", cdf[max(values)] == 1)

diff = cdf[7] - cdf[6]
print()
print(f"  F(7) - F(6) = {cdf[7]} - {cdf[6]} = {diff}, and P(Y=7) = {pmf[7]}")
check("F(7) - F(6) equals P(Y=7) exactly", diff == pmf[7])

# A second interval, to show the running-total trick generalises: the
# probability that the sum falls in {5, 6, 7, 8, 9} without re-summing five
# pmf entries.
interval = cdf[9] - cdf[4]
direct = sum((pmf[k] for k in range(5, 10)), Fraction(0))
print(f"  P(5 <= Y <= 9) via cdf: F(9) - F(4) = {interval}")
print(f"  P(5 <= Y <= 9) via direct sum of five pmf entries: {direct}")
check("the cdf-difference route matches the direct sum", interval == direct)

print()
if all(ok for _, ok in checks_held):
    print(f"02_cdf_from_pmf.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
