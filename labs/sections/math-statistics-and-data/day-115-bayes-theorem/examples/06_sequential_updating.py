"""Exercise 6 -- two positive tests, updated one at a time, in both orders.

Test A: 99% sensitive, 99% specific -- the opening scenario's test.
Test B: 95% sensitive, 98% specific -- a genuinely different, less accurate
test. Both come back positive. The order they are applied in does not
matter, and this script proves it by actually computing both orders and
comparing the results exactly, rather than asserting it from the algebra
alone.
"""

from fractions import Fraction

import bayes as B
import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


test_a = (D.TEST_A_SENSITIVITY, D.TEST_A_SPECIFICITY)
test_b = (D.TEST_B_SENSITIVITY, D.TEST_B_SPECIFICITY)

print("Two different tests, both positive")
print("-" * 60)
print(f"  test A: sensitivity {test_a[0]}, specificity {test_a[1]}")
print(f"  test B: sensitivity {test_b[0]}, specificity {test_b[1]}")
print(f"  prior:  P(condition) = {D.PREVALENCE}")

print()
print("Update with A first, then B")
print("-" * 60)
odds_after_a = B.update_odds(B.probability_to_odds(D.PREVALENCE), B.likelihood_ratio(*test_a))
posterior_after_a = B.odds_to_probability(odds_after_a)
print(f"  after A: posterior = {posterior_after_a}  ({float(posterior_after_a):.6f})")
odds_after_ab = B.update_odds(odds_after_a, B.likelihood_ratio(*test_b))
posterior_a_then_b = B.odds_to_probability(odds_after_ab)
print(f"  after A then B: posterior = {posterior_a_then_b}  ({float(posterior_a_then_b):.6f})")

print()
print("Update with B first, then A")
print("-" * 60)
odds_after_b = B.update_odds(B.probability_to_odds(D.PREVALENCE), B.likelihood_ratio(*test_b))
posterior_after_b = B.odds_to_probability(odds_after_b)
print(f"  after B: posterior = {posterior_after_b}  ({float(posterior_after_b):.6f})")
odds_after_ba = B.update_odds(odds_after_b, B.likelihood_ratio(*test_a))
posterior_b_then_a = B.odds_to_probability(odds_after_ba)
print(f"  after B then A: posterior = {posterior_b_then_a}  ({float(posterior_b_then_a):.6f})")

print()
print("Via sequential_posterior(), both orders in one call each")
print("-" * 60)
via_ab = B.sequential_posterior(D.PREVALENCE, [test_a, test_b])
via_ba = B.sequential_posterior(D.PREVALENCE, [test_b, test_a])
print(f"  [A, B] -> {via_ab}   [B, A] -> {via_ba}")

check("A-then-B matches B-then-A exactly", posterior_a_then_b == posterior_b_then_a)
check("both hand-worked orders match sequential_posterior()'s [A, B] result", posterior_a_then_b == via_ab)
check("both hand-worked orders match sequential_posterior()'s [B, A] result", posterior_b_then_a == via_ba)
check("the two-test posterior is exactly 1045/1267", via_ab == Fraction(1045, 1267))
check("two positive tests move the posterior well past one-half", via_ab > Fraction(1, 2))
check(
    "a single test's posterior (~9%) is far below the two-test posterior (~82%)",
    posterior_after_a < via_ab,
)

print()
print("Why the order never matters")
print("-" * 60)
print("  Each update multiplies the running odds by one more likelihood")
print("  ratio. Multiplication of real (or Fraction) numbers is")
print("  commutative -- a x b always equals b x a -- so a chain of")
print("  updates is the same product regardless of the order the factors")
print("  arrive in. This is not a special property of Bayes' theorem; it")
print("  is a special property of multiplication that Bayes' theorem")
print("  happens to be built from.")

print()
if all(ok for _, ok in checks_held):
    print(f"06_sequential_updating.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
