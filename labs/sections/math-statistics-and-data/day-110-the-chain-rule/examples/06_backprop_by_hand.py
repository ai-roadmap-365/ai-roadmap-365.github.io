"""Backpropagation through a tiny network, by hand, then by the engine.

Every number here is exact in float64, so you can check the whole backward
pass with a pen and nothing will be off in the twelfth decimal place.

Run from inside `examples/`:

    ../.venv/bin/python3 06_backprop_by_hand.py
"""

import dataset as D
import network as N

print("=" * 74)
print("1. The network")
print("=" * 74)
print()
print("      x1, x2  ->  two tanh hidden units  ->  one linear output  ->  loss")
print()
print("      a_pre = wA1*x1 + wA2*x2 + bA        a = tanh(a_pre)")
print("      b_pre = wB1*x1 + wB2*x2 + bB        b = tanh(b_pre)")
print("      out   = vA*a + vB*b + c")
print("      loss  = (out - target) squared")
print()
print("     name     value      name     value")
print("     " + "-" * 42)
print(f"     x1       {D.NET_X1:<10g} x2       {D.NET_X2:g}")
print(f"     wA1      {D.NET_WA1:<10g} wB1      {D.NET_WB1:g}")
print(f"     wA2      {D.NET_WA2:<10g} wB2      {D.NET_WB2:g}")
print(f"     bA       {D.NET_BA:<10g} bB       {D.NET_BB:.10f}")
print(f"     vA       {D.NET_VA:<10g} vB       {D.NET_VB:g}")
print(f"     c        {D.NET_C:<10g} target   {D.NET_TARGET:g}")
print()
print("  bB is half the natural logarithm of 3. That is not a magic number:")
print("  it is chosen so that tanh(bB) is exactly 0.5 in float64 and its")
print("  slope is exactly 0.75, which makes every line below checkable with")
print("  a pen. Nothing about backpropagation depends on the choice.")

assert D.NET_BB == D.HALF_LN3

print()
print("=" * 74)
print("2. The forward pass")
print("=" * 74)
print()
fw = N.forward(D.NET_X1, D.NET_X2, N.default_parameter_values())
print(f"      a_pre = 1*1 + (-0.5)*2 + 0        = {fw['a_pre']:g}")
print(f"      a     = tanh(0)                   = {fw['a']:g}")
print(f"      b_pre = (-0.5)*1 + 0.25*2 + bB    = {fw['b_pre']:.10f}")
print(f"      b     = tanh(bB)                  = {fw['b']:g}")
print(f"      out   = 2*0 + (-3)*0.5 + 1        = {fw['out']:g}")
print(f"      loss  = (-0.5 - 1) squared        = {fw['loss']:g}")

assert fw["a_pre"] == D.NET_A_PRE
assert fw["a"] == D.NET_A
assert fw["b"] == D.NET_B
assert fw["out"] == D.NET_OUT
assert fw["loss"] == D.NET_LOSS
# The two exactness claims the whole section rests on, asserted not assumed.
assert D.NET_B == 0.5
assert (1.0 - D.NET_B * D.NET_B) == 0.75

print()
print("=" * 74)
print("3. The backward pass, one local rate at a time")
print("=" * 74)
print()
print("  Start at the end. d(loss)/d(loss) is 1 -- the derivative of anything")
print("  with respect to itself. Everything else follows by multiplying.")
print()
hand = N.hand_gradients()
print("     step                        local rate            gradient")
print("     " + "-" * 62)
rows = (
    ("d loss / d out", "2 x (out - target) = 2 x (-1.5)", "out"),
    ("d loss / d c", "x 1", "c"),
    ("d loss / d vA", "x a = x 0", "vA"),
    ("d loss / d vB", "x b = x 0.5", "vB"),
    ("d loss / d a", "x vA = x 2", "a"),
    ("d loss / d b", "x vB = x (-3)", "b"),
    ("d loss / d a_pre", "x (1 - a^2) = x 1", "a_pre"),
    ("d loss / d b_pre", "x (1 - b^2) = x 0.75", "b_pre"),
    ("d loss / d wA1", "x x1 = x 1", "wA1"),
    ("d loss / d wA2", "x x2 = x 2", "wA2"),
    ("d loss / d bA", "x 1", "bA"),
    ("d loss / d wB1", "x x1 = x 1", "wB1"),
    ("d loss / d wB2", "x x2 = x 2", "wB2"),
    ("d loss / d bB", "x 1", "bB"),
)
for label, rate, key in rows:
    print(f"     {label:<26s}  {rate:<22s} {hand[key]:>9g}")
