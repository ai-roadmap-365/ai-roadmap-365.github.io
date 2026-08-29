"""Exercise 1 -- the two-dice sum as a random variable, and its pmf.

Almost everyone's first instinct is that the sum of two dice is roughly
even-handed across 2 through 12. It is not remotely. This script builds the
pmf by enumeration and shows exactly how far from uniform it is: 7 is six
times as likely as 2 or 12.
"""

from fractions import Fraction

import dataset as D
import distributions as dist

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("The random variable Y = X1 + X2, the sum of two fair dice")
print("-" * 60)

pmf = dist.dice_sum_pmf()
for value, prob in pmf.items():
    bar = "#" * int(float(prob) * 200)
    print(f"  P(Y={value:>2}) = {str(prob):>6}  {float(prob):.4f}  {bar}")

check("the pmf has one entry per sum from 2 to 12", set(pmf) == set(range(2, 13)))
check("every probability sums to exactly 1", sum(pmf.values()) == 1)
check("P(Y=7) is exactly Fraction(1, 6)", pmf[7] == Fraction(1, 6))

most_likely = max(pmf.values())
least_likely = min(pmf.values())
ratio = most_likely / least_likely
print()
print(f"  most likely sum (7):  {pmf[7]}   least likely sums (2 and 12): {pmf[2]}")
print(f"  ratio of most likely to least likely: {ratio} = {int(ratio)}")
check("7 is exactly 6 times as likely as 2 or 12", ratio == 6)
check("the distribution is NOT uniform", len(set(pmf.values())) > 1)

print()
if all(ok for _, ok in checks_held):
    print(f"01_pmf_of_a_sum.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
