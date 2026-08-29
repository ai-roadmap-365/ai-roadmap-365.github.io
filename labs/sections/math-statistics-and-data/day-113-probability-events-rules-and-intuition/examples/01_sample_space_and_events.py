"""Exercise 1 -- the sample space, events as sets, and probability as counting.

Two fair dice. Enumerate every outcome, define an event as the subset of
outcomes where something is true, and read a probability off the ratio of
two counts -- exactly, with a Fraction, never a float that might be
0.16666666666666663 instead of 1/6.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("The sample space of two dice")
print("-" * 60)

space = P.sample_space_two_dice()
print(f"  built with itertools.product: {len(space)} outcomes")
print(f"  first five: {space[:5]}")
check("the space has 36 outcomes", len(space) == 36)
check("it matches the outcomes dataset.py enumerates", set(space) == set(D.TWO_DICE_SPACE))

print()
print("An event is just a subset of the space")
print("-" * 60)

sum_seven = P.event(space, D.is_sum(7))
print(f"  'sum == 7': {sorted(sum_seven)}")
check("6 outcomes sum to 7", len(sum_seven) == 6)

p_sum_seven = P.probability(sum_seven, space)
print(f"  P(sum == 7) = {p_sum_seven} = {float(p_sum_seven):.6f}")
check("P(sum == 7) is exactly Fraction(1, 6)", p_sum_seven == Fraction(1, 6))
check("probability() returns a Fraction, not a float", isinstance(p_sum_seven, Fraction))

double = P.event(space, D.is_double)
p_double = P.probability(double, space)
print(f"  P(both dice match) = {p_double} = {float(p_double):.6f}")
check("P(double) is exactly Fraction(1, 6)", p_double == Fraction(1, 6))

p_whole = P.probability(space, space)
p_empty = P.probability(frozenset(), space)
print(f"  P(whole space) = {p_whole},  P(empty set) = {p_empty}")
check("the three axioms hold here: P(space) = 1", p_whole == 1)
check("and P(empty) = 0", p_empty == 0)
check("and every probability is non-negative", p_sum_seven >= 0 and p_double >= 0)

print()
if all(ok for _, ok in checks_held):
    print(f"01_sample_space_and_events.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
