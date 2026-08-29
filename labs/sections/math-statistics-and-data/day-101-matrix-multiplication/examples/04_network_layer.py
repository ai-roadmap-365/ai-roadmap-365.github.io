"""One layer of a neural network is a matrix multiply plus a vector add.

Run from inside this directory:

    ../.venv/bin/python3 04_network_layer.py

Every number below is small enough to work out with a pen, and the hand-worked
answers in dataset.py were derived that way before anything was run. This is
the operation that consumes essentially all the compute in training any model
you will ever use. It is `X @ W + b`, and that is the whole of it.
"""

import numpy as np

from dataset import BIAS, LAYER_OUT, W, X, XW
from matmul import add_bias, matmul_loops, multiplication_count, shape

npX = np.array(X)
npW = np.array(W)
npB = np.array(BIAS)

print("=" * 74)
print("1. The three things a layer is made of")
print("=" * 74)
print(f"  X, the batch      shape {npX.shape}  {npX.tolist()}")
print("      two examples, three features each. One example per ROW — that is")
print("      the convention almost every framework uses, and the reason the")
print("      weights end up on the right-hand side of the multiply.")
print(f"  W, the weights    shape {npW.shape}  {npW.tolist()}")
print("      three inputs in, two outputs out. Column j holds the weights that")
print("      produce output j. Read it that way and the shape rule is obvious")
print("      rather than memorised.")
print(f"  b, the bias       shape {npB.shape}     {npB.tolist()}")
print("      one number per output unit. Not per example — per OUTPUT.")

print()
print("=" * 74)
print("2. The multiply, worked out by hand")
print("=" * 74)
print("  Entry (i, j) of X @ W is example i dotted with the weights of output j.")
print()
print("  example 0 = [1, 2, 0]")
print("    output 0, weights [2, -1, 0]:  1*2 + 2*(-1) + 0*0  =  2 - 2 + 0  =  0")
print("    output 1, weights [0,  1, 4]:  1*0 + 2*1    + 0*4  =  0 + 2 + 0  =  2")
print("  example 1 = [0, 1, 3]")
print("    output 0, weights [2, -1, 0]:  0*2 + 1*(-1) + 3*0  =  0 - 1 + 0  = -1")
print("    output 1, weights [0,  1, 4]:  0*0 + 1*1    + 3*4  =  0 + 1 + 12 = 13")
print()
product = npX @ npW
print(f"  X @ W = {product.tolist()}   shape {product.shape}")
assert product.tolist() == XW
assert product.shape == (2, 2)
print("  Two examples in, two outputs each. The 3 was consumed — it had to")
print("  match, and it is gone from the answer. The 2 on the left survived")
print("  because it is the batch, and the 2 on the right survived because it is")
print("  the width of the layer. Neither of those numbers is the same kind of")
print("  thing, and they are only both 2 here by accident.")

print()
print("=" * 74)
print("3. The bias, broadcast across the rows")
print("=" * 74)
print(f"  b has shape {npB.shape} and X @ W has shape {product.shape}.")
print("  Broadcasting (Day 100) lines the shapes up from the right: (2, 2)")
print("  against (2,) pads to (1, 2), the trailing 2s match, and the 1 stretches")
print("  down the rows. So EVERY example gets the same bias:")
print()
print("    example 0: [ 0,  2] + [5, -2] = [5,  0]")
print("    example 1: [-1, 13] + [5, -2] = [4, 11]")
print()
out = product + npB
print(f"  X @ W + b = {out.tolist()}   shape {out.shape}")
assert out.tolist() == LAYER_OUT

print()
print("  Written out as an explicit loop, with no broadcasting at all:")
by_hand = add_bias(matmul_loops(X, W), BIAS)
print(f"  add_bias(matmul_loops(X, W), b) = {by_hand}")
assert by_hand == LAYER_OUT
print("  Same answer. The broadcast is shorthand for that loop, and knowing it")
print("  is shorthand is what stops it being magic.")

print()
print("  And the mistake worth meeting once: a bias of the wrong length.")
try:
    product + np.array([5, -2, 7])
except ValueError as exc:
    print(f"    (2, 2) + (3,) raises {type(exc).__name__}: {exc}")
    assert "could not be broadcast" in str(exc)
else:  # pragma: no cover
    raise AssertionError("a length-3 bias on a 2-wide layer should have raised")
print("    One bias per OUTPUT. A layer two units wide takes two numbers, and")
print("    the exception is the shape rule from Day 100 doing its job.")

