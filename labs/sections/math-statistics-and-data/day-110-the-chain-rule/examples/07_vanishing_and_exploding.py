"""Fifty factors below one collapse. Fifty above one blow up. Same rule.

Run from inside `examples/`:

    ../.venv/bin/python3 07_vanishing_and_exploding.py
"""

import dataset as D
from autodiff import (
    Value,
    forward_mode_gradient,
    numeric_gradient,
    reverse_mode_gradient,
)
from chainrule import order_of_magnitude, product_trace, repeated_product

print("=" * 74)
print("1. A gradient walking back through fifty layers")
print("=" * 74)
print()
print("  The chain rule says the gradient at the far end of a chain is the")
print("  product of every local rate on the way. If each layer contributes a")
print("  rate of 0.9, the product is 0.9 to the fiftieth power. If each")
print("  contributes 1.1, it is 1.1 to the fiftieth.")
print()
print("  Neither factor looks alarming. Watch anyway.")
print()
decay = repeated_product(D.DECAY_FACTOR, D.CHAIN_LENGTH)
growth = repeated_product(D.GROWTH_FACTOR, D.CHAIN_LENGTH)
decay_trace = product_trace(D.DECAY_FACTOR, D.CHAIN_LENGTH)
growth_trace = product_trace(D.GROWTH_FACTOR, D.CHAIN_LENGTH)
print("     layers      x 0.9 each        x 1.1 each")
print("     " + "-" * 48)
for n in (1, 5, 10, 20, 30, 40, 50):
    print(f"     {n:<11d} {decay_trace[n - 1]:<17.6e} {growth_trace[n - 1]:.6e}")
print()
print(f"  After {D.CHAIN_LENGTH} layers the shrinking chain has lost more than")
print("  two orders of magnitude and the growing one has gained more than two.")
print("  The early layers of the shrinking network receive a gradient a few")
print("  thousandths the size of the one the last layer receives, so they")
print("  learn a few thousandths as fast. They are not broken. They are slow")
print("  by a factor nobody budgeted for.")
print()
print("  Asserted as orders of magnitude, not as digits -- the scale is the")
print("  lesson and the digits are float64 rounding:")
print()
print(f"      0.9 ** 50 = {decay:.6e}   order {order_of_magnitude(decay)}")
print(f"      1.1 ** 50 = {growth:.6e}   order {order_of_magnitude(growth)}")

assert order_of_magnitude(decay) == D.DECAY_ORDER
assert order_of_magnitude(growth) == D.GROWTH_ORDER
assert decay < 1e-2
assert growth > 1e2

print()
print("=" * 74)
print("2. Deeper, and harsher")
print("=" * 74)
print()
print("     factor   layers    product            order    lost in a weight of 1?")
print("     " + "-" * 68)
weight = 1.0
for factor, count in (
    (D.DECAY_FACTOR, D.LONG_CHAIN_LENGTH),
    (D.GROWTH_FACTOR, D.LONG_CHAIN_LENGTH),
    (D.MILD_DECAY, D.CHAIN_LENGTH),
    (D.SHARP_DECAY, D.CHAIN_LENGTH),
    (D.SHARP_GROWTH, D.CHAIN_LENGTH),
):
    value = repeated_product(factor, count)
    lost = "yes" if weight + value == weight else "no"
    print(
        f"     {factor:<8g} {count:<9d} {value:<18.6e} "
        f"{order_of_magnitude(value):<8d} {lost}"
    )
