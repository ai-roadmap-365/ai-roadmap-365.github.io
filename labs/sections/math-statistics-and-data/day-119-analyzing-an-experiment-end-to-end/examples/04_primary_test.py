"""Exercise 4 -- the test and the interval, together.

A p-value alone tells you whether to be surprised by chance. It says
nothing about how big the effect is or how uncertain that size is. This
step always reports the difference AND a confidence interval on it, built
from `math.erf` exactly as Day 118 built it -- no scipy.stats involved.
"""

from pathlib import Path

from experiment import load_experiment, primary_test

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")

result = primary_test(rows_a)

print(f"p_control    = {result['p_control']:.4f}")
print(f"p_treatment  = {result['p_treatment']:.4f}")
print(f"diff         = {result['diff'] * 100:.3f} percentage points")
print(f"z            = {result['z']:.3f}")
print(f"p_value      = {result['p_value']:.6f}")
print(f"95% CI       = [{result['ci_low'] * 100:.3f}, {result['ci_high'] * 100:.3f}] percentage points")

assert result["p_value"] < 0.05, "dataset A's primary test should be significant at alpha=0.05"
assert result["excludes_zero"], "dataset A's confidence interval should exclude zero"
assert result["ci_low"] > 0.0, "both endpoints should be positive -- treatment beat control"
assert result["ci_high"] > result["ci_low"], "the interval must be well-formed"

# A quick agreement check: the z-test p-value and "the interval excludes
# zero at 95%" should never disagree at alpha=0.05 -- they are the same
# question asked two ways.
assert (result["p_value"] < 0.05) == result["excludes_zero"], (
    "the significance test and the 95% interval disagreed -- something is wrong "
    "with one of the two calculations"
)

print("04_primary_test.py: every assertion held.")
