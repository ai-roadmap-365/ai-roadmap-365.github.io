"""`*` and `@` are different operations, and NumPy will not warn you.

Run from inside this directory:

    ../.venv/bin/python3 03_star_versus_at.py

The trap is not that one of them is wrong. It is that on the right operands
BOTH are legal, both return an array, and only the shape gives you away — and
sometimes not even that. This script meets it deliberately, then covers the
three spellings of matrix multiplication and how to read a shape error.
"""

import numpy as np

from dataset import P, P_AT_Q, P_TIMES_Q, Q, U, W, X, X_AT_U, X_AT_XT, X_TIMES_U, XT_AT_X

print("=" * 74)
print("1. Same two operands, both operations legal, different answers")
print("=" * 74)

npP, npQ = np.array(P), np.array(Q)
print(f"  P = {npP.tolist()}   Q = {npQ.tolist()}   both shape {npP.shape}")
print()
print(f"  P * Q  -> shape {(npP * npQ).shape}  {(npP * npQ).tolist()}")
print("             entry by entry: 1*5=5, 2*6=12, 3*7=21, 4*8=32. Nothing summed.")
print(f"  P @ Q  -> shape {(npP @ npQ).shape}  {(npP @ npQ).tolist()}")
print("             row dotted with column: 1*5 + 2*7 = 19, and so on.")
assert (npP * npQ).tolist() == P_TIMES_Q
assert (npP @ npQ).tolist() == P_AT_Q
assert (npP * npQ).shape == (npP @ npQ).shape == (2, 2)
print()
print("  Note the shapes are IDENTICAL. Two square matrices of the same size")
print("  give a same-sized answer either way, so a shape check catches nothing")
print("  here. Only the numbers differ, and nothing will tell you which you got.")

print()
print("=" * 74)
print("2. The version where the shapes do give you away")
print("=" * 74)

npX, npU = np.array(X), np.array(U)
print(f"  X = {npX.tolist()}   shape {npX.shape}")
print(f"  u = {npU.tolist()}                 shape {npU.shape}")
print()
star = npX * npU
at = npX @ npU
print(f"  X * u  -> shape {star.shape}  {star.tolist()}")
print("             u is broadcast across both rows (Day 100), then multiplied")
print("             entry by entry. Three numbers per row go in, three come out.")
print(f"  X @ u  -> shape {at.shape}     {at.tolist()}")
print("             each row is multiplied by u AND THEN SUMMED:")
print("               row 0: 1*10 + 2*2 + 0*5 = 10 + 4 + 0  = 14")
print("               row 1: 0*10 + 1*2 + 3*5 =  0 + 2 + 15 = 17")
assert star.tolist() == X_TIMES_U
assert at.tolist() == X_AT_U
assert star.shape == (2, 3)
assert at.shape == (2,)
print()
print("  The summing is the whole difference. `*` keeps every product; `@` adds")
print("  them up and loses a dimension doing it. That collapse is what makes it")
print("  a transformation rather than a rescaling.")

print()
print("=" * 74)
print("3. Three spellings of the same operation")
print("=" * 74)

by_at = npX @ np.array(W)
by_matmul = np.matmul(npX, np.array(W))
by_dot = np.dot(npX, np.array(W))
print(f"  X @ W            = {by_at.tolist()}")
print(f"  np.matmul(X, W)  = {by_matmul.tolist()}")
print(f"  np.dot(X, W)     = {by_dot.tolist()}")
assert by_at.tolist() == by_matmul.tolist() == by_dot.tolist()
print()
print("  All three agree on two-dimensional arrays, and `@` is the one to use:")
print("  it says at a glance which operation you meant. The other two exist for")
print("  reasons that matter only when the arrays have more than two dimensions,")
print("  where matmul and dot genuinely differ — matmul treats leading axes as a")
print("  stack of matrices, dot does not. Here is that difference, on shapes")
print("  small enough to read:")

stack = np.arange(8).reshape(2, 2, 2)
plain = np.arange(4).reshape(2, 2)
other = np.arange(8).reshape(2, 2, 2)

print(f"      a stack of two 2x2 matrices, shape {stack.shape}, times one 2x2:")
print(f"        np.matmul -> {np.matmul(stack, plain).shape}")
print(f"        np.dot    -> {np.dot(stack, plain).shape}")
print("        Here they agree, in shape AND in every value. This case was")
print("        checked rather than assumed, and the assumption would have been")
print("        that they differ. They do not.")
assert np.matmul(stack, plain).shape == (2, 2, 2)
assert np.dot(stack, plain).shape == (2, 2, 2)
assert np.array_equal(np.matmul(stack, plain), np.dot(stack, plain))

