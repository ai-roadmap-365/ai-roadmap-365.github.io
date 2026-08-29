"""Exercise 9 -- .describe(), .info(), .head() and memory_usage(deep=True)
on a column with hand-computable values, tying back to Day 116.

Run: python3 09_describe_known_column.py

These four commands are what you run on any frame you have not met before.
`.describe()` computes exactly the summary statistics Day 116 taught by
hand -- count, mean, standard deviation, min, the quartiles, max -- so this
script checks its output against arithmetic done independently of pandas,
the same discipline Day 116 insisted on: never trust a reported number
without knowing what produced it.
"""

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


print(f"pandas {pd.__version__}")

values = [2, 4, 4, 4, 5, 5, 7, 9]
scores = pd.Series(values, name="score")
print(f"\nscores: {values}")

desc = scores.describe()
print("\n.describe():")
print(desc)

hand_count = len(values)
hand_mean = sum(values) / len(values)
hand_min = min(values)
hand_max = max(values)

print(f"\nhand-computed count={hand_count}, mean={hand_mean}, min={hand_min}, max={hand_max}")

check("describe()'s count matches len(values) exactly", desc["count"] == hand_count)
check("describe()'s mean matches sum(values)/len(values) exactly", desc["mean"] == hand_mean)
check("describe()'s min matches min(values) exactly", desc["min"] == hand_min)
check("describe()'s max matches max(values) exactly", desc["max"] == hand_max)

# Day 116's Bessel-corrected sample standard deviation: divide the sum of
# squared deviations by n - 1, not n, then take the square root.
mean = hand_mean
sq_dev = sum((v - mean) ** 2 for v in values)
hand_std = (sq_dev / (hand_count - 1)) ** 0.5
print(f"hand-computed sample std (n-1 denominator, Day 116's Bessel correction): {hand_std:.6f}")
check("describe()'s std uses the same n-1 (Bessel-corrected) denominator as Day 116", abs(desc["std"] - hand_std) < 1e-9)

# A small DataFrame to exercise .head(), .info() and memory_usage(deep=True).
df = pd.DataFrame({"score": values, "grade": ["F", "D", "D", "D", "C", "C", "B", "A"]})
print("\n.head(3):")
print(df.head(3))
check(".head(3) returns exactly 3 rows", len(df.head(3)) == 3)
check(".head(3) returns the FIRST 3 rows, in order", df.head(3)["score"].tolist() == values[:3])

print("\n.info():")
df.info()

usage_shallow = df.memory_usage(deep=False)
usage_deep = df.memory_usage(deep=True)
print("\n.memory_usage(deep=False):")
print(usage_shallow)
print(".memory_usage(deep=True):")
print(usage_deep)
check("memory_usage(deep=True) reports a positive byte count for the string column", usage_deep["grade"] > 0)

# A version-specific surprise worth recording: because the pandas-3.0 `str`
# dtype already stores its bytes contiguously (PyArrow-backed) rather than
# as pointers to scattered Python objects, deep=True and deep=False report
# the SAME number for a str column -- there is no hidden pointer indirection
# left for "deep" to go and discover. That is new in 3.0; the object dtype,
# still reachable on request, is the one where "deep" used to matter.
check(
    "for the pandas-3.0 str dtype, deep=True and deep=False report the SAME byte count (no pointer indirection left to find)",
    usage_deep["grade"] == usage_shallow["grade"],
)

df_legacy_object = df.astype({"grade": "object"})
usage_legacy_shallow = df_legacy_object.memory_usage(deep=False)
usage_legacy_deep = df_legacy_object.memory_usage(deep=True)
print("\nthe SAME column forced back to the legacy object dtype:")
print(f"  deep=False: {usage_legacy_shallow['grade']} bytes   deep=True: {usage_legacy_deep['grade']} bytes")
check(
    "on the legacy object dtype, deep=True reports far MORE bytes than deep=False -- the old surprise is still there if you ask for object",
    usage_legacy_deep["grade"] > usage_legacy_shallow["grade"],
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("09_describe_known_column.py: every assertion held.")
