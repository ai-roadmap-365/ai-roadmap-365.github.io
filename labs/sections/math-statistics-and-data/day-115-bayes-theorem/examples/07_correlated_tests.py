"""Exercise 7 -- the honest caveat: multiplying likelihood ratios twice
assumes the two runs are conditionally independent given the hypothesis,
and that assumption can be badly false.

Same test (99% sensitive, 99% specific), run twice on ONE sample. Half the
time (modelled here as correlation_weight = 1/2), both runs are yoked to a
single shared failure mode -- a contaminated sample, a bad reagent batch --
so they either BOTH come back positive or BOTH come back negative,
regardless of the true condition. This script computes the posterior two
ways: the naive way, which assumes full independence, and the correct way,
which accounts for the correlation -- and the naive answer is not just
different, it is dramatically more confident than it has any right to be.
"""

from fractions import Fraction

import bayes as B
import dataset as D

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


print("Same test, same sample, run twice. Both runs come back positive.")
print("-" * 60)
print(f"  single-run sensitivity {D.CORRELATED_SENSITIVITY}, specificity {D.CORRELATED_SPECIFICITY}")
print(f"  correlation weight (probability the two runs share one failure mode): {D.CORRELATION_WEIGHT}")

print()
print("The NAIVE model: treat the two runs as independent")
print("-" * 60)
naive_tp_pair = B.independent_pair_probability(D.CORRELATED_SENSITIVITY)
naive_fp_pair = B.independent_pair_probability(1 - D.CORRELATED_SPECIFICITY)
print(f"  P(both positive | condition)    = sensitivity^2 = {naive_tp_pair}")
print(f"  P(both positive | no condition) = (1-specificity)^2 = {naive_fp_pair}")
naive_posterior = B.posterior_general(D.PREVALENCE, naive_tp_pair, naive_fp_pair)
print(f"  naive posterior = {naive_posterior}  ({float(naive_posterior):.6f})")

print()
print("The CORRECT model: half the time, one shared draw decides both runs")
print("-" * 60)
correct_tp_pair = B.correlated_pair_probability(D.CORRELATED_SENSITIVITY, D.CORRELATION_WEIGHT)
correct_fp_pair = B.correlated_pair_probability(1 - D.CORRELATED_SPECIFICITY, D.CORRELATION_WEIGHT)
print(f"  P(both positive | condition)    = {D.CORRELATION_WEIGHT} x sens + (1-{D.CORRELATION_WEIGHT}) x sens^2"
      f" = {correct_tp_pair}")
print(f"  P(both positive | no condition) = {D.CORRELATION_WEIGHT} x (1-spec) + (1-{D.CORRELATION_WEIGHT}) x (1-spec)^2"
      f" = {correct_fp_pair}")
correct_posterior = B.posterior_general(D.PREVALENCE, correct_tp_pair, correct_fp_pair)
print(f"  correct posterior = {correct_posterior}  ({float(correct_posterior):.6f})")

print()
print("Both numbers, side by side")
print("-" * 60)
print(f"  naive (assumes independence):  {float(naive_posterior):.4f}  ({round(float(naive_posterior) * 100, 1)}% confident)")
print(f"  correct (accounts for the shared failure mode): {float(correct_posterior):.4f}"
      f"  ({round(float(correct_posterior) * 100, 1)}% confident)")

check("the naive calculation is exactly 363/400", naive_posterior == Fraction(363, 400))
check("the naive posterior is strictly higher than the correct one", naive_posterior > correct_posterior)
check(
    "the naive answer overstates confidence by more than a factor of five",
    naive_posterior / correct_posterior > 5,
)
check("both posteriors still exceed a single test's ~9% posterior", correct_posterior > D.OPENING_POSTERIOR_EXACT)

print()
print("Which one is right? The correct one -- by construction of this scenario")
print("-" * 60)
print("  The naive calculation is not a rounding error; it is answering a")
print("  question that was never asked. It computes the posterior for a")
print("  world where the two positive results are independent evidence.")
print("  In THIS world, half the time they are not two pieces of evidence")
print("  at all -- they are one piece of evidence, reported twice. Treating")
print("  a correlated pair as independent double-counts it, exactly the")
print("  way the addition rule's naive sum double-counted an overlap back")
print("  on Day 113 -- a different rule, the same shape of mistake.")

print()
if all(ok for _, ok in checks_held):
    print(f"07_correlated_tests.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
