"""Exercise 2 -- data round-trip.

ax.plot(x, y) does not transform the data before storing it on the Line2D
artist. ax.lines[0].get_xydata() should return exactly the arrays that
went in -- an exact equality check, not an approximate one, because nothing
about plotting a line involves floating-point recomputation of the points
themselves.
"""

import numpy as np

import plotting as P

x = np.array([0.0, 1.5, 3.0, 4.5, 7.25])
y = np.array([2.0, -1.0, 0.5, 7.25, -3.5])

fig, ax = P.make_line_axes(x, y)
xy = ax.lines[0].get_xydata()

print(f"input x  = {x}")
print(f"stored x = {xy[:, 0]}")
print(f"input y  = {y}")
print(f"stored y = {xy[:, 1]}")

assert np.array_equal(xy[:, 0], x), "x did not round-trip exactly"
assert np.array_equal(xy[:, 1], y), "y did not round-trip exactly"

print("\n02_data_round_trip.py: every assertion held.")
