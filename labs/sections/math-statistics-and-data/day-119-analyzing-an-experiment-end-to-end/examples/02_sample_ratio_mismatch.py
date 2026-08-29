"""Exercise 2 -- the sample-ratio mismatch check.

The single most valuable, most-often-skipped check in this lesson. Before
anything about the effect is trustworthy, the randomization itself has to be
trustworthy: if you planned 50/50 and the final counts came out lopsided,
that is itself a testable hypothesis, and it is tested here with a one-shot
chi-squared goodness-of-fit test at a conservative alpha.
"""

from pathlib import Path

from experiment import load_experiment, srm_check

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
rows_b = load_experiment(DATA_DIR / "exp_b.csv")

srm_a = srm_check(rows_a)
srm_b = srm_check(rows_b)

print("dataset A:")
print(f"  n_control={srm_a['n_control']} n_treatment={srm_a['n_treatment']} "
      f"observed_split={srm_a['observed_split']:.4f}")
print(f"  chi2={srm_a['chi2']:.4f} p_value={srm_a['p_value']:.6f} passed={srm_a['passed']}")

print("dataset B:")
print(f"  n_control={srm_b['n_control']} n_treatment={srm_b['n_treatment']} "
      f"observed_split={srm_b['observed_split']:.4f}")
print(f"  chi2={srm_b['chi2']:.4f} p_value={srm_b['p_value']:.3e} passed={srm_b['passed']}")

assert srm_a["passed"], "the SRM check must PASS on the clean dataset A"
assert not srm_b["passed"], "the SRM check must FAIL on the haunted dataset B"
assert srm_a["p_value"] > 0.5, "A's split is exactly as planned, so its p-value should sit nowhere near the threshold"
assert srm_b["p_value"] < srm_b["alpha"], "B's mismatch must clear its own alpha threshold to count as a failure"
assert srm_b["observed_split"] < 0.49, (
    f"B's planted mismatch should read close to 48/52, got {srm_b['observed_split']:.4f}"
)

print("02_sample_ratio_mismatch.py: every assertion held.")
