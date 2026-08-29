"""Exercise 5 — settling axis=0 against axis=1, once, with a small example.

Run from the lab directory:

    .venv/bin/python3 examples/05_axes.py

Everybody gets this wrong at least once, and the reason is that both readings
sound right in English. "Sum along the rows" can mean sum each row, or sum in
the direction the rows are stacked. English will not save you. One rule will:

    THE AXIS YOU NAME IS THE AXIS THAT DISAPPEARS.

A (3, 4) array summed with axis=0 loses the 3 and returns shape (4,).
A (3, 4) array summed with axis=1 loses the 4 and returns shape (3,).

Because 3 and 4 are different here, the shape of the answer tells you which
one you got, every time, without thinking. That is why this matrix is not
square.
"""

import numpy as np

from dataset import (
    INGREDIENT_NAMES,
    LITRES_PER_BAG,
    LITRES_PER_INGREDIENT,
    MIX_NAMES,
    RECIPES,
)

TOL = 1e-12


def L(a):
    """Render a numpy array as a plain Python list, with no dtype noise."""
    return np.asarray(a).tolist()


def rule(title):
    print()
    print(title)
    print("-" * len(title))


M = np.array(RECIPES)

rule("5a. The matrix, small enough to check on paper")
print("           " + "".join(f"{n:>9}" for n in INGREDIENT_NAMES))
for name, row in zip(MIX_NAMES, M):
    print(f"{name:>10} " + "".join(f"{v:>9}" for v in row))
print(f"  shape {M.shape}  -> axis 0 has length 3, axis 1 has length 4")

rule("5b. axis=0 removes axis 0, which is the rows")
total0 = M.sum(axis=0)
print(f"  M.sum(axis=0) = {L(total0)}   shape {total0.shape}")
print("  Four numbers, one per COLUMN. The three mixes were collapsed into one.")
print("  Worked by hand, column by column:")
for name, col in zip(INGREDIENT_NAMES, M.T):
    print(f"    {name:>10}: {' + '.join(str(v) for v in col)} = {sum(col)}")
assert total0.shape == (4,)
assert list(total0) == LITRES_PER_INGREDIENT == [8, 10, 7, 12]

rule("5c. axis=1 removes axis 1, which is the columns")
total1 = M.sum(axis=1)
print(f"  M.sum(axis=1) = {L(total1)}   shape {total1.shape}")
print("  Three numbers, one per ROW. The four ingredients were collapsed into one.")
print("  Worked by hand, row by row:")
for name, row in zip(MIX_NAMES, M):
    print(f"    {name:>10}: {' + '.join(str(v) for v in row)} = {sum(row)}")
assert total1.shape == (3,)
assert list(total1) == LITRES_PER_BAG == [10, 14, 13]

rule("5d. No axis at all collapses everything")
print(f"  M.sum() = {M.sum()}   shape {np.shape(M.sum())}  (a scalar)")
print("  Which is also the sum of either of the two answers above:")
print(f"    sum of the axis=0 answer: {total0.sum()}")
print(f"    sum of the axis=1 answer: {total1.sum()}")
assert M.sum() == 37
assert total0.sum() == total1.sum() == M.sum()

rule("5e. The same rule holds for every reduction, not just sum")
table = [
    ("sum", np.sum),
    ("mean", np.mean),
    ("min", np.min),
    ("max", np.max),
    ("argmax", np.argmax),
]
print(f"  {'function':>10} {'axis=0 result':>34} {'shape':>8}")
for name, fn in table:
    value = fn(M, axis=0)
    print(f"  {name:>10} {str(np.round(value, 4)):>34} {str(value.shape):>8}")
print(f"  {'function':>10} {'axis=1 result':>34} {'shape':>8}")
for name, fn in table:
    value = fn(M, axis=1)
    print(f"  {name:>10} {str(np.round(value, 4)):>34} {str(value.shape):>8}")
assert np.allclose(M.mean(axis=0), [8 / 3, 10 / 3, 7 / 3, 4.0], atol=TOL)
assert np.allclose(M.mean(axis=1), [2.5, 3.5, 3.25], atol=TOL)
assert list(np.argmax(M, axis=0)) == [2, 1, 2, 1]
assert list(np.argmax(M, axis=1)) == [1, 3, 0]

rule("5f. argmax with an axis returns positions, not values")
print(f"  numpy.argmax(M, axis=1) = {L(np.argmax(M, axis=1))}")
print("  Read it as: within row 0 the largest entry is at column 1; within")
print("  row 1 at column 3; within row 2 at column 0. Turning those into names:")
for name, j in zip(MIX_NAMES, np.argmax(M, axis=1)):
    print(f"    {name:>10}'s largest ingredient is {INGREDIENT_NAMES[j]} ({M[MIX_NAMES.index(name), j]} litres)")
assert INGREDIENT_NAMES[np.argmax(M, axis=1)[2]] == "base"

rule("5g. The same rule tells you what keepdims does")
print(f"  M.sum(axis=0).shape                = {M.sum(axis=0).shape}")
print(f"  M.sum(axis=0, keepdims=True).shape = {M.sum(axis=0, keepdims=True).shape}")
print(f"  M.sum(axis=1, keepdims=True).shape = {M.sum(axis=1, keepdims=True).shape}")
print("  keepdims=True leaves a 1 in place of the axis instead of removing it,")
print("  which is exactly what broadcasting needs to line the answer back up")
print("  against the matrix it came from.")
assert M.sum(axis=0, keepdims=True).shape == (1, 4)
assert M.sum(axis=1, keepdims=True).shape == (3, 1)
share = M / M.sum(axis=1, keepdims=True)
print("  Each row as a fraction of its own total — the operation that")
print("  keepdims exists for:")
print(np.round(share, 4))
assert np.allclose(share.sum(axis=1), np.ones(3), atol=TOL)

rule("5h. The table worth memorising")
print("  For a 2-D array of shape (rows, columns):")
print()
print("    argument   collapses   answer is one number per   answer shape")
print("    axis=0     the rows    column                     (columns,)")
print("    axis=1     the columns row                        (rows,)")
print("    no axis    everything  whole array                ()")
print()
print("  And the check that never lies: look at the LENGTH of the answer.")
print(f"  Here, a length-{len(total0)} answer came from axis=0 and a length-{len(total1)}")
print("  answer came from axis=1, because 4 columns and 3 rows.")

print()
print("05_axes.py: every assertion held.")
