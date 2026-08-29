"""Exercise 5 -- the effect size, in its own units.

"p = 0.0003" tells a reader nothing they can act on. "1.79 percentage
points, a 17.7% relative lift, 95% CI [0.82, 2.76] points" tells them
exactly what changed and how confident to be in the size of the change.
This step asserts BOTH numbers are always reported together -- never a bare
p-value.
"""

from pathlib import Path

from experiment import effect_size, load_experiment, primary_test

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
result = primary_test(rows_a)
effect = effect_size(result)

print(f"absolute difference : {effect['abs_diff_pp']:.3f} percentage points")
print(f"relative lift        : {effect['relative_lift_pct']:.2f}%")
print(f"95% CI (abs, pp)      : [{effect['ci_low_pp']:.3f}, {effect['ci_high_pp']:.3f}]")

assert "abs_diff_pp" in effect and "relative_lift_pct" in effect, (
    "the effect size must report BOTH the absolute difference and the relative lift"
)
assert effect["relative_lift_pct"] is not None, "control rate was nonzero, relative lift should be defined"
assert 10.0 < effect["relative_lift_pct"] < 25.0, (
    f"expected a relative lift somewhere in the high teens, got {effect['relative_lift_pct']:.2f}%"
)
assert 0.5 < effect["abs_diff_pp"] < 3.5, (
    f"expected an absolute lift of a couple of percentage points, got {effect['abs_diff_pp']:.3f}"
)

print("05_effect_size.py: every assertion held.")
