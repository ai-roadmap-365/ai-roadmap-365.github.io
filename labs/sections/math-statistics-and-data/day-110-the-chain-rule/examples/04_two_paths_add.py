"""When a variable reaches the output twice, the contributions ADD.

This is the section to slow down in. Everything before it multiplies;
everything after it depends on knowing when to add.

Run from inside `examples/`:

    ../.venv/bin/python3 04_two_paths_add.py
"""

import dataset as D
from chainrule import (
    central_difference,
    partial_difference,
    path_contributions,
    total_derivative,
    wrong_single_path_derivative,
)

print("=" * 74)
print("1. One input, two routes to the output")
print("=" * 74)
print()
print("  Build a small graph in which x is used twice:")
print()
print("      u = x squared")
print("      v = 3x")
print("      f = u x v")
print()
print("  Draw it and x has two arrows leaving it, one into u and one into v.")
print("  Both of them end up at f.")
print()
x = D.TWO_PATH_X
u = x * x
v = 3.0 * x
f = u * v
print(f"      at x = {x}:   u = {u},  v = {v},  f = {f}")

assert u == D.TWO_PATH_U
assert v == D.TWO_PATH_V
assert f == D.TWO_PATH_OUTPUT

print()
print("=" * 74)
print("2. The two path products")
print("=" * 74)
print()
print("  Along each path, multiply the local rates as usual:")
print()
print("      path through u:   df/du x du/dx  =  v   x 2x  = 6 x 4 = 24")
print("      path through v:   df/dv x dv/dx  =  u   x 3   = 4 x 3 = 12")
print()
paths = [[v, 2.0 * x], [u, 3.0]]
contributions = path_contributions(paths)
print(f"      contributions = {contributions}")
print()
print("  Now the question the whole day turns on: is the answer 24, is it 12,")
print("  is it 24 x 12 = 288, or is it 24 + 12 = 36?")

assert contributions == list(D.TWO_PATH_CONTRIBUTIONS)

print()
print("=" * 74)
print("3. Ask the measurement, which has no opinion about rules")
print("=" * 74)
print()
measured = central_difference(D.two_path_direct, x, D.H)
summed = total_derivative(paths)
wrong_a = wrong_single_path_derivative(paths, 0)
wrong_b = wrong_single_path_derivative(paths, 1)
multiplied = contributions[0] * contributions[1]
print("  Substitute the intermediates away and the function is just")
print("  f = x squared x 3x = 3 x cubed, which we can nudge directly.")
print()
print(f"      central difference of 3x cubed at x = 2:   {measured:.9f}")
print()
print("     candidate answer            value      matches the measurement?")
print("     " + "-" * 60)
for label, value in (
    ("sum of the paths, 24 + 12", summed),
    ("path through u alone", wrong_a),
    ("path through v alone", wrong_b),
    ("product of the paths", multiplied),
):
    verdict = "YES" if abs(value - measured) < D.NUMERIC_TOL else "no"
    print(f"     {label:<27s} {value:<10.6g} {verdict}")
print()
print("  Only the sum survives. And it is not a convention: changing x moves")
print("  the output through u AND through v, both movements are real, and")
print("  both happen at once. Adding them is what 'both happen' means.")
print()
print("  Check it against the closed form too. f = 3x cubed, so df/dx = 9x")
print(f"  squared, which at x = 2 is {D.d_two_path_direct(x)}.")

assert summed == D.TWO_PATH_DERIVATIVE
assert abs(summed - measured) < D.NUMERIC_TOL
assert abs(D.d_two_path_direct(x) - summed) < D.ANALYTIC_TOL
# The instructive failures, asserted as failures so the suite would notice if
# a future edit made the single-path answer accidentally correct.
assert abs(wrong_a - measured) > 1.0
assert abs(wrong_b - measured) > 1.0
assert abs(multiplied - measured) > 1.0

print()
print("=" * 74)
print("4. Why the cancelling mnemonic breaks here")
print("=" * 74)
print()
print("  The 'du cancels' reading of dy/dx = dy/du x du/dx has nothing to")
print("  say about this graph, because there are two different intermediates")
print("  and no single symbol to cancel. Written honestly the rule is:")
print()
print("      df      df   du     df   dv")
print("      --  =   -- x --  +  -- x --")
print("      dx      du   dx     dv   dx")
print()
print("  A product for each route, a sum across routes. Every backward pass")
print("  in every framework is that formula applied node by node, and the")
print("  '+' is why a gradient is accumulated with += rather than assigned.")

print()
print("=" * 74)
print("5. The full multivariable case: two inputs, two intermediates")
print("=" * 74)
print()
print("      z = u squared + v squared,   u = s x t,   v = s - t")
print()
s, t = D.SURFACE_POINT
u2 = s * t
v2 = s - t
z = u2 * u2 + v2 * v2
print(f"      at (s, t) = ({s:g}, {t:g}):  u = {u2:g}, v = {v2:g}, z = {z:g}")
print()
print("      dz/du = 2u = 12          dz/dv = 2v = -2")
print("      du/ds = t  = 3           du/dt = s  = 2")
print("      dv/ds = 1                dv/dt = -1")
print()
dz_ds = D.SURFACE_DZ_DU * t + D.SURFACE_DZ_DV * 1.0
dz_dt = D.SURFACE_DZ_DU * s + D.SURFACE_DZ_DV * -1.0
print(f"      dz/ds = 12 x 3 + (-2) x 1    = {dz_ds:g}")
print(f"      dz/dt = 12 x 2 + (-2) x (-1) = {dz_dt:g}")
print()
num_ds = partial_difference(D.surface, D.SURFACE_POINT, 0, D.H)
num_dt = partial_difference(D.surface, D.SURFACE_POINT, 1, D.H)
print("     quantity   chain rule    partial difference     gap")
print("     " + "-" * 52)
print(f"     dz/ds      {dz_ds:<13g} {num_ds:<22.9f} {abs(dz_ds - num_ds):.2e}")
print(f"     dz/dt      {dz_dt:<13g} {num_dt:<22.9f} {abs(dz_dt - num_dt):.2e}")
print()
print("  Two inputs, two intermediates, four paths in total, and every")
print("  gradient is a sum of two products. That is the entire multivariable")
print("  chain rule, and it is the reason a branching computation graph is")
print("  no harder to differentiate than a straight line -- only longer.")

assert z == D.SURFACE_Z
assert (dz_ds, dz_dt) == D.SURFACE_GRADIENT
assert abs(dz_ds - num_ds) < D.NUMERIC_TOL
assert abs(dz_dt - num_dt) < D.NUMERIC_TOL

print()
print("04_two_paths_add.py: every assertion held.")
