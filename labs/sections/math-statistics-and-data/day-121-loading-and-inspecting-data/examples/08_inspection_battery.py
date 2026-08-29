"""Exercise 8 -- the inspection battery you run on any unfamiliar frame.

Run: python3 08_inspection_battery.py

In order: .head(), .info(), .dtypes, .describe(), .isna().sum(),
.nunique(), .value_counts(), memory_usage(deep=True). Each answers a
different question about data you have not seen before, and running all
eight, in this order, costs seconds and catches most of the silent
failures the earlier exercises demonstrate one at a time. This exercise
builds a frame with KNOWN properties -- an exact missing-value count, an
exact number of distinct values per column, and one column whose most
common value is known in advance -- and checks the battery's answers
against those known values.
"""

import io

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


df = pd.DataFrame(
    {
        "region": ["north", "south", "north", "east", "north", "south", None, "north"],
        "amount": [10, 20, None, 15, 30, 20, 25, 10],
    }
)
print("the frame under inspection:")
print(df)

# 1. .head() -- the fastest sanity check that the data loaded the way you expected.
print("\n1. .head(3):")
print(df.head(3))
check(".head(3) returns exactly 3 rows", len(df.head(3)) == 3)

# 2. .info() -- row count, columns, non-null counts and dtypes in one block.
print("\n2. .info():")
buf = io.StringIO()
df.info(buf=buf)
info_text = buf.getvalue()
print(info_text)
check(".info() reports the correct row count (8 entries)", "8 entries" in info_text)
check(".info() names both columns", "region" in info_text and "amount" in info_text)

# 3. .dtypes -- what kind of thing is actually in each column.
print("3. .dtypes:")
print(df.dtypes)
check("region is the pandas-3.0 str dtype", str(df["region"].dtype) == "str")
check("amount, with a None in it, is float64 (int64 has no missing-value slot)", df["amount"].dtype == "float64")

# 4. .describe() -- summary statistics for the numeric columns.
print("\n4. .describe():")
desc = df.describe()
print(desc)
check(".describe() counts only the 7 non-missing amount values", desc.loc["count", "amount"] == 7.0)

# 5. .isna().sum() -- exactly how much is missing, per column.
print("\n5. .isna().sum():")
na_counts = df.isna().sum()
print(na_counts)
check("region has exactly 1 missing value", na_counts["region"] == 1)
check("amount has exactly 1 missing value", na_counts["amount"] == 1)

# 6. .nunique() -- how many distinct values, per column (missing values not counted).
print("\n6. .nunique():")
uniq = df.nunique()
print(uniq)
check("region has exactly 3 distinct non-missing values (north, south, east)", uniq["region"] == 3)
check("amount has exactly 5 distinct non-missing values (10, 20, 15, 30, 25)", uniq["amount"] == 5)

# 7. .value_counts() -- the actual distribution, most common first.
print("\n7. region.value_counts():")
vc = df["region"].value_counts()
print(vc)
check("the single most common region is 'north'", vc.index[0] == "north")
check("'north' appears exactly 4 times", vc.iloc[0] == 4)

# 8. memory_usage(deep=True) -- the real byte cost, including string storage.
print("\n8. memory_usage(deep=True):")
mem = df.memory_usage(deep=True)
print(mem)
check("memory_usage(deep=True) reports a positive byte count for every column", (mem > 0).all())

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("08_inspection_battery.py: every assertion held.")
