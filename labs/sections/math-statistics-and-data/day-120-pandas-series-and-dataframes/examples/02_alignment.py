"""Exercise 2 -- index alignment, the opening failure of this whole day.

Run: python3 02_alignment.py

Adding two Series does NOT add them position by position. pandas lines the
two indexes up by LABEL first, and any label that exists on only one side
produces NaN. This is the single most common source of a silently corrupted
feature column in a real pipeline: two Series built from different filters,
joins or sorts end up with different row orders, and '+' still "succeeds" --
it just answers a different question than the one you meant to ask.
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


x = pd.Series([1, 2, 3], index=["a", "b", "c"])
y = pd.Series([10, 20, 30], index=["b", "c", "d"])
print("x:")
print(x)
print("y:")
print(y)

z = x + y
print("\nx + y (label-aligned):")
print(z)

expected_nan_labels = {"a", "d"}
actual_nan_labels = set(z.index[z.isna()])
check("labels present on only one side become NaN: a and d", actual_nan_labels == expected_nan_labels)
check("label b, present on both sides, sums to 2 + 10 = 12", z["b"] == 12.0)
check("label c, present on both sides, sums to 3 + 20 = 23", z["c"] == 23.0)
check("alignment promotes the result to float64 (NaN is a float)", z.dtype == np.dtype("float64"))

# Opting out: .to_numpy() (or .values) drops the labels and adds by position.
z_positional = x.to_numpy() + y.to_numpy()
print("\nx.to_numpy() + y.to_numpy() (positional, labels discarded):")
print(z_positional)
check(
    "positional addition on the raw arrays gives 1+10, 2+20, 3+30",
    list(z_positional) == [11, 22, 33],
)
check(
    "the positional answer and the aligned answer disagree at every position",
    not np.array_equal(z_positional, z.dropna().to_numpy()),
)

# reset_index(drop=True) is the DataFrame-shaped version of the same opt-out:
# it discards the current labels and replaces them with a fresh RangeIndex,
# so alignment then happens positionally because the labels now agree by
# construction.
x_reset = x.reset_index(drop=True)
y_reset = y.reset_index(drop=True)
z_reset = x_reset + y_reset
print("\nx.reset_index(drop=True) + y.reset_index(drop=True):")
print(z_reset)
check(
    "reset_index(drop=True) reproduces the positional sum with no NaN",
    list(z_reset) == [11, 22, 33] and not z_reset.isna().any(),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("02_alignment.py: every assertion held.")
