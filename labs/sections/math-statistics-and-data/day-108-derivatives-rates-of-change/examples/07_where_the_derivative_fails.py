"""A corner has no slope -- and the central difference will hand you one anyway.

Run from inside `examples/`:

    ../.venv/bin/python3 07_where_the_derivative_fails.py

This is the script to remember. Everything before it showed a method working.
This one shows the method being confidently, quietly wrong, on the exact shape
you will meet inside every neural network you ever train.
"""

from __future__ import annotations

import dataset as D
from derivatives import (
    backward_difference,
    central_difference,
    forward_difference,
    second_difference,
)

print("Day 108 / 07 — where no derivative exists")
print()

H = D.CORNER_WIDTH

# --------------------------------------------------------------------------
print("1. f(x) = |x| near zero")
# --------------------------------------------------------------------------
print()
print("     x        |x|")
for x in [-0.2, -0.1, 0.0, 0.1, 0.2]:
    print(f"     {x:<8.1f} {D.absolute(x):.1f}")
print()
print("   Two straight lines meeting at a point. To the left of zero the slope")
print("   is -1 everywhere. To the right it is +1 everywhere. At zero it is")
print("   neither, and there is no third answer hiding between them.")
print()
print("   The definition of the derivative asks for a single number that the")
print("   difference quotient settles on as h shrinks -- from BOTH sides. Here")
print("   the two sides settle on different numbers, so the limit does not")
print("   exist, and neither does the derivative. |x| is continuous at zero")
print("   and not differentiable at zero; those are different questions.")
print()

# --------------------------------------------------------------------------
print("2. Ask the three rules anyway")
# --------------------------------------------------------------------------
print()
forward = forward_difference(D.absolute, 0.0, H)
backward = backward_difference(D.absolute, 0.0, H)
central = central_difference(D.absolute, 0.0, H)
print(f"     forward_difference(abs, 0, {H:.0e})    {forward!r}")
print(f"     backward_difference(abs, 0, {H:.0e})   {backward!r}")
print(f"     central_difference(abs, 0, {H:.0e})    {central!r}")
print()
assert forward == D.ABS_FORWARD_AT_ZERO
assert backward == D.ABS_BACKWARD_AT_ZERO
assert central == D.ABS_CENTRAL_AT_ZERO
print("   The two one-sided rules disagree, which is the truth: they are")
print("   reporting the two different slopes that meet here, and their")
print("   disagreement is exactly the reason there is no derivative.")
print()
print("   The central rule returns 0.0. Not an error, not a warning, not a nan.")
print("   Zero, which is the average of -1 and +1, and which is the answer to a")
print("   question nobody asked. It is the average of two slopes rather than")
print("   the slope of anything.")
print()
print("   Worse, 0.0 is a plausible-looking answer. It is what you would get at")
print("   the bottom of a valley, and here it means the opposite -- the")
print("   function is changing as fast as it possibly can in both directions.")
print()
print("   Shrinking h does not help, because nothing is converging:")
print()
print("     h            forward     backward    central")
for h in [1e-2, 1e-5, 1e-8, 1e-11]:
    print(f"     {h:<12.0e} {forward_difference(D.absolute, 0.0, h):<11.1f} "
          f"{backward_difference(D.absolute, 0.0, h):<11.1f} "
          f"{central_difference(D.absolute, 0.0, h):.1f}")
    assert central_difference(D.absolute, 0.0, h) == 0.0
print()
print("   Every row is the same. There is no h small enough to reveal a limit")
print("   that is not there. Compare that with script 02, where the numbers")
print("   visibly settled -- settling is the evidence, and here there is none.")
print()

# --------------------------------------------------------------------------
print("3. The second derivative at a corner is worse still")
# --------------------------------------------------------------------------
print()
print("     h            second_difference(abs, 0, h)")
for h in [1e-2, 1e-3, 1e-5]:
    curve = second_difference(D.absolute, 0.0, h)
    print(f"     {h:<12.0e} {curve:,.1f}")
    assert abs(curve - 2.0 / h) < 1e-6 * (2.0 / h)
print()
print("   It is 2/h, so it grows without limit as h shrinks. A number that")
print("   doubles every time you halve h is not converging on anything, and")
print("   that divergence is a far better warning sign than the first")
print("   derivative's calm 0.0. If a curvature estimate explodes when you")
print("   shrink the step, you are standing on a corner.")
print()

