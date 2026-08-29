"""Exercise 3 -- operator precedence: `&` binds TIGHTER than comparisons.

Run: python3 03_precedence.py

`df[df.a > 1 & df.b < 2]` does not group the way it reads. In Python, `&`
binds more tightly than `<` and `>`, and `>`/`<` chain (Python rewrites
`A > B < C` as the equivalent of `(A > B) and (B < C)`). So the expression
actually parses as `df.a > (1 & df.b) < 2`, which chains through the same
`and` this lab's exercise 2 already showed raises ValueError on a Series.
The fix is unconditional: wrap every comparison in its own parentheses
before combining them with `&`, `|` or `~`.
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


table = pd.DataFrame({"a": [0, 1, 2, 3, 4], "b": [5, 3, 1, 0, -1]})
print("table:")
print(table)

# The unparenthesised form. Written the way it "reads" -- rows where a > 1
# AND b < 2 -- but that is not what it parses as.
try:
    wrong = table[table.a > 1 & table.b < 2]
    unparenthesised_raised = False
    wrong_repr = repr(wrong)
except ValueError as exc:
    unparenthesised_raised = True
    wrong_repr = str(exc)

print(f"\ntable.a > 1 & table.b < 2 -> {'ValueError: ' + wrong_repr if unparenthesised_raised else wrong_repr}")
check(
    "the unparenthesised form raises ValueError, for the same ambiguous-truth-value reason as `and`",
    unparenthesised_raised,
)
check(
    "the error is the familiar ambiguous-truth-value message, confirming it is chained `and` in disguise",
    "ambiguous" in wrong_repr,
)

# The intended query, with each comparison parenthesised.
intended_mask = (table.a > 1) & (table.b < 2)
intended = table[intended_mask]
print("\n(table.a > 1) & (table.b < 2) mask:", intended_mask.tolist())
print("(table.a > 1) & (table.b < 2) rows:")
print(intended)

check("the parenthesised mask has exactly 3 True values", intended_mask.sum() == 3)
check(
    "the parenthesised form selects rows where a in {2,3,4} and b in {1,0,-1}",
    intended["a"].tolist() == [2, 3, 4] and intended["b"].tolist() == [1, 0, -1],
)

# A second precedence trap, and the more dangerous kind: `~` also binds
# tighter than `==`, and this one does NOT raise -- it silently computes the
# wrong thing. `~table.a` is the bitwise-NOT of the integer column itself
# (~0=-1, ~1=-2, ~2=-3, ...), computed BEFORE the == 2 comparison runs, so
# `~table.a == 2` asks "which rows have bitwise-NOT(a) equal to 2", not
# "which rows have a NOT equal to 2" -- and since no value of a in this
# table has ~a == 2, the wrong query quietly returns zero rows.
wrong_tilde = table[~table.a == 2]
print(f"\n~table.a == 2 (WRONG -- parses as (~table.a) == 2): {len(wrong_tilde)} rows")
check(
    "~table.a == 2 does NOT raise -- it silently returns the wrong (empty) result",
    len(wrong_tilde) == 0,
)
correct_tilde = table[~(table.a == 2)]
print(f"~(table.a == 2)  (correct -- excludes only a == 2): {len(correct_tilde)} rows -> {correct_tilde['a'].tolist()}")
check(
    "the parenthesised form ~(table.a == 2) correctly excludes only a == 2",
    correct_tilde["a"].tolist() == [0, 1, 3, 4],
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("03_precedence.py: every assertion held.")
