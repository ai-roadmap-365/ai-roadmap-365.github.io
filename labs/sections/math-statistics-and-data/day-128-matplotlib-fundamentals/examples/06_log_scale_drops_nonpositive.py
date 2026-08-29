"""Exercise 6 -- log scale silently drops non-positive data.

set_yscale('log') on data containing a zero does not raise. It also does
not warn, in this version, when at least one value in the series is
positive -- matplotlib only emits its "Data has no positive values, and
therefore cannot be log-scaled" warning when EVERY value is non-positive.
What actually happens with a mix, measured here on matplotlib 3.11.1: the
rendered y-limits are silently narrowed to exclude the non-positive point,
while the underlying line data is untouched. The zero-valued point is
still in ax.lines[0].get_xydata() -- it simply never gets drawn, because
log(0) has no y-pixel to draw it at.
"""

import matplotlib.pyplot as plt

import plotting as P

x = [0, 1, 2, 3, 4]
y = [0, 1, 4, 9, 16]

fig, ax = P.plot_with_log_yscale(x, y)

yscale = ax.get_yscale()
ymin, ymax = ax.get_ylim()
xy = ax.lines[0].get_xydata()

print(f"y data plotted: {y}")
print(f"ax.get_yscale() = {yscale!r}")
print(f"ax.get_ylim()   = ({ymin:.4f}, {ymax:.4f})")
print(f"stored data still contains the zero point: {xy[0].tolist()}")
print(
    "the y=0 point is present in the data but excluded from the visible"
    " range -- it renders as nothing, with no error and no visible gap"
    " marker, which is exactly what makes this easy to miss in a report."
)

assert yscale == "log", f"expected yscale 'log', got {yscale!r}"
assert ymin > 0, f"expected the log axis's lower limit to be > 0, got {ymin}"
assert xy[0, 1] == 0, "the original data should still contain the y=0 point"

plt.close(fig)
print("\n06_log_scale_drops_nonpositive.py: every assertion held.")
