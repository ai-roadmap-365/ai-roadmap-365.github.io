"""The reverse-mode engine, exercised and checked against measurements.

Run from inside `examples/`:

    ../.venv/bin/python3 05_the_value_engine.py
"""

import math

import dataset as D
from autodiff import (
    Value,
    graph_size,
    numeric_gradient,
    reverse_mode_gradient,
    topological_order,
)
from chainrule import central_difference

print("=" * 74)
print("1. The smallest possible graph")
print("=" * 74)
print()
print("      a = 3,  b = 4,  c = a x b")
print()
a = Value(3.0, label="a")
b = Value(4.0, label="b")
c = a * b
c.backward()
print(f"      c.data = {c.data}")
print(f"      a.grad = {a.grad}   <- dc/da, which is b")
print(f"      b.grad = {b.grad}   <- dc/db, which is a")
print()
print("  For a product, each input's local rate is the other input's value.")
print("  Nudge a by one and c moves by b. That is the whole `__mul__`")
print("  backward step, and it took two lines to write.")

assert c.data == 12.0
assert a.grad == 4.0
assert b.grad == 3.0

print()
print("=" * 74)
print("2. A value used twice: where the += earns its keep")
print("=" * 74)
print()
print("      x = 3,  y = x + x")
print()
x = Value(3.0, label="x")
y = x + x
y.backward()
print(f"      y.data = {y.data}")
print(f"      x.grad = {x.grad}")
print()
print("  x receives a contribution from each of its two uses, and they add.")
print("  If the engine assigned the gradient instead of accumulating it, the")
print("  second contribution would overwrite the first and this would print")
print("  1.0 -- a plausible-looking, confidently wrong number. That is the")
print("  same sum-over-paths fact as script 04, now as one character of code.")
print()
print("  The same thing with a multiplication, where the answer is less")
print("  obvious:")
print()
print("      x = 3,  y = x x x")
x2 = Value(3.0, label="x")
y2 = x2 * x2
y2.backward()
print(f"      y.data = {y2.data},  x.grad = {x2.grad}   <- 2x, the power rule")
print()
print("  The engine has never heard of the power rule. It applied the product")
print("  rule and added the two contributions, and the power rule fell out.")

assert y.data == 6.0
assert x.grad == 2.0
assert y2.data == 9.0
assert x2.grad == 6.0

print()
print("=" * 74)
print("3. The topological order, and why it cannot be skipped")
print("=" * 74)
print()
p = Value(2.0, label="p")
q = Value(-3.0, label="q")
r = p * q
s = r + p
out = s.tanh()
order = topological_order(out)
print("      p = 2,  q = -3,  r = p x q,  s = r + p,  out = tanh(s)")
print()
print("     position   node")
print("     " + "-" * 46)
for i, node in enumerate(order):
    name = node.label or node._op or "const"
    print(f"     {i}          {name:<10s} data = {node.data:.6g}")
print()
print("  Every node sits after everything it was computed from, so walking")
print("  the list backwards guarantees a node has received all of its")
print("  gradient before it passes any of it on. p is used twice -- once by")
print("  r and once by s -- and if s handed its gradient to p before r had")
print("  finished, p's total would be short by one path.")
print()
out.backward()
print(f"      out.data = {out.data:.12f}")
print(f"      p.grad   = {p.grad:.12f}")
print(f"      q.grad   = {q.grad:.12f}")
print()


def scalar_out(pv: float) -> float:
    """The same expression in plain floats, for a central difference."""
    return math.tanh(pv * -3.0 + pv)


measured_p = central_difference(scalar_out, 2.0, D.H)
print(f"      central difference for p: {measured_p:.12f}")
print(f"      gap: {abs(p.grad - measured_p):.3e}")

assert graph_size(out) == len(order)
assert abs(p.grad - measured_p) < D.NUMERIC_TOL

print()
print("=" * 74)
print("4. Four expressions, each differentiated two independent ways")
print("=" * 74)
print()
print("  The engine only has +, x and tanh, so it cannot build a sine or a")
print("  logarithm. What it CAN build is any polynomial and any tanh network,")
print("  which is enough to check it hard. Every gradient below is produced")
print("  by the engine and then measured with a central difference that")
print("  knows nothing about the graph.")
print()


def expr1(vals):
    (xv,) = vals
    return (3.0 * xv + 1.0) * (3.0 * xv + 1.0)


def expr2(vals):
    (xv,) = vals
    return (xv * xv * xv) + (-2.0) * xv


def expr4(vals):
    xv, yv = vals
    return (xv * yv + xv) * (yv + 3.0)


def expr5(vals):
    xv, yv, zv = vals
    return ((xv * yv).tanh() * zv + xv * zv) * (1.0 + yv)


CASES = (
    ("(3x + 1) squared            ", expr1, [2.0]),
    ("x cubed - 2x                ", expr2, [1.5]),
    ("(xy + x)(y + 3)             ", expr4, [2.0, -1.0]),
    ("tanh(xy)z + xz, times (1+y) ", expr5, [0.7, 0.4, -1.3]),
)

print("     expression                     input   engine grad     measured")
print("     " + "-" * 68)
for label, build, point in CASES:

    def plain(vals, build=build):
        node = build([Value(v) for v in vals])
        return node.data

    grads, passes = reverse_mode_gradient(build, point)
    numeric, num_passes = numeric_gradient(plain, point, D.H)
    for i, (g, n) in enumerate(zip(grads, numeric)):
        shown = label if i == 0 else " " * len(label)
        print(f"     {shown} {point[i]:>7.4g} {g:>14.9f} {n:>14.9f}")
        assert abs(g - n) < D.NUMERIC_TOL + D.NUMERIC_REL_TOL * abs(n), label
    assert passes == 1, label
    assert num_passes == 2 * len(point), label
print()
print("  Every engine gradient agrees with a central difference of the same")
print("  expression to within the numerical rule's own error. The engine had")
print("  no formula for any of these functions -- it composed +, x and tanh")
print("  and let the chain rule do the rest.")
print()
print("  Note the pass counts, which the assertions above also check: the")
print("  engine used ONE forward-and-backward sweep per expression no matter")
print("  how many inputs it had, and the central difference needed two")
print("  evaluations per input. Script 07 makes that gap the point.")

print()
print("=" * 74)
print("5. A tanh identity the engine reproduces without being told")
print("=" * 74)
print()
z = Value(0.6, label="z")
t = z.tanh()
t.backward()
print("      z = 0.6,  t = tanh(z)")
print(f"      t.data = {t.data:.12f}")
print(f"      z.grad = {z.grad:.12f}")
print(f"      1 - t squared = {1.0 - t.data * t.data:.12f}")
print()
print("  The derivative of tanh is 1 - tanh squared, and the engine's")
print("  backward step for tanh is literally that expression -- reusing the")
print("  forward value rather than recomputing anything. Every framework does")
print("  this, and it is why a backward pass needs the forward pass's values")
print("  kept in memory. That memory cost is the price reverse mode pays for")
print("  its speed, and on a large model it is the dominant one.")

assert abs(z.grad - (1.0 - t.data * t.data)) < D.ANALYTIC_TOL
assert abs(t.data - math.tanh(0.6)) < D.ANALYTIC_TOL

print()
print("05_the_value_engine.py: every assertion held.")
