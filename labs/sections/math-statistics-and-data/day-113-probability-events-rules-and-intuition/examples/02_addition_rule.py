"""Exercise 2 -- the addition rule, and exactly how the naive sum lies.

A = "the dice sum to 7" (6 outcomes). B = "the first die shows 6" (6
outcomes). Someone in a hurry adds P(A) + P(B) and gets 1/3. The true answer
is 11/36, and the gap is exactly P(A and B) -- the one outcome, (6, 1), that
belongs to both events and got counted twice.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


space = P.sample_space_two_dice()
a = P.event(space, D.ADDITION_EVENT_A)
b = P.event(space, D.ADDITION_EVENT_B)
a_and_b = a & b

print("A = 'sum is 7', B = 'first die is 6'")
print("-" * 60)
print(f"  A = {sorted(a)}")
print(f"  B = {sorted(b)}")
print(f"  A and B = {sorted(a_and_b)}   <- exactly one outcome, double-counted")

p_a = P.probability(a, space)
p_b = P.probability(b, space)
p_a_and_b = P.probability(a_and_b, space)
print(f"  P(A) = {p_a},  P(B) = {p_b},  P(A and B) = {p_a_and_b}")

naive = P.naive_sum(p_a, p_b)
true_union = P.addition_rule(p_a, p_b, p_a_and_b)
print()
print(f"  naive P(A) + P(B)              = {naive}  = {float(naive):.6f}   WRONG")
print(f"  true  P(A) + P(B) - P(A and B) = {true_union}  = {float(true_union):.6f}   correct")

# Verify the true union directly by counting the union set, independent of
# the formula -- a second, unrelated route to the same number.
union_by_counting = P.probability(a | b, space)
print(f"  counting |A union B| directly  = {union_by_counting}   <- agrees")

check("A has 6 outcomes", len(a) == 6)
check("B has 6 outcomes", len(b) == 6)
check("A and B overlap in exactly one outcome", len(a_and_b) == 1)
check("the naive sum is 1/3", naive == Fraction(1, 3))
check("the true union is 11/36", true_union == Fraction(11, 36))
check("counting the union directly agrees with the formula", union_by_counting == true_union)
check(
    "the naive sum overstates the truth by exactly P(A and B)",
    naive - true_union == p_a_and_b,
)
check("the naive sum is measurably wrong", naive != true_union)

print()
if all(ok for _, ok in checks_held):
    print(f"02_addition_rule.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
