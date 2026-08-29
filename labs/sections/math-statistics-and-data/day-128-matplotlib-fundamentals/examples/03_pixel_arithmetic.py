"""Exercise 3 -- pixel arithmetic.

savefig's output size in pixels is figsize (inches) times dpi -- exactly,
as long as bbox_inches='tight' is not used to trim the output afterward.
A 6x4 inch figure at 100 dpi is 600x400 pixels; doubling the dpi to 200
doubles both dimensions to 1200x800. This script proves both claims by
reading the saved PNG's own header, not by trusting the arithmetic.
"""

import os
import tempfile

import matplotlib.pyplot as plt

import plotting as P

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot([0, 1, 2, 3], [0, 1, 4, 9])
ax.set_xlabel("x")
ax.set_ylabel("y")

with tempfile.TemporaryDirectory(prefix="d128-") as d:
    p100 = os.path.join(d, "fig_100dpi.png")
    p200 = os.path.join(d, "fig_200dpi.png")
    p50 = os.path.join(d, "fig_50dpi.png")

    P.save_at_size_and_dpi(fig, p100, dpi=100)
    P.save_at_size_and_dpi(fig, p200, dpi=200)
    P.save_at_size_and_dpi(fig, p50, dpi=50)

    dims100 = P.png_dimensions(p100)
    dims200 = P.png_dimensions(p200)
    dims50 = P.png_dimensions(p50)

    print(f"figsize=(6, 4) inches, dpi=100  -> {dims100} pixels")
    print(f"figsize=(6, 4) inches, dpi=200  -> {dims200} pixels")
    print(f"figsize=(6, 4) inches, dpi=50   -> {dims50} pixels")

    assert dims100 == (600, 400), f"expected (600, 400) at 100dpi, got {dims100}"
    assert dims200 == (1200, 800), f"expected (1200, 800) at 200dpi, got {dims200}"
    assert dims50 == (300, 200), f"expected (300, 200) at 50dpi, got {dims50}"
    assert dims200 == (dims100[0] * 2, dims100[1] * 2), "doubling dpi should exactly double pixel dimensions"

plt.close(fig)
print("\n03_pixel_arithmetic.py: every assertion held.")
