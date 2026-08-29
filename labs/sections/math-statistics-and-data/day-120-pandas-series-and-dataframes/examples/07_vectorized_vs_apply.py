"""Exercise 7 -- vectorised arithmetic against .apply with a lambda, on the
same column.

Run: python3 07_vectorized_vs_apply.py

`.apply(lambda x: ...)` calls a real Python function once per row, from
Python. `series * 1.08` never leaves compiled code (Day 104's lesson on
NumPy). This script measures both on an identical column and reports the
result as a RATIO and a SHAPE -- "at least N times faster, on M rows" --
never a millisecond figure, because a millisecond figure is a property of
this one machine on this one day and would be misleading reported any more
precisely than that.
"""

import time

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

rng = np.random.default_rng(42)
n = 200_000
df = pd.DataFrame({"price": rng.uniform(1, 1000, n)})
print(f"\ncolumn shape: {df.shape}")


def vectorized():
    return df["price"] * 1.08


def apply_lambda():
    return df["price"].apply(lambda x: x * 1.08)


# One untimed call each to warm up caches before the timed runs.
vectorized()
apply_lambda()

reps = 5
t0 = time.perf_counter()
for _ in range(reps):
    result_vectorized = vectorized()
vectorized_time = (time.perf_counter() - t0) / reps

t0 = time.perf_counter()
for _ in range(reps):
    result_apply = apply_lambda()
apply_time = (time.perf_counter() - t0) / reps

ratio = apply_time / vectorized_time
print(f"apply / vectorized time ratio, averaged over {reps} runs: {ratio:.1f}x")
print("(one machine, one day -- this ratio is a shape, not a promise)")

check(
    "the two approaches compute the identical result",
    np.allclose(result_vectorized.to_numpy(), result_apply.to_numpy()),
)
check(
    f"vectorised arithmetic is at least 20x faster than .apply on {n:,} rows (measured {ratio:.1f}x)",
    ratio >= 20,
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("07_vectorized_vs_apply.py: every assertion held.")
