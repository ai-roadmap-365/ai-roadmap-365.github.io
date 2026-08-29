"""Choosing h, Day 108's U-curve in two dimensions, and what numpy.gradient does.

Run from inside `examples/`:

    ../.venv/bin/python3 06_step_size_and_the_u_curve.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import forward_partial, gradient, partial

print(__doc__.splitlines()[0])
print()

POINT = (2.0, 1.0)
EXACT_DX = float(S.cubic_gradient(POINT)[0])

# --------------------------------------------------------------------------
print("1. On a cubic, the truncation error is not merely small -- it is exactly h^2")
# --------------------------------------------------------------------------
#
# Script 01 showed that a central difference is algebraically exact on a
# quadratic. f(x, y) = x^3 + x*y^2 is the first surface here that is not, and
# its error can be written down in closed form rather than bounded:
#
#     ((x+h)^3 - (x-h)^3) / (2h)
#   = (x^3 + 3x^2h + 3xh^2 + h^3 - x^3 + 3x^2h - 3xh^2 + h^3) / (2h)
#   = (6x^2 h + 2h^3) / (2h)
#   = 3x^2 + h^2
#
# and the exact partial is 3x^2. So the numerical answer overshoots by exactly
# h squared, with no other terms at all. The y^2 x term contributes nothing to
# the x-partial's error because it is linear in x.

print(f"  f(x, y) = x^3 + x*y^2 at {POINT}. Exact df/dx = 3x^2 + y^2 = {EXACT_DX}")
print()
print(f"  {'h':>10}  {'numerical df/dx':>20}  {'error':>16}  {'h^2':>16}  {'relative gap':>13}")
for k in (1, 2, 3):
    h = 10.0 ** (-k)
    value = partial(S.cubic, POINT, 0, h)
    error = value - EXACT_DX
    gap = abs(error - h * h) / (h * h)
    print(f"  {h:10.0e}  {value:20.14f}  {error:16.12f}  {h * h:16.12f}  {gap:13.3e}")
    assert gap < 1e-5, (h, gap)

print()
print("  The error column and the h^2 column are the same column. This is the")
print("  clearest statement available of what 'second-order accurate' means:")
print("  divide the step by ten and the method error divides by a hundred.")

# --------------------------------------------------------------------------
print()
print("2. Day 108's U-curve, on a partial derivative")
# --------------------------------------------------------------------------
#
# Shrinking h forever does not work, and Day 108 already showed why in one
# dimension: the method error falls but the ROUNDOFF error rises, because
# subtracting two numbers that are nearly equal throws away the leading digits
# they had in common. Nothing about that changes when the function has more
# than one input.
#
# Two curves are printed, because the choice between them is the whole reason
# this lab uses a central difference.

print(f"  {'h':>10}  {'central error':>16}  {'forward error':>16}   shape")
central = {}
forward = {}
for k in range(0, 15):
    h = 10.0 ** (-k)
    c = abs(partial(S.cubic, POINT, 0, h) - EXACT_DX)
    f = abs(forward_partial(S.cubic, POINT, 0, h) - EXACT_DX)
    central[h] = c
    forward[h] = f
    bar = "#" * max(0, int(round(16 + np.log10(max(c, 1e-16)))))
    print(f"  {h:10.0e}  {c:16.3e}  {f:16.3e}   {bar}")

best_central = min(central, key=central.get)
best_forward = min(forward, key=forward.get)
eps = float(np.finfo(float).eps)
print()
print(f"  best h for the central difference: {best_central:.0e}"
      f"   (error {central[best_central]:.3e})")
print(f"  best h for the forward difference: {best_forward:.0e}"
      f"   (error {forward[best_forward]:.3e})")
print()
print("  Theory says the trough sits where the two error sources balance:")
print(f"    central: around the cube root of machine epsilon = {eps ** (1 / 3):.3e}")
print(f"    forward: around the square root of machine epsilon = {eps ** 0.5:.3e}")
print()
print("  Both predictions land on the measured trough to within one decade.")
assert best_central == 1e-05
assert best_forward == 1e-08
assert central[best_central] < forward[best_forward]

print()
print("  Read the two error columns at h = 1e-5, the step this lab uses:")
print(f"    central  {central[1e-05]:.3e}")
print(f"    forward  {forward[1e-05]:.3e}")
print(f"    the central difference is {forward[1e-05] / central[1e-05]:,.0f} times more accurate here,")
print("    for one extra evaluation of f per input. That is the trade, and it")
print("    is not close.")
print()
print("  And the far end of the table is the part worth remembering: at")
print(f"  h = 1e-14 the central difference is out by {central[1e-14]:.3e}, which is")
print(f"  {central[1e-14] / central[1e-01]:.0f} times WORSE than the answer at h = 0.1 -- a step a trillion")
print("  times bigger. Shrinking h past the trough does not buy a slightly")
print("  worse answer. It buys nonsense, confidently.")
assert central[1e-14] > central[1e-01]
assert central[1e-05] < central[1e-01]

# --------------------------------------------------------------------------
print()
print("3. What happens to the whole gradient, not just one partial")
# --------------------------------------------------------------------------

print(f"  {'h':>10}  {'gradient of the cubic at (2, 1)':>36}  {'max error':>12}")
for k in (1, 3, 5, 8, 12):
    h = 10.0 ** (-k)
    g = gradient(S.cubic, POINT, h)
    err = float(np.max(np.abs(g - S.cubic_gradient(POINT))))
    shown = "[" + ", ".join(f"{v:16.10f}" for v in g) + "]"
    print(f"  {h:10.0e}  {shown:>36}  {err:12.3e}")

print()
print("  Both components degrade together, because both are computed the same")
print("  way. There is no step size that is right for one and wrong for the")
print("  other here -- though on a function whose inputs have wildly different")
print("  scales there would be, which is an argument for scaling your inputs")
print("  before you differentiate anything.")

# --------------------------------------------------------------------------
print()
print("4. numpy.gradient does something related and different")
# --------------------------------------------------------------------------
#
# NumPy has a function called `gradient`, and reaching for it here would be a
# mistake -- not because it is bad, but because it answers a different
# question. Ours takes a FUNCTION and a point. NumPy's takes an ARRAY of
# values already sampled on a grid, and returns the differences between
# neighbouring samples. It cannot be asked for the gradient at a point that is
# not a grid point, and it cannot choose its own step, because the step is
# whatever spacing the data already has.

xs = np.linspace(0.0, 4.0, 9)
ys = np.linspace(0.0, 4.0, 9)
X, Y = np.meshgrid(xs, ys, indexing="ij")
spacing = float(xs[1] - xs[0])

print(f"  A 9 by 9 grid over [0, 4] x [0, 4], spacing {spacing}.")
print()
print("  On the bowl x^2 + 3y^2, whose gradient a central difference gets")
print("  exactly right at any step, numpy.gradient is exact in the interior:")
Z = X * X + 3.0 * Y * Y
gx, gy = np.gradient(Z, xs, ys)
print(f"    interior sample at (x, y) = ({xs[2]}, {ys[2]}):"
      f" numpy [{gx[2, 2]:.6f}, {gy[2, 2]:.6f}]"
      f"  exact [{S.bowl_gradient((xs[2], ys[2]))[0]:.6f},"
      f" {S.bowl_gradient((xs[2], ys[2]))[1]:.6f}]")
assert abs(gx[2, 2] - 2.0 * xs[2]) < 1e-12
assert abs(gy[2, 2] - 6.0 * ys[2]) < 1e-12

print()
print("  but not at the edge, because by default it drops to a one-sided")
print("  first-order formula there:")
print(f"    corner sample at (0.0, 0.0):  numpy [{gx[0, 0]:.6f}, {gy[0, 0]:.6f}]"
      f"   exact [0.0, 0.0]")
assert abs(gx[0, 0] - 0.5) < 1e-12
assert abs(gy[0, 0] - 1.5) < 1e-12

gx2, gy2 = np.gradient(Z, xs, ys, edge_order=2)
print(f"    the same corner with edge_order=2: [{gx2[0, 0]:.6f}, {gy2[0, 0]:.6f}]"
      "   exact, this time")
assert abs(gx2[0, 0]) < 1e-12 and abs(gy2[0, 0]) < 1e-12
print()
print("  That default is worth knowing about before it costs you an afternoon:")
print("  every interior value is second-order accurate and every boundary")
print("  value is first-order, unless you ask otherwise.")

print()
print("  On the cubic, where the method error is real, the difference between")
print("  the two functions becomes the point:")
Zc = X ** 3 + X * Y * Y
cgx, _cgy = np.gradient(Zc, xs, ys, edge_order=2)
i = j = 4
p = (float(xs[i]), float(ys[j]))
exact = float(S.cubic_gradient(p)[0])
ours = float(partial(S.cubic, p, 0))
print(f"    at (x, y) = {p}, exact df/dx = {exact}")
print(f"      numpy.gradient on the sampled array : {cgx[i, j]:14.10f}"
      f"   error {abs(cgx[i, j] - exact):.3e}")
print(f"      grid spacing squared                 : {spacing ** 2:14.10f}")
print(f"      our gradient, on the function itself : {ours:14.10f}"
      f"   error {abs(ours - exact):.3e}")
assert abs(abs(cgx[i, j] - exact) - spacing ** 2) < 1e-12
assert abs(ours - exact) < S.GRADIENT_TOL

print()
print("  It is the same h^2 law from section 1 -- but h is now the grid")
print("  spacing, which is fixed by the data you were given. You cannot")
print("  shrink it without going back and sampling more finely, and if the")
print("  samples came from a sensor you may not be able to at all.")
print()
print("  So: numpy.gradient when you HAVE an array of values -- an image, a")
print("  height field, a measured series. Our `gradient` when you have a")
print("  function you can call. They are not competitors.")

print()
print("06_step_size_and_the_u_curve.py: every assertion held.")
