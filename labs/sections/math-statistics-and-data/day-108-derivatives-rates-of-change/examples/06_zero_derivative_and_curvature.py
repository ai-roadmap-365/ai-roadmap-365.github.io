"""A zero derivative says the ground is level. It does not say where you are.

Run from inside `examples/`:

    ../.venv/bin/python3 06_zero_derivative_and_curvature.py
"""

from __future__ import annotations

import dataset as D
from derivatives import central_difference, classify_stationary_point, second_difference

print("Day 108 / 06 — flat points, and telling them apart")
print()

H = D.STATIONARY_WIDTH
TOL = D.STATIONARY_TOL

# --------------------------------------------------------------------------
print("1. Three places where the slope is zero")
# --------------------------------------------------------------------------
print()
print("     f(x) = (x - 2)**2 + 1   at x = 2     the bottom of a valley")
print("     f(x) = x**3 - 3x        at x = -1    the top of a hill")
print("     f(x) = x**3             at x = 0     neither: a flat step")
print()
print(f"   Measured with the central difference at h = {H:.0e}:")
print()
print("     function            x       f(x)        f'(x) measured")
cases = [
    ("(x - 2)**2 + 1", D.parabola, 2.0),
    ("x**3 - 3x", D.cubic, -1.0),
    ("x**3 - 3x", D.cubic, 1.0),
    ("x**3", D.plain_cube, 0.0),
]
for label, f, x in cases:
    slope = central_difference(f, x, H)
    print(f"     {label:<19} {x:<7.1f} {f(x):<11.4f} {slope:.3e}")
    assert abs(slope) < TOL, (label, x, slope)
print()
print("   Four flat points, four slopes indistinguishable from zero. The first")
print("   derivative has now told you everything it knows, and it has not told")
print("   you which of these is a minimum. That is not a limitation of the")
print("   measurement. It is a limitation of the question.")
print()

# --------------------------------------------------------------------------
print("2. Look at the neighbourhood and the difference is obvious")
# --------------------------------------------------------------------------
print()
print("   Step a little either way from each point and compare the values:")
print()
print("     function            x        f(x - 0.1)   f(x)        f(x + 0.1)   verdict")
for label, f, x in cases:
    left, here, right = f(x - 0.1), f(x), f(x + 0.1)
    if left > here < right:
        verdict = "both sides higher -> minimum"
    elif left < here > right:
        verdict = "both sides lower  -> maximum"
    else:
        verdict = "one of each       -> neither"
    print(f"     {label:<19} {x:<8.1f} {left:<12.5f} {here:<11.5f} {right:<12.5f} {verdict}")
print()
print("   That works, and it is what your eye does when it looks at a graph.")
print("   It is also not a formula, and it needs you to pick 0.1 out of the")
print("   air. The second derivative is the same idea made precise.")
print()

# --------------------------------------------------------------------------
print("3. The second derivative: the rate of change of the rate of change")
# --------------------------------------------------------------------------
print()
print("   The derivative of a function is a function, so it has a derivative")
print("   of its own. Written f''(x), or d2y/dx2. It answers: is the slope")
print("   itself increasing or decreasing as you move right?")
print()
print("   Numerically, taking a central difference of central differences and")
print("   letting the algebra collapse gives one formula:")
print()
print("     f''(x)  ~  ( f(x + h) - 2*f(x) + f(x - h) ) / h**2")
print()
print("   Read it as: how much does the middle sag below the average of its")
print("   two neighbours? Sagging down is positive curvature, a bowl. Bulging")
print("   up is negative curvature, a dome.")
print()
print("     function            x        f'(x)         f''(x)        shape")
for label, f, x in cases:
    slope = central_difference(f, x, H)
    curve = second_difference(f, x, H)
    shape = "bowl" if curve > TOL else ("dome" if curve < -TOL else "flat both ways")
    print(f"     {label:<19} {x:<8.1f} {slope:<13.3e} {curve:<13.6f} {shape}")
print()

parabola_second = second_difference(D.parabola, 2.0, H)
cubic_min_second = second_difference(D.cubic, 1.0, H)
cubic_max_second = second_difference(D.cubic, -1.0, H)
cube_second = second_difference(D.plain_cube, 0.0, H)

