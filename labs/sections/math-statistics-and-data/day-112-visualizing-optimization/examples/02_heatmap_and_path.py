"""Script 2 -- a Pillow heatmap, and a descent path drawn on top of it.

Writes into a temporary directory and removes it before exiting: this lab
leaves no image files behind, on purpose, so that "did the lab clean up"
is a check you can actually run rather than a claim you have to trust.
"""

import shutil
import tempfile
from pathlib import Path

from dataset import ILL_F, ILL_GRAD, LEARNING_RATE, START, STEPS
from descent import gradient_descent
from gridviz import evaluate_grid, world_to_pixel
from imaging import draw_path_on_heatmap, heatmap_png
from PIL import Image

XLIM = (-4.0, 4.0)
YLIM = (-4.0, 4.0)

_, _, Z = evaluate_grid(ILL_F, XLIM, YLIM, 101)

tmp = Path(tempfile.mkdtemp(prefix="d112-"))
try:
    heat_path = tmp / "heatmap.png"
    heatmap_png(Z, XLIM, YLIM, str(heat_path))
    img = Image.open(heat_path)
    print(f"heatmap.png: size={img.size}, mode={img.mode}")
    assert img.size == (101, 101)

    px, py = world_to_pixel(0.0, 0.0, XLIM, YLIM, 101, 101)
    center_color = img.convert("RGB").getpixel((round(px), round(py)))
    print(f"pixel at the minimum (0, 0) -> ({round(px)}, {round(py)}): color {center_color}")
    assert center_color == (13, 27, 84), "the minimum should be the ramp's lowest-value color"

    path = gradient_descent(ILL_GRAD, START, LEARNING_RATE, STEPS)
    path_out = tmp / "descent.png"
    draw_path_on_heatmap(Z, XLIM, YLIM, path, str(path_out))
    print(f"descent.png: {len(path)} points drawn over the ill-conditioned bowl")

    start_px = world_to_pixel(*path[0], XLIM, YLIM, 101, 101)
    end_px = world_to_pixel(*path[-1], XLIM, YLIM, 101, 101)
    min_px = world_to_pixel(0.0, 0.0, XLIM, YLIM, 101, 101)
    print(f"first marker pixel: {tuple(round(v, 2) for v in start_px)}")
    print(f"last marker pixel:  {tuple(round(v, 2) for v in end_px)}")
    print(f"minimum pixel:      {tuple(round(v, 2) for v in min_px)}")

    distance = ((end_px[0] - min_px[0]) ** 2 + (end_px[1] - min_px[1]) ** 2) ** 0.5
    print(f"distance from the last marker to the minimum: {distance:.3f} pixels")
    assert distance < 5.0

    print()
    print("02_heatmap_and_path.py: every assertion held.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
