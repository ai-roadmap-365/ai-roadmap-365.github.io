"""Exercise 3 -- the moment a NaN enters an int64 column.

Run: python3 03_dtype_promotion.py

NumPy's int64 has no bit pattern reserved for "missing". The instant a
missing value enters an int64 Series, pandas silently promotes the WHOLE
column to float64, because float64 has NaN available. That is how an ID
column -- something you never intended to do arithmetic on -- quietly loses
exact-integer precision the moment one row is missing. The nullable Int64
dtype (capital I) exists specifically to avoid this: it carries its own
missing marker (pd.NA) without leaving the integer family.
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


ids = pd.Series([1001, 1002, 1003], dtype="int64")
print("a clean int64 column of IDs:")
print(ids)
check("a clean column of whole numbers is int64", ids.dtype == np.dtype("int64"))

# reindex() is what a real pipeline does when a join fails to find a match
# for one label: it asks the Series for a row that was not there, and
# pandas fills the gap with NaN. NumPy's int64 array has no bit pattern
# reserved for "missing", so the ENTIRE column is silently rebuilt as
# float64 -- not just the new row -- so that NaN has somewhere to live.
ids_with_gap = ids.reindex([0, 1, 2, 3])
print("\nafter reindexing onto a label that was never there (a join miss):")
print(ids_with_gap)
check(
    "the ENTIRE column is promoted to float64, not just the missing row",
    ids_with_gap.dtype == np.dtype("float64"),
)
check("the missing row reads as NaN", pd.isna(ids_with_gap.iloc[3]))

# The precision loss this enables: an ID large enough to exceed float64's
# 53-bit exact-integer mantissa silently rounds once it is forced to share a
# column with a float.
big_id = 2**53 + 1  # the first integer float64 cannot represent exactly
mixed = pd.Series([big_id], dtype="int64").reindex([0, 1])
recovered = int(mixed.iloc[0])
print(f"\noriginal big ID:  {big_id}")
print(f"after promotion:  {recovered}")
check(
    "an ID past 2**53 loses its exact value once promoted to float64",
    recovered != big_id,
)

# The nullable Int64 dtype avoids all of this: it stays in the integer
# family and represents the missing entry as pd.NA instead of NaN, even
# after the same reindex onto a label that was never there.
ids_nullable = pd.Series([1001, 1002, 1003], dtype="Int64").reindex([0, 1, 2, 3])
print("\nthe same reindex, but the column is declared nullable Int64:")
print(ids_nullable)
check("a nullable Int64 column stays Int64 after the same reindex", ids_nullable.dtype == "Int64")
check("the missing entry is pd.NA, not NaN", ids_nullable.iloc[3] is pd.NA)
check(
    "the surviving values keep exact integer precision under Int64",
    int(ids_nullable.iloc[0]) == 1001,
)

big_id_nullable = pd.Series([big_id], dtype="Int64").reindex([0, 1])
check(
    "even a value past 2**53 keeps its exact integer value under Int64",
    int(big_id_nullable.iloc[0]) == big_id,
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("03_dtype_promotion.py: every assertion held.")
