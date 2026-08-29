"""Two ways to estimate a slope from function values, and why one is far better.

Run from inside `examples/`:

    ../.venv/bin/python3 04_forward_and_central.py
"""

from __future__ import annotations

import math

import dataset as D
from derivatives import (
    backward_difference,
    central_difference,
    forward_difference,
    numpy_gradient_slope,
    numpy_gradient_slope_from_coordinates,
)

print("Day 108 / 04 — forward, backward, central")
print()

# --------------------------------------------------------------------------
print("1. The three rules")
# --------------------------------------------------------------------------
print()
print("     forward    ( f(x + h) - f(x)     ) / h        one step ahead")
print("     backward   ( f(x)     - f(x - h) ) / h        one step behind")
print("     central    ( f(x + h) - f(x - h) ) / (2h)     straddling x")
print()
print("   The central rule is the average of the other two, and the averaging")
print("   is the entire trick. Forward leans one way off the tangent, backward")
print("   leans the other way by almost exactly the same amount, and adding")
print("   them cancels the leaning. It costs one function call more than")
print("   forward and none at all more than computing both one-sided rules.")
print()

# --------------------------------------------------------------------------
print("2. All three on f(x) = x**2 at x = 3, where the answer is 6")
# --------------------------------------------------------------------------
print()
print("     h         forward       backward      central       f-err     c-err")
for h in [1.0, 0.1, 0.01, 0.001]:
    fwd = forward_difference(D.square, 3.0, h)
    bwd = backward_difference(D.square, 3.0, h)
    cen = central_difference(D.square, 3.0, h)
    print(f"     {h:<9.4f} {fwd:<13.9f} {bwd:<13.9f} {cen:<13.9f} {abs(fwd - 6.0):<9.2e} {abs(cen - 6.0):.1e}")
    assert abs(fwd - (6.0 + h)) < 1e-9
    assert abs(bwd - (6.0 - h)) < 1e-9
    assert abs(cen - 6.0) < 1e-9
print()
print("   Forward is 6 + h. Backward is 6 - h. Their average is 6, and for a")
print("   parabola that is not an approximation -- it is exact, at every h.")
print("   The forward rule's error is proportional to h; the central rule's")
print("   error on a quadratic is zero because a quadratic has no third")
print("   derivative for it to trip over.")
print()

# --------------------------------------------------------------------------
print("3. On e**x at x = 1, where central is very good but not exact")
# --------------------------------------------------------------------------
print()
print(f"   The right answer is e = {math.e!r}")
print()
print("     h            forward error    central error    central is better by")
for h in [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]:
    fwd_err = abs(forward_difference(D.exponential, 1.0, h) - math.e)
    cen_err = abs(central_difference(D.exponential, 1.0, h) - math.e)
    print(f"     {h:<12.0e} {fwd_err:<16.6e} {cen_err:<16.6e} {fwd_err / cen_err:>10.0f}x")
    assert cen_err < fwd_err
print()
print("   Read down the two error columns. Each time h drops by a factor of 10,")
print("   the forward error drops by about 10 and the central error by about")
print("   100. That is the difference between an error proportional to h and an")
print("   error proportional to h**2, and it compounds: at h = 1e-5 the central")
print("   rule is over two hundred thousand times more accurate for one extra")
print("   function call.")
print()
h = D.COMPARE_WIDTH
fwd_err = abs(forward_difference(D.exponential, 1.0, h) - math.e)
cen_err = abs(central_difference(D.exponential, 1.0, h) - math.e)
assert fwd_err < D.FORWARD_TOL
assert cen_err < D.CENTRAL_TOL
assert cen_err * 1000.0 < fwd_err
print(f"   At h = {h:.0e}: forward error {fwd_err:.6e}, central error {cen_err:.6e}.")
print(f"   Both are inside the tolerances derived in dataset.py "
      f"({D.FORWARD_TOL:.0e} and {D.CENTRAL_TOL:.0e}).")
print()

# --------------------------------------------------------------------------
print("4. Where the h**2 comes from, without any calculus")
# --------------------------------------------------------------------------
print()
print("   Taylor's expansion writes a smooth function near x as a polynomial:")
print()
print("     f(x + h) = f(x) + h*f'(x) + (h**2/2)*f''(x) + (h**3/6)*f'''(x) + ...")
print("     f(x - h) = f(x) - h*f'(x) + (h**2/2)*f''(x) - (h**3/6)*f'''(x) + ...")
print()
print("   Subtract the first from f(x) and divide by h and the f'' term")
print("   survives, multiplied by h/2. That is the forward rule's error.")
print()
print("   Subtract the SECOND from the first and the f'' terms cancel -- they")
print("   have the same sign in both lines. Divide by 2h and the first survivor")
print("   is the f''' term, multiplied by h**2/6. That is the central rule's")
print("   error, and it is why halving h quarters it.")
print()
print("   Check the prediction against the measurement on e**x at x = 1, where")
print("   every derivative equals e:")
print()
print("     h         predicted h**2/6 * e    measured central error   ratio")
for h_ in [1e-2, 1e-3, 1e-4]:
    predicted = (h_ * h_ / 6.0) * math.e
    measured = abs(central_difference(D.exponential, 1.0, h_) - math.e)
    print(f"     {h_:<9.0e} {predicted:<23.6e} {measured:<24.6e} {measured / predicted:.4f}")
    assert 0.99 < measured / predicted < 1.01, (h_, measured / predicted)
print()
print("   Within one percent, three times over. The formula is not folklore.")
print()

# --------------------------------------------------------------------------
print("5. The same job, handed to NumPy")
# --------------------------------------------------------------------------
print()
print("   numpy.gradient differentiates SAMPLES, not functions: you give it")
print("   values you already have and it returns a slope estimate at each one.")
print("   Interior points get the central rule; the two ends have nothing on")
print("   one side and fall back to a one-sided rule.")
print()
mine = central_difference(D.exponential, 1.0, D.COMPARE_WIDTH)
theirs = numpy_gradient_slope(D.exponential, 1.0, D.COMPARE_WIDTH)
print(f"     central_difference        {mine!r}")
print(f"     np.gradient (interior)    {theirs!r}")
print(f"     identical to the last bit {mine == theirs}")
assert mine == theirs
print()
coords = numpy_gradient_slope_from_coordinates(D.exponential, 1.0, D.COMPARE_WIDTH)
print("   One honest wrinkle, found while building this lab. Pass np.gradient a")
print("   scalar spacing and it is bit-for-bit our central difference. Pass it")
print("   an ARRAY of coordinates -- the same evenly spaced points -- and it")
print("   uses its general unevenly-spaced formula instead:")
print()
print(f"     np.gradient(ys, h)        {theirs!r}")
print(f"     np.gradient(ys, xs)       {coords!r}")
print(f"     they differ by            {abs(coords - theirs):.3e}")
assert coords != theirs
assert abs(coords - theirs) < 1e-10
print()
print("   Both are correct. Neither is the exact answer. 'The same formula' is")
print("   a claim about the mathematics, and the mathematics does not fix the")
print("   order the additions happen in.")
print()

print("04_forward_and_central.py: every assertion held.")