print()
mild = repeated_product(D.MILD_DECAY, D.CHAIN_LENGTH)
sharp = repeated_product(D.SHARP_DECAY, D.CHAIN_LENGTH)
print("  The last column asks a blunt question: if this were the gradient")
print("  and you added it to a weight of about 1, would the weight change at")
print("  all, or would the update disappear into rounding?")
print()
print("  The 0.5 row is worth pausing on, because the obvious guess about it")
print("  is wrong. Fifty halvings give")
print()
print(f"      0.5 ** 50 = {mild:.6e},  which is {mild / D.EPSILON:g} x EPSILON")
print()
print(f"  EPSILON here is {D.EPSILON:.6e}, the gap between 1.0 and the next")
print("  float64 above it. So this gradient is four of those gaps wide and it")
print("  DOES still move a weight of 1. It takes about three more halvings to")
print("  disappear -- 0.5 to the 53rd is half an EPSILON, and half a gap")
print("  rounds away to nothing.")
print()
print("  The row underneath is the one that actually vanishes. 0.25 is the")
print("  largest slope the sigmoid ever has, measured back in script 02, so a")
print("  stack of sigmoid layers is multiplying numbers no bigger than this:")
print()
print(f"      0.25 ** 50 = {sharp:.6e}")
print(f"      1.0 + {sharp:.6e} == 1.0  ->  {weight + sharp == weight}")
print()
print("  That is not a metaphor for a vanishing gradient. It is one, and the")
print("  factor being used is the sigmoid at its most generous rather than at")
print("  anything like a typical value.")

assert order_of_magnitude(repeated_product(D.DECAY_FACTOR, D.LONG_CHAIN_LENGTH)) == -10
assert order_of_magnitude(repeated_product(D.GROWTH_FACTOR, D.LONG_CHAIN_LENGTH)) == 8
# Measured, and it contradicts the obvious guess: four EPSILONs still counts.
assert mild == 4.0 * D.EPSILON
assert weight + mild != weight
assert repeated_product(D.MILD_DECAY, 53) == 0.5 * D.EPSILON
assert weight + repeated_product(D.MILD_DECAY, 53) == weight
# And the sigmoid's best case, which does not.
assert sharp < D.EPSILON
assert weight + sharp == weight

print()
print("=" * 74)
print("3. The same collapse, through the real engine")
print("=" * 74)
print()
print("  Nothing above needed the autodiff engine, so it could be accused of")
print("  being a story about exponents. Build the chain for real instead:")
print("  fifty multiplications by 0.9, differentiated by one backward pass.")
print()


def deep_chain(vals):
    (xv,) = vals
    node = xv
    for _ in range(D.CHAIN_LENGTH):
        node = node * D.DECAY_FACTOR
    return node


grads, passes = reverse_mode_gradient(deep_chain, [1.0])
print(f"      engine gradient after {D.CHAIN_LENGTH} layers: {grads[0]:.6e}")
print(f"      0.9 ** {D.CHAIN_LENGTH} for comparison:        {decay:.6e}")
print(f"      backward passes used:                {passes}")
print()
print("  The engine reproduces the collapse exactly, because the collapse IS")
print("  the chain rule. Nothing has gone wrong; the arithmetic is correct")
print("  and the answer is useless. Those are different complaints, and")
print("  every fix the course reaches later -- careful initialisation,")
print("  residual connections, normalisation, gradient clipping, ReLU in")
print("  place of a saturating non-linearity -- is an attempt to keep this")
print("  product near 1 rather than to make the chain rule behave otherwise.")

assert abs(grads[0] - decay) < D.ANALYTIC_TOL
assert passes == 1

print()
print("=" * 74)
print("4. Forward mode against reverse mode, counted")
print("=" * 74)
print()
print("  Both modes apply the same chain rule. They differ in which end they")
print("  start from, and that decides the cost.")
print()


def many_inputs(vals):
    """One output built from every input, with a non-linearity in the way."""
    total = vals[0] * 1.0
    for value in vals[1:]:
        total = total + value * value
    return (total * 0.1).tanh()


print("     inputs   reverse passes   forward passes   central-diff passes")
print("     " + "-" * 66)
for n in (1, 2, 5, 10, 25):
    point = [0.1 * (i + 1) for i in range(n)]

    def plain(vals):
        return many_inputs([Value(v) for v in vals]).data

    r_grads, r_passes = reverse_mode_gradient(many_inputs, point)
    f_grads, f_passes = forward_mode_gradient(many_inputs, point)
    n_grads, n_passes = numeric_gradient(plain, point, D.H)
    print(f"     {n:<8d} {r_passes:<16d} {f_passes:<16d} {n_passes}")
    for i in range(n):
        assert abs(r_grads[i] - f_grads[i]) < D.ANALYTIC_TOL, (n, i)
        assert abs(r_grads[i] - n_grads[i]) < D.NUMERIC_TOL, (n, i)
    assert r_passes == 1
    assert f_passes == n
    assert n_passes == 2 * n
