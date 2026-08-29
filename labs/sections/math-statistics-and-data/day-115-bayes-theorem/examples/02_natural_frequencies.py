"""Exercise 2 -- the same arithmetic, made obvious by counting people
instead of multiplying percentages.

Stop using percentages. Count 100,000 people. This script builds the exact
table and shows that the fraction TP / (TP + FP) -- read straight off four
integers -- equals exercise 1's formula answer exactly.
"""

from fractions import Fraction

import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print(f"Out of {D.NATURAL_FREQUENCY_POPULATION:,} people")
print("-" * 60)
print(f"  {D.NATURAL_FREQUENCY_SICK} have the condition, {D.NATURAL_FREQUENCY_WELL:,} do not")
check(
    "sick + well accounts for everyone",
    D.NATURAL_FREQUENCY_SICK + D.NATURAL_FREQUENCY_WELL == D.NATURAL_FREQUENCY_POPULATION,
)

print()
print("Of the sick people:")
print(f"  {D.NATURAL_FREQUENCY_TP} test positive (true positives)")
print(f"  {D.NATURAL_FREQUENCY_FN} tests negative (false negative)")
check(
    "TP + FN accounts for every sick person",
    D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FN == D.NATURAL_FREQUENCY_SICK,
)

print()
print("Of the healthy people:")
print(f"  {D.NATURAL_FREQUENCY_FP} test positive anyway (false positives)")
print(f"  {D.NATURAL_FREQUENCY_TN:,} correctly test negative (true negatives)")
check(
    "FP + TN accounts for every healthy person",
    D.NATURAL_FREQUENCY_FP + D.NATURAL_FREQUENCY_TN == D.NATURAL_FREQUENCY_WELL,
)

print()
print("So, of everyone who tests positive:")
print("-" * 60)
total_positive = D.NATURAL_FREQUENCY_TP + D.NATURAL_FREQUENCY_FP
print(f"  true positives  {D.NATURAL_FREQUENCY_TP}")
print(f"  false positives {D.NATURAL_FREQUENCY_FP}")
print(f"  total positives {total_positive}")
natural_posterior = Fraction(D.NATURAL_FREQUENCY_TP, total_positive)
print(f"  P(condition | positive) = {D.NATURAL_FREQUENCY_TP} / {total_positive} = {natural_posterior}"
      f" ~ {round(float(natural_posterior), 4)}")

check("total positives is exactly 1,098", total_positive == 1098)
check("TP / (TP + FP) equals the exact posterior from exercise 1", natural_posterior == D.OPENING_POSTERIOR_EXACT)
check("nine false alarms for every true positive, roughly", D.NATURAL_FREQUENCY_FP / D.NATURAL_FREQUENCY_TP > 9)

print()
print("The percentages were never wrong -- they were just opaque")
print("-" * 60)
print("  1% of 999,000... no: 1% of the 99,900 healthy people IS 999 people,")
print("  and 999 false positives dwarfs the 99 true positives a 99%-sensitive")
print("  test catches out of only 100 sick people. Counting makes that")
print("  imbalance impossible to miss; percentages hid it in plain sight.")

print()
if all(ok for _, ok in checks_held):
    print(f"02_natural_frequencies.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