assert abs(parabola_second - 2.0) < D.SECOND_TOL, parabola_second
assert abs(cubic_min_second - 6.0) < D.SECOND_TOL, cubic_min_second
assert abs(cubic_max_second - (-6.0)) < D.SECOND_TOL, cubic_max_second
assert abs(cube_second) < D.SECOND_TOL, cube_second
assert cubic_min_second > 0.0 > cubic_max_second

print("   The exact values are 2, 6, -6 and 0, and all four measurements match")
print(f"   them to inside {D.SECOND_TOL:.0e}. Note that the first derivative gave the")
print("   same answer at all four points and the second derivative gave four")
print("   different ones. That is the whole point of computing it.")
print()

# --------------------------------------------------------------------------
print("4. The classification, and the case it refuses to decide")
# --------------------------------------------------------------------------
print()
print("     function            x        classification")
for label, f, x in cases + [("x**3 - 3x", D.cubic, 0.0)]:
    verdict = classify_stationary_point(f, x, H, TOL)
    print(f"     {label:<19} {x:<8.1f} {verdict}")
print()
assert classify_stationary_point(D.parabola, 2.0, H, TOL) == "minimum"
assert classify_stationary_point(D.cubic, 1.0, H, TOL) == "minimum"
assert classify_stationary_point(D.cubic, -1.0, H, TOL) == "maximum"
assert classify_stationary_point(D.plain_cube, 0.0, H, TOL) == "undecided"
assert classify_stationary_point(D.cubic, 0.0, H, TOL) == "not stationary"
print("   'undecided' is not a bug and it is not a failure of the numerics.")
print("   x**3 at 0 is flat and has zero curvature, and so does x**4 at 0.")
print("   The first is a step in a rising slope and the second is a genuine")
print("   minimum, and no amount of second-derivative information separates")
print("   them. A function that reported 'minimum' there would be lying with")
print("   confidence, which is worse than saying it does not know.")
print()
fourth_slope = central_difference(lambda x: x**4, 0.0, H)
fourth_curve = second_difference(lambda x: x**4, 0.0, H)
print(f"     x**4 at 0:  f' = {fourth_slope:.3e}   f'' = {fourth_curve:.3e}   (a real minimum)")
print(f"     x**3 at 0:  f' = {central_difference(D.plain_cube, 0.0, H):.3e}   "
      f"f'' = {cube_second:.3e}   (not a minimum)")
assert abs(fourth_slope) < TOL and abs(fourth_curve) < D.SECOND_TOL
print()
print("   Both readings are zero as far as this method can see -- 2e-8 and 0")
print("   are the same number to a rule whose own rounding noise here is")
print(f"   around {D.SECOND_TOL:.0e}. Same readings, different answers. This is the honest")
print("   boundary of what a second derivative can do.")
print()

# --------------------------------------------------------------------------
print("5. Why any of this matters for training a model")
# --------------------------------------------------------------------------
print()
print("   Training searches for the minimum of a loss function, and the")
print("   derivative is how it knows which way is downhill:")
print()
print("     f'(x) > 0   the function rises to the right, so step LEFT")
print("     f'(x) < 0   the function falls to the right, so step RIGHT")
print("     f'(x) = 0   flat: nothing to learn from the first derivative")
print()
print("   Watch that read out along the parabola, whose minimum is at x = 2:")
print()
print("     x        f(x)        f'(x)        which way is downhill")
for x in [-1.0, 0.5, 1.5, 2.0, 2.5, 4.0]:
    slope = central_difference(D.parabola, x, H)
    if slope > TOL:
        direction = "left"
    elif slope < -TOL:
        direction = "right"
    else:
        direction = "already flat"
    print(f"     {x:<8.1f} {D.parabola(x):<11.4f} {slope:<12.4f} {direction}")
    assert abs(slope - D.parabola_derivative(x)) < D.SECOND_TOL
print()
print("   Every one of those arrows points towards x = 2, and none of them was")
print("   told where x = 2 is. That is gradient descent in one dimension, and")
print("   Day 111 will write the four-line loop that follows the arrows.")
print()

print("06_zero_derivative_and_curvature.py: every assertion held.")
