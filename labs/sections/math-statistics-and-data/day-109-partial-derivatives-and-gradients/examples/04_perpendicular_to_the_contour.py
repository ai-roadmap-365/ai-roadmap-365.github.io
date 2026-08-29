"""The gradient is perpendicular to the contour through the point.

This is the geometric fact that makes every optimisation picture in the rest
of the course readable, so it is demonstrated rather than asserted -- and
demonstrated CAREFULLY, because the obvious way to demonstrate it is circular.

Run from inside `examples/`:

    ../.venv/bin/python3 04_perpendicular_to_the_contour.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import contour_chord, gradient, magnitude, unit

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. The trap this script is built to avoid")
# --------------------------------------------------------------------------
#
# The lazy demonstration is: take the gradient, rotate it 90 degrees, call
# that "the contour direction", and observe that it is perpendicular to the
# gradient. That proves nothing whatever -- it is perpendicular because it was
# constructed to be.
#
# So every contour used below is an exact algebraic curve, derived on paper
# from the function alone, with the gradient nowhere in its derivation. And
# before any of it is used, the script CHECKS that f really is constant along
# each curve, so the reader is not asked to trust the algebra either.

print("  Three exactly parametrised contours, none derived from a gradient:")
print()
print("    bowl     x^2 + 3y^2 = L    x = sqrt(L) cos t,  y = sqrt(L/3) sin t")
print("    product  xy = L           x = t,  y = L/t")
print("    dome     -(x^2+y^2) = L   x = sqrt(-L) cos t,  y = sqrt(-L) sin t")
print()
print("  Substituting the first into x^2 + 3y^2 gives L cos^2 t + 3 (L/3) sin^2 t,")
print("  which is L (cos^2 t + sin^2 t) = L for every t. No gradient anywhere.")
print()
print("  Checked numerically at eight parameter values per curve:")
print(f"    {'surface':>9}  {'level L':>9}  {'max |f(point) - L| over the curve':>36}")
for name, (f, contour, level, _t0) in S.CONTOURS.items():
    ts = np.linspace(0.3, 2.6, 8)
    drift = max(abs(f(contour(level, t)) - level) for t in ts)
    print(f"    {name:>9}  {level:9.2f}  {drift:36.3e}")
    assert drift < 1e-12, (name, drift)

# --------------------------------------------------------------------------
print()
print("2. Step along the contour, and dot with the gradient")
# --------------------------------------------------------------------------
#
# Take a point p on the curve at parameter t, and a second point q at
# parameter t + delta. The unit vector from p to q is a CHORD of the contour.
# Dot it with the unit gradient at p.
#
# The result is not exactly zero and should not be expected to be, because a
# chord is not a tangent: it is tilted away from the tangent by an angle of
# roughly delta. So the honest evidence is not one small number -- it is the
# number shrinking in step with delta.

print(f"  {'surface':>9}  {'delta':>9}  {'unit gradient . unit chord':>28}  {'ratio to previous':>18}")
for name, (f, contour, level, t0) in S.CONTOURS.items():
    previous = None
    for k in (2, 3, 4, 5, 6):
        delta = 10.0 ** (-k)
        chord, p, _q, f_p, f_q = contour_chord(f, contour, level, t0, delta)
        g = unit(gradient(f, p))
        dot = float(np.dot(g, chord))
        ratio = "" if previous is None else f"{previous / abs(dot):18.4f}"
        print(f"  {name:>9}  {delta:9.0e}  {dot:+28.10e}  {ratio:>18}")
        assert abs(f_p - f_q) < 1e-12, "the two points are not on the same contour"
        if previous is not None:
            # Tenfold smaller step, tenfold smaller dot product: first order.
            assert 9.0 < previous / abs(dot) < 11.0, (name, delta, previous / abs(dot))
        previous = abs(dot)
    print()

print("  Every ratio is close to 10. Divide the step by ten and the dot")
print("  product divides by ten. That is what 'it goes to zero' looks like")
print("  when you can only ever take a finite step: not a small number, but a")
print("  number that shrinks at exactly the rate the geometry predicts.")

# --------------------------------------------------------------------------
print()
print("3. The same claim at the tolerance the lab actually asserts")
# --------------------------------------------------------------------------

print(f"  step along the contour: delta = {S.CONTOUR_DELTA:g}")
print(f"  asserted tolerance:            {S.CONTOUR_DOT_TOL:g}")
print()
print(f"  {'surface':>9}  {'t':>6}  {'point on the contour':>26}  {'unit gradient':>24}  {'dot':>13}")
worst = 0.0
for name, (f, contour, level, _t0) in S.CONTOURS.items():
    for t in (0.4, 0.9, 1.4, 1.9):
        chord, p, _q, _fp, _fq = contour_chord(f, contour, level, t, S.CONTOUR_DELTA)
        g = unit(gradient(f, p))
        dot = abs(float(np.dot(g, chord)))
        worst = max(worst, dot)
        shown_p = "(" + ", ".join(f"{v:10.6f}" for v in p) + ")"
        shown_g = "[" + ", ".join(f"{v:9.6f}" for v in g) + "]"
        print(f"  {name:>9}  {t:6.1f}  {shown_p:>26}  {shown_g:>24}  {dot:13.3e}")
        assert dot < S.CONTOUR_DOT_TOL, (name, t, dot)

print()
print(f"  Worst dot product across all {3 * 4} checks: {worst:.3e}, which is")
print(f"  {S.CONTOUR_DOT_TOL / worst:.0f} times inside the asserted tolerance. The tolerance was")
print("  chosen from section 2's measured rate before any of these ran, not")
print("  tightened afterwards until it looked impressive.")

# --------------------------------------------------------------------------
print()
print("4. Exactly zero, if you use the exact tangent instead of a chord")
# --------------------------------------------------------------------------
#
# The residual above is entirely the chord's fault. Differentiate the bowl's
# parametrisation with respect to t and you get the true tangent:
#
#     p(t)  = ( sqrt(L) cos t,       sqrt(L/3) sin t )
#     p'(t) = ( -sqrt(L) sin t,      sqrt(L/3) cos t )
#
# Dot that with the exact gradient (2x, 6y) = (2 sqrt(L) cos t, 6 sqrt(L/3) sin t):
#
#     -2L sin t cos t  +  6 (L/3) sin t cos t  =  (-2L + 2L) sin t cos t  =  0
#
# Identically zero, for every t and every level. No tolerance required.

level = 4.0
print(f"  bowl, contour level L = {level}")
print(f"    {'t':>6}  {'exact tangent':>26}  {'exact gradient':>26}  {'dot':>13}")
a = np.sqrt(level)
b = np.sqrt(level / 3.0)
for t in (0.0, 0.4, 0.9, 1.4, 1.9, 2.7):
    p = S.bowl_contour(level, t)
    tangent = np.array([-a * np.sin(t), b * np.cos(t)])
    g = S.bowl_gradient(p)
    dot = float(np.dot(tangent, g))
    shown_t = "[" + ", ".join(f"{v:10.6f}" for v in tangent) + "]"
    shown_g = "[" + ", ".join(f"{v:10.6f}" for v in g) + "]"
    print(f"    {t:6.1f}  {shown_t:>26}  {shown_g:>26}  {dot:13.3e}")
    assert abs(dot) < 1e-14

print()
print("  So the perpendicularity is exact and the small numbers in sections 2")
print("  and 3 are an artefact of measuring with finite steps, not a hedge.")

# --------------------------------------------------------------------------
print()
print("5. Why this is the fact that makes gradient descent make sense")
# --------------------------------------------------------------------------
#
# A contour is the set of points where f has one particular value -- a level
# set. On a real map it is the line joining points of equal height. Walking
# along it, you gain nothing and lose nothing.
#
# Perpendicular to it is therefore the only direction with anything to gain,
# and the gradient points along it. Everything else follows: the steepest
# ascent of script 03 is perpendicular to the contour, the steepest descent is
# the same line the other way, and the picture of an optimiser crossing
# contour lines at right angles -- which is what Day 112 will draw -- is not a
# stylisation. It is what the arrows do.

p = np.array([1.0, 1.0])
g = gradient(S.bowl, p)
along = np.array([-g[1], g[0]])   # a right angle to the gradient, by rotation
step = 0.001
print(f"  Stand at ({p[0]:.1f}, {p[1]:.1f}) on f = x^2 + 3y^2, where f = {S.bowl(p):.6f}")
print(f"    a step of {step} ALONG the contour direction changes f by "
      f"{S.bowl(p + step * unit(along)) - S.bowl(p):+.3e}")
print(f"    the same step ACROSS it, up the gradient, changes f by "
      f"{S.bowl(p + step * unit(g)) - S.bowl(p):+.3e}")
print(f"    the ratio of those two changes is about "
      f"{abs((S.bowl(p + step * unit(g)) - S.bowl(p)) / (S.bowl(p + step * unit(along)) - S.bowl(p))):.0f} to 1")
gain_across = S.bowl(p + step * unit(g)) - S.bowl(p)
gain_along = S.bowl(p + step * unit(along)) - S.bowl(p)
assert abs(gain_along) < 1e-5
assert gain_across > 100 * abs(gain_along)
print()
print(f"    and the gradient's length says how fast: {magnitude(g):.6f} units of f")
print(f"    per unit of distance, so a step of {step} up the gradient should gain")
print(f"    about {magnitude(g) * step:.6f}, against the {gain_across:.6f} actually measured.")
assert abs(gain_across - magnitude(g) * step) < 1e-4

print()
print("04_perpendicular_to_the_contour.py: every assertion held.")