print()
print("  Two of those deserve a second look.")
print()
print(f"      d loss / d vA = {hand['vA']:g}")
print()
print("  Not small -- exactly zero. vA multiplies a, and a is exactly 0, so")
print("  nudging vA does not move the output at all. A weight feeding a unit")
print("  whose activation is zero receives no gradient and does not learn on")
print("  this step. That is not a bug in the arithmetic; it is the arithmetic")
print("  telling you something true about the network.")
print()
print(f"      d loss / d b_pre = {hand['b']:g} x 0.75 = {hand['b_pre']:g}")
print()
print("  The 0.75 is tanh's slope, and it is below 1. Every tanh unit a")
print("  gradient passes through multiplies it by a number in (0, 1]. Stack")
print("  fifty of them and script 07 shows what happens.")

print()
print("=" * 74)
print("4. The inputs, where two paths meet")
print("=" * 74)
print()
print("  x1 is used by BOTH hidden units, so it reaches the loss twice.")
print()
first, second = D.NET_X1_CONTRIBUTIONS
print(f"      through unit A:  d loss/d a_pre x wA1 = {hand['a_pre']:g} x {D.NET_WA1:g} = {first:g}")
print(f"      through unit B:  d loss/d b_pre x wB1 = {hand['b_pre']:g} x {D.NET_WB1:g} = {second:g}")
print(f"      total:           {first:g} + {second:g} = {hand['x1']:g}")
print()
print(f"      and for x2:      {hand['a_pre']:g} x {D.NET_WA2:g} + {hand['b_pre']:g} x {D.NET_WB2:g} = {hand['x2']:g}")
print()
print("  A product-only chain rule would report -6 or -3.375 here and look")
print("  entirely reasonable doing it. The measurement in section 5 settles")
print("  it, exactly as it did for the two-path graph in script 04.")

assert hand["x1"] == first + second
assert hand["x1"] == D.NET_GRADIENTS["x1"]
assert hand["x2"] == D.NET_GRADIENTS["x2"]

print()
print("=" * 74)
print("5. Three independent routes to the same sixteen numbers")
print("=" * 74)
print()
engine = N.engine_gradients()
numeric = N.numeric_parameter_gradients(D.H)
numeric.update(N.numeric_input_gradients(D.H))
print("     quantity   by hand      engine       central difference   gap")
print("     " + "-" * 64)
for key in ("wA1", "wA2", "bA", "wB1", "wB2", "bB", "vA", "vB", "c", "x1", "x2"):
    gap = abs(hand[key] - numeric[key])
    print(
        f"     {key:<10s} {hand[key]:>10g} {engine[key]:>12g} {numeric[key]:>20.9f}  {gap:.1e}"
    )
    assert hand[key] == engine[key], key
    assert abs(hand[key] - D.NET_GRADIENTS[key]) < D.ANALYTIC_TOL, key
    assert gap < D.NUMERIC_TOL, key
print()
print("  The hand column and the engine column are equal bit for bit, because")
print("  they perform the same multiplications in the same order on the same")
print("  exact values. The central-difference column is close but not equal,")
print("  and it never will be -- it is an approximation with its own error,")
print("  which is why it is compared with a tolerance a million times looser")
print("  than the one used between the first two columns.")
print()
print(f"      analytic vs analytic tolerance:  {D.ANALYTIC_TOL:g}")
print(f"      analytic vs measured tolerance:  {D.NUMERIC_TOL:g}")

print()
print("=" * 74)
print("6. What one backward pass cost")
print("=" * 74)
print()
forward_grads, forward_passes = N.forward_mode_parameter_gradients()
print(f"     reverse mode:  1 forward pass + 1 backward pass  -> all "
      f"{len(D.NET_PARAMETERS)} parameter gradients")
print(f"     forward mode:  {forward_passes} complete runs of the network "
      f"-> the same {len(D.NET_PARAMETERS)} gradients")
print(f"     central diff:  {2 * len(D.NET_PARAMETERS)} complete runs "
      "-> the same gradients, approximately")
print()
print("  Nine parameters is a toy. A model with a hundred million parameters")
print("  and one loss makes that ratio a hundred million to one, and that")
print("  single asymmetry is why training a large model is possible at all.")
for key, value in forward_grads.items():
    assert abs(value - hand[key]) < D.ANALYTIC_TOL, key
assert forward_passes == len(D.NET_PARAMETERS)

print()
print("06_backprop_by_hand.py: every assertion held.")
