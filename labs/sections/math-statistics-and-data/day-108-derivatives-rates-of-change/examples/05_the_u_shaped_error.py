"""Making h smaller makes the answer better -- until it makes it much worse.

Run from inside `examples/`:

    ../.venv/bin/python3 05_the_u_shaped_error.py

This is the script the lab exists for. It contradicts the obvious intuition,
and it contradicts it with a measurement rather than an argument.
"""

from __future__ import annotations

import math

import dataset as D
from derivatives import (
    best_step,
    central_difference,
    error_curve,
    forward_difference,
    is_u_shaped,
    numpy_error_curve,
)

print("Day 108 / 05 — the U-shaped error curve")
print()

# --------------------------------------------------------------------------
print("1. The intuition, and why it is wrong")
# --------------------------------------------------------------------------
print()
print("   The derivative is the limit of the difference quotient as h goes to")
print("   zero. So a smaller h should give a better answer, and h = 1e-300")
print("   should give a nearly perfect one.")
print()
print("   It gives 0.0. Here it is:")
print()
tiny = forward_difference(D.exponential, 1.0, 1e-300)
print(f"     forward_difference(exp, 1.0, 1e-300)  ->  {tiny!r}")
print(f"     the right answer is                       {math.e!r}")
assert tiny == 0.0
print()
print("   Not slightly wrong. Not wrong in the eighth decimal place. Zero,")
print("   with total confidence and no warning of any kind.")
print()
print("   The reason: exp(1 + 1e-300) and exp(1) are the same float64. There is")
print("   no float between them, so their difference is exactly 0.0, and 0.0")
print("   divided by anything is 0.0. The subtraction destroyed every digit the")
print("   two numbers had in common -- which was all of them.")
print()
same = math.exp(1.0 + 1e-300) == math.exp(1.0)
print(f"     exp(1 + 1e-300) == exp(1)  ->  {same}")
assert same
print()

# --------------------------------------------------------------------------
print("2. Two errors, pulling in opposite directions")
# --------------------------------------------------------------------------
print()
print("   TRUNCATION error comes from the mathematics. The formula is the")
print("   limit's approximation at a finite h, and it is wrong by roughly")
print("     forward:  (h/2)    * f''(x)")
print("     central:  (h**2/6) * f'''(x)")
print("   Both SHRINK as h shrinks. This is the term everybody knows about.")
print()
print("   ROUNDING error comes from the arithmetic. f(x+h) and f(x-h) are each")
print("   stored to about 1e-16 relative precision. Subtracting two nearly")
print("   equal numbers throws away their leading digits and leaves the noise;")
print("   dividing by a tiny h then multiplies that noise by 1/h:")
print("     either rule:  about  EPSILON * |f(x)| / h")
print("   This term GROWS as h shrinks. This is the term that surprises people.")
print()
print(f"     EPSILON (float64) = {D.EPSILON!r}")
print()
print("   Add a term that shrinks to a term that grows and you get a U. The")
print("   bottom of the U is the best h there is, and it is nowhere near zero.")
print()

# --------------------------------------------------------------------------
print("3. The measurement: 27 step sizes from 1e-1 down to 1e-14")
# --------------------------------------------------------------------------
print()
print("   f(x) = e**x at x = 1. The exact slope is e, so the error is knowable.")
print()
forward_errors = error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, forward_difference)
central_errors = error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)

print("     h            forward error   central error   central error, log-log")
scale = 3.0
for h, fe, ce in zip(D.U_WIDTHS, forward_errors, central_errors):
    exponent = math.log10(ce) if ce > 0 else -18.0
    bar_length = max(0, int(round((exponent + 12.0) * scale)))
    print(f"     {h:<12.3e} {fe:<15.6e} {ce:<15.6e} {'#' * bar_length}")
print()
print("   Read the bars. They shorten as h shrinks -- the error is falling --")
print("   reach their shortest in the middle of the table, and then lengthen")
print("   again all the way to the bottom. That is the U, drawn sideways.")
print()