print()
print("=" * 74)
print("3b. A convention clash worth meeting head on")
print("=" * 74)
print("  02_composition.py said matrices compose RIGHT TO LEFT: in A @ B, B runs")
print("  first, because B is the one standing next to the vector in A @ (B @ v).")
print("  Then this script writes a layer as X @ W, with the data on the LEFT and")
print("  the transformation on the right. Those two look like they contradict")
print("  each other. They do not, and the reason is worth knowing.")
print()
print("  It comes down to whether a vector is a column or a row.")
print()
print("    Column convention (textbooks, 02_composition.py):")
print("      v is (n, 1), the matrix goes on the LEFT:      y = A @ v")
print("      chaining reads right to left:                  y = B @ (A @ v)")
print()
print("    Row convention (this script, and every framework you will use):")
print("      each example is a ROW, the matrix goes on the RIGHT: y = x @ A")
print("      chaining reads left to right:                        y = x @ A @ B")
print()
print("  Both compute the same thing. One is the transpose of the other:")
v_row = np.array([1, 2, 0])
A_col = npW.T  # (2, 3): the same layer written for column vectors
print(f"      row form:    x @ W        = {(v_row @ npW).tolist()}")
print(f"      column form: W.T @ x      = {(A_col @ v_row).tolist()}")
assert np.array_equal(v_row @ npW, A_col @ v_row)
print("  Identical, because (x @ W) and (W.T @ x) are the same numbers written")
print("  the two different ways round.")
print()
print("  Why frameworks chose rows: a batch is a stack of examples, and stacking")
print("  them as rows means example i lives at X[i], which is how every dataset,")
print("  CSV file and database table you have met since Day 65 is already laid")
print("  out. The cost is this one moment of confusion, and you have now had it.")

print()
print("=" * 74)
print("4. What changes when the batch grows, and what does not")
print("=" * 74)
bigger = np.array([[1, 2, 0], [0, 1, 3], [2, 0, 1], [1, 1, 1]])
bigger_out = bigger @ npW + npB
print(f"  a batch of {bigger.shape[0]} instead of {npX.shape[0]}: {bigger.shape} @ {npW.shape} "
      f"-> {(bigger @ npW).shape}, plus b -> {bigger_out.shape}")
print(f"  {bigger_out.tolist()}")
assert bigger_out.shape == (4, 2)
assert bigger_out[:2].tolist() == LAYER_OUT
print("  The first two rows are unchanged, because each row is computed")
print("  independently of the others. W did not change shape and b did not")
print("  change shape — only the batch dimension moved. That independence is")
print("  exactly what makes a batch worth having: the same weights, reused")
print("  across every example, in one multiply.")

print()
print("=" * 74)
print("5. Stacking two layers is multiplying three matrices")
print("=" * 74)
W2 = np.array([[1, 0, 2], [3, 1, 0]])  # (2, 3): the 2-wide layer feeds a 3-wide one
b2 = np.array([0, 1, -1])
hidden = npX @ npW + npB
final = hidden @ W2 + b2
print(f"  layer 1: X {npX.shape} @ W {npW.shape} + b {npB.shape} -> {hidden.shape}")
print(f"           {hidden.tolist()}")
print(f"  layer 2: h {hidden.shape} @ W2 {W2.shape} + b2 {b2.shape} -> {final.shape}")
print(f"           {final.tolist()}")
assert hidden.tolist() == LAYER_OUT
assert final.shape == (2, 3)
print()
print("  The shapes chain: 3 features in, 2 hidden, 3 out. Each layer's output")
print("  width must equal the next layer's input width, and that is the shape")
print("  rule again, wearing a different hat.")
print()
print("  Now the honest caveat, and it matters. Without a non-linear function")
print("  between the layers, those two layers COLLAPSE into one:")
collapsed_W = npW @ W2
collapsed_b = npB @ W2 + b2
collapsed = npX @ collapsed_W + collapsed_b
print(f"      W @ W2 has shape {collapsed_W.shape}, and X @ (W @ W2) + (b @ W2 + b2) =")
print(f"      {collapsed.tolist()}")
assert collapsed.tolist() == final.tolist()
print("      — identical to running the two layers separately. That is")
print("      associativity, and it is the reason activation functions exist:")
print("      a stack of pure matrix multiplies is just one matrix multiply, no")
print("      matter how many layers deep you make it.")

print()
print("=" * 74)
print("6. The cost, at a size people actually train")
print("=" * 74)
print("  This layer:")
m, n = shape(X)
_, p = shape(W)
print(f"      ({m}, {n}) @ ({n}, {p}) = {multiplication_count(m, n, p)} multiplications. You could do it on paper.")
for batch, d_in, d_out, label in [
    (32, 768, 768, "one modest layer, batch 32"),
    (1024, 4096, 4096, "one wide layer, batch 1024"),
]:
    count = multiplication_count(batch, d_in, d_out)
    print(f"  {label}:")
    print(f"      ({batch}, {d_in}) @ ({d_in}, {d_out}) = {count:,} multiplications")
assert multiplication_count(32, 768, 768) == 18_874_368
assert multiplication_count(1024, 4096, 4096) == 17_179_869_184
print()
print("  Seventeen billion multiplications, for ONE layer, on ONE batch, in ONE")
print("  forward pass. A model has many layers, training does a backward pass")
print("  too, and you repeat the whole thing for every batch in the dataset,")
print("  many times over. This is where the compute goes. Not somewhere else.")

print()
print("04_network_layer.py: every assertion held.")
