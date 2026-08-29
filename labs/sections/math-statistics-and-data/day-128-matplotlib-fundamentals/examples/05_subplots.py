"""Exercise 5 -- subplots.

plt.subplots(nrows, ncols) with either dimension greater than 1 returns a
genuine 2-D numpy array of Axes objects, shaped exactly (nrows, ncols).
Each entry is its own object with its own state: labelling one Axes must
leave every other Axes in the grid untouched.
"""

import matplotlib.pyplot as plt
import numpy as np

import plotting as P

fig, axes = P.make_grid(2, 3)
print(f"type(axes) = {type(axes).__name__}")
print(f"axes.shape = {axes.shape}")

assert isinstance(axes, np.ndarray), f"expected a numpy array, got {type(axes)}"
assert axes.shape == (2, 3), f"expected shape (2, 3), got {axes.shape}"

axes[0, 0].set_xlabel("only axes[0, 0]")
axes[1, 2].set_title("only axes[1, 2]")

labels = {(r, c): axes[r, c].get_xlabel() for r in range(2) for c in range(3)}
titles = {(r, c): axes[r, c].get_title() for r in range(2) for c in range(3)}
print(f"xlabels across the grid: {labels}")
print(f"titles across the grid:  {titles}")

for r in range(2):
    for c in range(3):
        if (r, c) != (0, 0):
            assert axes[r, c].get_xlabel() == "", f"axes[{r},{c}] picked up a label it was never given"
        if (r, c) != (1, 2):
            assert axes[r, c].get_title() == "", f"axes[{r},{c}] picked up a title it was never given"

assert axes[0, 0].get_xlabel() == "only axes[0, 0]"
assert axes[1, 2].get_title() == "only axes[1, 2]"

plt.close(fig)
print("\n05_subplots.py: every assertion held.")
