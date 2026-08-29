"""Exercise 3 — reshape, flatten, slice, and the word "view".

Run from the lab directory:

    .venv/bin/python3 examples/03_views_and_copies.py

A NumPy array is two things: a flat block of memory, and a description of how
to read it as a grid. Reshaping usually rewrites only the description. When it
does, the two names are two windows onto ONE block of numbers, and writing
through either window changes what the other one sees.

That is not a bug and it is not a subtlety you can ignore. It is the reason
NumPy is fast, and it is the reason a function that "just reshapes" its input
can quietly edit your dataset.
"""

import numpy as np

from dataset import RECIPES

TOL = 1e-12


def L(a):
    """Render a numpy array as a plain Python list, with no dtype noise."""
    return np.asarray(a).tolist()


def rule(title):
    print()
    print(title)
    print("-" * len(title))


def fresh():
    return np.array(RECIPES)


rule("3a. Reshape rewrites the description, not the numbers")
M = fresh()
flat = M.reshape(12)
print(f"  M.shape    = {M.shape}")
print(f"  flat.shape = {flat.shape}")
print(f"  flat       = {L(flat)}")
print("  The entries come out row by row: the whole of row 0, then row 1, then")
print("  row 2. NumPy calls that C order, and it is the default everywhere.")
assert list(flat) == [2, 4, 1, 3, 0, 5, 2, 7, 6, 1, 4, 2]
assert M.size == flat.size == 12

print()
print(f"  M.reshape(2, 6) =\n{M.reshape(2, 6)}")
print(f"  M.reshape(4, 3) =\n{M.reshape(4, 3)}")
print("  Any shape whose entries multiply to 12 is allowed, and -1 means")
print(f"  'work it out': M.reshape(6, -1).shape = {M.reshape(6, -1).shape}")
assert M.reshape(6, -1).shape == (6, 2)

bad = None
try:
    M.reshape(5, 3)
except ValueError as exc:
    bad = str(exc)
print(f"  M.reshape(5, 3) raises ValueError: {bad}")
assert bad is not None and "reshape" in bad

rule("3b. The proof: mutate the reshaped array, watch the original change")
M = fresh()
flat = M.reshape(12)
print(f"  before: M[0, 0] = {M[0, 0]}, flat[0] = {flat[0]}")
flat[0] = 99
print("  flat[0] = 99")
print(f"  after : M[0, 0] = {M[0, 0]}, flat[0] = {flat[0]}")
print("  Nothing was assigned to M. M changed anyway.")
assert M[0, 0] == 99
print(f"  flat.base is M           -> {flat.base is M}")
print(f"  numpy.shares_memory(M, flat) -> {np.shares_memory(M, flat)}")
assert flat.base is M
assert np.shares_memory(M, flat)

rule("3c. .copy() breaks the link")
M = fresh()
independent = M.copy().reshape(12)
print(f"  before: M[0, 0] = {M[0, 0]}, independent[0] = {independent[0]}")
independent[0] = 99
print("  independent[0] = 99")
print(f"  after : M[0, 0] = {M[0, 0]}, independent[0] = {independent[0]}")
assert M[0, 0] == 2, "the original is untouched"
assert independent[0] == 99
print(f"  numpy.shares_memory(M, independent) -> {np.shares_memory(M, independent)}")
assert not np.shares_memory(M, independent)
print()
print("  A warning about the obvious-looking test. `.base is None` is NOT the")
print("  question to ask:")
print(f"    independent.base is None -> {independent.base is None}")
print("  It is False, and the array is still fully independent of M. The reason")
print("  is that M.copy().reshape(12) made TWO arrays: an anonymous copy, and a")
print("  reshaped view of that copy. `.base` truthfully points at the copy,")
print("  which no longer has a name and which nothing else can reach.")
print("  numpy.shares_memory(a, b) asks the question you actually care about.")
assert independent.base is not None
assert np.shares_memory(independent, independent.base)
assert not np.shares_memory(M, independent.base)
print("  A view costs nothing and shares everything. A copy costs the memory")
print("  and shares nothing. Neither is the right answer; knowing which one")
print("  you have is.")

rule("3d. A slice is a view too — this is the one that bites")
M = fresh()
grit = M[:, 2]
print(f"  grit = M[:, 2] = {L(grit)}   (the third column, counting from 0)")
grit[0] = 50
print("  grit[0] = 50")
print(f"  M is now:\n{M}")
assert M[0, 2] == 50
assert np.shares_memory(M, grit)
print("  Slicing a Python list gives you a new list. Slicing a NumPy array")
print("  gives you a window. The syntax is identical and the behaviour is not.")

py_list = [[2, 4, 1, 3], [0, 5, 2, 7]]
sliced = py_list[0][:]
sliced[0] = 50
print(f"  for contrast, a Python list slice: original still {py_list[0]}")
assert py_list[0][0] == 2

rule("3e. Fancy indexing always copies")
M = fresh()
picked = M[[0, 2]]
picked[0, 0] = 77
print("  M[[0, 2]] selects rows 0 and 2 by a LIST of indices, not a slice.")
print(f"  after picked[0, 0] = 77, M[0, 0] is still {M[0, 0]}")
assert M[0, 0] == 2
assert not np.shares_memory(M, picked)
print(f"  numpy.shares_memory(M, picked) -> {np.shares_memory(M, picked)}")
print("  Rule of thumb: basic slicing with colons gives a view; indexing with")
print("  a list or a boolean mask gives a copy. When in doubt, ask")
print("  numpy.shares_memory rather than guessing.")

rule("3f. .ravel() versus .flatten()")
M = fresh()
r = M.ravel()
f = M.flatten()
print(f"  M.ravel()   shares memory with M: {np.shares_memory(M, r)}")
print(f"  M.flatten() shares memory with M: {np.shares_memory(M, f)}")
print("  Same numbers, same shape, opposite ownership. ravel gives a view when")
print("  it can; flatten always copies. The names do not tell you that, so this")
print("  is a fact to memorise rather than derive.")
assert np.shares_memory(M, r)
assert not np.shares_memory(M, f)
assert np.array_equal(r, f)

rule("3g. Transpose is a view as well")
M = fresh()
t = M.T
print(f"  M.T.shape = {t.shape}, shares memory with M: {np.shares_memory(M, t)}")
t[0, 0] = 42
print(f"  after t[0, 0] = 42, M[0, 0] = {M[0, 0]}")
assert np.shares_memory(M, t)
assert M[0, 0] == 42
print("  Transposing a large matrix moves no numbers at all — it swaps two")
print("  entries in the description of how to walk the memory. That is why")
print("  transpose is free and why it is a view.")

print()
print("03_views_and_copies.py: every assertion held.")
