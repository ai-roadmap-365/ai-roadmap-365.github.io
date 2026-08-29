"""Exercise 5 -- .loc is label-based and INCLUSIVE of the stop; .iloc is
positional and EXCLUSIVE of the stop.

Run: python3 05_loc_vs_iloc.py

Putting `.loc['b':'d']` and `.iloc[1:4]` side by side on a 5-row frame
indexed a..e looks, at first glance, like the two behave the same way --
both return b, c, d. That similarity is what makes the asymmetry dangerous:
it hides until you write the stop value the "obvious" way and get a
different answer. The sharp version of the rule: to get the SAME rows out
of .loc and .iloc you must write a DIFFERENT stop value, because .loc's
stop is the label to include and .iloc's stop is the position to stop
before. Change only the number -- .iloc[1:3] instead of .iloc[1:4] -- and
one row silently disappears, even though 3 is the position of the label
'd' that .loc happily included.
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


df = pd.DataFrame({"val": [10, 20, 30, 40, 50]}, index=["a", "b", "c", "d", "e"])
print("frame, index a..e:")
print(df)

by_label = df.loc["b":"d"]
print("\ndf.loc['b':'d']  (label-based, stop 'd' INCLUDED):")
print(by_label)

by_position_4 = df.iloc[1:4]
print("\ndf.iloc[1:4]  (positional, stop position 4 EXCLUDED -- but position 4 is 'e', so 'd' still shows):")
print(by_position_4)

check(
    "with a DIFFERENT stop value (1:4, not 1:3), .loc['b':'d'] and .iloc[1:4] return the same three rows",
    by_label.equals(by_position_4),
)
check("both forms include the label 'd'", "d" in by_label.index and "d" in by_position_4.index)

# The sharp version of the rule: 'd' sits at position 3. Writing .iloc[1:3]
# -- the "matching number" a reader expects after seeing .loc['b':'d'] --
# EXCLUDES position 3, so 'd' is silently dropped and only two rows survive.
by_position_3 = df.iloc[1:3]
print("\ndf.iloc[1:3]  (stop position 3 EXCLUDED -- position 3 IS 'd', so 'd' is now dropped):")
print(by_position_3)

check(
    ".iloc[1:3] is SHORTER than .loc['b':'d'] -- one row missing -- even though 3 is 'd''s own position",
    len(by_position_3) == len(by_label) - 1,
)
check("'d' is present in the .loc result", "d" in by_label.index)
check("'d' is ABSENT from .iloc[1:3], which stops before position 3", "d" not in by_position_3.index)
check(
    "the row count differs: 3 labels from .loc, 2 rows from .iloc[1:3]",
    (len(by_label), len(by_position_3)) == (3, 2),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("05_loc_vs_iloc.py: every assertion held.")
