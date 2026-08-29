"""Script 4 -- an animated GIF of a descent, one frame per step.

Pillow needs nothing beyond Image.save(..., save_all=True) to write an
animation: build one Image per frame and hand Pillow the list.
"""

import shutil
import tempfile
from pathlib import Path

from dataset import ILL_F, ILL_GRAD, LEARNING_RATE, START
from descent import gradient_descent
from gridviz import evaluate_grid
from imaging import animated_descent_gif
from PIL import Image

XLIM = (-4.0, 4.0)
YLIM = (-4.0, 4.0)
N_FRAMES = 25

_, _, Z = evaluate_grid(ILL_F, XLIM, YLIM, 101)
path = gradient_descent(ILL_GRAD, START, LEARNING_RATE, N_FRAMES)
print(f"path has {len(path)} points (start + {N_FRAMES} steps)")

tmp = Path(tempfile.mkdtemp(prefix="d112-"))
try:
    out = tmp / "descent.gif"
    animated_descent_gif(Z, XLIM, YLIM, path, str(out))
    size_bytes = out.stat().st_size
    print(f"descent.gif written: {size_bytes} bytes")

    reopened = Image.open(out)
    print(f"format={reopened.format}, size={reopened.size}, n_frames={reopened.n_frames}")
    assert reopened.format == "GIF"
    assert reopened.n_frames == len(path)

    print()
    print("04_animated_gif.py: every assertion held.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
