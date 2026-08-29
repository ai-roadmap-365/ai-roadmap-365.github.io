"""Exercise 4 -- independence versus dependence, the most common conflation
in the subject.

Two events are independent when P(A and B) == P(A) x P(B) -- knowing one
happened tells you nothing about the other. This script finds one genuinely
independent pair and one genuinely dependent pair inside the same sample
space, so the difference is not abstract.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


space = P.sample_space_two_dice()


def summarize(name_a, pred_a, name_b, pred_b):
    a = P.event(space, pred_a)
    b = P.event(space, pred_b)
    p_a = P.probability(a, space)
    p_b = P.probability(b, space)
    p_ab = P.probability(a & b, space)
    independent = P.is_independent(p_a, p_b, p_ab)
    print(f"  {name_a}: P = {p_a}   {name_b}: P = {p_b}")
    print(f"  P(both) = {p_ab}   P(A) x P(B) = {p_a * p_b}   independent? {independent}")
    return p_a, p_b, p_ab, independent


print("A genuinely independent pair")
print("-" * 60)
print("  A = 'sum is 7', B = 'first die is 3'")
print("  Reasoning: whatever the first die shows, exactly one value of the")
print("  second die makes the sum 7 -- so P(sum=7 | first die=v) = 1/6 for")
print("  EVERY v. Conditioning on the first die changes nothing.")
p_a1, p_b1, p_ab1, indep1 = summarize("sum=7", D.is_sum(7), "first=3", D.is_first_die(3))
check("P(sum=7) is 1/6", p_a1 == Fraction(1, 6))
check("P(first=3) is 1/6", p_b1 == Fraction(1, 6))
check("P(A and B) equals P(A) x P(B) exactly", p_ab1 == p_a1 * p_b1)
check("is_independent() reports True", indep1 is True)

print()
print("A genuinely dependent pair")
print("-" * 60)
print("  A = 'sum is 2', B = 'first die is 1'")
print("  Reasoning: sum=2 is ONLY possible when both dice show 1 -- so")
print("  P(sum=2 | first die=1) = 1/6, but P(sum=2 | first die != 1) = 0.")
print("  Conditioning on the first die changes everything.")
p_a2, p_b2, p_ab2, indep2 = summarize("sum=2", D.is_sum(2), "first=1", D.is_first_die(1))
check("P(A and B) does NOT equal P(A) x P(B)", p_ab2 != p_a2 * p_b2)
check("is_independent() reports False", indep2 is False)

print()
print("The conflation this exercise exists to prevent")
print("-" * 60)
print("  | Property             | Independent          | Mutually exclusive        |")
print("  | --------------------- | --------------------- | -------------------------- |")
print("  | P(A and B)             | P(A) x P(B), generally > 0 | exactly 0                    |")
print("  | knowing A happened      | tells you nothing about B | tells you B did NOT happen |")
print("  | can both have P > 0?    | yes                    | yes, but never together    |")
print("  independent events with non-zero probability CAN both happen at once.")
print("  mutually exclusive events with non-zero probability NEVER can --")
print("  which, as exercise 5 shows next, makes them dependent.")

print()
if all(ok for _, ok in checks_held):
    print(f"04_independence_vs_dependence.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