# --------------------------------------------------------------------------
print("4. Where the bottom is")
# --------------------------------------------------------------------------
print()
best_forward_h, best_forward_error = best_step(D.U_WIDTHS, forward_errors)
best_central_h, best_central_error = best_step(D.U_WIDTHS, central_errors)
print(f"     forward:  best h = {best_forward_h:.3e}   error there = {best_forward_error:.6e}")
print(f"     central:  best h = {best_central_h:.3e}   error there = {best_central_error:.6e}")
print()
assert is_u_shaped(forward_errors)
assert is_u_shaped(central_errors)
assert best_central_error < best_forward_error
assert forward_errors[0] > 10.0 * best_forward_error
assert forward_errors[-1] > 10.0 * best_forward_error
assert central_errors[0] > 10.0 * best_central_error
assert central_errors[-1] > 10.0 * best_central_error
print("   Both curves are U-shaped by the test in derivatives.py: the minimum")
print("   is in the interior, and both ends are more than ten times worse than")
print("   the middle. Both facts are asserted, not eyeballed.")
print()
print("   Balancing the two error terms predicts where the bottom should be.")
print("   Setting (h/2)*e equal to EPSILON*e/h and solving gives h about")
print("   sqrt(2*EPSILON) for the forward rule; setting (h**2/6)*e equal to")
print("   EPSILON*e/h gives h about (3*EPSILON)**(1/3) for the central rule.")
print()
predicted_forward = math.sqrt(2.0 * D.EPSILON)
predicted_central = (3.0 * D.EPSILON) ** (1.0 / 3.0)
print(f"     forward:  predicted {predicted_forward:.3e}   measured {best_forward_h:.3e}")
print(f"     central:  predicted {predicted_central:.3e}   measured {best_central_h:.3e}")
print()
assert 0.1 < best_forward_h / predicted_forward < 10.0
assert 0.1 < best_central_h / predicted_central < 10.0
print("   Both measurements land within a factor of ten of the prediction, and")
print("   a factor of ten is the right expectation: the grid here has three")
print("   steps per decade, the constants in the two error terms were dropped,")
print("   and the rounding term is a random walk rather than a smooth curve.")
print("   The lab asserts the order of magnitude and reports the rest.")
print()
print("   The practical rule that falls out, for float64:")
print()
print("     forward difference   h around 1e-8")
print("     central difference   h around 1e-5 to 1e-6")
print()
print("   And the practical warning: h = 1e-12 is not a careful choice. It is")
print(f"   a worse answer than h = 1e-3, by a factor of "
      f"{central_errors[D.U_WIDTHS.index(1e-12)] / central_errors[D.U_WIDTHS.index(1e-3)]:,.0f} "
      "on this run.")
print()

# --------------------------------------------------------------------------
print("5. The noise at the bottom is real noise")
# --------------------------------------------------------------------------
print()
print("   The error does not fall smoothly to a point and rise smoothly away.")
print("   Around the minimum it jitters, because the rounding term depends on")
print("   exactly which bits happen to survive the subtraction at that h:")
print()
print("     h            central error")
for h, ce in zip(D.U_WIDTHS, central_errors):
    if 1e-8 <= h <= 1e-5:
        print(f"     {h:<12.3e} {ce:.6e}")
print()
print("   That is why the lab's U-shape test asks about the ends against the")
print("   middle rather than for a monotone descent. A test demanding smooth")
print("   monotonicity here would be a test demanding something untrue.")
print()

# --------------------------------------------------------------------------
print("6. The array version, for the plot")
# --------------------------------------------------------------------------
print()
array_errors = numpy_error_curve(D.exponential, D.U_POINT, D.U_EXACT_SLOPE, D.U_WIDTHS, central_difference)
print(f"     dtype               {array_errors.dtype}")
print(f"     shape               {array_errors.shape}")
print(f"     argmin              {int(array_errors.argmin())}")
print(f"     h at that index     {D.U_WIDTHS[int(array_errors.argmin())]:.3e}")
print(f"     same as best_step   {D.U_WIDTHS[int(array_errors.argmin())] == best_central_h}")
assert D.U_WIDTHS[int(array_errors.argmin())] == best_central_h
assert array_errors.shape == (len(D.U_WIDTHS),)
print()
print("   Same numbers, different container. The array form is what makes a")
print("   log-log plot one call, and the U is unmistakable when it is drawn.")
print()

print("05_the_u_shaped_error.py: every assertion held.")
