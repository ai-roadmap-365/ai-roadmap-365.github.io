"""Exercise 4 — broadcasting: the rule, a success, a failure, and a trap.

Run from the lab directory:

    .venv/bin/python3 examples/04_broadcasting.py

Broadcasting is where NumPy stops being obvious. Up to here, every operation
did the boring thing. Broadcasting invents entries that were never written
down, and it does so silently, which makes it the single most productive
source of results that are wrong without being errors.

The rule, from the NumPy documentation, applied right to left:

    1. Line the two shapes up from the RIGHT-hand end.
    2. A missing entry on the left of the shorter shape counts as 1.
    3. Two dimensions are compatible when they are equal, or one of them is 1.
    4. If any pair is neither, the operation is a ValueError.
    5. The result takes the larger of each pair.

Nothing is copied. The stretching is a fiction maintained by walking the
smaller array's memory more than once.
"""

import numpy as np

from dataset import PRICE_PER_LITRE, RECIPES

TOL = 1e-12


def L(a):
    """Render a numpy array as a plain Python list, with no dtype noise."""
    return np.asarray(a).tolist()


def rule(title):
    print()
    print(title)
    print("-" * len(title))


def align(a, b):
    """Print the right-aligned shape comparison the rule actually describes."""
    width = max(len(a), len(b))
    pad = lambda s: (1,) * (width - len(s)) + s  # noqa: E731 - a local, read once
    top, bottom = pad(a), pad(b)
    ok = all(x == y or x == 1 or y == 1 for x, y in zip(top, bottom))
    result = tuple(max(x, y) for x, y in zip(top, bottom)) if ok else None
    print(f"    {str(a):>12}   padded to {top}")
    print(f"    {str(b):>12}   padded to {bottom}")
    print(f"    -> {'result ' + str(result) if ok else 'INCOMPATIBLE'}")
    return result


M = np.array(RECIPES)
prices = np.array(PRICE_PER_LITRE)

rule("4a. The simplest case: an array and one number")
print(f"  M * 2 has shape {(M * 2).shape}; the 2 is treated as (1, 1)")
print(M * 2)
assert np.array_equal(M * 2, M + M)

rule("4b. (3, 4) with (4,) — this succeeds, and here is why")
align((3, 4), (4,))
print()
print(f"  M       shape {M.shape}:\n{M}")
print(f"  prices  shape {prices.shape}: {L(prices)}")
scaled = M * prices
print(f"  M * prices shape {scaled.shape}:\n{scaled}")
print()
print("  Read row by row: the price vector was applied to EVERY row, because")
print("  the rows are the axis that had to stretch. Row 0 became")
print(f"  {L(M[0])} * {L(prices)} = {L(scaled[0])}.")
assert scaled.shape == (3, 4)
assert list(scaled[0]) == [20, 8, 5, 3]
assert list(scaled[1]) == [0, 10, 10, 7]
assert list(scaled[2]) == [60, 2, 20, 2]
print()
print("  And nothing was copied. numpy.broadcast_to shows the fiction directly:")
stretched = np.broadcast_to(prices, (3, 4))
print(stretched)
print(f"  shares memory with prices: {np.shares_memory(stretched, prices)}")
print(f"  writeable: {stretched.flags.writeable}  (it has to be read-only —")
print("  one write would appear in three places at once)")
assert np.shares_memory(stretched, prices)
assert stretched.flags.writeable is False

rule("4c. (3, 4) with (3,) — this fails, and the rule predicted it")
align((3, 4), (3,))
print()
per_mix = np.array([100, 200, 300])
failure = None
try:
    M + per_mix
except ValueError as exc:
    failure = exc
print(f"  M + numpy.array({L(per_mix)}) raises")
print(f"    {type(failure).__name__}: {failure}")
assert isinstance(failure, ValueError)
assert "could not be broadcast together" in str(failure)
print()
print("  There is nothing special about 3 versus 4 here. The trailing")
print("  dimensions were 4 and 3, neither equal nor 1, so the rule stopped.")
print("  The fix is to say which axis you meant:")
column = per_mix.reshape(3, 1)
align((3, 4), (3, 1))
print(f"  per_mix.reshape(3, 1) has shape {column.shape}, and M + it works:")
print(M + column)
assert (M + column).shape == (3, 4)
assert list((M + column)[0]) == [102, 104, 101, 103]
assert list((M + column)[2]) == [306, 301, 304, 302]

