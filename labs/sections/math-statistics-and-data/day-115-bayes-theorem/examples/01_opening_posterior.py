"""Exercise 1 -- the opening failure, derived exactly.

A test is 99% sensitive and 99% specific. The condition affects 1 person in
1,000. You test positive. Almost everyone -- including, in published
studies, most physicians asked this exact question -- answers "about 99%".
The true answer is close to 9%. This script derives it exactly with
Bayes' theorem, as a Fraction, and asserts both the true value and the
misconception it corrects.
"""

from fractions import Fraction

import bayes as B
import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("The scenario")
print("-" * 60)
print(f"  prevalence   P(condition)          = {D.PREVALENCE}")
print(f"  sensitivity  P(positive|condition) = {D.SENSITIVITY}")
print(f"  specificity  P(negative|no cond.)  = {D.SPECIFICITY}")

print()
print("Bayes' theorem, worked term by term")
print("-" * 60)

p_condition_and_positive = D.PREVALENCE * D.SENSITIVITY
p_no_condition_and_positive = (1 - D.PREVALENCE) * (1 - D.SPECIFICITY)
evidence = p_condition_and_positive + p_no_condition_and_positive
result = p_condition_and_positive / evidence

print(f"  P(condition and positive)    = {D.PREVALENCE} x {D.SENSITIVITY} = {p_condition_and_positive}")
print(f"  P(no condition and positive) = {1 - D.PREVALENCE} x {1 - D.SPECIFICITY} = {p_no_condition_and_positive}")
print(f"  P(positive)  [the evidence]  = {p_condition_and_positive} + {p_no_condition_and_positive} = {evidence}")
print(f"  P(condition | positive)      = {p_condition_and_positive} / {evidence} = {result}")
print(f"                                = {float(result):.6f}  ~ {round(float(result), 4)}")

via_function = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
check("posterior() agrees with the term-by-term derivation", via_function == result)
check("the exact posterior is 99/1098", result == Fraction(99, 1098))
check("which reduces to 11/122", result == Fraction(11, 122))
check("and rounds to 0.0902", round(float(result), 4) == 0.0902)
check("the posterior is NOT 0.99 -- the answer almost everyone gives", result != Fraction(99, 100))
check("in fact it is roughly 11x smaller than the naive 0.99 guess", Fraction(99, 100) / result > 10)

print()
print("Ninety-one out of every hundred positives are false alarms")
print("-" * 60)
false_alarm_share = 1 - result
print(f"  P(no condition | positive) = 1 - {result} = {false_alarm_share} ~ {round(float(false_alarm_share), 4)}")
check("over 90% of positives are false alarms", float(false_alarm_share) > 0.90)

print()
if all(ok for _, ok in checks_held):
    print(f"01_opening_posterior.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
