"""Exercise 1 -- the partition invariant, the opening failure of this day.

Run: python3 01_partition_invariant.py

A filter that reports "high performers" and a filter that reports
"everyone else" should, together, account for every row. Split a column
with missing values two ways -- score > 50 and score <= 50 -- and the two
groups do NOT add up to the whole frame. Rows where score is NaN fail BOTH
comparisons and vanish from both halves, because NaN compared with < or >
or <= or >= is always False. Nobody deleted them; they are simply not in
either answer. The fix is not cleverness, it is a habit: name the missing
rows explicitly and check that all three groups together account for the
whole frame.
"""

import numpy as np
import pandas as pd

checks = 0
failures = 0


def check(label, condition):
    global checks, failures
    checks += 1
    if condition:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}")
        failures += 1


scores = pd.DataFrame(
    {
        "name": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gio", "Hu"],
        "score": [72, 45, np.nan, 91, 50, np.nan, 88, 33],
    }
)
print("scores:")
print(scores)

total = len(scores)
high = scores[scores.score > 50]
low = scores[scores.score <= 50]
missing_count = int(scores.score.isna().sum())

print(f"\ntotal rows:           {total}")
print(f"high (score > 50):    {len(high)}  -> {high.name.tolist()}")
print(f"low  (score <= 50):   {len(low)}   -> {low.name.tolist()}")
print(f"missing (score NaN):  {missing_count} -> {scores.loc[scores.score.isna(), 'name'].tolist()}")

# The broken invariant: the two "obvious" halves do not sum to the total.
check("high has exactly 3 rows (Ada, Dee, Gio)", len(high) == 3)
check("low has exactly 3 rows (Bo, Eli, Hu)", len(low) == 3)
check("scores has 2 rows with a missing score (Cy, Fay)", missing_count == 2)
check(
    "the naive two-way split does NOT add up: len(high) + len(low) != total",
    len(high) + len(low) != total,
)
check(
    "the shortfall is exactly the missing-value count: total - high - low == isna().sum()",
    total - len(high) - len(low) == missing_count,
)

# The fix: name the missing rows as their own group, and the three-way
# partition -- high, low, missing -- accounts for every row exactly once.
missing_rows = scores[scores.score.isna()]
check(
    "handled explicitly, the three-way partition sums to the total: high + low + missing == total",
    len(high) + len(low) + len(missing_rows) == total,
)
check(
    "no row is double-counted: the three index sets are pairwise disjoint",
    set(high.index) & set(low.index) == set()
    and set(high.index) & set(missing_rows.index) == set()
    and set(low.index) & set(missing_rows.index) == set(),
)

# A second, equally valid fix: build the "everyone else" half as the boolean
# complement of "high" rather than a second independent comparison. Because
# NaN > 50 is False, its complement ~(score > 50) is True for a NaN row --
# so the complement bucket automatically catches the missing rows too.
low_or_missing = scores[~(scores.score > 50)]
check(
    "the complement of high (~(score > 50)) automatically catches the missing rows too",
    len(high) + len(low_or_missing) == total,
)
check(
    "the complement bucket is exactly low UNION missing",
    set(low_or_missing.index) == set(low.index) | set(missing_rows.index),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("01_partition_invariant.py: every assertion held.")
