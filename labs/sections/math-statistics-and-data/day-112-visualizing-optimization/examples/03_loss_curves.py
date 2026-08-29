"""Script 3 -- loss against iteration, linear and log, and why the log axis
is not decoration.

For a run where the update is an exact geometric recursion (the
well-conditioned bowl below), loss_k = c * rho^k, so log10(loss_k) is a
straight line in k with slope log10(rho). This script draws both curves and
then proves the log one is a line by fitting it and reading off the residual
-- from the picture's own pixel coordinates, not from the formula.
"""

import shutil
import tempfile
from pathlib import Path

import numpy as np

from dataset import LEARNING_RATE, START, STEPS, WELL_F, WELL_GRAD
from descent import gradient_descent, losses_along
from imaging import loss_curve_png, loss_curve_points

path = gradient_descent(WELL_GRAD, START, LEARNING_RATE, STEPS)
losses = losses_along(WELL_F, path)

print(f"loss at step 0:  {losses[0]:.6g}")
print(f"loss at step {STEPS}: {losses[-1]:.6g}")
print(f"ratio of consecutive losses (should be ~constant for a straight log line):")
ratios = losses[1:11] / losses[0:10]
for k, r in enumerate(ratios):
    print(f"  loss[{k+1}] / loss[{k}] = {r:.6f}")
assert np.max(ratios) - np.min(ratios) < 1e-9, "a geometric decay has a constant ratio"

tmp = Path(tempfile.mkdtemp(prefix="d112-"))
try:
    lin_path = tmp / "loss_linear.png"
    log_path = tmp / "loss_log.png"
    loss_curve_png(losses, str(lin_path), log=False)
    loss_curve_png(losses, str(log_path), log=True)
    print(f"\nloss_linear.png and loss_log.png written and read back successfully")

    points = loss_curve_points(losses, width=500, height=350, margin=50, log=True)
    xs = np.array([p[0] for p in points])
    ys = np.array([p[1] for p in points])
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    residual = np.max(np.abs(ys - (slope * xs + intercept)))
    print(f"log-axis points: best-fit line residual (max, in pixels) = {residual:.3e}")
    assert residual < 1e-6

    print()
    print("03_loss_curves.py: every assertion held.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
