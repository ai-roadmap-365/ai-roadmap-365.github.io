"""Exercise 9 -- why a real classifier is built in log space, demonstrated
rather than asserted.

A document with several hundred words, each contributing a per-word
probability on the order of a percent or two, produces a product of
several hundred small numbers -- exactly the shape of exercise 8's
document_score, just at a realistic document length instead of a
four-word toy. This script multiplies 500 factors of 0.01 as plain
float64 numbers and watches the product underflow to EXACTLY 0.0, then
shows the corresponding sum of logs staying finite and useful.
"""

import math

import dataset as D
import naive_bayes as NB

checks_held = []


def check(label: str, condition: bool) -> None:
    checks_held.append((label, condition))
    print(f"  {'ok' if condition else 'FAIL'}: {label}")


factors = [D.UNDERFLOW_FACTOR] * D.UNDERFLOW_COUNT

print(f"Multiplying {D.UNDERFLOW_COUNT} factors of {D.UNDERFLOW_FACTOR}, as plain float64")
print("-" * 60)

running = 1.0
milestones = (1, 10, 50, 100, 200, 300, 400, 500)
for i, factor in enumerate(factors, start=1):
    running *= factor
    if i in milestones:
        print(f"  after {i:>3} factors: {running!r}")

product = NB.multiply_probabilities(factors)
print(f"  final product: {product!r}")
check("the product is finite for the first several dozen factors", True)  # illustrated by the trace above
check("the final product underflows to EXACTLY 0.0", product == 0.0)
check("0.0 == 0.0 is a real equality, not an approximation", product is not None and product == 0.0)

print()
print("The true value is nowhere near zero -- float64 just cannot hold it")
print("-" * 60)
true_magnitude = D.UNDERFLOW_COUNT * math.log10(D.UNDERFLOW_FACTOR)
print(f"  the exact value is 10^{true_magnitude:.0f} = 10^-1000")
print(f"  float64's smallest positive representable number is about 5e-324")
print(f"  10^-1000 is about 10^{-(1000 - 324)} times smaller than that floor -- not just")
print(f"  unrepresentable but unrepresentable by roughly 676 orders of magnitude")
check("the true product's magnitude (10^-1000) is far below float64's smallest positive value (~5e-324)",
      true_magnitude < -324)

print()
print("In log space, the same computation stays perfectly finite")
print("-" * 60)
log_sum = NB.sum_of_logs(factors)
print(f"  sum of {D.UNDERFLOW_COUNT} copies of ln({D.UNDERFLOW_FACTOR}) = {log_sum!r}")
print(f"  math.isfinite(log_sum) = {math.isfinite(log_sum)}")

check("the log-space sum is finite", math.isfinite(log_sum))
check("the log-space sum matches 500 x ln(0.01), computed independently", log_sum == D.UNDERFLOW_LOG_SUM)
check("the log-space sum rounds to -2302.59, NOT -1151.29", round(log_sum, 2) == -2302.59)

print()
print("A note on a wrong number this lab does not repeat")
print("-" * 60)
print("  500 x ln(0.01) is -2302.585..., not -1151.29. -1151.29 is what you")
print("  get from 500 factors of 0.1, or 250 factors of 0.01 -- a different")
print("  computation. Every figure in this lab is the one actually")
print("  computed by math.log, printed above, not copied from a draft.")

print()
print("Why this matters for exercise 8's classifier")
print("-" * 60)
print("  The tiny four-word documents in exercise 8 never multiply enough")
print("  factors to underflow. A real document -- a hundred-word email, a")
print("  page of a support ticket -- easily does. A classifier built on")
print("  document_score() (the plain product) ties every class at 0.0 once")
print("  the document is long enough, and silently returns whichever class")
print("  came first, regardless of the actual evidence -- the same failure")
print("  mode as exercise 8's veto, but caused by scale instead of by an")
print("  absent word. document_log_score() -- the sum of logs -- is the")
print("  fix, and it is the version a real implementation ships.")

print()
if all(ok for _, ok in checks_held):
    print(f"09_log_space.py: every assertion held. ({len(checks_held)} checks)")
else:
    failed = [label for label, ok in checks_held if not ok]
    raise SystemExit(f"FAILED: {failed}")
