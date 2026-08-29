"""Composition first, then the chain rule, then the rule checked by measurement.

Run from inside `examples/`:

    ../.venv/bin/python3 02_composition_and_the_chain_rule.py
"""

import dataset as D
from chainrule import central_difference, chain_rule, compose

print("=" * 74)
print("1. Composition, with numbers and no derivatives at all")
print("=" * 74)
print()
print("  Two ordinary functions:")
print()
print("      g(x) = 3x + 1        the inner function, runs first")
print("      f(u) = u squared     the outer function, runs on g's answer")
print()
print("  Composing them means feeding one into the other:")
print()
print("      f(g(x)) = (3x + 1) squared")
print()
print("  At x = 2, in the order the arithmetic actually happens:")
print()
inner_value = D.line(2.0)
outer_value = D.square(inner_value)
print(f"      g(2)     = 3*2 + 1 = {inner_value}")
print(f"      f(g(2))  = {inner_value} squared = {outer_value}")
print()
print("  Read the parentheses inside out. The inner function runs first even")
print("  though it is written second, which is the one piece of bookkeeping")
print("  that trips people up before any calculus arrives.")

assert inner_value == 7.0
assert outer_value == 49.0
assert compose(D.square, D.line)(2.0) == 49.0

print()
print("=" * 74)
print("2. Now ask how fast the answer moves")
print("=" * 74)
print()
print("  Nudge x a little. Two things happen in sequence:")
print()
print("      x moves by 1 unit    ->  u = g(x) moves by 3 units")
print("      u moves by 1 unit    ->  y = f(u) moves by 2u = 14 units")
print()
print("  So x moving by 1 moves y by 3 x 14 = 42. The rates multiplied,")
print("  exactly as the gears did.")
print()
print("      dy/dx = dy/du x du/dx = 14 x 3 = 42")
print()
print("  The single most common mistake in this line is evaluating the")
print("  outer derivative at x instead of at u. f'(u) = 2u, and u is 7 here,")
print("  not 2. Using x would give 2*2 = 4 and an answer of 12, which is")
print("  wrong by more than a factor of three.")
print()
d_outer_at_u = D.d_square(inner_value)
d_outer_at_x_wrong = D.d_square(2.0)
print(f"      f'(u) at u = 7  ->  {d_outer_at_u}   correct")
print(f"      f'(x) at x = 2  ->  {d_outer_at_x_wrong}    the mistake")
print(f"      correct answer   ->  {d_outer_at_u} x 3 = {d_outer_at_u * 3.0}")
print(f"      the mistake gives -> {d_outer_at_x_wrong} x 3 = {d_outer_at_x_wrong * 3.0}")

assert d_outer_at_u == 14.0
assert d_outer_at_u * 3.0 == 42.0
assert d_outer_at_x_wrong * 3.0 == 12.0

print()
print("=" * 74)
print("3. Six compositions, each checked against a central difference")
print("=" * 74)
print()
print("  The central difference from Day 108 knows nothing about the chain")
print("  rule. It moves x by a hair and watches the output move. That")
print("  independence is what makes it a real check rather than a restatement.")
print()
print(f"  Step size h = {D.H:g}, tolerance {D.NUMERIC_TOL:g}.")
print()
print("     composition                 chain rule      measured        gap")
print("     " + "-" * 63)
for case in D.COMPOSITIONS:
    analytic = chain_rule(case.d_outer, case.inner, case.d_inner, case.x)
    measured = central_difference(compose(case.outer, case.inner), case.x, D.H)
    gap = abs(analytic - measured)
    print(
        f"     {case.name:<26s} {analytic:>13.9f} {measured:>13.9f}  {gap:.2e}"
    )
    assert abs(analytic - case.exact) < D.ANALYTIC_TOL, case.name
    assert gap < D.NUMERIC_TOL, case.name
print()
print("  Every gap is around 1e-10 or smaller, which is the central")
print("  difference's own error and not a disagreement about the rule.")

print()
print("=" * 74)
print("4. Two of those six are worth naming")
print("=" * 74)
print()
sigmoid_case = D.COMPOSITIONS[4]
sigmoid_slope = chain_rule(
    sigmoid_case.d_outer, sigmoid_case.inner, sigmoid_case.d_inner, 0.0
)
print("  'the sigmoid' is 1 / (1 + e to the minus x), which is a composition")
print("  of a reciprocal with an exponential. Its slope at 0 is")
print()
print(f"      dy/dx = (-1/4) x (-1) = {sigmoid_slope}")
print()
print("  and 0.25 is the LARGEST slope the sigmoid ever has. Every other")
print("  point is shallower. Stack fifty sigmoid layers and you are")
print("  multiplying fifty numbers no bigger than 0.25. Script 07 does that")
print("  arithmetic; this is where the answer comes from.")
print()
tanh_case = D.COMPOSITIONS[5]
tanh_slope = chain_rule(
    tanh_case.d_outer, tanh_case.inner, tanh_case.d_inner, -0.5
)
print("  'tanh of a line' is tanh(2x + 1) at x = -0.5, where the inner")
print("  function is exactly 0. tanh'(0) = 1 - tanh(0) squared = 1, so the")
print(f"  whole answer is 1 x 2 = {tanh_slope}, exactly. That exactness is")
print("  used again in script 06 to make a whole backward pass checkable")
print("  with a pen.")

assert sigmoid_slope == 0.25
assert tanh_slope == 2.0

print()
print("02_composition_and_the_chain_rule.py: every assertion held.")
