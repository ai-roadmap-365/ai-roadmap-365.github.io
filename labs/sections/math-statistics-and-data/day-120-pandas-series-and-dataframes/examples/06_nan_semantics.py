"""Exercise 6 -- NaN is not equal to anything, including itself.

Run: python3 06_nan_semantics.py

NaN ("not a number") follows IEEE 754: by definition, NaN != NaN, and every
comparison against NaN using ==, <, >, <=, >= is False -- never an error,
never True. That is exactly why pandas gives you .isna() as a dedicated
test rather than expecting `series == float('nan')` to work: the second
form always returns an all-False mask, silently finding nothing, no matter
how many missing values are actually present.
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

# The raw Python/IEEE-754 fact underneath everything else in this exercise.
raw_nan = float("nan")
print(f"\nfloat('nan') != float('nan'): {raw_nan != raw_nan}")
check("a bare NaN is never equal to itself", raw_nan != raw_nan)
check("a bare NaN is also never LESS than itself (not just !=)", not (raw_nan < raw_nan))

s = pd.Series([1.0, np.nan, 3.0])
print("\nSeries with a NaN:")
print(s)

isna_mask = s.isna()
print(f"s.isna(): {isna_mask.tolist()}")
check(".isna() correctly finds the NaN at position 1", isna_mask.tolist() == [False, True, False])

eq_nan_mask = s == np.nan
print(f"s == np.nan: {eq_nan_mask.tolist()}")
check(
    "comparing == np.nan is USELESS for finding missing values -- always all False",
    eq_nan_mask.tolist() == [False, False, False],
)
check(
    "== np.nan never finds the NaN, even at the position where it actually is",
    eq_nan_mask.iloc[1] == False,
)

# None behaves differently depending on the surrounding dtype: in a numeric
# column it is converted to NaN on entry; in a string column (the new pandas
# 3.0 default `str` dtype) it is also reported as missing by isna(), even
# though the underlying stored value differs from a numeric column's NaN.
numeric_with_none = pd.Series([1, None, 3])
print(f"\nnumeric column built with None: dtype={numeric_with_none.dtype}, values={numeric_with_none.tolist()}")
check("None inserted into a numeric Series becomes float64 NaN", numeric_with_none.dtype == np.dtype("float64"))
check("isna() finds it there too", numeric_with_none.isna().tolist() == [False, True, False])

string_with_none = pd.Series(["a", None, "c"])
print(f"string column built with None: dtype={string_with_none.dtype}, isna={string_with_none.isna().tolist()}")
check("isna() finds None in a string-dtype column just as reliably", string_with_none.isna().tolist() == [False, True, False])

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("06_nan_semantics.py: every assertion held.")
