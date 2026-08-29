"""Exercise 4 -- the base rate decides the answer. Sweep it and watch.

Everything about sensitivity and specificity stays fixed at 99%/99%
throughout this script. Only the prevalence changes -- and the posterior
climbs from under a tenth of a percent at one case in 100,000, to exactly
0.99 at a prevalence of one-half. 0.99 is the number nearly everyone
wrongly gives for the 1-in-1,000 case; this script shows it is the RIGHT
answer, just for a completely different question.
"""

from fractions import Fraction

import bayes as B
import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("Sensitivity and specificity fixed at 99% / 99%. Prevalence varies.")
print("-" * 60)

results: list[Fraction] = []
for prevalence in D.PREVALENCE_SWEEP:
    posterior = B.posterior(prevalence, D.SENSITIVITY, D.SPECIFICITY)
    results.append(posterior)
    print(f"  prevalence {str(prevalence):>8} -> posterior {str(posterior):>10}"
          f"  ({float(posterior):.6f})")

print()
check(
    "the posterior is strictly increasing as prevalence rises",
    all(results[i] < results[i + 1] for i in range(len(results) - 1)),
)

last_prevalence, last_posterior = D.PREVALENCE_SWEEP[-1], results[-1]
check("the sweep's final prevalence is exactly 1/2", last_prevalence == Fraction(1, 2))
check("at prevalence 1/2 the posterior is EXACTLY 0.99", last_posterior == Fraction(99, 100))

opening_posterior = B.posterior(D.PREVALENCE, D.SENSITIVITY, D.SPECIFICITY)
check(
    "0.99 -- everyone's wrong guess for the 1-in-1,000 case -- is over 10x the true answer there",
    Fraction(99, 100) / opening_posterior > 10,
)
check(
    "...but is the EXACT right answer once the base rate is 1 in 2",
    last_posterior == Fraction(99, 100),
)

print()
print("The number 0.99 was never wrong. It just answered a different question.")
print("-" * 60)
print("  Sensitivity and specificity describe the TEST. The posterior")
print("  describes the PATIENT, and the patient's answer depends on how")
print("  common the condition was before the test ever ran.")

print()
if all(ok for _, ok in checks_held):
    print(f"04_prevalence_sweep.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
