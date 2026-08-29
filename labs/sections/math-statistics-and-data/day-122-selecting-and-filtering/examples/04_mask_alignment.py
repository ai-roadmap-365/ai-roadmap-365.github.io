"""Exercise 4 -- a mask is a Series with an index, so filtering aligns.

Run: python3 04_mask_alignment.py

A boolean mask is not a bare array of True/False; it is a Series, with an
index of its own. When you write df[mask], pandas does not walk df and mask
in lockstep -- it looks up each of df's row labels in mask's index and uses
whatever boolean sits at that LABEL, regardless of the physical order mask
happens to be stored in. Build a mask from a reordered copy of a frame,
apply it to the original, and the result is still correct, in the
original's own row order -- because alignment is by label. Convert that
same mask to a raw NumPy array first, and the label information is gone:
applying it now walks POSITION by position, and silently returns the wrong
rows, because df's own row order does not match the order the mask array
was built in.
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
    },
    index=[10, 11, 12, 13, 14, 15, 16, 17],
)
print("scores (in original row order):")
print(scores)

# The correct rows, computed directly, for comparison.
expected = scores[scores.score > 60]
print(f"\nexpected rows (score > 60), computed directly: {expected.index.tolist()}")

# Build the SAME mask from a differently-ordered copy of the frame.
reordered = scores.sort_values("score", ascending=False)
print(f"\na reordered copy's row order: {reordered.index.tolist()}")
mask_from_reordered = reordered["score"] > 60
print(f"mask, stored in the reordered copy's own order: {list(zip(mask_from_reordered.index.tolist(), mask_from_reordered.tolist()))}")

aligned_result = scores[mask_from_reordered]
print(f"\nscores[mask_from_reordered] index: {aligned_result.index.tolist()}  (label-aligned)")

check(
    "a mask built from a reordered copy, applied by LABEL, still returns the correct rows",
    aligned_result.index.tolist() == expected.index.tolist(),
)
check(
    "the aligned result is identical to computing the mask directly on scores",
    aligned_result.equals(expected),
)
check(
    "the aligned result comes back in SCORES' own row order, not the mask's storage order",
    aligned_result.index.tolist() == sorted(aligned_result.index.tolist()),
)

# Now strip the labels with .to_numpy() and apply the SAME boolean values
# positionally. This is the silent disaster: the values are identical, but
# with the index gone, pandas has nothing left to align on.
positional_array = mask_from_reordered.to_numpy()
positional_result = scores[positional_array]
print(f"\nscores[mask_from_reordered.to_numpy()] index: {positional_result.index.tolist()}  (POSITIONAL, wrong)")

check(
    "applying the same booleans positionally (via .to_numpy()) gives a DIFFERENT set of rows",
    positional_result.index.tolist() != aligned_result.index.tolist(),
)
check(
    "the positional result is wrong: it does not match scores where score > 60",
    not positional_result.equals(expected),
)
check(
    "the positional result picked rows 10, 11, 12 -- the reordered copy's first three POSITIONS, not the correct labels",
    positional_result.index.tolist() == [10, 11, 12],
)

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("04_mask_alignment.py: every assertion held.")
