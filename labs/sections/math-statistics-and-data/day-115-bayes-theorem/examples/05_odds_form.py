"""Exercise 5 -- the odds form: posterior odds = prior odds x likelihood
ratio.

This is the cleanest way to think about updating a belief, because the
likelihood ratio isolates exactly how much a piece of evidence is worth,
completely independent of what you believed before you saw it.
"""

from fractions import Fraction

import bayes as B
import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("Prior odds")
print("-" * 60)
prior_odds = B.probability_to_odds(D.PREVALENCE)
print(f"  P(condition) = {D.PREVALENCE}")
print(f"  prior odds   = {D.PREVALENCE} / (1 - {D.PREVALENCE}) = {prior_odds}  (about 1 in 999)")

print()
print("Likelihood ratio")
print("-" * 60)
ratio = B.likelihood_ratio(D.SENSITIVITY, D.SPECIFICITY)
print(f"  LR+ = P(positive|condition) / P(positive|no condition)")
print(f"      = {D.SENSITIVITY} / (1 - {D.SPECIFICITY}) = {ratio}")
print(f"  a positive result is {ratio}x more likely under the condition than without it")

print()
print("Posterior odds, and back to a probability")
print("-" * 60)
posterior_odds = B.update_odds(prior_odds, ratio)
posterior_probability = B.odds_to_probability(posterior_odds)
print(f"  posterior odds = {prior_odds} x {ratio} = {posterior_odds}")
print(f"  posterior probability = {posterior_odds} / (1 + {posterior_odds}) = {posterior_probability}"
      f"  ({float(posterior_probability):.6f})")

direct = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
check("posterior odds equal prior odds times the likelihood ratio, exactly", posterior_odds == prior_odds * ratio)
check("converting back to a probability matches exercise 1's direct answer exactly", posterior_probability == direct)
check("the likelihood ratio here is exactly 99", ratio == 99)
check("prior odds are exactly 1/999", prior_odds == Fraction(1, 999))

print()
print("Why the odds form earns its place")
print("-" * 60)
print("  The likelihood ratio (99, here) says exactly how much a positive")
print("  result is worth as evidence, and that number does not change if")
print("  the prior changes. Multiply it onto ANY prior odds and you get")
print("  that prior's correctly updated posterior odds -- which is exactly")
print("  what exercise 6 does twice in a row.")

print()
if all(ok for _, ok in checks_held):
    print(f"05_odds_form.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
