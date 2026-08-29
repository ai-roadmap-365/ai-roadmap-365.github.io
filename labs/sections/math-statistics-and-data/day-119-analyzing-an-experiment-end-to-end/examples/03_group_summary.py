"""Exercise 3 -- look before you test.

Before touching the primary metric, look at the shape of the data: are
there missing values (checked in exercise 1), and does the continuous
metric look the way a mean-only summary would lead you to believe? A
handful of planted bot-like sessions (thousands of seconds on a page a real
visitor leaves in under a minute) drag the MEAN of time-on-page well above
the MEDIAN in both datasets -- Day 116's lesson, paying off here on data
nobody labeled as containing outliers.
"""

from pathlib import Path

from experiment import group_summary, load_experiment

DATA_DIR = Path(__file__).parent.parent / "data"

rows_a = load_experiment(DATA_DIR / "exp_a.csv")
rows_b = load_experiment(DATA_DIR / "exp_b.csv")

summary_a = group_summary(rows_a)
summary_b = group_summary(rows_b)

for label, summary in (("A", summary_a), ("B", summary_b)):
    print(f"dataset {label} -- time_on_page_sec:")
    for group, stats in summary.items():
        print(
            f"  {group:<10} n={stats['n']:>6} mean={stats['mean']:>8.2f} "
            f"median={stats['median']:>6.2f} stdev={stats['stdev']:>8.2f} "
            f"min={stats['min']:>6.2f} max={stats['max']:>8.2f}"
        )

for label, summary in (("A", summary_a), ("B", summary_b)):
    for group, stats in summary.items():
        gap = stats["mean"] - stats["median"]
        assert gap > 15.0, (
            f"dataset {label} group {group}: expected the mean to sit well above the "
            f"median under the planted outliers, got mean={stats['mean']:.2f} "
            f"median={stats['median']:.2f} (gap {gap:.2f})"
        )
        assert stats["max"] > 2000.0, (
            f"dataset {label} group {group}: expected at least one bot-like outlier "
            f"session above 2000s, max was {stats['max']:.2f}"
        )

print("03_group_summary.py: every assertion held.")
