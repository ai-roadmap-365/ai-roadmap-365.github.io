"""Exercise 9 -- the verdict.

Every prior step feeds one final, plain-language decision. Dataset A passes
every check and ships. Dataset B fails the very first check -- the
sample-ratio mismatch -- and the verdict function REFUSES to compute
ship/inconclusive from the (impressive-looking) primary result at all. That
refusal, not a number, is B's correct output.
"""

from pathlib import Path

from experiment import (
    guardrail_check,
    load_experiment,
    primary_test,
    segment_analysis,
    srm_check,
    verdict,
)

DATA_DIR = Path(__file__).parent.parent / "data"


def analyze(path):
    rows = load_experiment(path)
    srm = srm_check(rows)
    primary = primary_test(rows)
    guardrail = guardrail_check(rows)
    segments = segment_analysis(rows)
    return verdict(srm, primary, guardrail, segments)


result_a = analyze(DATA_DIR / "exp_a.csv")
result_b = analyze(DATA_DIR / "exp_b.csv")

print("dataset A verdict:")
for key, value in result_a.items():
    print(f"  {key}: {value}")

print("dataset B verdict:")
for key, value in result_b.items():
    print(f"  {key}: {value}")

assert result_a["verdict"] == "ship", f"expected 'ship' for dataset A, got {result_a['verdict']!r}"
assert not result_a["refused"], "dataset A's SRM check passed, verdict must not refuse"

assert result_b["verdict"] == "do not trust this result", (
    f"expected 'do not trust this result' for dataset B, got {result_b['verdict']!r}"
)
assert result_b["refused"], "dataset B's SRM check failed, the verdict must explicitly refuse"
assert "estimate_pp" not in result_b, (
    "a refused verdict must not smuggle out an effect estimate computed from untrustworthy data"
)
assert "sample-ratio mismatch" in result_b["reason"]

print("09_verdict.py: every assertion held.")
