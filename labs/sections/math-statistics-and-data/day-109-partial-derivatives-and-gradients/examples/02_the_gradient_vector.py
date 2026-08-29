"""Collect every partial derivative into one vector and you have the gradient.

Run from inside `examples/`:

    ../.venv/bin/python3 02_the_gradient_vector.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import angle_degrees, gradient, magnitude, unit

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. Six surfaces, five points each, numerical against exact")
# --------------------------------------------------------------------------
#
# The gradient is not a new idea. It is the partial derivatives of script 01
# written side by side in square brackets instead of on separate lines. What
# makes it worth a name is that the result is a VECTOR, and Days 99 to 103
# already taught what to do with one: it has a length, it has a direction, and
# it can be dotted with another vector.
#
# Everything below is checked against a gradient worked out with a pencil.

worst = 0.0
count = 0
for name, (f, exact_gradient, expression, gradient_expression) in S.SURFACES.items():
    print(f"  f(x, y) = {expression:<14}   {gradient_expression}")
    print(f"    {'point':>14}  {'numerical gradient':>34}  {'exact':>18}  {'max error':>11}")
    for p in S.PROBE_POINTS:
        numeric = gradient(f, p)
        exact = exact_gradient(p)
        error = float(np.max(np.abs(numeric - exact)))
        worst = max(worst, error)
        count += 1
        shown_numeric = "[" + ", ".join(f"{v:14.10f}" for v in numeric) + "]"
        shown_exact = "[" + ", ".join(f"{v:7.3f}" for v in exact) + "]"
        print(f"    {str(p):>14}  {shown_numeric:>34}  {shown_exact:>18}  {error:11.3e}")
        assert error < S.GRADIENT_TOL, (name, p, error)
    print()

print(f"  {count} gradients checked. Worst single error {worst:.3e},")
print(f"  against an asserted tolerance of {S.GRADIENT_TOL:g}.")

# --------------------------------------------------------------------------
print()
print("2. The gradient is a vector, so it has a length and a bearing")
# --------------------------------------------------------------------------
#
# Two numbers come out of the same object and they answer different questions.
# The DIRECTION answers "which way is uphill". The LENGTH answers "how steep is
# it that way", in units of f gained per unit of distance walked.

print(f"  {'surface':>9}  {'point':>13}  {'gradient':>17}  {'length':>10}  {'bearing':>9}")
for name in ("bowl", "plane", "saddle", "cubic"):
    f, exact_gradient = S.SURFACES[name][0], S.SURFACES[name][1]
    for p in ((1.0, 1.0), (2.0, -1.0)):
        g = gradient(f, p)
        shown = "[" + ", ".join(f"{v:7.4f}" for v in g) + "]"
        print(f"  {name:>9}  {str(p):>13}  {shown:>17}  {magnitude(g):10.6f}"
              f"  {angle_degrees(g):8.3f}d")
        assert abs(magnitude(g) - magnitude(exact_gradient(p))) < S.GRADIENT_TOL

print()
print("  Read the bowl's two rows. At (1, 1) the gradient is about [2, 6]:")
print("  three times as much climb per step north as per step east, because")
print("  the 3 in front of y^2 makes the bowl three times steeper that way.")

# --------------------------------------------------------------------------
print()
print("3. A gradient is a direction in the INPUT space, not a point on the surface")
# --------------------------------------------------------------------------
#
# This is the most common way to misread the object. f(x, y) = x^2 + 3y^2 has
# a two-dimensional input and a one-dimensional output, and lives naturally as
# a surface in three dimensions. The gradient has TWO components, not three.
# It is an arrow drawn on the flat map you are standing on, not an arrow
# pointing up out of the hillside.

p = (1.0, 1.0)
g = gradient(S.bowl, p)
print(f"  f takes a point with {len(p)} coordinates and returns 1 number:")
print(f"    f{p} = {S.bowl(p)}")
print(f"  and its gradient has {g.size} components, matching the INPUT:")
print(f"    grad f{p} = [{g[0]:.6f}, {g[1]:.6f}]")
stepped = np.array(p) + g
print("  Add the gradient to the point and you get another point, "
      f"({stepped[0]:.4f}, {stepped[1]:.4f}),")
print("  which is a legal thing to do and is exactly what Day 111 will do,")
print("  with a minus sign in front.")
assert g.size == len(p)

# --------------------------------------------------------------------------
print()
print("4. The unit gradient: direction with the steepness divided out")
# --------------------------------------------------------------------------

for p in ((1.0, 1.0), (0.25, 0.75), (3.0, 0.5)):
    g = gradient(S.bowl, p)
    u = unit(g)
    print(f"  at {str(p):>13}  gradient [{g[0]:9.5f}, {g[1]:9.5f}]"
          f"   unit [{u[0]:8.5f}, {u[1]:8.5f}]   |unit| = {magnitude(u):.15f}")
    assert abs(magnitude(u) - 1.0) < 1e-12
    assert abs(angle_degrees(u) - angle_degrees(g)) < 1e-9

print()
print("  Same bearing, length exactly 1. Script 03 needs the unit version,")
print("  because a rate of change 'in a direction' is meaningless until the")
print("  direction has a fixed length -- otherwise drawing a longer arrow")
print("  would make the hill steeper.")

# --------------------------------------------------------------------------
print()
print("5. The zero gradient, and what it does not tell you")
# --------------------------------------------------------------------------

print("  Three different surfaces, all with gradient [0, 0] at the origin:")
print(f"    {'surface':>9}  {'gradient at origin':>32}  {'length':>12}  what the origin IS")
for name, kind, why in S.STATIONARY_AT_ORIGIN:
    f = S.SURFACES[name][0]
    g = gradient(f, (0.0, 0.0))
    shown = "[" + ", ".join(f"{v:14.11f}" for v in g) + "]"
    print(f"    {name:>9}  {shown:>32}  {magnitude(g):12.3e}  {kind} -- {why}")
    assert magnitude(g) < S.GRADIENT_TOL

print()
print("  The gradient is identical in all three cases and the points are not")
print("  remotely alike. A zero gradient says 'the ground is level here'. It")
print("  does not say whether you are at the bottom of a valley, on top of a")
print("  hill, or in a mountain pass. Script 05 shows the difference by")
print("  walking away from each one.")

print()
print("02_the_gradient_vector.py: every assertion held.")
