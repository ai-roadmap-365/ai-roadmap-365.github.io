"""Script 1 -- evaluate a surface over a grid, then look at it without an
image viewer.

Every picture later in this lab starts here: numpy.meshgrid plus a function
call, and a way to check that Z's rows and columns line up with X and Y the
way you think they do.
"""

import numpy as np

from dataset import WELL_F
from gridviz import ascii_contour, evaluate_grid

XLIM = (-4.0, 4.0)
YLIM = (-4.0, 4.0)
N = 101

X, Y, Z = evaluate_grid(WELL_F, XLIM, YLIM, N)
print(f"grid shape: X {X.shape}, Y {Y.shape}, Z {Z.shape}")
assert X.shape == Y.shape == Z.shape == (N, N)

iy, ix = np.unravel_index(np.argmin(Z), Z.shape)
print(f"minimum at grid cell (row={iy}, col={ix}) -> x={X[iy, ix]:.4f}, y={Y[iy, ix]:.4f}, f={Z[iy, ix]:.6g}")
assert abs(X[iy, ix]) < 1e-9 and abs(Y[iy, ix]) < 1e-9

_, _, small_Z = evaluate_grid(lambda x, y: x**2 + y**2, (-2, 2), (-2, 2), 5)
print()
print("ASCII contour of x^2 + y^2 on a 5x5 grid spanning [-2, 2] x [-2, 2]:")
print(ascii_contour(small_Z))
rows = ascii_contour(small_Z).split("\n")
assert rows[2][2] == " ", "the centre cell (the minimum) should be the lightest character"
assert rows[0][0] == "#", "a corner (the maximum) should be the densest character"

print()
print("01_grid_and_ascii.py: every assertion held.")
