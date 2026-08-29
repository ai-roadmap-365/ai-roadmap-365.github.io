"""Every parameter of a model gets a partial derivative. That collection is the gradient.

Run from inside `examples/`:

    ../.venv/bin/python3 07_one_partial_per_parameter.py
"""

from __future__ import annotations

import numpy as np

import surfaces as S
from gradients import gradient, magnitude, unit

print(__doc__.splitlines()[0])
print()

# --------------------------------------------------------------------------
print("1. The smallest thing that is honestly a model")
# --------------------------------------------------------------------------
#
# Three parameters and four invented samples. `pred = w1*a + w2*b + c`, and
# the loss is the mean of the squared differences between what the model says
# and what the target says.
#
# Nothing about this is a toy version of the idea. It IS the idea. A network
# with a hundred million parameters differs from this in exactly one respect:
# the number of parameters.

print("  Four invented samples. Nothing here was measured; the numbers were")
print("  chosen so every step below can be checked with a pencil.")
print()
print(f"    {'a':>6}  {'b':>6}  {'target':>8}")
for a, b, target in S.SAMPLES:
    print(f"    {a:6.1f}  {b:6.1f}  {target:8.1f}")

params = S.START_PARAMS
w1, w2, c = params
print()
print(f"  Parameters to start with: w1 = {w1}, w2 = {w2}, c = {c}")
print()
print(f"    {'a':>6}  {'b':>6}  {'prediction':>11}  {'target':>8}  {'residual':>9}  {'squared':>9}")
total = 0.0
for a, b, target in S.SAMPLES:
    pred = w1 * a + w2 * b + c
    residual = pred - target
    total += residual * residual
    print(f"    {a:6.1f}  {b:6.1f}  {pred:11.2f}  {target:8.1f}  {residual:9.2f}  {residual ** 2:9.2f}")
print(f"    {'':>6}  {'':>6}  {'':>11}  {'':>8}  {'sum':>9}  {total:9.2f}")
print(f"    mean squared error over {len(S.SAMPLES)} samples: {total / len(S.SAMPLES)}")
assert S.model_loss(params) == total / len(S.SAMPLES)
assert S.model_loss(params) == 22.5

# --------------------------------------------------------------------------
print()
print("2. One partial derivative per parameter")
# --------------------------------------------------------------------------
#
# The loss is a function of THREE inputs -- and they are not the data. The
# data is fixed; what varies, and what the derivative is taken with respect
# to, is the parameters. That swap is the thing worth stopping on: a and b are
# constants inside this function, and w1, w2 and c are the variables.

numeric = gradient(S.model_loss, params)
exact = S.model_loss_gradient(params)
print("  Nudge each parameter on its own, hold the other two still:")
print()
print(f"    {'parameter':>10}  {'numerical':>18}  {'exact, by hand':>15}  {'error':>11}")
for i, label in enumerate(("w1", "w2", "c")):
    print(f"    {label:>10}  {numeric[i]:18.12f}  {exact[i]:15.4f}"
          f"  {abs(numeric[i] - exact[i]):11.3e}")
    assert abs(numeric[i] - exact[i]) < S.GRADIENT_TOL

print()
print("  Working the first one by hand, to show there is no magic:")
print("    L = (1/4) sum (w1*a + w2*b + c - y)^2")
print("    dL/dw1 = (2/4) sum (w1*a + w2*b + c - y) * a       [chain rule, Day 110]")
print("           = 0.5 * ( -4*1  +  -3*2  +  -8*3  +  -1*0 )")
print("           = 0.5 * (-34)")
print("           = -17")
assert exact[0] == -17.0
assert exact[1] == -18.0
assert exact[2] == -8.0

print()
print(f"  So grad L = [{exact[0]:.0f}, {exact[1]:.0f}, {exact[2]:.0f}] -- three numbers, one per parameter,")
print("  and they are all negative, which says every parameter is currently")
print("  too small: increasing any of them increases the loss's rate of")
print("  DEcrease. Day 111 acts on that.")

# --------------------------------------------------------------------------
print()
print("3. The gradient is still just a vector, so everything from Day 99 applies")
# --------------------------------------------------------------------------

