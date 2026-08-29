"""Exercise 2 -- why `and` and `or` raise on a mask, and `&`/`|`/`~` do not.

Run: python3 02_and_or_raise.py

Python's `and` and `or` are control-flow keywords: they need to convert
their operand to a single True/False using __bool__, so they can decide
which branch to take. A boolean Series has no single truth value -- it is
many booleans, one per row -- so pandas refuses to guess and raises
ValueError rather than silently picking `.any()` or `.all()` for you.
`&`, `|` and `~` are ordinary operators (bitwise-and, bitwise-or, bitwise-
not), which pandas overloads to mean elementwise boolean combination; they
never need a single truth value, so they work on a whole mask at once.
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


scores = pd.DataFrame(
    {
        "name": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gio", "Hu"],
        "score": [72, 45, np.nan, 91, 50, np.nan, 88, 33],
    }
)

mask1 = scores.score > 60
mask2 = scores.name.str.len() > 2
print("mask1 (score > 60):        ", mask1.tolist())
print("mask2 (len(name) > 2):     ", mask2.tolist())

try:
    combined = mask1 and mask2
    print("mask1 and mask2 did NOT raise -- result:", combined)
    raised = False
    error_text = ""
except ValueError as exc:
    raised = True
    error_text = str(exc)
    print(f"\nmask1 and mask2 raised ValueError: {error_text}")

check("`mask1 and mask2` raises ValueError", raised)
check(
    "the error names the ambiguity: mentions 'truth value' and 'ambiguous'",
    "truth value" in error_text and "ambiguous" in error_text,
)

# The `&` form works: elementwise boolean AND, one result per row.
and_mask = mask1 & mask2
print("\nmask1 & mask2 (elementwise AND):", and_mask.tolist())
check("mask1 & mask2 does not raise and returns 8 booleans", len(and_mask) == 8)
check(
    "mask1 & mask2 matches hand computation, row by row",
    and_mask.tolist()
    == [m1 and m2 for m1, m2 in zip(mask1.tolist(), mask2.tolist())],
)

or_mask = mask1 | mask2
print("mask1 | mask2 (elementwise OR): ", or_mask.tolist())
check(
    "mask1 | mask2 matches hand computation, row by row",
    or_mask.tolist() == [m1 or m2 for m1, m2 in zip(mask1.tolist(), mask2.tolist())],
)

not_mask = ~mask1
print("~mask1 (elementwise NOT):       ", not_mask.tolist())
check(
    "~mask1 is the exact elementwise negation of mask1",
    not_mask.tolist() == [not m for m in mask1.tolist()],
)

# `or` raises for the identical reason `and` does.
try:
    scores.score.gt(60) or scores.score.lt(40)
    or_raised = False
except ValueError:
    or_raised = True
check("`or` between two masks also raises ValueError", or_raised)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("02_and_or_raise.py: every assertion held.")
