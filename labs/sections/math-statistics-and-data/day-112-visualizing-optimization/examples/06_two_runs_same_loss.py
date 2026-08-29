"""Script 6 -- the day's opening failure, made into a measurement.

Two runs, same starting point, same learning rate, same number of steps.
Their final losses agree to within a few percent. Their paths do not agree
at all: one is short and nearly straight, the other is over ten times
longer because it zig-zagged across a narrow valley. The final-loss number
alone cannot tell these runs apart -- only the path can.
"""

from dataset import (
    ILL_A,
    ILL_B,
    ILL_F,
    ILL_GRAD,
    LEARNING_RATE,
    LOSS_MATCH_TOL,
    PATH_LENGTH_RATIO_MIN,
    START,
    STEPS,
    WELL_A,
    WELL_B,
    WELL_F,
    WELL_GRAD,
)
from descent import gradient_descent, losses_along, path_length

well_path = gradient_descent(WELL_GRAD, START, LEARNING_RATE, STEPS)
ill_path = gradient_descent(ILL_GRAD, START, LEARNING_RATE, STEPS)

well_losses = losses_along(WELL_F, well_path)
ill_losses = losses_along(ILL_F, ill_path)

well_len = path_length(well_path)
ill_len = path_length(ill_path)

print(f"well-conditioned bowl: f(x, y) = {WELL_A:g} x^2 + {WELL_B:g} y^2")
print(f"ill-conditioned bowl:  f(x, y) = {ILL_A:g} x^2 + {ILL_B:g} y^2")
print(f"both start at {tuple(START)}, learning rate {LEARNING_RATE}, {STEPS} steps")
print()
print(f"well-conditioned final loss: {well_losses[-1]:.6e}")
print(f"ill-conditioned final loss:  {ill_losses[-1]:.6e}")
relative_gap = abs(well_losses[-1] - ill_losses[-1]) / max(well_losses[-1], ill_losses[-1])
print(f"relative gap between the two final losses: {relative_gap:.4f}")
print()
print(f"well-conditioned path length: {well_len:.4f}")
print(f"ill-conditioned path length:  {ill_len:.4f}")
print(f"ratio: {ill_len / well_len:.2f}x longer")

assert relative_gap < LOSS_MATCH_TOL, "the two final losses should be nearly indistinguishable"
assert ill_len / well_len > PATH_LENGTH_RATIO_MIN, "the paths should differ by a large factor"

print()
print(
    "A reader who only sees the two final-loss numbers above would call these runs "
    "equivalent. Only the path length -- or the picture -- shows that one of them "
    "spent most of its steps bouncing across the narrow axis instead of heading "
    "toward the minimum."
)
print()
print("06_two_runs_same_loss.py: every assertion held.")
