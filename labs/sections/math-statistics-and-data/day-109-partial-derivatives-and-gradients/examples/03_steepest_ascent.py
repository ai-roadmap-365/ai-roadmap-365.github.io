"""The gradient really is the steepest way up. Measured, not asserted.

Run from inside `examples/`:

    ../.venv/bin/python3 03_steepest_ascent.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import (
    angle_degrees,
    angular_gap_degrees,
    directional_derivative,
    directional_derivative_direct,
    gradient,
    magnitude,
    sweep_directions,
    unit,
)

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. A directional derivative, measured two ways that must agree")
# --------------------------------------------------------------------------
#
# "How fast does f change if I walk THIS way" is a question the partial
# derivatives do not directly answer, because they only know about the axes.
# There are two ways to answer it.
#
#   Directly: step h forward along the direction and h back along it, and
#   divide by 2h. That is Day 108's central difference with the step taken
#   along a diagonal rather than along an axis. It never forms a gradient.
#
#   Via the gradient: dot the gradient with the unit direction. That is Day
#   103's dot product, and it is not obvious that it should work.
#
# They agree. That agreement is the reason the gradient is worth assembling:
# two numbers, computed once, answer the question for every direction at once.

point = (1.0, 1.0)
g = gradient(S.bowl, point)
print(f"  f(x, y) = x^2 + 3y^2 at {point}, gradient about [{g[0]:.4f}, {g[1]:.4f}]")
print()
print(f"    {'direction':>16}  {'unit direction':>20}  {'via gradient':>15}  {'measured direct':>16}  {'gap':>10}")
directions = (
    (1.0, 0.0),
    (0.0, 1.0),
    (1.0, 1.0),
    (-1.0, 2.0),
    (3.0, -1.0),
    (-2.0, -5.0),
    (7.0, 0.5),
)
for d in directions:
    u = unit(np.array(d))
    via = directional_derivative(S.bowl, point, d)
    direct = directional_derivative_direct(S.bowl, point, d)
    shown_u = "[" + ", ".join(f"{v:8.5f}" for v in u) + "]"
    print(f"    {str(d):>16}  {shown_u:>20}  {via:15.9f}  {direct:16.9f}  {abs(via - direct):10.2e}")
    assert abs(via - direct) < S.GRADIENT_TOL

print()
print("  Look at the first two rows. Walking due east gives 2.0 and walking")
print("  due north gives 6.0 -- which are exactly the two partial derivatives.")
print("  A partial derivative is just the directional derivative along an axis.")
assert abs(directional_derivative(S.bowl, point, (1.0, 0.0)) - 2.0) < S.GRADIENT_TOL
assert abs(directional_derivative(S.bowl, point, (0.0, 1.0)) - 6.0) < S.GRADIENT_TOL

print()
print("  And note the last row: [7, 0.5] is a long arrow and [1, 0] is a short")
print("  one, but the answer depends only on the bearing, because both were")
print("  scaled to length 1 first.")
print()
print("  One row is worth stopping on. The direction (3, -1) gives a rate of")
print("  exactly zero, and it is not a coincidence: 3 times 2 plus -1 times 6")
print("  is 0, so that direction is perpendicular to the gradient. Walk that")
print("  way and, to first order, f does not change at all. Script 04 is about")
print("  what that means geometrically.")
assert abs(directional_derivative(S.bowl, point, (3.0, -1.0))) < S.GRADIENT_TOL

# --------------------------------------------------------------------------
print()
print("2. Try every direction and see which one wins")
# --------------------------------------------------------------------------
#
# The claim is that no direction climbs faster than the gradient's. So try
# them: 360 bearings evenly spaced around the circle, each one measured
# DIRECTLY with a central difference along that bearing, so the gradient is
# nowhere involved in producing the numbers being compared.

print(f"  {S.N_DIRECTIONS} directions, one per degree, measured directly.")
print()
print(f"  {'surface':>8}  {'point':>13}  {'best bearing':>13}  {'gradient bearing':>17}"
      f"  {'gap':>8}  {'best rate':>12}  {'|gradient|':>12}")

trials = (
    ("bowl", (1.0, 1.0)),
    ("bowl", (0.25, 0.75)),
    ("bowl", (3.0, -2.0)),
    ("product", (2.0, -1.0)),
    ("saddle", (1.5, 0.5)),
    ("cubic", (1.0, 1.0)),
    ("plane", (-2.0, 4.0)),
)
worst_gap = 0.0
for name, p in trials:
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    angles, rates = sweep_directions(f, p)
    best = int(np.argmax(rates))
    best_bearing = float(np.degrees(angles[best]))
    gradient_bearing = angle_degrees(exact_gradient(p))
    gap = angular_gap_degrees(best_bearing, gradient_bearing)
    worst_gap = max(worst_gap, gap)
    steepness = magnitude(exact_gradient(p))
    print(f"  {name:>8}  {str(p):>13}  {best_bearing:12.1f}d  {gradient_bearing:16.4f}d"
          f"  {gap:7.4f}d  {rates[best]:12.7f}  {steepness:12.7f}")
    assert gap <= S.ANGLE_TOL_DEGREES, (name, p, gap)
    # No direction may beat the gradient's own magnitude, ever.
    assert rates[best] <= steepness + S.GRADIENT_TOL

print()
print(f"  Worst gap across all {len(trials)} trials: {worst_gap:.4f} degrees,")
print(f"  against an asserted tolerance of {S.ANGLE_TOL_DEGREES} degree.")
print()
print("  The gap is not zero and cannot be. With one sample per degree, the")
print("  nearest sampled bearing to the true one is at most half a degree")
print("  away. The tolerance is that bound plus a little slack -- it is a")
print("  property of the sampling, not of the calculus.")

# --------------------------------------------------------------------------
print()
print("3. The winning rate is the gradient's LENGTH, and the shortfall is exactly cos(gap)")
# --------------------------------------------------------------------------
#
# Since the directional derivative is grad . u and both grad and u have fixed
# lengths, Day 103's geometric reading of the dot product applies unchanged:
#
#     grad . u = |grad| * |u| * cos(angle) = |grad| * cos(angle)
#
# So the best possible rate is |grad|, achieved when the angle is zero, and
# any other bearing gets |grad| times the cosine of how far off it is. That is
# not a rough statement; it is checkable to nine decimal places.

print(f"  {'surface':>8}  {'point':>13}  {'best rate / |grad|':>20}  {'cos(gap)':>18}  {'difference':>12}")
for name, p in trials:
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    angles, rates = sweep_directions(f, p)
    best = int(np.argmax(rates))
    gap = angular_gap_degrees(float(np.degrees(angles[best])),
                             angle_degrees(exact_gradient(p)))
    ratio = rates[best] / magnitude(exact_gradient(p))
    predicted = float(np.cos(np.radians(gap)))
    print(f"  {name:>8}  {str(p):>13}  {ratio:20.12f}  {predicted:18.12f}"
          f"  {abs(ratio - predicted):12.2e}")
    assert abs(ratio - predicted) < 1e-9

print()
print("  Five of the seven gaps above are the identical 0.4349 degrees, which")
print("  looks suspicious and is not. Those five gradients have bearings whose")
print("  fractional part is the same -- 26.5651, 71.5651, 116.5651, 296.5651,")
print("  341.5651 -- because they are all arctangents of ratios of the same")
print("  small whole numbers, separated by exact multiples of 45 degrees. A")
print("  grid sampled every whole degree therefore misses each of them by the")
print("  same amount. The two rows that break the pattern, at bearings 83.6598")
print("  and 326.3099, have different gaps. Pick a point with less tidy")
print("  coordinates and the gap changes again:")
for p in ((1.0, 0.4), (2.3, 1.7)):
    angles, rates = sweep_directions(S.bowl, p)
    best = int(np.argmax(rates))
    gap = angular_gap_degrees(float(np.degrees(angles[best])),
                             angle_degrees(S.bowl_gradient(p)))
    print(f"    bowl at {str(p):>12}: gradient bearing"
          f" {angle_degrees(S.bowl_gradient(p)):8.4f}d, gap {gap:.4f}d")
    assert gap <= S.ANGLE_TOL_DEGREES

# --------------------------------------------------------------------------
print()
print("4. The other end: the worst direction, and the two that go nowhere")
# --------------------------------------------------------------------------

p = (1.0, 1.0)
angles, rates = sweep_directions(S.bowl, p)
best = int(np.argmax(rates))
worst = int(np.argmin(rates))
flat = np.argsort(np.abs(rates))[:2]
steepness = magnitude(S.bowl_gradient(p))

print(f"  f(x, y) = x^2 + 3y^2 at {p}, |gradient| = {steepness:.7f}")
print(f"    steepest UP        bearing {np.degrees(angles[best]):6.1f}d"
      f"   rate {rates[best]:+12.7f}")
print(f"    steepest DOWN      bearing {np.degrees(angles[worst]):6.1f}d"
      f"   rate {rates[worst]:+12.7f}")
for i in sorted(flat):
    print(f"    no change at all   bearing {np.degrees(angles[i]):6.1f}d"
          f"   rate {rates[i]:+12.7f}")

print()
print("  The steepest descent is the exact opposite bearing, 180 degrees round,")
print("  and its rate is the negative of the steepest ascent. That symmetry is")
print("  the whole of Day 111 in one line: to go DOWN, step against the")
print("  gradient.")
opposite = angular_gap_degrees(float(np.degrees(angles[best])),
                               float(np.degrees(angles[worst])))
print(f"    angular separation of the two extremes: {opposite:.4f} degrees")
assert abs(opposite - 180.0) < 1e-9
assert abs(rates[best] + rates[worst]) < 1e-6

print()
print("  The two bearings where the rate is nearest zero are 90 degrees from")
print("  the gradient, one each way. Walking along either one keeps f the same")
print("  to first order -- which means they run along the contour. Script 04")
print("  makes that precise without going anywhere near this sweep.")
for i in flat:
    off = angular_gap_degrees(float(np.degrees(angles[i])),
                              angle_degrees(S.bowl_gradient(p)))
    assert abs(off - 90.0) <= S.ANGLE_TOL_DEGREES, off

print()
print("03_steepest_ascent.py: every assertion held.")
