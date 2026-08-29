"""Exercise 7 -- the law of total probability, two urns.

Urn 1 has 3 red and 7 blue balls. Urn 2 has 6 red and 4 blue. A fair coin
picks the urn, then a ball is drawn. What is P(red), overall? Weight each
urn's conditional probability of red by the probability of picking that urn,
and sum. Then check the answer a completely different way: enumerate the
combined 20-outcome experiment directly and count.

This rule is the one Day 115's Bayes' theorem runs backwards.
"""

from fractions import Fraction

import dataset as D
import probability as P

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("The setup")
print("-" * 60)
print(f"  urn 1: {D.URN_1_RED} red, {D.URN_1_BLUE} blue")
print(f"  urn 2: {D.URN_2_RED} red, {D.URN_2_BLUE} blue")
print(f"  P(urn 1) = P(urn 2) = 1/2, chosen by a fair coin")

print()
print("Method 1: the law of total probability")
print("-" * 60)
total = P.total_probability(D.URN_PRIOR, D.URN_CONDITIONAL_RED)
for i, (prior, cond) in enumerate(zip(D.URN_PRIOR, D.URN_CONDITIONAL_RED), start=1):
    print(f"  P(urn {i}) x P(red | urn {i}) = {prior} x {cond} = {prior * cond}")
print(f"  P(red) = sum of those = {total} = {float(total)}")

print()
print("Method 2: enumerate the combined 20-outcome experiment directly")
print("-" * 60)
urn1 = ["red"] * D.URN_1_RED + ["blue"] * D.URN_1_BLUE
urn2 = ["red"] * D.URN_2_RED + ["blue"] * D.URN_2_BLUE
combined = [("urn1", ball) for ball in urn1] + [("urn2", ball) for ball in urn2]
print(f"  combined space: {len(combined)} equally likely (urn, ball) pairs")
reds = [outcome for outcome in combined if outcome[1] == "red"]
enumerated = Fraction(len(reds), len(combined))
print(f"  {len(reds)} of them are red: P(red) = {len(reds)}/{len(combined)} = {enumerated}")

check("the weighted total is exactly 9/20", total == Fraction(9, 20))
check("the enumeration agrees exactly with the weighted total", enumerated == total)
check("both equal 0.45", float(total) == 0.45 and float(enumerated) == 0.45)

print()
print("A structural note for Day 115")
print("-" * 60)
print("  P(red) was built by summing P(urn) x P(red | urn) over every urn.")
print("  Bayes' theorem asks the reverse question -- given that the ball WAS")
print("  red, how likely is it that it came from urn 2? -- and its denominator")
print("  is exactly this rule, computed for the event that was observed.")

print()
if all(ok for _, ok in checks_held):
    print(f"07_law_of_total_probability.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
