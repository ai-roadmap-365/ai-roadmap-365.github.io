"""Exercise 9 -- vector versus raster, made testable.

An SVG is markup: text elements are literal <text> tags, so the axis label
appears in the file as searchable characters. A PNG is pixels: the same
label is rendered into a grid of colour values, and the string that
produced it does not appear anywhere in the file's bytes. This is the
entire argument for shipping SVG or PDF instead of PNG for anything that
will be printed, zoomed, or edited later -- made into two assertions
instead of a claim to take on faith.
"""

import os
import tempfile

import matplotlib.pyplot as plt

import plotting as P

fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3], [10, 15, 13, 18])
ax.set_xlabel("depth (m)")
ax.set_title("Sensor reading by depth")

with tempfile.TemporaryDirectory(prefix="d128-") as d:
    png_path = os.path.join(d, "reading.png")
    svg_path = os.path.join(d, "reading.svg")
    P.save_png_and_svg(fig, png_path, svg_path)

    svg_text = open(svg_path, encoding="utf-8").read()
    png_bytes = open(png_path, "rb").read()

    svg_has_label = "depth (m)" in svg_text
    png_has_label = b"depth (m)" in png_bytes

    print(f"SVG file size: {len(svg_text):,} characters")
    print(f"PNG file size: {len(png_bytes):,} bytes")
    print(f"'depth (m)' found as text inside the SVG: {svg_has_label}")
    print(f"b'depth (m)' found as bytes inside the PNG: {png_has_label}")

    assert svg_has_label, "expected the axis label to appear as text in the SVG"
    assert not png_has_label, "the axis label should not appear as raw bytes in the PNG"

plt.close(fig)
print("\n09_vector_versus_raster.py: every assertion held.")
