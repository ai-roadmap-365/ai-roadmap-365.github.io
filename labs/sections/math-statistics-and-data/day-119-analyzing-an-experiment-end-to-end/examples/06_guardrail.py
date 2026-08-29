"""Exercise 6 -- the guardrail.

A primary metric going up is not enough to ship. A guardrail metric -- here,
page-render latency -- must not get worse by more than a pre-declared
tolerance, regardless of how good the primary number looks. This check can
VETO an otherwise-positive result; exercise 9's verdict wires that veto in
directly.
"""

from pathlib import Path

from experiment import guardrail_check, load_experiment

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
result = guardrail_check(rows_a, metric="latency_ms", tolerance=5.0, lower_is_better=True)

print(f"control mean latency   = {result['control_mean']:.2f} ms")
print(f"treatment mean latency = {result['treatment_mean']:.2f} ms")
print(f"difference              = {result['diff']:+.2f} ms (tolerance {result['tolerance']} ms)")
print(f"guardrail passed         = {result['passed']}")

assert result["passed"], "dataset A's guardrail should not have worsened beyond tolerance"
assert result["diff"] < result["tolerance"], "the diff must sit under the stated tolerance to pass"

# Prove the check CAN fail: re-run it with a tolerance so tight that even A's
# tiny (and actually favorable) difference cannot possibly clear it.
tight = guardrail_check(rows_a, metric="latency_ms", tolerance=-1.0, lower_is_better=True)
assert not tight["passed"], "an impossible tolerance of -1.0 ms must make the guardrail fail"
print(f"(self-check) tolerance=-1.0 ms -> passed={tight['passed']} -- proves the check can fail")

print("06_guardrail.py: every assertion held.")