# --------------------------------------------------------------------------
print("4. Why this is not a curiosity: ReLU")
# --------------------------------------------------------------------------
print()
print("   ReLU is max(x, 0): the most widely used activation function in deep")
print("   learning, and Day 102 already met it as a transformation. Its graph")
print("   is flat to the left of zero and a 45-degree line to the right --")
print("   the same corner as |x|, with one arm flattened.")
print()
print("     x        relu(x)")
for x in [-0.2, -0.1, 0.0, 0.1, 0.2]:
    print(f"     {x:<8.1f} {D.relu(x):.1f}")
print()
relu_forward = forward_difference(D.relu, 0.0, H)
relu_backward = backward_difference(D.relu, 0.0, H)
relu_central = central_difference(D.relu, 0.0, H)
print(f"     forward   {relu_forward!r}     the slope on the right")
print(f"     backward  {relu_backward!r}     the slope on the left")
print(f"     central   {relu_central!r}     the average of two slopes that disagree")
assert relu_forward == D.RELU_FORWARD_AT_ZERO
assert relu_backward == D.RELU_BACKWARD_AT_ZERO
assert relu_central == D.RELU_CENTRAL_AT_ZERO
print()
print("   Training a network needs a derivative of ReLU at every input,")
print("   including exactly zero. There is no derivative there, so a framework")
print("   has to choose one of 0 and 1 by convention and carry on. That is an")
print("   engineering decision rather than a mathematical result, and it is")
print("   defensible: an input that is exactly 0.0 in float64 is vanishingly")
print("   rare, and both candidate answers are finite and small.")
print()
print("   This lab does not have a deep-learning framework installed and so")
print("   makes no claim about which value any particular one picks -- check")
print("   your framework's own documentation rather than a course's memory of")
print("   it. What this lab CAN show you is that 0.5, the number the central")
print("   difference produced, is not either of the two defensible choices. If")
print("   you ever use a numerical derivative to check a framework's gradients")
print("   -- which is a real and useful technique -- it will disagree with the")
print("   framework at exactly this point, and the framework will not be wrong.")
print()

# --------------------------------------------------------------------------
print("5. Away from the corner, everything is fine")
# --------------------------------------------------------------------------
print()
print("     x        relu'(x) measured      exact   error")
for x in [-1.0, -0.5, 0.5, 1.0]:
    measured = central_difference(D.relu, x, H)
    exact = 0.0 if x < 0 else 1.0
    print(f"     {x:<8.1f} {measured!r:<22} {exact:<7.1f} {abs(measured - exact):.1e}")
    assert abs(measured - exact) < D.CENTRAL_TOL
print()
print("   On the flat left arm the answer is exactly 0.0, because both sampled")
print("   values are exactly 0.0 and their difference is exactly zero. On the")
print("   sloping right arm it is 1 to within about 2e-12, which is rounding")
print("   error and nothing else: the exact answer 1 is not exactly")
print("   representable as a difference of two nearby float64 values.")
print()
print("   The failure is at one point, not everywhere, and that is why ReLU is")
print("   usable at all. The rule to carry away: a numerical derivative always")
print("   returns a number, and returning a number is not the same as there")
print("   being one. Corners, jumps and vertical tangents all produce")
print("   confident nonsense, and none of them raises an exception.")
print()
print("   The cheapest check costs one extra call: compute the forward and")
print("   backward differences too, and if they disagree by more than the")
print("   tolerance you expect, do not trust the central one.")
print()
print("     function   forward   backward   disagree?   trust the central value?")
for label, f, x in [("x**2", D.square, 3.0), ("|x|", D.absolute, 0.0), ("relu", D.relu, 0.0)]:
    fwd = forward_difference(f, x, H)
    bwd = backward_difference(f, x, H)
    disagree = abs(fwd - bwd) > 1e-3
    print(f"     {label:<10} {fwd:<9.4f} {bwd:<10.4f} {str(disagree):<11} {'no' if disagree else 'yes'}")
print()
assert abs(forward_difference(D.square, 3.0, H) - backward_difference(D.square, 3.0, H)) < 1e-3
assert abs(forward_difference(D.absolute, 0.0, H) - backward_difference(D.absolute, 0.0, H)) > 1e-3
assert abs(forward_difference(D.relu, 0.0, H) - backward_difference(D.relu, 0.0, H)) > 1e-3
print("   That check would have caught both corners here, and it is the same")
print("   two function values the central rule already computed.")
print()

print("07_where_the_derivative_fails.py: every assertion held.")
