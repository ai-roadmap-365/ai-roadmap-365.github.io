"""Exercise 5 -- mutually exclusive events with non-zero probability are
NECESSARILY dependent.

This is the sharpest possible case of dependence, and it is the one most
people get backwards: "mutually exclusive" sounds like it should mean
"unrelated", and it means the opposite. If A and B cannot both happen, then
knowing B happened tells you everything about A -- specifically, that A did
not happen, even though A was possible before you knew anything.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


space = P.sample_space_two_dice()
pred_a, pred_b = D.MUTUALLY_EXCLUSIVE_PAIR
a = P.event(space, pred_a)
b = P.event(space, pred_b)

print("A = 'sum is 2' (only (1,1)), B = 'sum is 12' (only (6,6))")
print("-" * 60)
print(f"  A = {sorted(a)}")
print(f"  B = {sorted(b)}")
print(f"  A and B = {sorted(a & b)}   <- empty. The dice cannot sum to both 2 and 12.")

p_a = P.probability(a, space)
p_b = P.probability(b, space)
p_a_and_b = P.probability(a & b, space)
print(f"  P(A) = {p_a},  P(B) = {p_b},  P(A and B) = {p_a_and_b}")

p_a_given_b = P.conditional(p_a_and_b, p_b)
print()
print(f"  P(A | B) = P(A and B) / P(B) = {p_a_and_b} / {p_b} = {p_a_given_b}")
print(f"  but P(A) on its own is {p_a}")
print(f"  P(A | B) != P(A)  ->  knowing B happened changed what you believe about A")
print(f"  ->  A and B are DEPENDENT, despite being unable to co-occur")

check("A and B are mutually exclusive: their intersection is empty", len(a & b) == 0)
check("P(A) is non-zero", p_a != 0)
check("P(B) is non-zero", p_b != 0)
check("P(A | B) is exactly zero", p_a_given_b == 0)
check("P(A | B) does not equal P(A) -- the events are dependent", p_a_given_b != p_a)

print()
print("Contrast this with the independent pair from exercise 4")
print("-" * 60)
indep_a, indep_b = D.INDEPENDENT_PAIR
ia = P.event(space, indep_a)
ib = P.event(space, indep_b)
p_ia = P.probability(ia, space)
p_ib = P.probability(ib, space)
p_ia_given_ib = P.conditional(P.probability(ia & ib, space), p_ib)
print(f"  independent pair: P(sum=7 | first=3) = {p_ia_given_ib} = P(sum=7) = {p_ia}")
check("for a genuinely independent pair, conditioning changes nothing", p_ia_given_ib == p_ia)
check(
    "mutual exclusivity and independence pull P(A | B) in opposite "
    "directions here: one collapses it to 0, the other leaves it unchanged",
    p_a_given_b == 0 and p_ia_given_ib == p_ia and p_a_given_b != p_ia_given_ib,
)

print()
if all(ok for _, ok in checks_held):
    print(f"05_mutual_exclusivity_implies_dependence.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