rule("4d. The trap: a square matrix, where the wrong answer is not an error")
S = np.array(
    [
        [1.0, 2.0, 3.0, 4.0],
        [10.0, 20.0, 30.0, 40.0],
        [100.0, 200.0, 300.0, 400.0],
        [1000.0, 2000.0, 3000.0, 4000.0],
    ]
)
print("  A (4, 4) matrix. Say you want to centre each ROW on its own mean —")
print("  a completely ordinary preprocessing step.")
row_means = S.mean(axis=1)
print(f"  row means, shape {row_means.shape}: {L(row_means)}")
wrong = S - row_means
right = S - S.mean(axis=1, keepdims=True)
print()
print(f"  S - row_means            (shape {wrong.shape}) — no error, no warning:")
print(wrong)
print(f"  S - S.mean(axis=1, keepdims=True) (shape {right.shape}) — what you meant:")
print(right)
print()
print("  The first one subtracted row 0's mean from COLUMN 0, row 1's mean from")
print("  column 1, and so on, because a (4,) lines up against the last axis and")
print("  the last axis is columns. It is a transposed answer wearing the right")
print("  shape. On a non-square matrix it would have been a ValueError and you")
print("  would have found out in one second.")
assert not np.allclose(wrong, right, atol=TOL)
# The correct centring makes every row sum to zero. The wrong one does not.
assert np.allclose(right.sum(axis=1), np.zeros(4), atol=1e-9)
assert not np.allclose(wrong.sum(axis=1), np.zeros(4), atol=1e-9)
print("  The check that catches it: after centring rows, every ROW must sum to 0.")
print(f"    right.sum(axis=1) = {L(right.sum(axis=1))}")
print(f"    wrong.sum(axis=1) = {L(wrong.sum(axis=1))}")

rule("4e. keepdims is the habit that prevents the whole family of bugs")
print(f"  S.mean(axis=1).shape                 = {S.mean(axis=1).shape}")
print(f"  S.mean(axis=1, keepdims=True).shape  = {S.mean(axis=1, keepdims=True).shape}")
print(f"  S.mean(axis=0, keepdims=True).shape  = {S.mean(axis=0, keepdims=True).shape}")
print("  keepdims=True leaves a 1 where the axis was, so the result still says")
print("  out loud which axis it came from, and broadcasting lines it up the way")
print("  you intended instead of the way the padding rule happened to choose.")
assert S.mean(axis=1, keepdims=True).shape == (4, 1)
assert S.mean(axis=0, keepdims=True).shape == (1, 4)

rule("4f. The outer-product surprise: (3, 1) with (1, 4)")
a = np.array([1, 2, 3]).reshape(3, 1)
b = np.array([10, 20, 30, 40]).reshape(1, 4)
align((3, 1), (1, 4))
print(f"  a * b has shape {(a * b).shape} — twelve entries from seven numbers:")
print(a * b)
print("  Both sides stretched. If you expected a length-3 or length-4 answer,")
print("  the size of the output is the first thing that tells you otherwise.")
assert (a * b).shape == (3, 4)
assert list((a * b)[2]) == [30, 60, 90, 120]

rule("4g. How to check your shapes before you trust the numbers")
print("  numpy.broadcast_shapes answers the question without doing the work:")
print(f"    broadcast_shapes((3, 4), (4,))    = {np.broadcast_shapes((3, 4), (4,))}")
print(f"    broadcast_shapes((3, 4), (3, 1))  = {np.broadcast_shapes((3, 4), (3, 1))}")
predicted = None
try:
    np.broadcast_shapes((3, 4), (3,))
except ValueError as exc:
    predicted = str(exc)
print(f"    broadcast_shapes((3, 4), (3,))    raises ValueError: {predicted}")
assert np.broadcast_shapes((3, 4), (4,)) == (3, 4)
assert predicted is not None
print("  Print .shape at every step you are unsure about. It costs one line and")
print("  it is the only debugging tool that works before the numbers are wrong.")

print()
print("04_broadcasting.py: every assertion held.")
