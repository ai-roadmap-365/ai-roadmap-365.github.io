"""Script 5 -- final loss against learning rate: the characteristic shape.

Slow on the left, a broad basin of good learning rates, then a cliff where
the run diverges. A good learning rate is a RANGE, and this script measures
that range rather than asserting it.
"""

import numpy as np

from dataset import SWEEP_STEPS, SWEEP_X0, sweep_f, sweep_grad
from descent import learning_rate_sweep

etas = np.round(np.arange(0.05, 2.55, 0.10), 2)
sweep = learning_rate_sweep(sweep_grad, sweep_f, SWEEP_X0, etas, SWEEP_STEPS)

print(f"{'eta':>6}  {'final loss':>14}")
for eta, loss in sweep:
    shown = "inf (diverged)" if not np.isfinite(loss) else f"{loss:.6e}"
    print(f"{eta:>6.2f}  {shown:>14}")

finite = [(e, loss) for e, loss in sweep if np.isfinite(loss)]
divergent = [(e, loss) for e, loss in sweep if not np.isfinite(loss)]

good = [e for e, loss in finite if loss < 1e-6]
best_eta = min(finite, key=lambda pair: pair[1])[0]
# Above eta = 1, |1 - 2 eta| > 1 and the run blows up exponentially -- these
# etas do NOT converge, they simply have not yet overflowed float64 in the
# number of steps this sweep runs. "Finite but huge" is not "good".
still_overflowing_soon = max(e for e, loss in finite if loss >= 1e-6)
first_divergent_eta = min(e for e, _ in divergent)

print()
print(f"{len(good)} learning rates reach essentially zero loss: {good}")
print(f"argmin at eta = {best_eta}")
print(
    f"largest eta whose blow-up has not yet overflowed float64 in {SWEEP_STEPS} steps: "
    f"{still_overflowing_soon} (already diverging, just not yet inf)"
)
print(f"smallest eta whose blow-up has overflowed to inf (caught, not an exception): {first_divergent_eta}")

assert len(good) >= 3, "the good range is a basin, not a single point"
assert etas[0] < best_eta < etas[-1], "the argmin must be interior to the sweep"
assert len(divergent) >= 1
assert all(loss == float("inf") for _, loss in divergent)
assert all(e > 1.0 for e, _ in divergent), "the theoretical threshold for f(x) = x^2 is eta = 1"

print()
print("05_learning_rate_sweep.py: every assertion held.")
