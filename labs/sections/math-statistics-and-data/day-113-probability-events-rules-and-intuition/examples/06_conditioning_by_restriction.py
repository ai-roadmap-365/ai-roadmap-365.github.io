"""Exercise 6 -- conditioning as restriction: throwing away rows.

P(sum = 8 | first die is even), computed two ways that have to agree: the
formula P(A and B) / P(B), and literally filtering the sample space down to
the rows where B is true and asking what fraction of THOSE rows satisfy A.
That second method is what conditioning IS -- not a formula to apply, but a
smaller table to look at.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


space = P.sample_space_two_dice()
a = P.event(space, D.CONDITIONING_EVENT_A)  # sum == 8
b = P.event(space, D.CONDITIONING_EVENT_B)  # first die even

print("Method 1: the formula, P(A | B) = P(A and B) / P(B)")
print("-" * 60)
p_a_and_b = P.probability(a & b, space)
p_b = P.probability(b, space)
by_formula = P.conditional(p_a_and_b, p_b)
print(f"  A and B = {sorted(a & b)}   P(A and B) = {p_a_and_b}")
print(f"  B = {sorted(b)}   P(B) = {p_b}")
print(f"  P(A | B) = {p_a_and_b} / {p_b} = {by_formula}")

print()
print("Method 2: restriction -- throw away every row where B is false")
print("-" * 60)
restricted_space = b  # the 18 outcomes where the first die is even
restricted_event = P.event(restricted_space, D.CONDITIONING_EVENT_A)
by_filtering = P.probability(restricted_event, restricted_space)
print(f"  restricted sample space (first die even): {len(restricted_space)} outcomes")
print(f"  of those, sum == 8: {sorted(restricted_event)}")
print(f"  P(A | B) by filtering = {len(restricted_event)}/{len(restricted_space)} = {by_filtering}")

check("both methods give exactly 1/6", by_formula == Fraction(1, 6) and by_filtering == Fraction(1, 6))
check("the two methods agree exactly, not approximately", by_formula == by_filtering)

print()
print("Compare against the UNCONDITIONED probability")
print("-" * 60)
p_a_unconditioned = P.probability(a, space)
print(f"  P(sum == 8), no conditioning: {p_a_unconditioned}")
print(f"  P(sum == 8 | first die even): {by_formula}")
check(
    "conditioning on 'first die even' changed the probability of sum=8",
    p_a_unconditioned != by_formula,
)

print()
if all(ok for _, ok in checks_held):
    print(f"06_conditioning_by_restriction.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
