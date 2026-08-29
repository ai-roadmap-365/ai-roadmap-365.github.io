"""Two functions, then three, then five. The product grows; nothing else does.

Run from inside `examples/`:

    ../.venv/bin/python3 03_deeper_chains.py
"""

import math

import dataset as D
from chainrule import (
    central_difference,
    chain_derivative,
    chain_function,
    chain_local_rates,
    chain_values,
    running_products,
)

print("=" * 74)
print("1. Depth two, three and five, side by side")
print("=" * 74)
print()
print("  The five stages, applied left to right starting from x = 1:")
print()
print("      1. double        u -> 2u")
print("      2. add three     u -> u + 3")
print("      3. square        u -> u squared")
print("      4. square root   u -> sqrt(u)")
print("      5. logarithm     u -> ln(u)")
print()
print("  Take the first two, then the first three, then all five, and watch")
print("  the derivative be the product of however many local rates there are.")
print()
print("     depth   value out        local rates                  product")
print("     " + "-" * 66)
for depth in (2, 3, 5):
    stages = D.FIVE_STAGES[:depth]
    rates = D.FIVE_RATES[:depth]
    out = chain_function(stages)(D.FIVE_START)
    local = chain_local_rates(stages, rates, D.FIVE_START)
    analytic = chain_derivative(stages, rates, D.FIVE_START)
    measured = central_difference(chain_function(stages), D.FIVE_START, D.H)
    rates_text = " x ".join(f"{r:g}" for r in local)
    print(f"     {depth}       {out:<15.10g} {rates_text:<27s} {analytic:.10g}")
    assert abs(analytic - measured) < D.NUMERIC_TOL, depth
print()
print("  Each row was also checked against a central difference of the whole")
print(f"  composed function, and every gap was below {D.NUMERIC_TOL:g}.")

print()
print("=" * 74)
print("2. The forward pass: what arrives where")
print("=" * 74)
print()
values = chain_values(D.FIVE_STAGES, D.FIVE_START)
local = chain_local_rates(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
print("     stage           input      output     local rate at that input")
print("     " + "-" * 62)
names = ("double", "add three", "square", "square root", "logarithm")
for i, name in enumerate(names):
    print(
        f"     {name:<15s} {values[i]:<10.6g} {values[i + 1]:<10.6g} {local[i]:.6g}"
    )
print()
print("  The column that matters is the last one. Stage 3's local rate is")
print("  2u, and the u it is evaluated at is 5 -- the value that ARRIVES at")
print("  stage 3, not the input x and not the final answer. Getting the")
print("  evaluation point wrong is the mistake that survives longest,")
print("  because the shape of the answer still looks right.")

assert values == list(D.FIVE_VALUES)
assert local == list(D.FIVE_LOCAL_RATES)

print()
print("=" * 74)
print("3. The product, and the same answer from an entirely different route")
print("=" * 74)
print()
analytic = chain_derivative(D.FIVE_STAGES, D.FIVE_RATES, D.FIVE_START)
print(f"     2 x 1 x 10 x 0.1 x 0.2 = {analytic}")
print()
print("  Now collapse the five stages by hand instead. Squaring and then")
print("  taking a square root of a positive number is the identity, so")
print()
print("      ln( sqrt( (2x + 3) squared ) ) = ln(2x + 3)")
print()
closed = D.d_five_chain_closed_form(D.FIVE_START)
measured = central_difference(chain_function(D.FIVE_STAGES), D.FIVE_START, D.H)
print(f"      d/dx ln(2x + 3) = 2 / (2x + 3),  at x = 1 that is {closed}")
print(f"      central difference of the five-stage chain:      {measured:.12f}")
print()
print("  Three routes -- five local rates multiplied, one collapsed formula,")
print("  and a measurement that knows about none of it -- agree.")

assert analytic == D.FIVE_DERIVATIVE
assert abs(closed - D.FIVE_DERIVATIVE) < D.ANALYTIC_TOL
assert abs(measured - D.FIVE_DERIVATIVE) < D.NUMERIC_TOL

print()
print("=" * 74)
print("4. What a backward pass is actually carrying")
print("=" * 74)
print()
carried = running_products(local)
print("  Walk the chain from the output end, multiplying as you go. After")
print("  k steps the number in your hand is the product of the last k local")
print("  rates -- which is exactly the gradient of the output with respect")
print("  to the value arriving at that stage.")
print()
print("     stage           value in    d(output)/d(that value)")
print("     " + "-" * 55)
for i, name in enumerate(names):
    print(f"     {name:<15s} {values[i]:<11.6g} {carried[i]:.10g}")
print()
print("  Read the last row upwards. The logarithm stage sees 0.2; the square")
print("  root stage sees 0.02; and by the time the walk reaches the input")
print(f"  the number is {carried[0]:.6g}, which is the answer.")
print()
print("  That is the entire backward pass. One walk, one multiplication per")
print("  stage, and every intermediate gradient computed on the way past --")
print("  not one walk per stage. Script 07 measures what that saves.")

assert abs(carried[0] - D.FIVE_DERIVATIVE) < D.ANALYTIC_TOL
assert carried[-1] == D.FIVE_LOCAL_RATES[-1]

print()
print("=" * 74)
print("5. A note on the order of the multiplications")
print("=" * 74)
print()
left_to_right = analytic
right_to_left = carried[0]
print(f"     multiplied forwards:  {left_to_right!r}")
print(f"     multiplied backwards: {right_to_left!r}")
print(f"     they differ by:       {abs(left_to_right - right_to_left):.3e}")
print()
print("  Float64 multiplication is not associative, so the two orders can")
print("  land on different bit patterns. The gap here is one unit in the")
print("  last place and it is reported rather than hidden, because a lab")
print(f"  that compared these with == would be lying. The tolerance used is")
print(f"  {D.ANALYTIC_TOL:g}, which is for two analytic routes to the same")
print("  number, and it is a thousand times tighter than the tolerance used")
print("  against a measured derivative.")

assert abs(left_to_right - right_to_left) < D.ANALYTIC_TOL
assert math.isfinite(left_to_right)

print()
print("03_deeper_chains.py: every assertion held.")
