"""Exercise 4 -- Copy-on-Write and chained assignment. This is the day's
most important check.

Run: python3 04_copy_on_write.py

pandas 3.0 has Copy-on-Write ALWAYS on; it can no longer be switched off.
One direct consequence: chained assignment -- indexing twice in one
statement, `df[mask]['col'] = value` -- silently does nothing. The first
`df[mask]` produces a temporary DataFrame; the second `['col'] = value`
assigns into that temporary, which is then discarded. The original `df` is
completely unchanged, and on 3.0.5 pandas raises a ChainedAssignmentError
*warning* (not an exception -- the statement still "succeeds" and moves on)
telling you exactly this. Reader beware: that warning is easy to miss if
warnings are filtered or redirected, which is exactly the situation every
tutorial written for pandas < 2.0 describes as silent and undetectable.
The fix is a single `.loc` call that does the selection and the assignment
in one step, which is the only form Copy-on-Write actually allows to work.
"""

import warnings

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

df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
original_b = df["b"].tolist()
print("\noriginal frame:")
print(df)
print(f"df['b'] before: {original_b}")

# The chained-assignment form: two lookups in one statement. Capture the
# warning pandas 3.0.5 raises about it, rather than letting it print to
# stderr, so this script's own output stays clean -- but the READER should
# see that warning by default; it is not suppressed anywhere else in this
# lab.
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df[df["a"] > 1]["b"] = 0  # chained assignment -- looks like it should work
    chained_warning_names = [w.category.__name__ for w in caught]

after_chained = df["b"].tolist()
print(f"\ndf['b'] after chained assignment `df[df['a'] > 1]['b'] = 0`: {after_chained}")
print(f"warning(s) raised by that statement: {chained_warning_names}")

check(
    "chained assignment leaves the original frame COMPLETELY unchanged",
    after_chained == original_b == [10, 20, 30],
)
check(
    "pandas 3.0.5 warns about it with ChainedAssignmentError (a Warning, not raised as an exception)",
    "ChainedAssignmentError" in chained_warning_names,
)

# The fix: one .loc call carrying both the row selector and the column
# selector, so there is only ever one object involved -- no temporary to
# lose the write to.
df.loc[df["a"] > 1, "b"] = 0
after_loc = df["b"].tolist()
print(f"\ndf['b'] after `.loc[df['a'] > 1, 'b'] = 0`: {after_loc}")
check("the .loc form DOES change the original frame", after_loc == [10, 0, 0])
check("the .loc form does not equal the untouched original", after_loc != original_b)

# The deprecated switch: pandas 3.0 removed the ability to turn Copy-on-Write
# off. Setting the old option is now a no-op that only warns.
print("\nsetting the old pd.options.mode.copy_on_write switch:")
with warnings.catch_warnings(record=True) as caught2:
    warnings.simplefilter("always")
    pd.options.mode.copy_on_write = False
    option_warning_messages = [str(w.message) for w in caught2]
for msg in option_warning_messages:
    print(f"  warning: {msg}")
check(
    "setting mode.copy_on_write now only emits a deprecation warning and has no effect",
    any("no impact" in msg or "no longer be disabled" in msg for msg in option_warning_messages),
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("04_copy_on_write.py: every assertion held.")
