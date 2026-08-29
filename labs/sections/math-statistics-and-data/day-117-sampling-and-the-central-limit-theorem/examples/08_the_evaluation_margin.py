"""Exercise 8 -- the evaluation-margin calculation.

Every accuracy number reported for a model on a held-out set is itself a
sample statistic -- a proportion, computed from a fixed number of examples --
and it carries a standard error exactly like any other. This exercise makes
the AI thread's claim a test: an accuracy of 91.4% measured on 500 examples
has a standard error of about 1.25 percentage points, so a 0.3-point
difference between two models on that same set is comfortably inside one
standard error of noise, not a demonstrated improvement.
"""

import dataset as D
from sampling import binomial_standard_error

se = binomial_standard_error(D.EVAL_ACCURACY, D.EVAL_N)
se_pct = se * 100.0

margin_in_se_units = D.EVAL_MARGIN_PCT / se_pct

print(f"accuracy = {D.EVAL_ACCURACY:.1%} on {D.EVAL_N} held-out examples")
print(f"standard error = sqrt(p_hat * (1 - p_hat) / n) = {se:.5f} = {se_pct:.3f} percentage points")
print()
print(f"a {D.EVAL_MARGIN_PCT} percentage-point difference between two models on this set "
      f"is {margin_in_se_units:.2f} standard errors -- ")
print("well inside one standard error, i.e. indistinguishable from noise on a set this size.")

assert abs(se_pct - D.EVAL_EXPECTED_SE_PCT) < D.EVAL_SE_TOLERANCE_PCT, (
    f"the binomial standard error came out to {se_pct:.3f} percentage points, "
    f"expected close to {D.EVAL_EXPECTED_SE_PCT}"
)
assert margin_in_se_units < 1.0, (
    f"a {D.EVAL_MARGIN_PCT}-point margin should sit well inside one standard error "
    f"({margin_in_se_units:.2f} SE), not outside it"
)

print("08_the_evaluation_margin.py: every assertion held.")