print(f"      the same stack times ANOTHER stack, {stack.shape} against {other.shape}:")
print(f"        np.matmul -> {np.matmul(stack, other).shape}   two matrices, paired up")
print(f"        np.dot    -> {np.dot(stack, other).shape}   every pairing, all four")
assert np.matmul(stack, other).shape == (2, 2, 2)
assert np.dot(stack, other).shape == (2, 2, 2, 2)
print("        THAT is where they part company, and the gap is a whole extra")
print("        axis. matmul pairs the stacks off matrix by matrix; dot sums over")
print("        the last axis of the left and the second-to-last of the right and")
print("        keeps everything else, so it produces every combination.")
print()
print("      The rule to carry is simpler than the exceptions: use `@` for")
print("      matrix multiplication and `np.dot` only for two plain vectors.")
print(f"      For two vectors, np.dot is exact and readable: np.dot([3,4],[4,3]) = "
      f"{np.dot([3, 4], [4, 3])}")

print()
print("=" * 74)
print("4. A shape error on purpose, and how to read it")
print("=" * 74)

print(f"  X is {npX.shape}. X @ X asks for ({npX.shape[0]}, {npX.shape[1]}) @ "
      f"({npX.shape[0]}, {npX.shape[1]}).")
print(f"  The inner dimensions are {npX.shape[1]} and {npX.shape[0]}, and they disagree.")
try:
    npX @ npX
except ValueError as exc:
    message = str(exc)
    print()
    print("  NumPy raises:")
    print(f"    {type(exc).__name__}: {message}")
    caught = type(exc)
else:  # pragma: no cover - only reached if NumPy changes its rules
    raise AssertionError("(2, 3) @ (2, 3) should have raised")

assert caught is ValueError
assert "size 2 is different from 3" in message
print()
print("  The first thing to check, always, is the two shapes and nothing else.")
print("  Print them before you read another word of the traceback:")
print(f"      left  {npX.shape}     right {npX.shape}")
print("      inner dimensions: 3 and 2 — that is the bug, and it is the whole bug.")

print()
print("=" * 74)
print("5. The transpose fixes it — but there are TWO fixes and they differ")
print("=" * 74)

left_fix = npX @ npX.T
right_fix = npX.T @ npX
print(f"  X @ X.T  is (2, 3) @ (3, 2) -> {left_fix.shape}")
print(f"      {left_fix.tolist()}")
print("      entry (i, j) is example i dotted with example j — a table of how")
print("      alike the two EXAMPLES are. Symmetric, as any such table must be.")
print(f"  X.T @ X  is (3, 2) @ (2, 3) -> {right_fix.shape}")
print(f"      {right_fix.tolist()}")
print("      entry (i, j) is feature i dotted with feature j — a table of how")
print("      alike the three FEATURES are. Also symmetric, and a different object.")
assert left_fix.tolist() == X_AT_XT
assert right_fix.tolist() == XT_AT_X
assert left_fix.shape == (2, 2)
assert right_fix.shape == (3, 3)
assert (left_fix == left_fix.T).all()
assert (right_fix == right_fix.T).all()
print()
print("  Both make the exception go away. Only one of them answers the question")
print("  you had. This is the reason 'just transpose it until it runs' is a bad")
print("  habit: the error was telling you something, and silencing it at random")
print("  swaps a loud failure for a quiet wrong answer.")

print()
print("=" * 74)
print("6. The full comparison table, checked")
print("=" * 74)
rows = [
    ("P * Q", (npP * npQ).shape, "entry by entry, nothing summed"),
    ("P @ Q", (npP @ npQ).shape, "rows dotted with columns"),
    ("X * u", star.shape, "u broadcast across rows, nothing summed"),
    ("X @ u", at.shape, "rows dotted with u, then summed"),
    ("X @ X", "ValueError", "inner dimensions 3 and 2 disagree"),
    ("X @ X.T", left_fix.shape, "example against example"),
    ("X.T @ X", right_fix.shape, "feature against feature"),
]
print(f"  {'expression':<10} {'result shape':<14} what it means")
for name, shp, meaning in rows:
    print(f"  {name:<10} {str(shp):<14} {meaning}")

print()
print("03_star_versus_at.py: every assertion held.")
