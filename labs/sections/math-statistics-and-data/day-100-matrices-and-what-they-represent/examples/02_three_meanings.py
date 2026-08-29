"""Exercise 2 — one matrix, read three ways.

Run from the lab directory:

    .venv/bin/python3 examples/02_three_meanings.py

The same twelve numbers are read as a table of data, then as a collection of
vectors, then as a transformation. Nothing about the numbers changes. What
changes is which question you are asking, and every operation in this lab is
downstream of that choice.

The data is invented; see dataset.py.
"""

import numpy as np

from dataset import (
    COST_PER_BAG_PENCE,
    INGREDIENT_NAMES,
    LITRES_PER_BAG,
    LITRES_PER_INGREDIENT,
    MIX_NAMES,
    PRICE_PER_LITRE,
    RECIPES,
)
from matrix import Matrix

TOL = 1e-12


def L(a):
    """Render a numpy array as a plain Python list, with no dtype noise."""
    return np.asarray(a).tolist()


def rule(title):
    print()
    print(title)
    print("-" * len(title))


M = np.array(RECIPES)
prices = np.array(PRICE_PER_LITRE)

rule("Meaning 1 — a table of data: rows are items, columns are features")
header = "           " + "".join(f"{name:>9}" for name in INGREDIENT_NAMES)
print(header)
for name, row in zip(MIX_NAMES, M):
    print(f"{name:>10} " + "".join(f"{value:>9}" for value in row))
print()
print(f"  shape {M.shape}: {M.shape[0]} items described by {M.shape[1]} features.")
print("  This is the shape a CSV file arrives in (Day 65) and the shape a")
print("  SELECT returns (Day 85). Row 1 is a mix. Column 1 is a measurement")
print("  made of every mix. They are different kinds of thing living in one")
print("  rectangle, which is exactly why the axis argument keeps catching")
print("  people out.")
assert M.shape == (3, 4)
assert list(M[MIX_NAMES.index("Alpine")]) == [6, 1, 4, 2]
assert list(M[:, INGREDIENT_NAMES.index("grit")]) == [1, 2, 4]

rule("Meaning 2 — a collection of vectors, and WHICH collection matters")
print("  Read as rows, each vector is one mix in ingredient-space:")
for name, row in zip(MIX_NAMES, M):
    print(f"    {name:>10} -> {L(row)}   length {np.linalg.norm(row):.4f}")
print()
print("  Read as columns, each vector is one ingredient across the range:")
for name, col in zip(INGREDIENT_NAMES, M.T):
    print(f"    {name:>10} -> {L(col)}   length {np.linalg.norm(col):.4f}")
print()
print("  Same twelve numbers. Three vectors of length 4, or four vectors of")
print("  length 3 — and the norms are entirely different numbers, so an")
print("  operation that assumed the wrong one gives a plausible wrong answer")
print("  rather than an error.")
row_norms = np.linalg.norm(M, axis=1)
col_norms = np.linalg.norm(M, axis=0)
assert row_norms.shape == (3,)
assert col_norms.shape == (4,)
# Seedling: sqrt(4 + 16 + 1 + 9) = sqrt(30); worked out by hand.
assert np.allclose(row_norms[0], np.sqrt(30.0), atol=TOL)
# base column: sqrt(4 + 0 + 36) = sqrt(40)
assert np.allclose(col_norms[0], np.sqrt(40.0), atol=TOL)
assert not np.allclose(np.sort(row_norms), np.sort(col_norms[:3]), atol=TOL)

rule("Meaning 3 — a transformation: give it a vector, get a vector back")
print(f"  in : the price of each ingredient in pence per litre {L(prices)}")
print("       (a vector of length 4, one entry per COLUMN of the matrix)")
by_hand = []
for name, row in zip(MIX_NAMES, M):
    terms = " + ".join(f"{q}*{p}" for q, p in zip(row, prices))
    total = int(np.sum(row * prices))
    by_hand.append(total)
    print(f"    {name:>10}: {terms} = {total}")
print(f"  out: the cost of one bag of each mix in pence {by_hand}")
print("       (a vector of length 3, one entry per ROW of the matrix)")
print()
print("  A (3, 4) matrix eats a vector of length 4 and returns one of length 3.")
print("  The 4 is consumed; the 3 survives. That is the whole shape rule, and")
print("  it is why a shape error is always a disagreement about which of the")
print("  three meanings each side assumed.")
assert by_hand == COST_PER_BAG_PENCE

scratch = Matrix(RECIPES).apply_to(PRICE_PER_LITRE)
broadcast = (M * prices).sum(axis=1)
print()
print(f"  from-scratch double loop : {scratch}")
print(f"  numpy (M * prices).sum(axis=1): {L(broadcast)}")
print("  Both are the same arithmetic. The packed operator that names it,")
print("  M @ prices, is Day 101.")
assert scratch == COST_PER_BAG_PENCE
assert np.allclose(broadcast, COST_PER_BAG_PENCE, atol=TOL)

rule("The identity transformation, on this data")
identity = np.eye(4, dtype=int)
print("  A (4, 4) identity matrix applied to the price vector returns it:")
print(f"    {L((identity * prices).sum(axis=1))}")
assert np.allclose((identity * prices).sum(axis=1), prices, atol=TOL)
print("  A diagonal matrix instead scales each ingredient's price separately.")
doubler = np.diag([2, 1, 1, 1])
print(f"    doubling only the base price: {L((doubler * prices).sum(axis=1))}")
assert list((doubler * prices).sum(axis=1)) == [20, 2, 5, 1]

rule("The two totals the table meaning wants")
print(f"  litres in each bag (sum across each row)      : {L(M.sum(axis=1))}")
print(f"  litres of each ingredient (sum down each col) : {L(M.sum(axis=0))}")
assert list(M.sum(axis=1)) == LITRES_PER_BAG
assert list(M.sum(axis=0)) == LITRES_PER_INGREDIENT

print()
print("02_three_meanings.py: every assertion held.")