print()
print("  All three columns produce the same gradients -- the first two")
print("  agree to the last bit, and the third to about a part in a billion.")
print("  Only the cost differs, and it differs by a factor that grows with")
print("  the number of inputs.")
print()
print("  So the rule of thumb is not about elegance, it is about shape:")
print()
print("      many inputs, one output   ->  reverse mode  (training a model)")
print("      one input, many outputs   ->  forward mode  (sensitivity to a")
print("                                    single parameter)")
print()
print("  Training a model is the first shape: millions of parameters in, one")
print("  scalar loss out. Reverse mode gets every gradient for roughly the")
print("  cost of two forward passes, and that is the entire economic basis")
print("  of modern machine learning.")

print()
print("=" * 74)
print("5. What reverse mode pays for it")
print("=" * 74)
print()
print("  Reverse mode has to keep the forward pass's intermediate values")
print("  alive until the backward pass consumes them, because the local")
print("  derivatives are written in terms of those values -- tanh's backward")
print("  step needs the tanh output, and a product's needs both inputs.")
print()
node = Value(1.0)
for _ in range(D.CHAIN_LENGTH):
    node = node * D.DECAY_FACTOR
from autodiff import graph_size  # noqa: E402  (imported here to keep it visible)

print(f"      a {D.CHAIN_LENGTH}-layer chain holds {graph_size(node)} nodes alive")
print()
print("  Forward mode holds almost nothing, which is its one real advantage.")
print("  On a large model the stored activations dominate memory use, and")
print("  that is why techniques for trading recomputation against memory")
print("  exist at all. The chain rule is free; remembering where you have")
print("  been is not.")

assert graph_size(node) > D.CHAIN_LENGTH

print()
print("=" * 74)
print("6. A measurement that corrects sections 1 and 2")
print("=" * 74)
print()
print("  Everything above multiplied a CONSTANT factor. Real layers do not")
print("  work that way: a local rate depends on where it is evaluated, and")
print("  the forward pass moves that point. So stack tanh on tanh on tanh and")
print("  measure what actually happens.")
print()


def stacked_tanh(depth):
    def deep(vals):
        node = vals[0]
        for _ in range(depth):
            node = node.tanh()
        return node

    return deep


print("     depth    gradient at x = 0.9     ratio to the row above")
print("     " + "-" * 58)
previous = None
measured = {}
for depth in (1, 5, 10, 20, 40, 80, 160):
    value = reverse_mode_gradient(stacked_tanh(depth), [0.9])[0][0]
    measured[depth] = value
    ratio = "-" if previous is None else f"{previous / value:.3f}"
    print(f"     {depth:<8d} {value:<23.6e} {ratio}")
    previous = value
print()
single = measured[1]
naive = single**40
print("  Now the naive prediction. tanh's slope at 0.9 is about")
print(f"  {single:.6f}, so forty tanh layers 'should' multiply the gradient")
print(f"  by that forty times over:")
print()
print(f"      {single:.6f} ** 40 = {naive:.6e}     the prediction")
print(f"      measured at depth 40 = {measured[40]:.6e}     the measurement")
print(f"      the measurement is larger by a factor of {measured[40] / naive:.3e}")
print()
print("  Ten orders of magnitude. The prediction is not slightly off, it is")
print("  wrong in kind, and the reason is worth more than the number: each")
print("  tanh pulls its input closer to 0, and tanh's slope AT 0 is 1. The")
print("  deeper the stack goes, the closer every local rate creeps back")
print("  towards 1, so the product decays like a power of the depth rather")
print("  than exponentially.")
print()
print("  A product of constants is the wrong model for a product of rates")
print("  that depend on where they are evaluated. Sections 1 and 2 are still")
print("  the right picture of what a chain of fixed factors does -- and a")
print("  weight matrix that is too small or too large really does behave that")
print("  way -- but 'tanh saturates, therefore gradients vanish' is a claim")
print("  that has to be measured on the network in front of you rather than")
print("  assumed from the shape of the curve.")

assert measured[40] > 1e9 * naive
assert naive < 1e-12
assert list(measured.values()) == sorted(measured.values(), reverse=True)

print()
print("07_vanishing_and_exploding.py: every assertion held.")
