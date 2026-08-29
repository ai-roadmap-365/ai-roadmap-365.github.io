"""What a partial derivative is: one input moves, the rest are held still.

Run from inside `examples/`:

    ../.venv/bin/python3 01_hold_everything_else_still.py

Every claim printed here is asserted. If the script exits 0 and ends with
"every assertion held.", the numbers above it were computed, not typed.
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import partial

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. A function of two inputs, and one slice through it")
# --------------------------------------------------------------------------
#
# f(x, y) = x^2 + 3y^2. Stand at (2, 1). There is no single "the slope" here,
# because there is no single direction to walk in. There is a slope if you
# walk east, a different slope if you walk north, and a different one again
# for every bearing in between.
#
# A partial derivative picks one of those and only one: freeze every input but
# the chosen one, which turns the function of two variables into a function of
# ONE variable, and then take Day 108's ordinary derivative of that.

point = (2.0, 1.0)
print(f"  f(x, y) = x^2 + 3y^2, standing at (x, y) = {point}")
print(f"  f at that point                    {S.bowl(point):.6f}")
print()
print("  Freeze y at 1. What is left is a function of x alone:")
print("      g(x) = f(x, 1) = x^2 + 3")
for x in (1.0, 1.5, 2.0, 2.5, 3.0):
    print(f"        g({x:>3}) = {S.bowl((x, 1.0)):8.4f}")
print("  and dg/dx = 2x, which at x = 2 is 4.")
print()
print("  Now freeze x at 2 instead. What is left is a function of y alone:")
print("      k(y) = f(2, y) = 4 + 3y^2")
for y in (0.0, 0.5, 1.0, 1.5, 2.0):
    print(f"        k({y:>3}) = {S.bowl((2.0, y)):8.4f}")
print("  and dk/dy = 6y, which at y = 1 is 6.")
print()
print("  Those two numbers, 4 and 6, are the two partial derivatives at (2, 1).")
print("  They are written  df/dx = 4  and  df/dy = 6, with the rounded d")
print("  rather than the straight one, and the rounded d is the entire notice")
print("  that other inputs exist and are being held still.")

assert S.bowl(point) == 7.0
assert S.bowl_gradient(point)[0] == 4.0
assert S.bowl_gradient(point)[1] == 6.0

# --------------------------------------------------------------------------
print()
print("2. The same two numbers, measured instead of derived")
# --------------------------------------------------------------------------
#
# Nothing above needed a computer. But a computer cannot read x^2 + 3y^2 and
# differentiate it; it can only evaluate it. So do what Day 108 did: nudge the
# input a little each way and divide the change by the distance moved. The
# only new instruction is "and change nothing else".

h = S.H_DEFAULT
print(f"  step size h = {h:g}")
print()
for index, name in ((0, "x"), (1, "y")):
    base = np.asarray(point, dtype=float)
    up = base.copy()
    down = base.copy()
    up[index] += h
    down[index] -= h
    measured = partial(S.bowl, point, index, h)
    exact = S.bowl_gradient(point)[index]
    print(f"  df/d{name}:")
    shown_up = "(" + ", ".join(f"{v:.5f}" for v in up) + ")"
    shown_down = "(" + ", ".join(f"{v:.5f}" for v in down) + ")"
    print(f"    point nudged up      {shown_up}   f = {S.bowl(up):.12f}")
    print(f"    point nudged down    {shown_down}   f = {S.bowl(down):.12f}")
    print(f"    difference / (2h)    {measured:.12f}")
    print(f"    exact, by hand       {exact:.12f}")
    print(f"    error                {abs(measured - exact):.3e}")
    assert abs(measured - exact) < S.GRADIENT_TOL

print()
print("  Both errors are far below the tolerance this lab asserts,")
print(f"  which is {S.GRADIENT_TOL:g}. Section 3 explains why they are THIS small.")

# --------------------------------------------------------------------------
print()
print("3. Why the error is roundoff rather than method error, here")
# --------------------------------------------------------------------------
#
# A central difference has a truncation error proportional to h^2 times the
# third derivative. x^2 + 3y^2 has no third derivative worth the name -- it is
# identically zero -- so the h^2 term vanishes and what is left is only the
# floating-point noise from subtracting two nearly equal numbers.
#
# The algebra is short enough to show. For g(x) = x^2:
#
#     ((x+h)^2 - (x-h)^2) / (2h)
#   = (x^2 + 2xh + h^2 - x^2 + 2xh - h^2) / (2h)
#   = 4xh / (2h)
#   = 2x,    for ANY h, exactly.
#
# So for a quadratic the central difference is not an approximation at all. It
# is the answer, and the only thing between you and it is float64.

print("  Central difference on a quadratic is algebraically EXACT:")
print("    ((x+h)^2 - (x-h)^2) / (2h) = 4xh / (2h) = 2x, for any h at all.")
print()
print("  So changing h should barely move the answer. It does not:")
print(f"    {'h':>10}  {'df/dx at (2, 1)':>20}  {'error':>12}")
for k in (1, 2, 3, 4, 5, 6):
    hh = 10.0 ** (-k)
    value = partial(S.bowl, point, 0, hh)
    print(f"    {hh:10.0e}  {value:20.14f}  {abs(value - 4.0):12.3e}")
    assert abs(value - 4.0) < 1e-7

print()
print("  Script 06 does this on a genuine cubic, where the h^2 term is real,")
print("  and the same table becomes the U-shaped curve from Day 108.")

# --------------------------------------------------------------------------
print()
print("4. The function whose partials need the other variable")
# --------------------------------------------------------------------------
#
# x^2 + 3y^2 is a soft case: freezing y leaves a function of x with no y in it
# at all, so it is easy to believe the two variables were never really
# interacting. f(x, y) = xy destroys that comfort.

print("  f(x, y) = xy.  df/dx = y  and  df/dy = x.")
print("  The slope in x depends on where you are in Y. Walk along the x-axis,")
print("  where y = 0, and f is identically zero, so the slope in x is zero.")
print("  Step off that line and it stops being zero.")
print()
print(f"    {'point':>14}  {'df/dx exact':>12}  {'measured':>16}  {'df/dy exact':>12}  {'measured':>16}")
for p in ((1.0, 0.0), (1.0, 1.0), (1.0, 5.0), (3.0, -2.0)):
    ex = S.product_gradient(p)
    mx = partial(S.product, p, 0)
    my = partial(S.product, p, 1)
    print(f"    {str(p):>14}  {ex[0]:12.4f}  {mx:16.12f}  {ex[1]:12.4f}  {my:16.12f}")
    assert abs(mx - ex[0]) < S.GRADIENT_TOL
    assert abs(my - ex[1]) < S.GRADIENT_TOL

print()
print("  Read the first row again: at (1, 0) the slope in x is exactly zero,")
print("  and the surface is emphatically not flat there -- the slope in y is 1.")
print("  A single partial derivative being zero says nothing about the point.")

# --------------------------------------------------------------------------
print()
print("5. Every input gets one, however many there are")
# --------------------------------------------------------------------------
#
# Nothing above used the fact that there were two inputs. `partial` takes an
# index, so it works on a point of any length. Here is a function of three.

three = S.START_PARAMS
print(f"  A three-parameter loss at {three}: L = {S.model_loss(three)}")
exact3 = S.model_loss_gradient(three)
for i, label in enumerate(("w1", "w2", "c")):
    measured = partial(S.model_loss, three, i)
    print(f"    dL/d{label:<2}  exact {exact3[i]:8.4f}   measured {measured:18.12f}"
          f"   error {abs(measured - exact3[i]):.3e}")
    assert abs(measured - exact3[i]) < S.GRADIENT_TOL

print()
print("  Three inputs, three partial derivatives, and six evaluations of L to")
print("  get them -- two per input. Script 07 follows that cost to its")
print("  conclusion, which is the reason autodiff exists.")

print()
print("01_hold_everything_else_still.py: every assertion held.")
