"""The handful of rules you actually need, each one checked against a number.

Run from inside `examples/`:

    ../.venv/bin/python3 03_rules_checked_numerically.py

A rule you have only been told is a rule you cannot check. Every one below is
stated, then computed numerically at a point, then compared.
"""

from __future__ import annotations

import math

import dataset as D
from derivatives import central_difference

print("Day 108 / 03 — the rules, and the numbers that agree with them")
print()

# --------------------------------------------------------------------------
print("1. Notation, defined once")
# --------------------------------------------------------------------------
print()
print("   Three ways of writing the same object, all in current use:")
print()
print("     f'(x)     'f prime of x'. Lagrange's notation. Compact, and the")
print("               one to reach for when the input variable is obvious.")
print("     dy/dx     Leibniz's notation, read 'dee y by dee x'. It names the")
print("               two variables, which matters the moment there is more")
print("               than one input -- Day 109's whole subject.")
print("     Df(x)     Euler's operator notation. You will meet it in papers.")
print()
print("   dy/dx is not a fraction, although it is descended from one and")
print("   behaves like one often enough to be dangerous. Read it as: the rate")
print("   at which y changes with respect to x.")
print()

# --------------------------------------------------------------------------
print("2. The rules")
# --------------------------------------------------------------------------
print()
print("     constant           d/dx of c          =  0")
print("     power              d/dx of x**n       =  n * x**(n-1)")
print("     constant multiple  d/dx of c * f(x)   =  c * f'(x)")
print("     sum                d/dx of f(x)+g(x)  =  f'(x) + g'(x)")
print("     exponential        d/dx of e**x       =  e**x")
print("     logarithm          d/dx of ln(x)      =  1/x")
print()
print("   The first four are worth understanding. The constant rule says a")
print("   flat line has no slope. The power rule generalises the (3+h)**2")
print("   expansion from script 02: multiply out, cancel the h, and what")
print("   survives is n * x**(n-1). The constant-multiple rule says stretching")
print("   a graph vertically by 5 stretches every slope by 5. The sum rule says")
print("   rates add, which is why it is safe to differentiate a long expression")
print("   one term at a time.")
print()
print("   The last two are facts to know. They are not obvious and today does")
print("   not derive them.")
print()

# --------------------------------------------------------------------------
print("3. Every rule, checked at a point")
# --------------------------------------------------------------------------
print()
print(f"   Numerically, with the central difference at h = {D.COMPARE_WIDTH}.")
print("   'exact' is what the rule says. 'measured' is what the arithmetic")
print("   says without knowing the rule.")
print()
print("     rule                                        at x    exact          measured       error")
for (name, f, exact_derivative, x), expected in zip(D.RULE_CASES, D.RULE_EXPECTED):
    exact = exact_derivative(x)
    measured = central_difference(f, x, D.COMPARE_WIDTH)
    error = abs(measured - exact)
    print(f"     {name:<42}  {x:<6.2f}  {exact:<14.9f} {measured:<14.9f} {error:.2e}")
    assert exact == expected or abs(exact - expected) < 1e-15, (name, exact, expected)
    assert error < D.RULE_TOL, (name, error)
print()
print(f"   Every error is below {D.RULE_TOL:.0e}, and that ceiling was not chosen by")
print("   running the check and enlarging the number until it passed. The")
print("   central difference's truncation error is about h**2/6 times the third")
print("   derivative; the worst case here is x**5 at 1.5, where the third")
print("   derivative is 135, giving 1e-10/6 * 135 = 2.25e-9. The ceiling is")
print("   four times that. See dataset.py, which shows the arithmetic.")
print()

# --------------------------------------------------------------------------
print("4. Why e is the special one")
# --------------------------------------------------------------------------
print()
print("   Take b**x for various bases and measure its slope at x = 0.")
print("   The value at x = 0 is 1 for every base, so the slope is the only")
print("   thing that distinguishes them.")
print()
print("     base b        f(0)      f'(0) measured")
ratios = {}
for base in [2.0, 2.5, math.e, 3.0, 10.0]:
    def power_of(x: float, b: float = base) -> float:
        return b**x

    slope = central_difference(power_of, 0.0, D.COMPARE_WIDTH)
    ratios[base] = slope
    label = "e = 2.718..." if base == math.e else f"{base}"
    print(f"     {label:<13} {power_of(0.0):<9.1f} {slope:.9f}")
print()
assert ratios[2.0] < 1.0 < ratios[3.0]
assert abs(ratios[math.e] - 1.0) < D.CENTRAL_TOL
print("   For base 2 the slope at 0 is less than 1. For base 3 it is more than")
print("   1. Somewhere between them is a base whose slope at 0 is EXACTLY 1,")
print("   and that base is e. Measured here as", f"{ratios[math.e]:.12f}.")
print()
print("   That is what makes e**x its own derivative. Every b**x is")
print("   proportional to its own derivative -- the graph's steepness is always")
print("   proportional to its height -- and e is the base for which the")
print("   constant of proportionality is 1 rather than 0.693 or 1.099.")
print()
print("   Check the proportionality directly, at three different points:")
print()
print("     x       e**x            measured f'(x)   ratio f'(x) / f(x)")
for x in [0.0, 1.0, 2.5]:
    value = math.exp(x)
    slope = central_difference(math.exp, x, D.COMPARE_WIDTH)
    ratio = slope / value
    print(f"     {x:<7.1f} {value:<15.9f} {slope:<16.9f} {ratio:.12f}")
    assert abs(ratio - 1.0) < 1e-9, (x, ratio)
print()
print("   The ratio is 1 everywhere, which is the whole claim.")
print()

print("03_rules_checked_numerically.py: every assertion held.")
