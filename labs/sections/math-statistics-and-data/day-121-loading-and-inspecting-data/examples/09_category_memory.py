"""Exercise 9 -- category memory: converting a low-cardinality string column.

Run: python3 09_category_memory.py

A "category" dtype stores each distinct value ONCE and represents every row
as a small integer code pointing at it. For a column with few distinct
values repeated many times -- region names, status flags, product
categories -- that trades a large amount of repeated string storage for a
small lookup table plus one integer per row. This exercise measures the
actual reduction on the authoring machine and asserts the RATIO clears a
stated factor, never a byte count, because byte counts are a fact about one
machine's malloc behaviour on one day.
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


rng = np.random.default_rng(42)
n_rows = 20_000
regions = rng.choice(["north", "south", "east", "west"], size=n_rows)
df = pd.DataFrame({"region": regions})
print(f"{n_rows} rows, {df['region'].nunique()} distinct region values")
print("region dtype:", df["region"].dtype)

mem_str = int(df["region"].memory_usage(deep=True))
df["region_cat"] = df["region"].astype("category")
mem_cat = int(df["region_cat"].memory_usage(deep=True))

print(f"\nmemory_usage(deep=True) as {df['region'].dtype}:  {mem_str:>8,} bytes")
print(f"memory_usage(deep=True) as category:          {mem_cat:>8,} bytes")
ratio = mem_str / mem_cat
print(f"reduction ratio: {ratio:.2f}x")

check("the category dtype has the same 4 distinct values as the original", df["region_cat"].nunique() == 4)
check(
    "the category column is genuinely smaller than the string column",
    mem_cat < mem_str,
)
check(
    "the reduction ratio clears at least 5x on this 4-category, 20,000-row column",
    ratio >= 5.0,
)
check(
    "converting to category does not change the actual values, only the storage",
    (df["region_cat"].astype("str") == df["region"]).all(),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("09_category_memory.py: every assertion held.")
