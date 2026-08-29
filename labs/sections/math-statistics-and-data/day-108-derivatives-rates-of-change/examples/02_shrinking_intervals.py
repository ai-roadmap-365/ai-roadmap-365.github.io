"""Shrink the interval and watch the answer settle. That settling is the limit.

Run from inside `examples/`:

    ../.venv/bin/python3 02_shrinking_intervals.py
"""

from __future__ import annotations

import dataset as D
from derivatives import average_rate, shrinking_slopes, tangent_at

print("Day 108 / 02 — the shrinking interval")
print()

# --------------------------------------------------------------------------
print("1. The car again, at t = 3, over intervals that get smaller")
# --------------------------------------------------------------------------
print()


def distance(t: float) -> float:
    return 4.0 * t * t


print("     width h    interval          average speed (m/s)")
for h in [1.0, 0.5, 0.1, 0.01, 0.001, 0.0001]:
    speed = average_rate(distance, 3.0, 3.0 + h)
    print(f"     {h:<10.4f} [3, {3.0 + h:<8.4f}]   {speed:19.6f}")
print()
print("   The numbers are 24 + 4h, and you can see them heading for 24 without")
print("   being told. Nobody computed a limit here; the sequence was watched.")
print()

# --------------------------------------------------------------------------
print("2. The same thing on f(x) = x**2 at x = 3, with the algebra shown")
# --------------------------------------------------------------------------
print()
print("     f(3 + h) - f(3)     (3 + h)**2 - 9      9 + 6h + h**2 - 9")
print("     ----------------  =  --------------  =  ------------------  =  6 + h")
print("            h                   h                    h")
print()
slopes = shrinking_slopes(D.square, D.SETTLE_POINT, D.SETTLE_WIDTHS)
print("     width h        secant slope     exactly 6 + h?   distance from 6")
for h, slope, expected in zip(D.SETTLE_WIDTHS, slopes, D.SETTLE_EXPECTED_SLOPES):
    matches = abs(slope - expected) < D.EXACT_TOL
    print(f"     {h:<12.4f}   {slope:<16.12f} {str(matches):<16} {abs(slope - 6.0):.4f}")
    assert matches, (h, slope, expected)
print()
print("   Two facts sit in that table and they are not the same fact.")
print()
print("   The first is that the slope over [3, 3 + h] is 6 + h EXACTLY, for")
print("   every h, with no approximation anywhere. That is algebra.")
print()
print("   The second is that as h shrinks, 6 + h gets arbitrarily close to 6.")
print("   That is the limit, and it is why the derivative of x**2 at 3 is 6.")
print()
print("   Notice what the algebra did that the arithmetic could not: it")
print("   cancelled the h in the denominator BEFORE h was allowed to reach")
print("   zero. At h = 0 the fraction is 0/0 and means nothing; the simplified")
print("   form 6 + h means something at every h including zero.")
print()

# --------------------------------------------------------------------------
print("3. The floating-point version of the same sequence is not exact")
# --------------------------------------------------------------------------
print()
print("     h            computed slope          6 + h            gap")
for h, slope, expected in zip(D.SETTLE_WIDTHS, slopes, D.SETTLE_EXPECTED_SLOPES):
    print(f"     {h:<12.4f} {slope!r:<24} {expected:<16.4f} {abs(slope - expected):.3e}")
print()
print("   The gaps are around 1e-13, and they are not mistakes in the formula.")
print("   They are the arithmetic: 3.001**2 cannot be stored exactly in binary,")
print("   the subtraction loses some of the digits the two numbers had in")
print("   common, and dividing by 0.001 multiplies what is left by a thousand.")
print("   Script 05 measures that effect properly, because it is the reason a")
print("   smaller h eventually makes a numerical derivative WORSE.")
print()

# --------------------------------------------------------------------------
print("4. Secants approaching a tangent")
# --------------------------------------------------------------------------
print()
print("   Each row is a straight line through (3, 9) and one other point on")
print("   the curve. As the other point slides in, the line pivots.")
print()
def line_text(slope: float, intercept: float) -> str:
    """y = mx + c, written with the sign of c folded into the operator."""
    sign = "-" if intercept < 0 else "+"
    return f"y = {slope:.2f}x {sign} {abs(intercept):.2f}"


print("     h        second point           slope    line through (3, 9)")
for h in [2.0, 1.0, 0.5, 0.1]:
    x2 = 3.0 + h
    slope = average_rate(D.square, 3.0, x2)
    intercept = 9.0 - slope * 3.0
    print(f"     {h:<8.2f} ({x2:.2f}, {D.square(x2):7.4f})       {slope:6.2f}   {line_text(slope, intercept)}")
print()
tangent_slope, tangent_intercept = tangent_at(D.square, 3.0, 1e-5)
print(f"     tangent (h -> 0)                       {tangent_slope:6.2f}   "
      f"{line_text(round(tangent_slope, 2), round(tangent_intercept, 2))}")
assert abs(tangent_slope - 6.0) < D.CENTRAL_TOL
assert abs(tangent_intercept - (-9.0)) < 1e-8
print()
print("   The tangent is not 'the line that touches the curve once' -- plenty")
print("   of lines do that and are not tangents. It is the line the secants")
print("   approach, and its slope is the derivative. y = 6x - 9 touches the")
print("   parabola at x = 3 and matches its direction there.")
print()

print("02_shrinking_intervals.py: every assertion held.")