g = exact
print(f"  gradient        [{g[0]:.0f}, {g[1]:.0f}, {g[2]:.0f}]")
print(f"  length          {magnitude(g):.6f}   -- how steep the loss surface is here")
u = unit(g)
print(f"  unit gradient   [{u[0]:.6f}, {u[1]:.6f}, {u[2]:.6f}]")
print(f"  its length      {magnitude(u):.15f}")
assert abs(magnitude(u) - 1.0) < 1e-12
print()
print("  There is no picture of this one. The input space has three dimensions")
print("  and the surface would need four, which nobody can draw. Every single")
print("  statement from the two-dimensional case survives the move anyway:")
print("  the gradient points the steepest way up, its length says how steep,")
print("  and it is perpendicular to the level set -- which is now a surface")
print("  rather than a curve. That transfer is the reason the day was spent on")
print("  pictures of hills.")

# --------------------------------------------------------------------------
print()
print("4. One step against the gradient, to show it is not a claim")
# --------------------------------------------------------------------------
#
# Day 111 is the day this becomes an algorithm. But the single step can be
# taken here in three lines, and it is more convincing than any amount of
# assurance that it would work.

print(f"  {'step size':>10}  {'new parameters':>34}  {'loss':>14}  {'change':>12}")
before = S.model_loss(params)
print(f"  {'0 (start)':>10}  "
      f"{'[' + ', '.join(f'{v:9.5f}' for v in params) + ']':>34}  {before:14.8f}  {'':>12}")
improved = 0
steps = (0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2)
losses = {}
for step in steps:
    moved = np.array(params) - step * np.array(exact)
    after = S.model_loss(moved)
    shown = "[" + ", ".join(f"{v:9.5f}" for v in moved) + "]"
    print(f"  {step:10.3f}  {shown:>34}  {after:14.8f}  {after - before:+12.6f}")
    losses[step] = after
    if after < before:
        improved += 1

print()
best_step = min(losses, key=losses.get)
print(f"  {improved} of the {len(steps)} step sizes reduced the loss, and the best of them was")
print(f"  {best_step}, which brought it from {before} down to {losses[best_step]:.5f}.")
print(f"  Past that the loss climbs again -- {losses[0.2]:.5f} at a step of 0.2, which is")
print("  WORSE than where it started. So stepping against the gradient is the")
print("  right DIRECTION, and how far to go along it is a separate question")
print("  with its own name -- the learning rate -- and its own way of going")
print("  wrong. Day 111 is about both.")
assert improved >= 4
assert losses[0.2] > before
assert losses[best_step] < before
assert S.model_loss(np.array(params) - 0.001 * np.array(exact)) < before

# --------------------------------------------------------------------------
print()
print("5. The cost, and why nobody trains a model this way")
# --------------------------------------------------------------------------
#
# `gradient` calls `partial` once per input, and `partial` evaluates f twice.
# So a numerical gradient of a function of n inputs costs 2n evaluations of
# the whole function. That is the entire argument for automatic
# differentiation, and it is arithmetic rather than opinion.

class Counter:
    """Wraps a function and counts how many times it is actually called."""

    def __init__(self, f):
        self.f = f
        self.calls = 0

    def __call__(self, point):
        self.calls += 1
        return self.f(point)


counted = Counter(S.model_loss)
gradient(counted, params)
print(f"  Parameters: {len(params)}")
print(f"  Evaluations of the loss to get one gradient: {counted.calls}")
print(f"  Which is 2 per parameter: {2 * len(params)}")
assert counted.calls == 2 * len(params)

print()
print("  Now scale that. One forward pass of a model is one evaluation of the")
print("  loss, so the table below is in units of 'complete forward passes")
print("  through the entire network, over the entire batch, per single")
print("  training step':")
print()
print(f"    {'parameters':>14}  {'forward passes for ONE numerical gradient':>44}")
for n in (3, 1_000, 1_000_000, 1_000_000_000):
    print(f"    {n:>14,}  {2 * n:>44,}")

print()
print("  A million-parameter model would need two million forward passes to")
print("  take one step. Reverse-mode automatic differentiation -- what")
print("  PyTorch's autograd and JAX's grad do -- gets the whole gradient for a")
print("  cost of roughly ONE forward pass plus one backward pass, no matter")
print("  how many parameters there are, and gets it exactly rather than to")
print("  within h^2. That is not an optimisation of the method in this file.")
print("  It is a different method, and it is the reason training large models")
print("  is possible at all.")
print()
print("  None of those libraries is installed in this lab and no output from")
print("  them is reproduced anywhere in it. What numerical differentiation IS")
print("  still good for is checking one: if your hand-written backward pass")
print("  disagrees with a numerical gradient on a small example, the")
print("  hand-written one is wrong. That check has a name -- gradient")
print("  checking -- and this file is a working implementation of it.")

print()
print("07_one_partial_per_parameter.py: every assertion held.")
