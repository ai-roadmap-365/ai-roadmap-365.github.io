"""Exercise 1 -- build a Series and a DataFrame three different ways.

Run: python3 01_three_ways_to_build.py

A Series is values plus an index. A DataFrame is a set of Series that share
one index. This script builds both from a dict, from a list of records, and
from a bare NumPy array with an explicit index supplied separately -- and
checks, rather than assumes, what the index and the dtypes become in each
case.
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


print(f"pandas {pd.__version__}, numpy {np.__version__}")
print()

# -- Series from a dict: the dict's keys become the index, in insertion order
print("-- Series from a dict --")
s_dict = pd.Series({"a": 10, "b": 20, "c": 30})
print(s_dict)
check("index becomes the dict's keys", list(s_dict.index) == ["a", "b", "c"])
check("dtype is inferred as int64 from all-int values", s_dict.dtype == np.dtype("int64"))

# -- DataFrame from a dict of lists: keys become column names, index is the
#    default RangeIndex 0..n-1 because nothing said otherwise
print("\n-- DataFrame from a dict of lists --")
df_dict = pd.DataFrame({"x": [1, 2, 3], "y": [4.0, 5.0, 6.0]})
print(df_dict)
print(df_dict.dtypes)
check("columns are the dict's keys, in order", list(df_dict.columns) == ["x", "y"])
check("index defaults to RangeIndex(0, 3)", list(df_dict.index) == [0, 1, 2])
check("column x is int64 (all ints)", df_dict["x"].dtype == np.dtype("int64"))
check("column y is float64 (all floats)", df_dict["y"].dtype == np.dtype("float64"))

# -- DataFrame from a list of records (one dict per row): same result as
#    above, because a "record" is just a row-oriented way of writing the
#    same table -- pandas transposes it for you
print("\n-- DataFrame from a list of records --")
records = [{"x": 1, "y": 4.0}, {"x": 2, "y": 5.0}, {"x": 3, "y": 6.0}]
df_records = pd.DataFrame(records)
print(df_records)
check("records give the same columns", list(df_records.columns) == ["x", "y"])
check("records give the same index", list(df_records.index) == [0, 1, 2])
check("records and dict-of-lists produce an identical frame", df_records.equals(df_dict))

# -- DataFrame from a bare NumPy array: the array carries NO labels at all --
#    you must supply both the index and the columns yourself, or pandas
#    falls back to the same default RangeIndex on both axes
print("\n-- DataFrame from a NumPy array, explicit index --")
arr = np.array([[1, 2], [3, 4], [5, 6]])
df_arr = pd.DataFrame(arr, index=["p", "q", "r"], columns=["c1", "c2"])
print(df_arr)
print(df_arr.dtypes)
check("explicit index is used verbatim", list(df_arr.index) == ["p", "q", "r"])
check("explicit columns are used verbatim", list(df_arr.columns) == ["c1", "c2"])
check("a plain int array gives int64 columns", (df_arr.dtypes == np.dtype("int64")).all())

df_arr_default = pd.DataFrame(arr)
check(
    "without an explicit index, a NumPy array also falls back to RangeIndex",
    list(df_arr_default.index) == [0, 1, 2] and list(df_arr_default.columns) == [0, 1],
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("01_three_ways_to_build.py: every assertion held.")
