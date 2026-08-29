"""Constant gradients, bowl gradients, and the three faces of a zero gradient.

Run from inside `examples/`:

    ../.venv/bin/python3 05_flat_ground_three_ways.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import angle_degrees, gradient, magnitude, unit

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. A plane: the same gradient everywhere, however far you walk")
# --------------------------------------------------------------------------
#
# f(x, y) = 3x - 2y + 5 is a flat tilted sheet. Its partial derivatives are 3
# and -2, and neither one mentions x or y, so the gradient is the constant
# vector [3, -2]. A tilted sheet has one slope and one uphill direction and
# they are the same at every point on it -- which is why a linear model has
# nothing to optimise: there is no bottom to fall into.

print("  f(x, y) = 3x - 2y + 5,  grad f = (3, -2) everywhere")
print()
print(f"  {'point':>18}  {'f':>12}  {'gradient':>22}  {'|gradient|':>12}  {'bearing':>10}")
seen = []
for p in ((0.0, 0.0), (1.0, 1.0), (-40.0, 17.5), (0.001, 0.002)):
    g = gradient(S.plane, p)
    seen.append(g)
    shown = "[" + ", ".join(f"{v:9.6f}" for v in g) + "]"
    print(f"  {str(p):>18}  {S.plane(p):12.4f}  {shown:>22}  {magnitude(g):12.7f}"
          f"  {angle_degrees(g):9.3f}d")
    assert abs(g[0] - 3.0) < S.GRADIENT_TOL
    assert abs(g[1] + 2.0) < S.GRADIENT_TOL

spread = float(np.max(np.abs(np.array(seen) - np.array(seen[0]))))
print()
print(f"  Largest disagreement between any two of those gradients: {spread:.3e}")
print("  -- which is floating-point noise, not variation. The value of f")
print("  swings from +6 to -150 across those points; the gradient does not")
print("  change at all.")
assert spread < S.GRADIENT_TOL

# --------------------------------------------------------------------------
print()
print("1b. Where that stops being measurable, and exactly why")
# --------------------------------------------------------------------------
#
# This section was not planned. It was found by putting (1000, -1000) in the
# table above and watching the assertion fail, and it is kept because it is
# more useful than the tidy version would have been.
#
# The gradient of a plane is constant, so a numerical estimate ought to be
# equally good anywhere. It is not. The central difference computes
#
#     ( f(x+h) - f(x-h) ) / 2h
#
# and the two values of f are stored with a relative error of about one
# machine epsilon EACH. At (1000, -1000) the function is worth about 5005, so
# each stored value carries an absolute error of roughly 5005 * 2.2e-16, and
# the subtraction keeps that error while the division by 2h = 2e-5 multiplies
# it by fifty thousand. Predicted noise: eps * |f| / (2h).
#
# That is not an approximation of the trouble; it is the trouble, and the
# prediction can be checked.

eps = float(np.finfo(float).eps)
print("  The same constant gradient, measured further and further from the origin:")
print()
print(f"  {'point':>26}  {'|f|':>13}  {'measured df/dx':>16}  {'error':>11}  {'eps|f|/2h':>11}")
for p in ((1.0, 1.0), (-40.0, 17.5), (1000.0, -1000.0),
          (100000.0, -100000.0), (10000000.0, -10000000.0)):
    g = gradient(S.plane, p)
    error = float(np.max(np.abs(g - np.array([3.0, -2.0]))))
    predicted = eps * abs(S.plane(p)) / (2.0 * S.H_DEFAULT)
    print(f"  {str(p):>26}  {abs(S.plane(p)):13.1f}  {g[0]:16.10f}  {error:11.3e}"
          f"  {predicted:11.3e}")
    # The prediction is a bound with a small constant, not an identity: the
    # measured error must be of the same order, never wildly above it.
    assert error < 3.0 * predicted + 1e-12, (p, error, predicted)

print()
print("  The last two columns track each other across seven orders of")
print("  magnitude. By ten million the estimate of a gradient that is exactly")
print("  3 has lost its fourth decimal place, and nothing about the calculus")
print("  went wrong -- only the arithmetic.")
print()
print("  This is the boundary on everything else in the lab. The tolerance of")
print(f"  {S.GRADIENT_TOL:g} that every other assertion uses is only achievable because every")
print("  probe point in `surfaces.py` keeps |f| small. Feed a numerical")
print("  gradient a loss of a hundred thousand and it will hand you a")
print("  confident answer with four good digits in it. Autodiff, which")
print("  differentiates the expression rather than sampling it, does not have")
print("  this failure mode at all -- which is the first of the two reasons")
print("  nobody trains a model this way.")

# --------------------------------------------------------------------------
print()
print("2. A bowl: the gradient points AWAY from the minimum, and grows with distance")
# --------------------------------------------------------------------------
#
# f(x, y) = x^2 + 3y^2 has its minimum at the origin. The gradient points
# uphill, and uphill from anywhere on a bowl is away from the bottom. Two
# consequences that Day 111 depends on: the NEGATIVE gradient always points
# roughly back towards the minimum, and it gets shorter as you approach, so
# the steps naturally shrink near the answer.

print(f"  {'point':>16}  {'distance from origin':>21}  {'gradient':>22}"
      f"  {'|gradient|':>12}  {'points away?':>13}")
for p in ((0.5, 0.5), (1.0, 1.0), (2.0, 2.0), (4.0, 4.0), (-3.0, 1.0)):
    q = np.array(p)
    g = gradient(S.bowl, p)
    outward = float(np.dot(unit(g), unit(q)))   # positive means "away from origin"
    shown = "[" + ", ".join(f"{v:9.5f}" for v in g) + "]"
    print(f"  {str(p):>16}  {magnitude(q):21.6f}  {shown:>22}  {magnitude(g):12.6f}"
          f"  {'yes' if outward > 0 else 'no':>13}")
    assert outward > 0.0

print()
print("  Every row points away from the bottom, and the length grows with")
print("  distance. Walk against it and you head back down -- which is the")
print("  entire algorithm of Day 111, and the reason the steps get smaller by")
print("  themselves as the answer gets closer.")

print()
print("  It is not, however, aimed exactly at the origin, because the bowl is")
print("  elliptical. Compare the gradient's bearing with the bearing straight")
print("  back to the minimum:")
print(f"    {'point':>16}  {'bearing of -gradient':>21}  {'bearing to origin':>19}  {'off by':>9}")
for p in ((1.0, 1.0), (3.0, 0.5), (0.5, 3.0)):
    g = gradient(S.bowl, p)
    back = angle_degrees(-g)
    straight = angle_degrees(-np.array(p))
    print(f"    {str(p):>16}  {back:20.3f}d  {straight:18.3f}d  {abs(back - straight):8.3f}d")

print()
print("  On a circular bowl those two would agree exactly. On this one they do")
print("  not, and that mismatch is precisely what makes gradient descent")
print("  zig-zag down a narrow valley instead of walking straight in.")

# --------------------------------------------------------------------------
print()
print("3. Zero gradient, three completely different points")
# --------------------------------------------------------------------------
#
# All three surfaces have gradient [0, 0] at the origin. The gradient is
# identical. The points are not. This is the honest limit of everything the
# day has built: a zero gradient tells you the ground is level, and stops.

print("  Walk 0.1 in eight directions from the origin and record what f does:")
print()
radius = 0.1
bearings = np.arange(0, 360, 45)
print(f"    {'surface':>9}  " + "  ".join(f"{b:>7}d" for b in bearings) + "   verdict")
for name, kind, why in S.STATIONARY_AT_ORIGIN:
    f = S.SURFACES[name][0]
    g = gradient(f, (0.0, 0.0))
    assert magnitude(g) < S.GRADIENT_TOL
    changes = []
    for b in bearings:
        a = np.radians(float(b))
        step = radius * np.array([np.cos(a), np.sin(a)])
        changes.append(f(step) - f(np.array([0.0, 0.0])))
    row = "  ".join(f"{c:+8.4f}" for c in changes)
    up = sum(1 for c in changes if c > 1e-12)
    down = sum(1 for c in changes if c < -1e-12)
    if down == 0:
        verdict = "all up -- a minimum"
    elif up == 0:
        verdict = "all down -- a maximum"
    else:
        level = len(changes) - up - down
        verdict = f"{up} up, {down} down, {level} flat -- a saddle"
    print(f"    {name:>9}  {row}   {verdict}")
    assert kind in verdict

print()
print("  The saddle's four flat entries are not rounding: on x^2 - y^2 the")
print("  diagonals are exactly where x^2 equals y^2, so f is unchanged along")
print("  them. They are the two contour lines that cross AT the saddle, which")
print("  is what makes a saddle a saddle.")
print()
print("  Same gradient. Three different answers. Nothing in the gradient")
print("  distinguishes them, and no amount of care computing it would help,")
print("  because the information simply is not in there: the gradient is built")
print("  from FIRST derivatives, and which kind of stationary point this is")
print("  depends on the SECOND ones. That object has a name -- the Hessian --")
print("  and this course does not develop it here.")

# --------------------------------------------------------------------------
print()
print("4. Why the saddle is the one that matters")
# --------------------------------------------------------------------------
#
# In two dimensions a saddle is a curiosity. In the parameter space of a
# model, where there are millions of directions rather than two, a point where
# every partial derivative is zero is overwhelmingly more likely to be a
# saddle than a true minimum -- because being a minimum requires the surface
# to curve upward in EVERY one of those millions of directions at once, and
# being a saddle only requires one direction to disagree.

print("  On f(x, y) = x^2 - y^2 the origin is level, and the two axes disagree:")
for label, direction in (("along x", (1.0, 0.0)), ("along y", (0.0, 1.0))):
    for r in (0.1, 0.5, 1.0):
        step = r * np.array(direction)
        print(f"    {label}, distance {r:>4}:  f = {S.saddle(step):+8.4f}")
    print()

print("  Walking east from the origin, f rises. Walking north, it falls. The")
print("  gradient at the origin is zero in both cases, and an optimiser that")
print("  stops when the gradient is zero would stop right there, in a place it")
print("  could have escaped by moving a millimetre north.")
assert S.saddle((0.5, 0.0)) > 0
assert S.saddle((0.0, 0.5)) < 0
assert magnitude(gradient(S.saddle, (0.0, 0.0))) < S.GRADIENT_TOL

print()
print("  And the gradient near the saddle is small without being zero, which")
print("  is the practical problem: progress crawls rather than stopping,")
print("  and it is hard to tell the two apart from the outside.")
print(f"    {'distance from the saddle':>26}  {'|gradient|':>12}")
for r in (1.0, 0.1, 0.01, 0.001):
    p = (r, r)
    print(f"    {r:26}  {magnitude(gradient(S.saddle, p)):12.6f}")

print()
print("05_flat_ground_three_ways.py: every assertion held.")
