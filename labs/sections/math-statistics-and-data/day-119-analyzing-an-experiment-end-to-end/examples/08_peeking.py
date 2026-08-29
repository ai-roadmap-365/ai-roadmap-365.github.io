"""Exercise 8 -- peeking on real data.

Day 118 showed, in simulation, that checking significance repeatedly and
stopping the moment p < 0.05 inflates the false-positive rate. This script
shows what that instability actually looks like inside ONE real dataset:
walk dataset A in the order its rows "arrived", computing the primary
p-value from everything seen so far every 500 rows, and watch it move.

Dataset A has a genuine, real effect, and the FULL-SAMPLE verdict at the end
is "ship". But the running p-value crosses below 0.05 as early as row
4,000, climbs back above it by row 5,000, and only settles for good after
row 5,500. A team with a fixed stopping rule reaches the same, well-supported
conclusion at n=16,000. A team that stops the instant it first sees p<0.05
would have stopped at row 4,000 -- on a fluctuation that had not yet
stabilized -- and gotten lucky that the sign didn't flip. This is exactly
why a stopping rule declared in advance matters even when, as here, the
final answer turns out to be correct.
"""

from pathlib import Path

from experiment import crossed_significance, load_experiment, peek_path

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
path = peek_path(rows_a, checkpoint_every=500)

for point in path:
    flag = " <-- crosses below 0.05" if point["significant"] else ""
    print(f"  n={point['n']:>6}  diff={point['diff_pp']:+6.3f} pp  p={point['p_value']:.4f}{flag}")

final = path[-1]
crossed_early = crossed_significance(path)

print(f"final checkpoint (n={final['n']}): p={final['p_value']:.6f}, significant={final['significant']}")
print(f"crossed below 0.05 at some point before the final checkpoint: {crossed_early}")

assert crossed_early, "the running p-value should dip below 0.05 at least once before the planned end"
assert final["significant"], "the FULL-SAMPLE verdict at the planned end should be significant"

# The instability itself: find the first crossing and confirm the path is
# not simply monotonically decreasing from that point on -- it dips back
# above 0.05 at least once more before settling, which is the whole point.
first_significant_index = next(i for i, p in enumerate(path) if p["significant"])
later_non_significant = any(
    not p["significant"] for p in path[first_significant_index + 1 :]
)
assert later_non_significant, (
    "expected the p-value to rise back above 0.05 again after its first dip below it -- "
    "if it never does, peeking and a fixed sample size would have agreed by luck, not by design"
)

print("08_peeking.py: every assertion held.")
